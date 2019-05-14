# commu/models.py

from django.db import models
from django.contrib.postgres.fields import JSONField

class CommuTweet(models.Model):
    text = models.TextField()
    tweet_id = models.CharField(max_length=20)
    promote_request_tweet_id = models.CharField(max_length=20)
    user_id = models.CharField(max_length=20)
    user_name = models.CharField(max_length=30)
    user_screen_name = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)