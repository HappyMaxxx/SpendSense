from django.contrib import admin

from .models import *


class SpentsAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'category', 'description', 'time_create', 'time_update')
    ordering = ('-time_create',)
    list_display_links = ('amount', 'category')
    list_filter = ('category',)
    search_fields = ('description',)


class EarningsAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'category', 'description', 'time_create', 'time_update')
    ordering = ('-time_create',)
    list_display_links = ('amount', 'category')
    list_filter = ('category',)
    search_fields = ('description',)


class MonoTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at")
    readonly_fields = ("created_at",)
    exclude = ("token",)


class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'balance', 'currency')
    list_display_links = ('name', 'user')
    list_filter = ('user', 'currency')

admin.site.register(Spents, SpentsAdmin)
admin.site.register(Earnings, EarningsAdmin)
admin.site.register(MonoToken, MonoTokenAdmin)
admin.site.register(Account, AccountAdmin)