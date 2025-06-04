from .models import (Spents, Earnings, MonoToken, MonoAccount,
                     Account, SpentCategory, EarnCategory, UserCategory, UserProfile)
from .services.mono_api import MonobankAPI
from .forms import RegisterUserForm, LoginUserForm, TransactionForm

from django.shortcuts import render, redirect, HttpResponseRedirect
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db import transaction
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta, date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import AccessMixin
from django.views import View
from django.views.generic import CreateView
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, logout
from django.utils import timezone

from operator import attrgetter
import json
import secrets
from decimal import Decimal
from .tasks import test_task


class LoginRequiredMixin(AccessMixin):
    login_url = reverse_lazy('auth')
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
    

class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'finance/register.html'
    success_url = '/login'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('profile')
        return super().get(request, *args, **kwargs)

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

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('profile')
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        next_url = self.request.GET.get('next') or self.request.POST.get('next')
        if next_url:
            return next_url
        return reverse_lazy('profile')


class LogoutUser(View):
    def get(self, request):
        logout(request)
        return redirect('auth')


class HomeView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return render(request, 'finance/index.html')
        
        user_accs = Account.objects.filter(user=request.user)
        total_balance = sum(acc.balance.to_decimal() for acc in user_accs) \
            if user_accs else 0

        earn_categories = EarnCategory.objects.all()
        user_categories_e = UserCategory.objects.filter(user=request.user, is_spent='earn')
        spent_categories = SpentCategory.objects.all()
        user_categories_s = UserCategory.objects.filter(user=request.user, is_spent='spent')
        today_date = date.today().isoformat()

        data = {'total_balance': total_balance,
                'accounts': user_accs,
                'earn_categories':  earn_categories,
                'user_categories_e': user_categories_e if user_categories_e.exists() else [],
                'spent_categories': spent_categories,
                'user_categories_s': user_categories_s if user_categories_s.exists() else [],
                'today': today_date}

        return render(request, 'finance/index.html', data)

    def post(self, request):
        if not request.user:
            return render(request, 'finance/index.html')
        
        action = request.POST.get('action')
        user_accs = Account.objects.filter(user=request.user)

        if action == 'add':
            name = request.POST.get('name')
            balance = request.POST.get('balance')
            currency = request.POST.get('currency', '₴')
            if name and balance:
                Account.objects.create(
                    user=request.user,
                    name=name,
                    balance=balance,
                    currency=currency
                )

        elif action == 'add_balance':
            try:
                account_id = request.POST.get('account_id')
                category_value = request.POST.get('category')
                amount = request.POST.get('amount')
                date_str = request.POST.get('date')
                description = request.POST.get('description')

                if not all([account_id, category_value, amount, date_str]):
                    messages.error(request, "All fields (account, category, amount, date) are required.")
                    return redirect('home')

                try:
                    if int(amount) <= 0:
                        messages.error(request, "Amount must be a positive number.")
                        return redirect('home')

                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    current_time = datetime.now().time()
                    time_create = datetime.combine(date_obj.date(), current_time)
                except ValueError as e:
                    messages.error(request, "Invalid date or amount format. Please check your input.")
                    return redirect('home')

                try:
                    account = Account.objects.get(id=account_id, user=request.user)
                except Account.DoesNotExist:
                    messages.error(request, "Selected account does not exist or you don't have permission to access it.")
                    return redirect('home')

                try:
                    base_cat = EarnCategory.objects.get(value=category_value)
                    category = base_cat
                except EarnCategory.DoesNotExist:
                    try:
                        user_cat = UserCategory.objects.get(value=category_value, is_spent='earn')
                        category = user_cat
                    except UserCategory.DoesNotExist:
                        messages.error(request, "Selected category is invalid or does not exist.")
                        return redirect('home')

                Earnings.objects.create(
                    account=account,
                    category=category,
                    amount=amount,  
                    time_create=time_create,
                    time_update=time_create,
                    description=description,
                    user=request.user
                )

                account.balance = Decimal(str(account.balance.to_decimal())) + Decimal(str(amount))
                account.save()

                return redirect('home')

            except Exception as e:
                messages.error(request, f"An unexpected error occurred: {str(e)}")
                return redirect('home')
        
        elif action == 'subtract_balance':
            try:
                account_id = request.POST.get('account_id')
                category_value = request.POST.get('category')
                amount = request.POST.get('amount')
                date_str = request.POST.get('date')
                description = request.POST.get('description')

                if not all([account_id, category_value, amount, date_str]):
                    messages.error(request, "All fields (account, category, amount, date) are required.")
                    return redirect('home')

                try:
                    if int(amount) <= 0:
                        messages.error(request, "Amount must be a positive number.")
                        return redirect('home')

                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    current_time = datetime.now().time()
                    time_create = datetime.combine(date_obj.date(), current_time)
                except ValueError as e:
                    messages.error(request, "Invalid date or amount format. Please check your input.")
                    return redirect('home')

                try:
                    account = Account.objects.get(id=account_id, user=request.user)
                except Account.DoesNotExist:
                    messages.error(request, "Selected account does not exist or you don't have permission to access it.")
                    return redirect('home')

                try:
                    base_cat = SpentCategory.objects.get(value=category_value)
                    category = base_cat
                except SpentCategory.DoesNotExist:
                    try:
                        user_cat = UserCategory.objects.get(value=category_value, is_spent='spent')
                        category = user_cat
                    except UserCategory.DoesNotExist:
                        messages.error(request, "Selected category is invalid or does not exist.")
                        return redirect('home')

                Spents.objects.create(
                    account=account,
                    category=category,
                    amount=amount,  
                    time_create=time_create,
                    time_update=time_create,
                    description=description,
                    user=request.user
                )

                account.balance = Decimal(str(account.balance.to_decimal())) - Decimal(str(amount))
                account.save()

                return redirect('home')

            except Exception as e:
                messages.error(request, f"An unexpected error occurred: {str(e)}")
                return redirect('home')

        elif action == 'add_category_e':
            if not request.user.is_authenticated:
                return redirect('home')
            
            try:
                new_cat = UserCategory.objects.create(
                    user=request.user,
                    name=request.POST.get('category_name'),
                    value=(request.POST.get('category_name')).lower(),
                    icon=request.POST.get('category_icon', '📌'),
                    is_spent='earn'
                )
                return redirect('home')
            except ValueError as e:
                return redirect('home')

        elif action == 'add_category_s':
            if not request.user.is_authenticated:
                return redirect('home')
            
            try:
                new_cat = UserCategory.objects.create(
                    user=request.user,
                    name=request.POST.get('category_name'),
                    value=request.POST.get('category_name').lower(),
                    icon=request.POST.get('category_icon', '📌'),
                    is_spent='spent'
                )
                return redirect('home')
            except ValueError as e:
                return redirect('home')

        elif action == 'update':
            account_id = request.POST.get('account_id')
            name = request.POST.get('name')
            balance = request.POST.get('balance')
            currency = request.POST.get('currency')
            if account_id and name and balance:
                account = user_accs.get(id=account_id)
                account.name = name
                account.balance = balance
                account.currency = currency
                account.save()

        elif action == 'delete':
            account_id = request.POST.get('account_id')
            if account_id:
                account = user_accs.get(id=account_id)
                account.delete()

        return HttpResponseRedirect(request.path_info)


class UserProfileView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user

        if not user:
            return render(request, 'finance/404.html', status=404)

        period = request.GET.get('period', 'month')

        end_date = timezone.now()
        if period == 'week':
            start_date = end_date - relativedelta(weeks=1)
        elif period == 'month':
            start_date = end_date - relativedelta(months=1)
        elif period == 'year':
            start_date = end_date - relativedelta(years=1)
        else:
            start_date = end_date - relativedelta(months=1)

        all_spents = Spents.objects.filter(user=user)
        all_earnings = Earnings.objects.filter(user=user)

        spents = [s for s in all_spents if start_date <= s.time_create <= end_date]
        earnings = [e for e in all_earnings if start_date <= e.time_create <= end_date]

        total_spending = sum(transaction.amount.to_decimal() for transaction in spents) if spents else 0
        total_earning = sum(transaction.amount.to_decimal() for transaction in earnings) if earnings else 0

        total_all_spending = sum(transaction.amount.to_decimal() for transaction in all_spents) if all_spents else 0
        total_all_earning = sum(transaction.amount.to_decimal() for transaction in all_earnings) if all_earnings else 0

        total_all_diff = total_all_earning - total_all_spending

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'total_spending': float(total_spending),  
                'total_earning': float(total_earning),   
                'spents': [
                    {'id': s.id, 'amount': float(s.amount.to_decimal()), 'time_create': s.time_create.isoformat()}
                    for s in spents
                ], 
                'earnings': [
                    {'id': e.id, 'amount': float(e.amount.to_decimal()), 'time_create': e.time_create.isoformat()}
                    for e in earnings
                ], 
            })

        context = {
            'user': user,
            'total_spending': total_spending,
            'total_earning': total_earning,
            'total_all_spending': total_all_spending,
            'total_all_earning': total_all_earning,
            'total_all_diff': total_all_diff,
            'class': 'minus' if total_all_diff < 0 else 'plus',
            'spents': spents,
            'earnings': earnings,
            'all_spents': all_spents,
            'all_earnings': all_earnings,
            'selected_period': period,
        }
        return render(request, 'finance/profile.html', context)


class UserExpenses(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        period = request.GET.get('period', 'all')
        transaction_type = request.GET.get('transaction_type', 'all')
        sort_by = request.GET.get('sort_by', 'date_desc')

        spents = Spents.objects.filter(user=user)
        earnings = Earnings.objects.filter(user=user)

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

        if transaction_type == 'spent':
            transactions = list(spents)
        elif transaction_type == 'earning':
            transactions = list(earnings)
        else:
            transactions = list(spents) + list(earnings)

        if sort_by == 'date_asc':
            transactions = sorted(transactions, key=attrgetter('time_update'))
        elif sort_by == 'amount_desc':
            transactions = sorted(transactions, key=lambda x: x.amount.to_decimal(), reverse=True)
        elif sort_by == 'amount_asc':
            transactions = sorted(transactions, key=lambda x: x.amount.to_decimal())
        else:
            transactions = sorted(transactions, key=attrgetter('time_update'), reverse=True)

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
def link_api(request):
    if request.method == "POST":
        action = request.POST.get('action')

        if action == 'ss_api':
            set_user_api_token(request)
            try:
                profile = UserProfile.objects.get(user=request.user)
            except UserProfile.DoesNotExist:
                profile = None
            return render(request, "finance/link_api.html", {'profile': profile})

        elif action == 'mono_api':
            token = request.POST.get("mono_token")
            try:
                client_info = MonobankAPI.get_client_info(token)
                mono_token, created = MonoToken.objects.update_or_create(
                    user=request.user, defaults={"token": token}
                )
                for account in client_info["accounts"]:
                    MonoAccount.objects.update_or_create(
                        user=request.user,
                        mono_account_id=account["id"],
                        defaults={"name": account.get("type", "Unknown"), "balance": account["balance"] / 100}
                    )
                return redirect("expenses")
            except Exception as e:
                return render(request, "finance/link_api.html", {"error": str(e)})
    
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        profile = None
    return render(request, "finance/link_api.html", {'profile': profile})

@login_required
def monobank_info_view(request):
    try:
        mono_token = MonoToken.objects.get(user=request.user)
        token = mono_token.token
    except MonoToken.DoesNotExist:
        return render(request, "finance/link_api.html", {"error": "Token not found."}) 

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

@login_required
def all_mono_transactions_view(request):
    try:
        mono_token = MonoToken.objects.get(user=request.user)
    except MonoToken.DoesNotExist:
        return render(request, "finance/link_api.html", {"error": "Token not found."}) 

    token = mono_token.token
    errors = []
    try:
        client_info = MonobankAPI.get_client_info(token)
        account_id = client_info["accounts"][0]["id"]
        transactions = MonobankAPI.get_all_transactions(token, account_id)

        transactions.sort(key=lambda tx: tx.get("time", 0), reverse=True)
    except Exception as e:
        transactions = []
        errors.append(e)

    for tx in transactions:
        tx['amount_norm'] = tx['amount'] / 100
        tx['time'] = datetime.fromtimestamp(tx['time'])

    return render(request, "finance/all_transactions.html", {
        "transactions": transactions,
        'errors': errors,
    })

def generate_unique_token():
    while True:
        token = secrets.token_hex(16)
        existing = UserProfile.objects.filter(api_key=token).exists()
        if not existing:
            return token

def set_user_api_token(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    if user_profile.api_key is None:
        user_profile.api_key = generate_unique_token()
        user_profile.save()

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

    trans_amount = transaction.amount.to_decimal()

    if not transaction:
        return render(request, 'finance/404.html', status=404)

    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save(user=user)
            acc = transaction.account
            acc_bal = acc.balance.to_decimal()
            
            acc.balance = acc_bal + (trans_amount - form.cleaned_data['amount'])
            acc.save()

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

def delete_api_token(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        user_profile.delete()
    except:
        user_profile = None
    
    return render(request, 'finance/link_api.html')

# Outer Api

def check_api_token(view_func):
    def wrapper(request, *args, **kwargs):
        api_token = request.headers.get('Authorization', '')
        if api_token.startswith('Bearer '):
            api_token = api_token[7:]
        else:
            return JsonResponse({'error': 'Token must statr with Bearer'}, status=401)
        if not api_token:
            return JsonResponse({'error': 'Token not given'}, status=401)
        
        try:
            profile = UserProfile.objects.get(api_key=api_token)
            request.api_user = profile.user
        except UserProfile.DoesNotExist:
            return JsonResponse({'error': 'Invalid token'}, status=401)
        
        return view_func(request, *args, **kwargs)
    return wrapper

@csrf_exempt
@check_api_token
@require_http_methods(["GET"])
def api_user_accounts(request):
    try:
        accounts = Account.objects.filter(user=request.api_user)
    except:
        return JsonResponse({'error': 'Accounts cannot be found'}, status=401)

    if accounts:
        data = {
            'username': request.api_user.username,
            'accounts': [
                {
                    'account': account.name,
                    'balance': account.balance.to_decimal(),
                }
                for account in accounts
            ]
        }

        return JsonResponse(data)
    return JsonResponse({'error': 'Accounts cannot be found'}, status=401)