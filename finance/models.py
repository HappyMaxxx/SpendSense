from django.db import models
from django.contrib.auth.models import User
from fernet_fields import EncryptedTextField


class MonoToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = EncryptedTextField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Token for {self.user.username}"


class MonoAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mono_account_id = models.CharField(max_length=255)
    name = models.CharField(max_length=100, blank=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Account {self.name} for {self.user.username}"
    

class Spents(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Trans: {self.amount} - {self.category}"
    

class Earnings(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Earn: {self.amount} - {self.category}"


class Account(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='₴')

    def __str__(self):
        return f"{self.name} {self.user} ({self.balance} {self.currency})"