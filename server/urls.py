from django.urls import path, include
from django.contrib import admin
from django.conf.urls import url
from django.urls import path
from apps.endpoints.urls import urlpatterns as endpoints_urlpatterns

admin.autodiscover()

urlpatterns = [
    path("admin/", admin.site.urls),
]

urlpatterns += endpoints_urlpatterns

