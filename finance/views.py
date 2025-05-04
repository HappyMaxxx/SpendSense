from django.shortcuts import render, redirect
from .models import Transaction
from .forms import RegisterUserForm, LoginUserForm
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db import transaction

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

        return redirect('home')


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
        return redirect('home')


class LoginUser(LoginView):
    form_class =  LoginUserForm
    template_name = 'finance/login.html'

    def get_success_url(self):
        return reverse_lazy('home')


class LogoutUser(View):
    def get(self, request):
        logout(request)
        return redirect('auth')
    

class PageNotFoundView(View):
    def get(self, request, exception):
        return render(request, 'finance/404.html', status=404)
    
# API
def check_username(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username', None)
        user = User.objects.filter(username=username).first()
        if username and user:
            return JsonResponse({'error': 'This username is already taken.'}, status=200)

        return JsonResponse({'error': ''}, status=200)
