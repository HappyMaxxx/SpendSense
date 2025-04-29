from django.shortcuts import render, redirect
from .models import Transaction
from django.urls import reverse_lazy
from django.contrib.auth.mixins import AccessMixin
from django.views import View
import random

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

def make_new_transaction(request):
    trans_products = random.sample(list(products.keys()), 2)
    transaction = Transaction(
        amount=products[trans_products[0]] + products[trans_products[1]],
        category='shopping',
        description=f'{trans_products[0]} and {trans_products[1]}',
    )
    transaction.save()
    return redirect('home')


class PageNotFoundView(View):
    def get(self, request, exception):
        return render(request, 'finance/404.html', status=404)