from .models import Spents, Earnings, MonoToken, Account
from .services.mono_api import MonobankAPI
from .forms import RegisterUserForm, LoginUserForm, TransactionForm

from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db import transaction
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from django.db.models import Sum

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import AccessMixin
from django.views import View
from django.views.generic import CreateView
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, logout
from django.utils import timezone

from operator import attrgetter
import json
import random
from .tasks import test_task


class LoginRequiredMixin(AccessMixin):
    login_url = reverse_lazy('auth')
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


def index(request):
    return render(request, 'finance/index.html')


class AddTransactionView(LoginRequiredMixin, View):
    def get(self, request):
        form = TransactionForm()
        return render(request, 'finance/new_transaction.html', {'form': form})
    
    def post(self, request):
            form = TransactionForm(request.POST)
            if form.is_valid():
                form.save(user=request.user)
                return redirect('expenses')
            

class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'finance/register.html'
    success_url = '/login'

    @transaction.atomic
    def form_valid(self, form):
        user = form.save(commit=False)
        if User.objects.filter(email=user.email).exists():
            form.add_error('email', "User with this email already exists")
            return self.form_invalid(form)
        
        user.save()

        login(self.request, user)
        return redirect('profile')


class LoginUser(LoginView):
    form_class =  LoginUserForm
    template_name = 'finance/login.html'

    def get_success_url(self):
        return reverse_lazy('profile')


class LogoutUser(View):
    def get(self, request):
        logout(request)
        return redirect('auth')


class UserProfile(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user

        if not user:
            return render(request, 'finance/404.html', status=404)

        period = request.GET.get('period', 'month')

        end_date = datetime.now()
        if period == 'week':
            start_date = end_date - relativedelta(weeks=1)
        elif period == 'month':
            start_date = end_date - relativedelta(months=1)
        elif period == 'year':
            start_date = end_date - relativedelta(years=1)
        else:
            start_date = end_date - relativedelta(months=1)

        spents = Spents.objects.filter(
            user=user,
            time_create__range=[start_date, end_date]
        )
        earnings = Earnings.objects.filter(
            user=user,
            time_create__range=[start_date, end_date]
        )

        total_spending = sum(transaction.amount.to_decimal() for transaction in spents) \
            if spents else 0
        total_earning = sum(transaction.amount.to_decimal() for transaction in earnings) \
            if earnings else 0

        # Check if the request is AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'total_spending': float(total_spending),  # Convert to float for JSON serialization
                'total_earning': float(total_earning),
            })

        context = {
            'user': user,
            'total_spending': total_spending,
            'total_earning': total_earning,
            'selected_period': period,
        }
        return render(request, 'finance/profile.html', context)


class UserExpenses(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        period = request.GET.get('period', 'all')
        transaction_type = request.GET.get('transaction_type', 'all')
        sort_by = request.GET.get('sort_by', 'date_desc')

        # Фільтрація за типом транзакцій
        spents = Spents.objects.filter(user=user)
        earnings = Earnings.objects.filter(user=user)

        # Фільтрація за періодом
        now = timezone.now()
        if period == 'year':
            spents = spents.filter(time_update__gte=now - timedelta(days=365))
            earnings = earnings.filter(time_update__gte=now - timedelta(days=365))
        elif period == 'month':
            spents = spents.filter(time_update__gte=now - timedelta(days=30))
            earnings = earnings.filter(time_update__gte=now - timedelta(days=30))
        elif period == 'week':
            spents = spents.filter(time_update__gte=now - timedelta(days=7))
            earnings = earnings.filter(time_update__gte=now - timedelta(days=7))

        # Об'єднання транзакцій
        if transaction_type == 'spent':
            transactions = list(spents)
        elif transaction_type == 'earning':
            transactions = list(earnings)
        else:
            transactions = list(spents) + list(earnings)

        # Сортування
        if sort_by == 'date_asc':
            transactions = sorted(transactions, key=attrgetter('time_update'))
        elif sort_by == 'amount_desc':
            transactions = sorted(transactions, key=lambda x: x.amount.to_decimal(), reverse=True)
        elif sort_by == 'amount_asc':
            transactions = sorted(transactions, key=lambda x: x.amount.to_decimal())
        else:  # date_desc
            transactions = sorted(transactions, key=attrgetter('time_update'), reverse=True)

        # Обчислення загальних сум
        total_expenses = sum(spent.amount.to_decimal() for spent in spents)
        total_earnings = sum(earning.amount.to_decimal() for earning in earnings)
        profit = total_earnings - total_expenses

        context = {
            'user': user,
            'transactions': transactions,
            'total_expenses': total_expenses,
            'total_earnings': total_earnings,
            'profit': profit,
            'period': period,
            'transaction_type': transaction_type,
            'sort_by': sort_by,
        }
        return render(request, 'finance/expenses.html', context)

@login_required
def link_monobank(request):
    if request.method == "POST":
        token = request.POST.get("mono_token")
        try:
            client_info = MonobankAPI.get_client_info(token)
            mono_token, created = MonoToken.objects.update_or_create(
                user=request.user, defaults={"token": token}
            )
            for account in client_info["accounts"]:
                Account.objects.update_or_create(
                    user=request.user,
                    mono_account_id=account["id"],
                    defaults={"name": account.get("type", "Unknown"), "balance": account["balance"] / 100}
                )
            return redirect("expenses")
        except Exception as e:
            return render(request, "finance/link_mono.html", {"error": str(e)})
    return render(request, "finance/link_mono.html")

@login_required
def monobank_info_view(request):
    try:
        mono_token = MonoToken.objects.get(user=request.user)
        token = mono_token.token
    except MonoToken.DoesNotExist:
        return render(request, "finance/link_mono.html", {"error": "Token not found."}) 

    try:
        client_info = MonobankAPI.get_client_info(token)
        raw_json = json.dumps(client_info, indent=2, ensure_ascii=False) 
    except Exception as e:
        client_info = None
        raw_json = None

    return render(request, "finance/client_info.html", {
        "client_info": client_info,
        "raw_json": raw_json
    })

# API
class PageNotFoundView(View):
    def get(self, request, exception):
        return render(request, 'finance/404.html', status=404)


def check_username(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username', None)
        user = User.objects.filter(username=username).first()
        if username and user:
            return JsonResponse({'error': 'This username is already taken.'}, status=200)

        return JsonResponse({'error': ''}, status=200)
    
def edit_transaction(request, transaction_id, transaction_type):
    user = request.user
    transaction = None

    if transaction_type == 0:
        transaction = Spents.objects.filter(id=transaction_id, user=user).first()
    elif transaction_type == 1:
        transaction = Earnings.objects.filter(id=transaction_id, user=user).first()

    if not transaction:
        return render(request, 'finance/404.html', status=404)

    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save(user=user)
            return redirect('expenses')
    else:
        form = TransactionForm(instance=transaction, initial={'transaction_type': 'expense' if transaction_type == 0 else 'income'})

    context = {
        'form': form,
        'transaction': transaction,
        'transaction_id': transaction_id,
        'transaction_type': transaction_type,
    }
    return render(request, 'finance/edit_transaction.html', context)

def delete_transaction(request, transaction_id, transaction_type):
    user = request.user
    transaction = None

    if transaction_type == 0:
        transaction = Spents.objects.filter(id=transaction_id, user=user).first()
    elif transaction_type == 1:
        transaction = Earnings.objects.filter(id=transaction_id, user=user).first()
    
    if not transaction:
        return render(request, 'finance/404.html', status=404)
    
    transaction.delete()
    return redirect('expenses')

def delete_mono_token(request):
    user = request.user
    try:
        mono_token = MonoToken.objects.get(user=user)
        mono_token.delete()
    except MonoToken.DoesNotExist:
        pass
    return redirect('profile')