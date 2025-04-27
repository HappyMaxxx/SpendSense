from django.shortcuts import render, redirect
from .models import Transaction

def index(request):
    return render(request, 'finance/index.html')

def make_new_transaction(request):
    transaction = Transaction(
        amount=100,
        category='shopping',
        description='Купив хліба і молока',
    )
    transaction.save()
    return redirect('index')

def page_not_found(request, exception):
    return render(request, 'finance/404.html', status=404)