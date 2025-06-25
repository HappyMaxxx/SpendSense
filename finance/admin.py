from django.contrib import admin

from .models import *

@admin.register(Spents)
class SpentsAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'category', 'description', 'account', 'time_create', 'time_update')
    ordering = ('-time_create',)
    list_display_links = ('user',)
    list_filter = ('category', 'account')
    search_fields = ('description',)

@admin.register(Earnings)
class EarningsAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'category', 'description', 'account', 'time_create', 'time_update')
    ordering = ('-time_create',)
    list_display_links = ('user',)
    list_filter = ('category', 'account')
    search_fields = ('description',)

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'balance', 'currency')
    list_display_links = ('name',)
    list_filter = ('user', 'currency')

@admin.register(EarnCategory)
class EarnCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'value', 'icon')
    list_display_links = ('name',)
    list_filter = ('value',)

@admin.register(SpentCategory)
class SpentCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'value', 'icon')
    list_display_links = ('name',)
    list_filter = ('value',)

@admin.register(UserCategory)
class UserCategoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'value', 'icon', 'is_spent')
    list_display_links = ('name', 'user')
    list_filter = ('value', 'is_spent')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'api_key', 'telegram_id')
    list_display_links = ('user',)