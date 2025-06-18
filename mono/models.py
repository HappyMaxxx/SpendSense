from django.db import models
from django.contrib.auth.models import User
from encrypted_model_fields.fields import EncryptedCharField

class MonoToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = EncryptedCharField(max_length=255)
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