from django.contrib import admin
from django.urls import include, path
from finance.views import PageNotFoundView
from django.conf import settings
from django.conf.urls import handler404
from django.conf.urls.static import static
from django.urls import re_path
from django.views.static import serve

urlpatterns = [
	path('admin/', admin.site.urls),
	path('', include('finance.urls')),
    path('', include('mono.urls')),
    path('', include('api.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += [re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),]

handler404 = PageNotFoundView.as_view()