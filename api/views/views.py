from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from api.utils import get_transactions_data
from api.decorators import time_logger

class CheckTokenView(APIView):
    """
    Checks if the API token is valid.

    Returns:
        JsonResponse: Status and the authenticated username.
    """
    @time_logger
    def get(self, request):
        user = request.user
        return Response({
            'status': 'valid',
            'user': user.username
        })


class ObtainAuthTokenView(APIView):
    """
    Obtain an API token by providing username and password.

    Request Body:
        username (str): User's username.
        password (str): User's password.

    Returns:
        Response: Token key or error message.
    """
    permission_classes = []  # No authentication required for this endpoint

    @time_logger
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {'error': 'Both username and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_400_BAD_REQUEST
        )
    

class ProfileDataView(APIView):
    """
    Retrieves aggregated profile statistics: total income, spending, and net.
    """
    @time_logger
    def get(self, request):
        user = request.user
        try:
            data = get_transactions_data(user, api=True)
            response_data = {
                'user': user.username,
                'total_all_spending': float(data['total_all_spending']),
                'total_all_earning': float(data['total_all_earning']),
                'total_all_diff': float(data['total_all_diff']),
            }
            return Response(response_data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)