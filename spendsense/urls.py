from django.contrib import admin
from django.urls import include, path
from finance.views import page_not_found
from django.conf import settings
from django.conf.urls import handler404

urlpatterns = [
	path('admin/', admin.site.urls),
	path('', include('finance.urls')),
]

if settings.DEBUG:
	import debug_toolbar
	urlpatterns = [
		path('__debug__/', include(debug_toolbar.urls)),
	] + urlpatterns

handler404 = page_not_found