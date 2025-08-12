from django.urls import path
from .views.views import CheckTokenView, ProfileDataView, ObtainAuthTokenView
from .views.account_views import UserAccountsView, CreateAccountView
from .views.category_views import CategoriesGetView, CreateCategoryView
from .views.transaction_views import UserTransactionsView, CreateTransactionView
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('api/v1/token/', ObtainAuthTokenView.as_view(), name='token_create'),
    path('api/v1/token/check/', CheckTokenView.as_view(), name='token_check'),
    path('api/v1/accounts/', UserAccountsView.as_view(), name='user-accounts'),
    path('api/v1/accounts/create/', CreateAccountView.as_view(), name='create-account'),
    path('api/v1/transactions/', UserTransactionsView.as_view(), name='api_transactions'),
    path('api/v1/transactions/create/', CreateTransactionView.as_view(), name='transactions_get'),
    path('api/v1/categories/', CategoriesGetView.as_view(), name='api_categories_get'),
    path('api/v1/categories/create/', CreateCategoryView.as_view(), name='api_categories_create'),
    path('api/v1/profile-data/', ProfileDataView.as_view(), name='profile_data'),
    path('api/v1/token/', obtain_auth_token),
]
