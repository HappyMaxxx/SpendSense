from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from finance.views import LoginRequiredMixin
from finance.models import Spents, Earnings
from .models import WeekAmount
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.db.models import Sum
from django.contrib import messages
import json

@login_required
def reports_view(request):
    return render(request, 'stats/reports.html')

def chart_data(request):
    period = request.GET.get('period', 'month')
    now = datetime.now()

    if period == '30days':
        date_from = now - timedelta(days=30)
    elif period == 'year':
        date_from = now - timedelta(days=365)
    elif period == 'week':
        date_from = now - timedelta(days=7)
    else:  # month
        date_from = now.replace(day=1)

    spents = Spents.objects.filter(user=request.user, time_create__gte=date_from).values('category', 'amount')

    category_totals = {}
    for item in spents:
        category = item['category']
        amount = item['amount']
        if category in category_totals:
            category_totals[category] += amount
        else:
            category_totals[category] = amount

    labels = list(category_totals.keys())
    data = list(category_totals.values())

    return JsonResponse({'labels': labels, 'data': data})

def fetch_weekly_amount_data(user):
    today = timezone.now().date()
    start_of_this_week = today - timedelta(days=today.weekday())
    start_of_last_week = start_of_this_week - timedelta(days=7)

    daily_sums = []
    for i in range(7):
        day_date = start_of_this_week + timedelta(days=i)
        
        total = Spents.objects.filter(
            user=user,
            time_create__date=day_date
        ).aggregate(total=Sum('amount'))['total'] or 0
        daily_sums.append(float(total))

    return daily_sums

@login_required
def weekly_chart_data(request):
    current_week_data = fetch_weekly_amount_data(request.user)
    
    week_amount, created = WeekAmount.objects.get_or_create(
        user=request.user,
        defaults={'data': json.dumps([0] * 7)}
    )
    
    updated = week_amount.update_data(fetch_weekly_amount_data)
    
    average_week_data = week_amount.get_data()
    
    return JsonResponse({
        'current_week': current_week_data,
        'average_week': average_week_data
    })