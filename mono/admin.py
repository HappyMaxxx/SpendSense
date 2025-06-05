from django.contrib import admin

from .models import *

class MonoTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at")
    readonly_fields = ("created_at",)
    exclude = ("token",)

admin.site.register(MonoToken, MonoTokenAdmin)