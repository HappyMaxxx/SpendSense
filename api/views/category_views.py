from finance.models import (SpentCategory, EarnCategory, UserCategory)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse

from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from api.decorators import check_api_token, time_logger
from api.validation import validate_required_params

import urllib.parse
import emoji

class CategoriesGetView(APIView):
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

    @time_logger
    def get(self, request):
        user = request.user
        type_param = request.query_params.get('type')
        user_param = request.query_params.get('user')

        include_user = user_param == 'true'
        categories = []

        try:
            if type_param == 'spent':
                # Get system spent categories
                categories += list(SpentCategory.objects.all())
                if include_user:
                    # User-created spent categories only
                    categories = list(UserCategory.objects.filter(user=user, is_spent='spent'))
                elif user_param is None:
                    # Add user-created spent categories
                    categories += list(UserCategory.objects.filter(user=user, is_spent='spent'))

            elif type_param == 'earn':
                categories += list(EarnCategory.objects.all())
                if include_user:
                    categories = list(UserCategory.objects.filter(user=user, is_spent='earn'))
                elif user_param is None:
                    categories += list(UserCategory.objects.filter(user=user, is_spent='earn'))

            elif type_param is None:
                # Both spent and earn system categories
                categories += list(SpentCategory.objects.all()) + list(EarnCategory.objects.all())
                if include_user:
                    categories = list(UserCategory.objects.filter(user=user))
                elif user_param is None:
                    categories += list(UserCategory.objects.filter(user=user))

            else:
                return Response({'error': 'Invalid type parameter. Must be "spent", "earn", or omitted.'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if categories:
            data = {
                'user': user.username,
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
            return Response(data)

        return Response({'error': 'Categories cannot be found'}, status=status.HTTP_404_NOT_FOUND)

class CreateCategoryView(APIView):
    """
    Creates a new category (income or expense) for the user.

    Query Parameters:
        name (str): New category name.
        icon (str): New category icon (emoji, either URL-encoded or raw emoji).
        type (str): Either 'spent' or 'earn'.

    Returns:
        JsonResponse: Status OK or error message.
    """

    @time_logger
    def get(self, request):
        user = request.user
        name_param = request.query_params.get('name')
        icon_param = request.query_params.get('icon')
        trans_type = request.query_params.get('type')

        # Check if icon is already a valid emoji
        if icon_param and emoji.is_emoji(icon_param) and len(icon_param) <= 2:
            decoded_icon = icon_param
        else:
            try:
                decoded_icon = urllib.parse.unquote(icon_param) if icon_param else None
                if decoded_icon and (not emoji.is_emoji(decoded_icon) or len(decoded_icon) > 2):
                    return Response({'error': 'Icon must be a single valid emoji.'}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'error': f'Invalid icon format: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        validation_response = validate_required_params({
            'name': name_param,
            'icon': decoded_icon,
            'type': trans_type
        })

        if validation_response:
            return Response(validation_response.data, status=validation_response.status_code)

        try:
            if trans_type not in ['earn', 'spent']:
                return Response({'error': 'The type parameter must be either "spent" or "earn"!'}, status=status.HTTP_400_BAD_REQUEST)

            UserCategory.objects.create(
                name=name_param,
                icon=decoded_icon,
                value=name_param.lower(),
                is_spent=trans_type,
                user=user
            )
            return Response({'status': 'ok'})

        except Exception as e:
            return Response({'error': f'A problem occurred while creating a category: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)