from django.contrib import admin

from .models import *

class WeekAmountAdmin(admin.ModelAdmin):
    list_display = ("user", "data", "last_update", "times_update")
    list_display_links = ('user', 'data')
    list_filter = ('user',)