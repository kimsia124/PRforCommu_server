# commu/views.py

from django.shortcuts import render
from rest_framework import viewsets
from .models import CommuTweet
from .serializers import CommuTweetSerializer

class CommuTweetViewSet(viewsets.ModelViewSet):
    queryset = CommuTweet.objects.all()
    serializer_class = CommuTweetSerializer