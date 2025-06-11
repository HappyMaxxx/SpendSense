from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('api/v1/accounts/', views.api_user_accounts, name='api_accounts'),
    path('api/v1/transactions/', views.api_user_transactions, name='api_transactions'),
    path('api/v1/token/check/', views.api_check_token, name='api_token_check'),
    path('api/v1/categories/get/', views.api_categories_get, name='api_categories_get'),
]
