from django.urls import path
from . import views

urlpatterns = [
	path('', views.HomeView.as_view(), name='home'),
     path('register/', views.RegisterUser.as_view(), name='register'),
     path('login/', views.LoginUser.as_view(), name='auth'),
     path('logout/', views.LogoutUser.as_view(), name='logout'),
     path('profile/', views.UserProfileView.as_view(), name='profile'),
     path('expenses/', views.UserExpenses.as_view(), name='expenses'),
     path("link_api/", views.link_api, name="link_api"),
     path("generate_api_token/", views.set_user_api_token, name="generate_api_token"),
     path('edit-transaction/<int:transaction_id>/<int:transaction_type>/', views.edit_transaction, 
         name='edit_transaction'),

     path('bot_redirect/', views.bot_redirect, name='bot_redirect'),
     
     # API endpoints
     path('api/check_username/', views.check_username, name='check_username'),
     path('api/delete-transaction/<int:transaction_id>/<int:transaction_type>/',
         views.delete_transaction, name='delete_transaction'),
     path('api/delete-api-token/', views.delete_api_token, name='unlink_api'),
]
