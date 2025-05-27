from django.contrib import admin

from .models import *


class SpentsAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'category', 'description', 'account', 'time_create', 'time_update')
    ordering = ('-time_create',)
    list_display_links = ('amount', 'category', 'account')
    list_filter = ('category', 'account')
    search_fields = ('description',)


class EarningsAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'category', 'description', 'account', 'time_create', 'time_update')
    ordering = ('-time_create',)
    list_display_links = ('amount', 'category', 'account')
    list_filter = ('category', 'account')
    search_fields = ('description',)


class MonoTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at")
    readonly_fields = ("created_at",)
    exclude = ("token",)


class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'balance', 'currency')
    list_display_links = ('name', 'user')
    list_filter = ('user', 'currency')


class EarnCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'value', 'icon')
    list_display_links = ('name',)
    list_filter = ('value',)


class SpentCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'value', 'icon')
    list_display_links = ('name',)
    list_filter = ('value',)


class UserCategoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'value', 'icon', 'is_spent')
    list_display_links = ('name', 'user')
    list_filter = ('value', 'is_spent')

admin.site.register(Spents, SpentsAdmin)
admin.site.register(Earnings, EarningsAdmin)
admin.site.register(MonoToken, MonoTokenAdmin)
admin.site.register(EarnCategory, EarnCategoryAdmin)
admin.site.register(SpentCategory, SpentCategoryAdmin)
admin.site.register(UserCategory, UserCategoryAdmin)