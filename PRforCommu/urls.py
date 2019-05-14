# PRforCommu/urls.py

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),

    path('commu/', include('commu.urls')),
    path('webhook/', include('webhook.urls')),
]
