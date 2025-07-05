from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('api/v1/token/check/', views.check_token, name='token_check'),
    path('api/v1/accounts/', views.user_accounts, name='api_accounts'),
    path('api/v1/transactions/', views.user_transactions, name='api_transactions'),
    path('api/v1/transactions/create/', views.create_transactions, name='transactions_get'),
    path('api/v1/categories/get/', views.categories_get, name='api_categories_get'),
    path('api/v1/profile-data/', views.profile_data, name='profile_data'),
]
