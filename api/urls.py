from django.urls import path
from .views.views import check_token, user_accounts, profile_data
from .views.category_views import categories_get, create_category
from .views.transaction_views import user_transactions, create_transactions

urlpatterns = [
    path('api/v1/token/check/', check_token, name='token_check'),
    path('api/v1/accounts/', user_accounts, name='api_accounts'),
    path('api/v1/transactions/', user_transactions, name='api_transactions'),
    path('api/v1/transactions/create/', create_transactions, name='transactions_get'),
    path('api/v1/categories/get/', categories_get, name='api_categories_get'),
    path('api/v1/categories/create/', create_category, name='api_categories_create'),
    path('api/v1/profile-data/', profile_data, name='profile_data'),
]
