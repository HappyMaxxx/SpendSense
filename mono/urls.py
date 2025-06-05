from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("monobank/", views.monobank_info_view, name="monobank_info"),
    path("all_mono/", views.all_mono_transactions_view, name="all_mono_transactions"),
    path('api/delete-mono-token/', views.delete_mono_token, name='unlink_monobank'),
]
