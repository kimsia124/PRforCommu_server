from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from commu.models import CommuTweet
from PRforCommu.settings.dev import TWITTER_CONSUMER_SECRET, TWITTER_ACCESS_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_CONSUMER, TWITTER_ACCOUNT_ID, BEARER_TOKEN

import base64
import hashlib
import hmac
import json
import tweepy

auth = tweepy.OAuthHandler(TWITTER_CONSUMER, TWITTER_CONSUMER_SECRET)
auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)

twitter_api = tweepy.API(auth)

@csrf_exempt
def twitter(request):
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)

        if body_data.get('tweet_create_events'):
            tweet_data = body_data.get('tweet_create_events')[0]

            if any(TWITTER_ACCOUNT_ID == i.get('id_str') for i in tweet_data.get('entities').get('user_mentions')):
                pr_tweet = CommuTweet()

                if tweet_data.get('in_reply_to_status_id_str') != tweet_data.get('id_str'):
                    pr_tweet.promote_request_tweet_id = current_tweet_id =tweet_data.get('id_str')

                    while True:
                        tweet_data = twitter_api.get_status(current_tweet_id)

                        if tweet_data.id_str == tweet_data.in_reply_to_status_id_str or tweet_data.in_reply_to_status_id_str is None:
                            pr_tweet.text = tweet_data.text
                            pr_tweet.tweet_id = tweet_data.id_str
                            pr_tweet.user_id = tweet_data.user.id_str
                            pr_tweet.user_name = tweet_data.user.name
                            pr_tweet.user_screen_name = tweet_data.user.screen_name
                            pr_tweet.profile_image_url = tweet_data.user.profile_image_url

                            break

                        current_tweet_id = tweet_data.in_reply_to_status_id_str

                else:
                    pr_tweet.text = res_data.get('text')
                    pr_tweet.tweet_id = res_data.get('id_str')
                    pr_tweet.user_id = res_data.get('user').get('id_str')
                    pr_tweet.user_name = res_data.get('user').get('name')
                    pr_tweet.user_screen_name = res_data.get('user').get('screen_name')
                    pr_tweet.profile_image_url = res_data.get('user').get('profile_image_url')

                twitter_api.retweet(pr_tweet.tweet_id)

                pr_tweet.save()

        return HttpResponse('200 OK')

    elif request.method == 'GET':
        sha256_hash_digest = hmac.new(TWITTER_CONSUMER_SECRET.encode(), msg=request.GET['crc_token'].encode(), digestmod=hashlib.sha256).digest()

        return JsonResponse({
            'response_token': 'sha256=' + base64.b64encode(sha256_hash_digest).decode(),
        })

    raise Http404