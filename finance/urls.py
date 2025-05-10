from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
	path('', views.index, name='home'),
    path('register/', views.RegisterUser.as_view(), name='register'),
    path('login/', views.LoginUser.as_view(), name='auth'),
    path('logout/', views.LogoutUser.as_view(), name='logout'),
    path('profile/', views.UserProfile.as_view(), name='profile'),
    path('new_transaction/', views.AddTransactionView.as_view(), name='new_transaction'),
    path('expenses/', views.UserExpenses.as_view(), name='expenses'),
    # API endpoints
    path('api/check_username/', views.check_username, name='check_username'),
    path('api/edit-transaction/<int:transaction_id>/<int:transaction_type>/', views.edit_transaction, name='edit_transaction'),
    path('api/delete-transaction/<int:transaction_id>/<int:transaction_type>/', views.delete_transaction, name='delete_transaction'),
]
