from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from finance.views import LoginRequiredMixin
from finance.models import Spents, Earnings
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.db.models import Sum
from django.contrib import messages

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
    else:  # month
        date_from = now.replace(day=1)

    spents = Spents.objects.filter(user=request.user, time_create__gte=date_from).values('category', 'amount')

    category_totals = {}
    for item in spents:
        category = item['category']
        amount = item['amount'].to_decimal()
        if category in category_totals:
            category_totals[category] += amount
        else:
            category_totals[category] = amount

    labels = list(category_totals.keys())
    data = list(category_totals.values())

    return JsonResponse({'labels': labels, 'data': data})