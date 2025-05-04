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