from django.db import models
from django.contrib.auth.models import User


class Account(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='₴')

    def __str__(self):
        return f"{self.name} {self.user} ({self.balance} {self.currency})"


class Spents(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time_create = models.DateTimeField()
    time_update = models.DateTimeField()
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='spents')
    
    def __str__(self):
        return f"Trans: {self.amount} - {self.category}"
    

class Earnings(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time_create = models.DateTimeField()
    time_update = models.DateTimeField()
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='earnings')

    def __str__(self):
        return f"Earn: {self.amount} - {self.category}"
    
    
class EarnCategory(models.Model):
    name =  models.CharField(max_length=100)
    value = models.CharField(max_length=100)
    icon = models.CharField(max_length=4)

    def __str__(self):
        return f'{self.value}'


class SpentCategory(models.Model):
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=100)
    icon = models.CharField(max_length=4)

    def __str__(self):
        return f'{self.value}'
    

class UserCategory(models.Model):
    TYPE_CHOICES = [
        ('spent', 'Spent'),
        ('earn', 'Earn'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=100)
    icon = models.CharField(max_length=4)
    is_spent = models.CharField(max_length=20, choices=TYPE_CHOICES, default='spent')

    def __str__(self):
        if self.is_spent == 'spent':
            return f'{self.value}'
        else:
            return f'{self.value}'


class UserProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_profile')
    api_key = models.CharField(max_length=32, unique=True, blank=True, null=True)
    telegram_id = models.BigIntegerField(null=True, blank=True, unique=True)