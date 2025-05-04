from django.contrib import admin

from .models import *


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'category', 'description', 'time_create', 'time_update')
    ordering = ('-time_create',)
    list_display_links = ('amount', 'category')
    list_filter = ('category',)
    search_fields = ('description',)


admin.site.register(Transaction, TransactionAdmin)
