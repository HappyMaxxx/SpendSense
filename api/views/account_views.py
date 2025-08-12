from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from finance.models import Account
from api.serializers import AccountSerializer
from api.decorators import time_logger
from api.validation import validate_required_params, validate_amount

class UserAccountsView(APIView):
    """
    Retrieves the authenticated user's accounts and balances.

    Returns:
        JsonResponse: Username and list of accounts with balances.
    """
    @time_logger
    def get(self, request):
        try:
            user = request.user
            accounts = Account.objects.filter(user=user)
        except:
            return Response({'error': 'Accounts cannot be found'}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = AccountSerializer(accounts, many=True)
        return Response({
            'user': user.username,
            'accounts': serializer.data
        })

class CreateAccountView(APIView):
    """
    Creates accounts and balances for an authenticated user.

    Query Parameters:
        account (str): Account name.
        amount (str or float): Account amount.

    Returns:
        JsonResponse: Status OK or error message.
    """
    @time_logger
    def get(self, request):
        user = request.user
        account_param = request.GET.get('account')
        amount_param = request.GET.get('amount')

        validation_response = validate_required_params({'account': account_param})
        if validation_response:
            return Response(validation_response.data, status=validation_response.status_code)

        try:
            if amount_param is not None:
                amount, amount_error = validate_amount(amount_param)
                if amount_error:
                    return Response(amount_error.data, status=amount_error.status_code)
            else:
                amount = 0

            Account.objects.create(user=user, name=account_param, balance=amount)
            return Response({'status': 'ok'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
