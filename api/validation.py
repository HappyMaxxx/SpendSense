from django.http import JsonResponse

def validate_required_params(params: dict):
    """Check for required parameters"""
    missing = [key for key, value in params.items() if not value]
    if missing:
        return JsonResponse({
            'error': f"The following parameters are required: {', '.join(missing)}"
        }, status=400)
    return None

def validate_amount(amount_str: str):
    """Check the validity of the amount"""
    try:
        amount = float(amount_str)
        if amount <= 0:
            return None, JsonResponse({'error': 'Amount must be a positive number!'}, status=400)
        if round(amount, 2) != amount:
            return None, JsonResponse({'error': 'Amount can have at most two decimal places!'}, status=400)
        return amount, None
    except ValueError:
        return None, JsonResponse({'error': 'Amount must be a valid number!'}, status=400)
