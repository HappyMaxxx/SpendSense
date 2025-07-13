from finance.models import (Spents, Earnings, Account, SpentCategory,
                     EarnCategory, UserCategory)

from django.http import JsonResponse
from datetime import datetime, timedelta
from django.utils import timezone

from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime
from api.decorators import check_api_token, time_logger
from api.validation import validate_required_params, validate_amount
from decimal import Decimal

@csrf_exempt
@time_logger
@check_api_token
@require_http_methods(["GET"])
def user_transactions(request):
    """
    Retrieves user transactions (both earnings and expenses) in a date range.

    Query Parameters:
        from (str): Start date in ISO 8601 format (optional).
        to (str): End date in ISO 8601 format (optional).

    Returns:
        JsonResponse: List of user transactions or error message.
    """
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
def create_transactions(request):
    """
    Creates a new transaction (income or expense) for the user.

    Query Parameters:
        account (str): Account name.
        category (str): Category value.
        amount (str or float): Transaction amount.
        type (str): Either 'spent' or 'earn'.

    Returns:
        JsonResponse: Status OK or error message.
    """
    user = request.api_user
    account_param = request.GET.get('account')
    category_param = request.GET.get('category')
    amount_param = request.GET.get('amount')
    trans_type = request.GET.get('type')

    validation_response = validate_required_params({
        'account': account_param,
        'category': category_param,
        'amount': amount_param,
        'type': trans_type
    })

    if validation_response:
        return validation_response

    try:
        account = Account.objects.get(user=user, name=account_param)

        if trans_type == 'earn':
            category = (
                EarnCategory.objects.filter(value=category_param).first() or
                UserCategory.objects.filter(user=user, is_spent='earn', value=category_param).first()
            )
        elif trans_type == 'spent':
            category = (
                SpentCategory.objects.filter(value=category_param).first() or
                UserCategory.objects.filter(user=user, is_spent='spent', value=category_param).first()
            )
        else:
            return JsonResponse({'error': 'The type parameter must be either “spent” or “earn”!'}, status=400)

        if not category:
            return JsonResponse({'error': 'Category not found!'}, status=404)

        amount, amount_error = validate_amount(amount_param)
        if amount_error:
            return amount_error

        try:
            now = timezone.now()
            if trans_type == "spent":
                Spents.objects.create(
                    account=account,
                    category=category_param,
                    amount=amount,  
                    time_create=now,
                    time_update=now,
                    user=user
                )
                account.balance = Decimal(str(account.balance)) - Decimal(str(amount))
                account.save()
            elif trans_type == "earn":
                Earnings.objects.create(
                    account=account,
                    category=category_param,
                    amount=amount,  
                    time_create=now,
                    time_update=now,
                    user=user
                )
                account.balance = Decimal(str(account.balance)) + Decimal(str(amount))
                account.save()
            else:
                return JsonResponse({'error': 'The type parameter must be either “spent” or “earn”!'}, status=400)
        except:
            return JsonResponse({'error': 'A problem occurred while creating a transaction.'}, status=400)
        return JsonResponse({'status': 'ok'})

    except Account.DoesNotExist:
        return JsonResponse({'error': 'Account not found!'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)