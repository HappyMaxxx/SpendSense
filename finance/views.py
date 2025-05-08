from django.shortcuts import render, redirect
from .models import Spents, Earnings
from .forms import RegisterUserForm, LoginUserForm, TransactionForm
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db import transaction
from dateutil.relativedelta import relativedelta
from datetime import datetime
from django.db.models import Sum

from django.contrib.auth.mixins import AccessMixin
from django.views import View
from django.views.generic import CreateView
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, logout

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
        spents = Spents.objects.filter(user=user).order_by('-time_update')
        earnings = Earnings.objects.filter(user=user).order_by('-time_update')
        transactions = list(spents) + list(earnings)
        total_expenses = sum(spent.amount.to_decimal() for spent in spents)
        total_earnings = sum(earning.amount.to_decimal() for earning in earnings)
        
        profit = total_earnings - total_expenses

        context = {
            'user': user,
            'transactions': transactions,
            'total_expenses': total_expenses,
            'total_earnings': total_earnings,
            'profit': profit,
        }
        return render(request, 'finance/expenses.html', context)
    
    
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
