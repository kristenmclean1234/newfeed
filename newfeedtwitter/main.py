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
import jinja2
import os
import webapp2
<<<<<<< HEAD:feedlytwitter/main.py
from google.appengine.api import users
import json
from google.appengine.api import urlfetch


jinja_environment = jinja2.Environment(
  loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class LoginHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('mainpage.html')
        self.response.out.write(template.render())
        data = urlfetch.fetch('''https://www.googleapis.com/plus/v1/people/100600334103193921902?key=AIzaSyDyYgPPyl7FBES41CbPcJ6Af1CM7tp8Cqc''').content
=======
import json
import logging
import oauth2
import requests
import requests_oauthlib
import tweepy
>>>>>>> 135a70a4956e994f7b617713c921933339000b0d:newfeedtwitter/main.py




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
    ('/login', LoginHandler),
    ('/', MainHandler)
], debug=True)
