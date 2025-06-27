from finance.models import (Spents, Earnings, Account, SpentCategory,
                     EarnCategory, UserCategory)

from django.http import JsonResponse
from datetime import datetime, timedelta

from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime
from .decorators import check_api_token, time_logger

@csrf_exempt
@time_logger
@check_api_token
@require_http_methods(["GET"])
def api_check_token(request):
    return JsonResponse({
        'status': 'valid',
        'user': request.api_user.username
    })

@csrf_exempt
@time_logger
@check_api_token
@require_http_methods(["GET"])
def api_user_accounts(request):
    try:
        accounts = Account.objects.filter(user=request.api_user)
    except:
        return JsonResponse({'error': 'Accounts cannot be found'}, status=401)

    if accounts:
        data = {
            'user': request.api_user.username,
            'accounts': [
                {
                    'account': account.name,
                    'balance': account.balance,
                }
                for account in accounts
            ]
        }

        return JsonResponse(data)
    return JsonResponse({'error': 'Accounts cannot be found'}, status=401)

@csrf_exempt
@time_logger
@check_api_token
@require_http_methods(["GET"])
def api_user_transactions(request):
    user = request.api_user
    from_param = request.GET.get('from')
    to_param = request.GET.get('to')

    try:
        if from_param:
            from_date = parse_datetime(from_param)
        else:
            from_date = datetime.now() - timedelta(days=30)

        if to_param:
            to_date = parse_datetime(to_param)
        else:
            to_date = datetime.now()

        spents = Spents.objects.filter(user=user)
        earnings = Earnings.objects.filter(user=user)

        spents = spents.filter(time_update__range=(from_date, to_date))
        earnings = earnings.filter(time_update__range=(from_date, to_date))

        if spents and earnings:
            transactions = list(spents) + list(earnings)
        elif earnings:
            transactions = list(earnings)
        elif spents:
            transactions = list(spents)
        else:
            transactions = []

    except Exception as e:
        return JsonResponse({'error': 'Invalid date format. Use ISO 8601 (e.g., 2024-06-01T00:00:00)'}, status=400)

    if transactions:
        data = {
            'user': request.api_user.username,
            'transactions': [
                {   
                    'type': 'spent' if str(transaction).startswith("Trans") else 'earn',
                    'amount': transaction.amount,
                    'category': transaction.category,
                    'description': transaction.description,
                    'account': transaction.account.name,
                    'time_create': transaction.time_create.isoformat(),
                    'time_update': transaction.time_update.isoformat(),
                }
                for transaction in transactions
            ]
        }
        return JsonResponse(data)

    return JsonResponse({'error': 'Transactions cannot be found'}, status=404)

@csrf_exempt
@time_logger
@check_api_token
@require_http_methods(["GET"])
def api_categories_get(request):
    user = request.api_user
    type_param = request.GET.get('type')  # 'spent', 'earn' or None
    user_param = request.GET.get('user')  # 'true', 'false' or None

    include_user = user_param == 'true'
    categories = []

    try:
        if type_param == 'spent':
            categories += list(SpentCategory.objects.all())
            if include_user:
                categories = list(UserCategory.objects.filter(user=user, is_spent='spent'))
            elif user_param is None:
                categories += list(UserCategory.objects.filter(user=user, is_spent='spent'))

        elif type_param == 'earn':
            categories += list(EarnCategory.objects.all())
            if include_user:
                categories = list(UserCategory.objects.filter(user=user, is_spent='earn'))
            elif user_param is None:
                categories += list(UserCategory.objects.filter(user=user, is_spent='earn'))

        elif type_param is None:
            categories += list(SpentCategory.objects.all()) + list(EarnCategory.objects.all())
            if include_user:
                categories = list(UserCategory.objects.filter(user=user))
            elif user_param is None:
                categories += list(UserCategory.objects.filter(user=user))

        else:
            return JsonResponse({'error': 'Invalid type parameter. Must be "spent", "earn", or omitted.'}, status=400)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

    if categories:
        data = {
            'user': request.api_user.username,
            'categories': [
            {
                'name': cat.name,
                'value': cat.value,
                'icon': getattr(cat, 'icon', None),
                'type': getattr(cat, 'is_spent', 'earn' if isinstance(cat, EarnCategory) else 'spent'),
                'transaction_name': str(cat),
            }
            for cat in categories
            ]
        }
        return JsonResponse(data)

    return JsonResponse({'error': 'Categories cannot be found'}, status=404)
