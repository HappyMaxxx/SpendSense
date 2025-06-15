from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from finance.views import LoginRequiredMixin

@login_required
def reports_view(request):
    # TODO
    return render(request, 'stats/reports.html')