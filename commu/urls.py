# commu/urls.py

from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'commu_tweets', views.CommuTweetViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
