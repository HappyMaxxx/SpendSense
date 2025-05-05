from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
	path('', views.index, name='home'),
    path('trans/', views.MakeNewTransaction.as_view(), name='new_transaction'),
    path('register/', views.RegisterUser.as_view(), name='register'),
    path('login/', views.LoginUser.as_view(), name='auth'),
    path('logout/', views.LogoutUser.as_view(), name='logout'),
    path('profile/', views.UserProfile.as_view(), name='profile'),
    # API endpoints
    path('api/check_username/', views.check_username, name='check_username'),
]
