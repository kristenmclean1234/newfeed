#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import json
import logging
import oauth2
import requests
import requests_oauthlib
import tweepy




class MainHandler(webapp2.RequestHandler):
    def get(self):
        # user = api.get_user('SiriusArtistry')
        # print user.screen_name
        # print user.followers_count
        # for friend in user.friends():
        #    print friend.screen_name
        consumer_key = 'kCh51IOR8BVdmW3Iuf0TpjYD6'
        consumer_secret = 'p4QsgwRFvBMa9wEMkwpzYRFEPwYc4znupLd4xlBWlFLYZLjOpf'
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        # auth.set_access_token(access_token, access_token_secret)

        api = tweepy.API(auth)

        public_tweets = api.home_timeline()
        for tweet in public_tweets:
            print tweet.text

app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
