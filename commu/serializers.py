from rest_framework import serializers
from .models import CommuTweet

class CommuTweetSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommuTweet
        fields = '__all__'