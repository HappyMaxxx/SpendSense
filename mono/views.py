from django.shortcuts import render
from .services.mono_api import MonobankAPI
from .models import MonoToken

from django.shortcuts import render, redirect
from datetime import datetime
import json

from django.contrib.auth.decorators import login_required

@login_required
def monobank_info_view(request):
    try:
        mono_token = MonoToken.objects.get(user=request.user)
        token = mono_token.token
    except MonoToken.DoesNotExist:
        return render(request, "finance/link_api.html", {"error": "Token not found."}) 

    try:
        client_info = MonobankAPI.get_client_info(token)
        raw_json = json.dumps(client_info, indent=2, ensure_ascii=False) 
    except Exception as e:
        client_info = None
        raw_json = None

    return render(request, "mono/client_info.html", {
        "client_info": client_info,
        "raw_json": raw_json
    })

@login_required
def all_mono_transactions_view(request):
    try:
        mono_token = MonoToken.objects.get(user=request.user)
    except MonoToken.DoesNotExist:
        return render(request, "finance/link_api.html", {"error": "Token not found."}) 

    token = mono_token.token
    errors = []
    try:
        client_info = MonobankAPI.get_client_info(token)
        account_id = client_info["accounts"][0]["id"]
        transactions = MonobankAPI.get_all_transactions(token, account_id)

        transactions.sort(key=lambda tx: tx.get("time", 0), reverse=True)
    except Exception as e:
        transactions = []
        errors.append(e)

    for tx in transactions:
        tx['amount_norm'] = tx['amount'] / 100
        tx['time'] = datetime.fromtimestamp(tx['time'])

    return render(request, "mono/all_transactions.html", {
        "transactions": transactions,
        'errors': errors,
    })

def delete_mono_token(request):
    user = request.user
    try:
        mono_token = MonoToken.objects.get(user=user)
        mono_token.delete()
    except MonoToken.DoesNotExist:
        pass
    return redirect('profile')