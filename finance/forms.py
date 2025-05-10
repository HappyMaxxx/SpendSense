import re
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import *


class RegisterUserForm(UserCreationForm):
    username = forms.CharField(label='Username', widget=forms.TextInput(attrs={'id': 'id_username'}))
    email = forms.EmailField(label='Email', widget=forms.EmailInput())
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput())
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.is_bound and not self.is_valid():
            self.data = self.data.copy() 
            self.data['password1'] = ''  
            self.data['password2'] = '' 


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Username', widget=forms.TextInput())
    password = forms.CharField(label='Password', widget=forms.PasswordInput())


class TransactionForm(forms.ModelForm):
    TRANSACTION_TYPES = (
        ('expense', 'Expense'),
        ('income', 'Income'),
    )
    transaction_type = forms.ChoiceField(
        choices=TRANSACTION_TYPES,
        widget=forms.Select
    )

    class Meta:
        model = Spents
        fields = ['transaction_type', 'amount', 'description', 'category']
        labels = {
            'amount': 'Amount',
            'description': 'Description',
            'category': 'Category',
            'transaction_type': 'Transaction Type',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        required = {
            'description': False,
        }

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if description and len(description) > 1000:
            raise forms.ValidationError('Description is too long, max 1000 characters.')
        return description

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError('Amount must be positive.')
        return amount

    def save(self, commit=True, user=None):
        transaction_type = self.cleaned_data.get('transaction_type')
        instance = self.instance

        if not instance.id:
            model = Spents if transaction_type == 'expense' else Earnings
            instance = model(user=user)

        instance.amount = self.cleaned_data['amount']
        instance.description = self.cleaned_data['description']
        instance.category = self.cleaned_data['category']
        instance.user = user

        if commit:
            instance.save()
        return instance