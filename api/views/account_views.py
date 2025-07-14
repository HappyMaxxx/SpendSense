from finance.models import Account

from django.http import JsonResponse

from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from api.decorators import check_api_token, time_logger
from api.validation import validate_required_params, validate_amount

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
def create_account(request):
    """
    Creates accounts and balances for an authenticated user.

    Query Parameters:
        account (str): Account name.
        amount (str or float): Account amount.

    Returns:
        JsonResponse: Status OK or error message.
    """
    user = request.api_user
    account_param = request.GET.get('account')
    amount_param = request.GET.get('amount')

    validation_response = validate_required_params({
        'account': account_param,
    })

    if validation_response:
        return validation_response

    try:
        if amount_param is not None:
            amount, amount_error = validate_amount(amount_param)
            if amount_error:
                return amount_error
        else:
            amount = 0

        try:
            Account.objects.create(
                user = user,
                balance = amount,
                name = account_param,
            )
        except:
            return JsonResponse({'error': 'A problem occurred while creating an account.'}, status=400)
        return JsonResponse({'status': 'ok'})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)