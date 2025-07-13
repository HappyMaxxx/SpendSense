from finance.models import (SpentCategory, EarnCategory, UserCategory)

from django.http import JsonResponse

from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from api.decorators import check_api_token, time_logger
from api.validation import validate_required_params

import urllib.parse
import emoji

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

@csrf_exempt
@time_logger
@check_api_token
@require_http_methods(["GET"])
def create_category(request):
    """
    Creates a new category (income or expense) for the user.

    Query Parameters:
        name (str): New category name.
        icon (str): New category icon (emoji, either URL-encoded or raw emoji).
        type (str): Either 'spent' or 'earn'.

    Returns:
        JsonResponse: Status OK or error message.
    """
    user = request.api_user
    name_param = request.GET.get('name')
    icon_param = request.GET.get('icon')
    trans_type = request.GET.get('type')

    # Check if icon is already a valid emoji
    if icon_param and emoji.is_emoji(icon_param) and len(icon_param) <= 2:
        decoded_icon = icon_param
    else:
        # Attempt to decode URL-encoded icon
        try:
            decoded_icon = urllib.parse.unquote(icon_param) if icon_param else None
            if decoded_icon and (not emoji.is_emoji(decoded_icon) or len(decoded_icon) > 2):
                return JsonResponse({'error': 'Icon must be a single valid emoji.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Invalid icon format: {str(e)}'}, status=400)

    validation_response = validate_required_params({
        'name': name_param,
        'icon': decoded_icon,
        'type': trans_type
    })

    if validation_response:
        return validation_response

    try:
        if trans_type not in ['earn', 'spent']:
            return JsonResponse({'error': 'The type parameter must be either "spent" or "earn"!'}, status=400)

        UserCategory.objects.create(
            name=name_param,
            icon=decoded_icon,
            value=name_param.lower(),
            is_spent=trans_type,
            user=user
        )
        return JsonResponse({'status': 'ok'})

    except Exception as e:
        return JsonResponse({'error': f'A problem occurred while creating a category: {str(e)}'}, status=400)