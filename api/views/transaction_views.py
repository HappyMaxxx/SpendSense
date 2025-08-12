from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from finance.models import Spents, Earnings, Account, SpentCategory, EarnCategory, UserCategory
from api.validation import validate_required_params, validate_amount
from api.decorators import time_logger
from decimal import Decimal
from django.utils.dateparse import parse_datetime
from datetime import datetime, timedelta

class UserTransactionsView(APIView):
    """
    Retrieves user transactions (both earnings and expenses) in a date range.

    Query Parameters:
        from (str): Start date in ISO 8601 format (optional).
        to (str): End date in ISO 8601 format (optional).

    Returns:
        Response: List of user transactions or error message.
    """

    @time_logger
    def get(self, request):
        user = request.user
        from_param = request.query_params.get('from')
        to_param = request.query_params.get('to')

        try:
            from_date = parse_datetime(from_param) if from_param else datetime.now() - timedelta(days=30)
            to_date = parse_datetime(to_param) if to_param else datetime.now()

            # Filter transactions by user and date range
            spents = Spents.objects.filter(user=user, time_update__range=(from_date, to_date))
            earnings = Earnings.objects.filter(user=user, time_update__range=(from_date, to_date))

            transactions = list(spents) + list(earnings)

        except Exception:
            return Response({'error': 'Invalid date format. Use ISO 8601 (e.g., 2024-06-01T00:00:00)'}, status=status.HTTP_400_BAD_REQUEST)

        if transactions:
            data = {
                'user': user.username,
                'transactions': [
                    {
                        'type': 'spent' if isinstance(transaction, Spents) else 'earn',
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
            return Response(data)

        return Response({'error': 'Transactions cannot be found'}, status=status.HTTP_404_NOT_FOUND)


class CreateTransactionView(APIView):
    """
    Creates a new transaction (income or expense) for the user.

    Query Parameters:
        account (str): Account name.
        category (str): Category value.
        amount (str or float): Transaction amount.
        type (str): Either 'spent' or 'earn'.

    Returns:
        Response: Status OK or error message.
    """

    @time_logger
    def get(self, request):
        user = request.user
        account_param = request.query_params.get('account')
        category_param = request.query_params.get('category')
        amount_param = request.query_params.get('amount')
        trans_type = request.query_params.get('type')

        # Validate required parameters
        validation_response = validate_required_params({
            'account': account_param,
            'category': category_param,
            'amount': amount_param,
            'type': trans_type
        })
        if validation_response:
            return Response(validation_response.data, status=validation_response.status_code)

        try:
            account = Account.objects.get(user=user, name=account_param)

            # Determine category based on type
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
                return Response({'error': 'The type parameter must be either "spent" or "earn"!'}, status=status.HTTP_400_BAD_REQUEST)

            if not category:
                return Response({'error': 'Category not found!'}, status=status.HTTP_404_NOT_FOUND)

            # Validate and parse amount
            amount, amount_error = validate_amount(amount_param)
            if amount_error:
                return Response(amount_error.data, status=amount_error.status_code)

            now = timezone.now()

            # Create transaction and update account balance
            if trans_type == 'spent':
                Spents.objects.create(
                    account=account,
                    category=category_param,
                    amount=amount,
                    time_create=now,
                    time_update=now,
                    user=user
                )
                account.balance = Decimal(str(account.balance)) - Decimal(str(amount))
            elif trans_type == 'earn':
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
            return Response({'status': 'ok'})

        except Account.DoesNotExist:
            return Response({'error': 'Account not found!'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)