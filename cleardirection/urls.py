from django.urls import include,path
from django.contrib import admin

urlpatterns = [
	path(r'',include('hello.urls')),
	path(r'lookup/',include('lookup.urls')),
    path(r'admin/', admin.site.urls),
]
