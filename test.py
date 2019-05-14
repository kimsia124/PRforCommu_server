
from __future__ import print_function

access_key = 'q4tV8xBLrijuJ0vmlNKlSj6xF'
access_secret = 'RaFefwSbG0KOVZAqMcw9IHbIDZgMdUVA7AfDbUukXTFA6Troa9'


# auth = tweepy.OAuthHandler("z3Joy83D7tuOKDpL2SFvN4Pjl", "faRdBcTLWrQ7X5JVwwydFgvvvMwVHMnC5JAklAx4yPincwzoXQ")
# auth.set_access_token("1104913553595629568-d7FxHAjWbbM5M1t6denO72p38Dl9Qq", "aGuN9Yqd7gVu03XW1moFnCt2I9wMU3EBLKNtKapxUuYY3")

# api = tweepy.API(auth)

# user_info = api.get_user('giyeoc')
# user_status = api.get_status(user_info.id)
# print(user_status)
# # for tweet in public_tweets:
# #     print(tweet.text)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2018 Bitergia
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, 51 Franklin Street, Fifth Floor, Boston, MA 02110-1335, USA.
#
# Authors:
#     Valerio Cosentino <valcos@bitergia.com>
#


import base64
import requests
import urllib.parse

OAUTH2_TOKEN = 'https://api.twitter.com/oauth2/token'


def get_bearer_token(consumer_key, consumer_secret):
    # enconde consumer key
    consumer_key = urllib.parse.quote(consumer_key)
    # encode consumer secret
    consumer_secret = urllib.parse.quote(consumer_secret)
    # create bearer token
    bearer_token = consumer_key + ':' + consumer_secret
    # base64 encode the token
    base64_encoded_bearer_token = base64.b64encode(bearer_token.encode('utf-8'))
    # set headers
    headers = {
        "Authorization": "Basic " + base64_encoded_bearer_token.decode('utf-8') + "",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "Content-Length": "29"}

    response = requests.post(OAUTH2_TOKEN, headers=headers, data={'grant_type': 'client_credentials'})
    to_json = response.json()
    print(to_json['access_token'])


def main():
    get_bearer_token(access_key, access_secret)


if __name__ == "__main__":
    main()