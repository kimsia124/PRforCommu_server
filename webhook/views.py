from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from commu.models import CommuTweet, Commu, CommuList
from PRforCommu.settings.dev import TWITTER_CONSUMER_SECRET, TWITTER_ACCESS_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_CONSUMER, TWITTER_ACCOUNT_ID, BEARER_TOKEN

import base64
import hashlib
import hmac
import json
import tweepy

auth = tweepy.OAuthHandler(TWITTER_CONSUMER, TWITTER_CONSUMER_SECRET)
auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)

twitter_api = tweepy.API(auth)


def commu_save(contents, title):
    tweet_commu = Commu()
    tweet_commu.title = title
    rating = {}

    def attr_save(key, string):
        if key == '플랫폼:':
            tweet_commu.plaform_type = {
                    'main': {
                        string: None,
                        'naver cafe': 'naver_cafe',
                        'cafe': 'naver_cafe',
                        '카페': 'naver_cafe',
                        '네이버 카페': 'naver_cafe',
                        '카커': 'naver_cafe',
                        'twt': 'twitter',
                        'twitter': 'twitter',
                        '트위터': 'twitter',
                        '트커': 'twitter',
                        'band': 'naver_band',
                        '밴드': 'naver_band',
                        'naver band': 'naver_band',
                        '네이버 밴드': 'naver_band',
                        '밴커': 'naver_band',
                        '밴드커': 'naver_band',
                        '비툴': 'homepage',
                        '홈커': 'homepage',
                        '홈소커': 'homepage',
                        '홈페이지커': 'homepage',
                        '홈페이지': 'homepage',
                        'homepage': 'homepage',
                    }[string]
                }
        elif key == '커뮤명:':
            tweet_commu.title = string
        elif key == '이용등급:':
            rating['grade'] = {
                string: None,
                '전체가': 'all',
                '전체이용가': 'all',
                '초등학생가': 'all',
                'ALL': 'all',
                '중학생가': '12',
                '12세 이상': '12',
                '12세': '12',
                '12': '12',
                '고등학생가': '15',
                '15세 이상': '15',
                '15세': '15',
                '15': '15',
                '성인가': '19',
                '19세 이상': '19',
                '19세': '19',
                '19': '19',
                '성인': '19',
            }[string]
            tweet_commu.rating = rating
        elif key == '나이제한:':
            num = int(''.join(filter(str.isdigit, string)))
            if num > 100:
                result = str(num)
            elif num > 70:
                result = '19' + str(num)
            elif num < 20 and num > 0:
                result = '20' + str(num).zfill(2)
            else:
                return
            tweet_commu.age_restriction['lte'] = result
        return

    KEYS = ['커뮤명:', '이용등급:', '활동방법:', '플랫폼:', '나이제한:']
    content = ' '.join(contents)
    sub_tag = list(filter(lambda x:'#자캐커뮤_'.find(x) != -1, content.split()))
    sub_content = list(filter(lambda x:'@#'.find(x[0]) == -1, content.split()))

    key_index = [i for i in range(len(sub_content)) if sub_content[i] in KEYS]
    string = ''

    for i in range(len(key_index)):
        if (len(key_index)-1 == i):
            string = ' '.join(sub_content[key_index[i]+1:])
        else:
            string = ' '.join(sub_content[key_index[i]+1:key_index[i+1]])

        attr_save(sub_content[key_index[i]], string)

    tweet_commu.save()
    return tweet_commu, sub_tag

def commu_tweet_save(tweet_data):
    def attr_save(commu_tweet, tweet_data):
        commu_tweet.text = tweet_data.text
        commu_tweet.tweet_id = tweet_data.id_str
        commu_tweet.user_id = tweet_data.user.id_str
        commu_tweet.user_name = tweet_data.user.name
        commu_tweet.user_screen_name = tweet_data.user.screen_name
        commu_tweet.profile_image_url_https = tweet_data.user.profile_image_url_https

        if  'media' in tweet_data.entities:
            commu_tweet.media = tweet_data.entities['media']

        return commu_tweet

    pr_tweet = CommuTweet()
    tweet_content = []
    tweet_data = twitter_api.get_status(tweet_data.get('id_str'))

    if tweet_data.in_reply_to_status_id_str != tweet_data.id_str:
        pr_tweet.promote_request_tweet_id = current_tweet_id = tweet_data.id_str
        tweet_content.append(tweet_data.text)

        while True:
            tweet_data = twitter_api.get_status(current_tweet_id)

            if tweet_data.id_str == tweet_data.in_reply_to_status_id_str or tweet_data.in_reply_to_status_id_str is None:
                pr_tweet = attr_save(pr_tweet, tweet_data)
                break

            tweet_content.append(tweet_data.text)
            current_tweet_id = tweet_data.in_reply_to_status_id_str

    else:
        pr_tweet = attr_save(pr_tweet, tweet_data)
        tweet_content.append(tweet_data.text)

    previous_retweet = CommuList.objects.filter(commu_tweet__tweet_id=pr_tweet.tweet_id, is_delete=False)

    if previous_retweet.exists():
        promote_cancel(pr_tweet.tweet_id, previous_retweet.last().commu_tweet.previous_retweet_id)

    pr_tweet.previous_retweet_id = twitter_api.retweet(pr_tweet.tweet_id).id_str
    pr_tweet.save()

    return pr_tweet, tweet_content


def cancle_rt(tweet_id):
    tweet_data = twitter_api.get_status(tweet_id)
    current_tweet_id = tweet_data.id_str

    if tweet_data.in_reply_to_status_id_str != tweet_id:
        while True:
            tweet_data = twitter_api.get_status(current_tweet_id)
            if tweet_data.id_str == tweet_data.in_reply_to_status_id_str or tweet_data.in_reply_to_status_id_str is None:
                promote_cancel(tweet_data.id_str)
                break
            current_tweet_id = tweet_data.in_reply_to_status_id_str
    else:
        promote_cancel(tweet_id)

    return

def promote_cancel(tweet_id, previous_retweet_id=None):
    if previous_retweet_id is None:
        twitter_api.destroy_status(CommuTweet.objects.filter(tweet_id=tweet_id).last().previous_retweet_id)
        CommuList.objects.filter(commu_tweet__tweet_id=tweet_id, is_delete=False).update(is_delete=True)

        return
    else:
        twitter_api.destroy_status(previous_retweet_id)
        CommuList.objects.filter(commu_tweet__tweet_id=tweet_id, is_delete=False).update(is_delete=True)

        return

@csrf_exempt
def twitter(request):
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)

        if body_data.get('tweet_create_events'):
            tweet_data = body_data.get('tweet_create_events')[0]

            if any(TWITTER_ACCOUNT_ID == i.get('id_str') for i in tweet_data.get('entities').get('user_mentions')):
                if ('알티 취소' in tweet_data.get('text')):
                    cancle_rt(tweet_data.get('id_str'))
                    return HttpResponse('200 OK')

                commu_list = CommuList()
                commu_list.commu_tweet, tweet_content = commu_tweet_save(tweet_data)
                commu_list.commu, sub_tag = commu_save(tweet_content, commu_list.commu_tweet.user_name)

                commu_list.save()

        return HttpResponse('200 OK')

    elif request.method == 'GET':
        sha256_hash_digest = hmac.new(TWITTER_CONSUMER_SECRET.encode(), msg=request.GET['crc_token'].encode(), digestmod=hashlib.sha256).digest()

        return JsonResponse({
            'response_token': 'sha256=' + base64.b64encode(sha256_hash_digest).decode(),
        })

    raise Http404