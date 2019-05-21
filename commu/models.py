# commu/models.py

from django.db import models
from django.contrib.postgres.fields import JSONField

class Tag(models.Model):
    title = models.CharField(max_length=20, unique=True)

class CommuTweet(models.Model):
    text = models.TextField()
    tweet_id = models.CharField(max_length=20)
    promote_request_tweet_id = models.CharField(max_length=20, unique=True)
    previous_retweet_id = models.CharField(max_length=20, unique=True)
    user_id = models.CharField(max_length=20)
    user_name = models.CharField(max_length=30)
    user_screen_name = models.CharField(max_length=30)
    profile_image_url_https = models.CharField(max_length=100)
    media = JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

class Commu(models.Model):
    title = models.CharField(max_length=50)
    activity_type = JSONField(default=dict)
    plaform_type = JSONField(default=dict)
    rating = JSONField(default=dict)
    age_restriction = JSONField(default=dict)

class CommuList(models.Model):
    commu = models.ForeignKey(Commu, on_delete=models.PROTECT)
    commu_tweet = models.ForeignKey(CommuTweet, on_delete=models.PROTECT, default=None, null=True)
    tags = models.ManyToManyField(Tag, related_name='commu_tag')
    is_delete = models.BooleanField(default=False)