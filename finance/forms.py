import re
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import *
from django.contrib import messages

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
    category = forms.ChoiceField(choices=[])

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

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None) 
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        transaction_type = self.data.get('transaction_type') or self.initial.get('transaction_type')
        if transaction_type == 'income':
            earn_categories = list(EarnCategory.objects.all().values('value', 'name'))
            user_earn_categories = list(UserCategory.objects.filter(user=self.user, is_spent='earn').values('value', 'name'))
            categories = [(cat['value'], cat['name']) for cat in earn_categories + user_earn_categories]
        else:
            spent_categories = list(SpentCategory.objects.all().values('value', 'name'))
            user_spent_categories = list(UserCategory.objects.filter(user=self.user, is_spent='spent').values('value', 'name'))
            categories = [(cat['value'], cat['name']) for cat in spent_categories + user_spent_categories]
        self.fields['category'].choices = categories
        if self.instance and self.instance.pk:
            self.initial['category'] = self.instance.category

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

    def clean_category(self):
        category_value = self.cleaned_data.get('category')
        transaction_type = self.cleaned_data.get('transaction_type')
        
        if transaction_type == 'income':
            try:
                EarnCategory.objects.get(value=category_value)
            except EarnCategory.DoesNotExist:
                try:
                    UserCategory.objects.get(value=category_value, is_spent='earn', user=self.user)
                except UserCategory.DoesNotExist:
                    raise forms.ValidationError('Invalid category selected.')
        else:
            try:
                SpentCategory.objects.get(value=category_value)
            except SpentCategory.DoesNotExist:
                try:
                    UserCategory.objects.get(value=category_value, is_spent='spent', user=self.user)
                except UserCategory.DoesNotExist:
                    raise forms.ValidationError('Invalid category selected.')
        return category_value

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