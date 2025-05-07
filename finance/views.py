from django.shortcuts import render, redirect
from .models import Transaction, Earnings
from .forms import RegisterUserForm, LoginUserForm
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

products = {
    'milk': 1.5,
    'bread': 2.0,
    'eggs': 3.0,
    'cheese': 4.0,
    'chocolate': 2.5,
    'coffee': 5.0,
    'tea': 3.5,
    'juice': 2.0,
    'water': 1.0,
    'snacks': 2.5,
    'fruits': 3.0,
    'vegetables': 2.0,
    'cereal': 4.0,
    'pasta': 2.5
}


class LoginRequiredMixin(AccessMixin):
    login_url = reverse_lazy('auth')
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


def index(request):
    return render(request, 'finance/index.html')


class MakeNewTransaction(LoginRequiredMixin, View):
    def get(self, request):
        trans_products = random.sample(list(products.keys()), 2)

        transaction = Transaction.objects.create(
            user=request.user,
            amount=products[trans_products[0]] + products[trans_products[1]],
            category='shopping',
            description=f'{trans_products[0]} and {trans_products[1]}',
        )

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

        transactions = Transaction.objects.filter(
            user=user,
            time_create__range=[start_date, end_date]
        )

        total_spending = sum(transaction.amount.to_decimal() for transaction in transactions) \
            if transactions else 0

        # Check if the request is AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'total_spending': float(total_spending),  # Convert to float for JSON serialization
            })

        context = {
            'user': user,
            'transactions': transactions,
            'total_spending': total_spending,
            'selected_period': period,
        }
        return render(request, 'finance/profile.html', context)

class UserExpenses(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        transactions = Transaction.objects.filter(user=user).order_by('-time_update')
        earnings = Earnings.objects.filter(user=user).order_by('-time_update')
        total_expenses = sum(transaction.amount.to_decimal() for transaction in transactions)
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
