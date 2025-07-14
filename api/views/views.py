from finance.models import Spents, Earnings

from django.http import JsonResponse

from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from api.decorators import check_api_token, time_logger

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