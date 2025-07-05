from finance.models import (Spents, Earnings, Account, SpentCategory,
                     EarnCategory, UserCategory)

from django.http import JsonResponse
from datetime import datetime, timedelta
from django.utils import timezone

from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime
from .decorators import check_api_token, time_logger
from .validation import validate_required_params, validate_amount

@csrf_exempt
@time_logger
@check_api_token
@require_http_methods(["GET"])
def check_token(request):
    """
    Checks if the API token is valid.

    Returns:
        JsonResponse: Status and the authenticated username.
    """
    return JsonResponse({
        'status': 'valid',
        'user': request.api_user.username
    })

@csrf_exempt
@time_logger
@check_api_token
@require_http_methods(["GET"])
def user_accounts(request):
    """
    Retrieves the authenticated user's accounts and balances.

    Returns:
        JsonResponse: Username and list of accounts with balances.
    """
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
def categories_get(request):
    """
    Retrieves expense or income categories for the authenticated user.

    Query Parameters:
        type (str): 'spent', 'earn', or None for all.
        user (str): 'true' for user-created categories only,
                    'false' for system categories only,
                    None for both.

    Returns:
        JsonResponse: List of categories with name, value, icon, and type.
    """
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
            }
            for cat in categories
            ]
        }
        return JsonResponse(data)

    return JsonResponse({'error': 'Categories cannot be found'}, status=404)

def get_transactions_data(user, start_date=None, end_date=None, api=False):
    """
    Collects transaction summary statistics for a user.

    Args:
        user (User): Authenticated user.
        start_date (datetime): Start filter date.
        end_date (datetime): End filter date.
        api (bool): If called from API.

    Returns:
        dict: Financial totals and filtered transactions if not API.
    """
    all_spents = Spents.objects.filter(user=user)
    all_earnings = Earnings.objects.filter(user=user)

    if not api:
        spents = [s for s in all_spents if start_date <= s.time_create <= end_date] if start_date and end_date else all_spents
        earnings = [e for e in all_earnings if start_date <= e.time_create <= end_date] if start_date and end_date else all_earnings

        total_spending = sum(transaction.amount for transaction in spents) if spents else 0
        total_earning = sum(transaction.amount for transaction in earnings) if earnings else 0

    total_all_spending = sum(transaction.amount for transaction in all_spents) if all_spents else 0
    total_all_earning = sum(transaction.amount for transaction in all_earnings) if all_earnings else 0
    total_all_diff = total_all_earning - total_all_spending

    data = {
        'total_all_spending': total_all_spending,
        'total_all_earning': total_all_earning,
        'total_all_diff': total_all_diff,
    }

    if not api:
        new_data = {
            'spents': spents,
            'earnings': earnings,
            'all_spents': all_spents,
            'all_earnings': all_earnings,
            'total_spending': total_spending,
            'total_earning': total_earning,
        } 
        data.update(new_data)

    return data

@csrf_exempt
@time_logger
@check_api_token
@require_http_methods(["GET"])
def profile_data(request):
    """
    Retrieves aggregated profile statistics: total income, spending, and net.

    Returns:
        JsonResponse: Financial profile summary or error.
    """
    user = request.api_user
    try:
        data = get_transactions_data(user, api=True)
        response_data = {
            'user': user.username,
            'total_all_spending': float(data['total_all_spending']),
            'total_all_earning': float(data['total_all_earning']),
            'total_all_diff': float(data['total_all_diff']),
        }
        return JsonResponse(response_data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

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
            elif trans_type == "earn":
                Earnings.objects.create(
                    account=account,
                    category=category_param,
                    amount=amount,  
                    time_create=now,
                    time_update=now,
                    user=user
                )
            else:
                return JsonResponse({'error': 'The type parameter must be either “spent” or “earn”!'}, status=400)
        except:
            return JsonResponse({'error': 'A problem occurred while creating a transaction.'}, status=400)
        return JsonResponse({'status': 'ok'})

    except Account.DoesNotExist:
        return JsonResponse({'error': 'Account not found!'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)