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
import random
from google.appengine.api import urlfetch
import jinja2
import os

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class MainHandler(webapp2.RequestHandler):
    def get(self):
        #template = jinja_environment.get_template('templates/search.html')
        #url: http://api.nytimes.com/svc/search/v2/articlesearch.response-format?[q=search term&fq=filter-field:(filter-term)&additional-params=values]&api-key=####
        #base_url = "http://api.nytimes.com/svc/search/v2/articlesearch.response-format?q=sports"
        #search_term =
        url = "http://api.nytimes.com/svc/search/v2/articlesearch.json?q=food&"
        api_key ="api-key=7169254a2f887db9ab1c3c629fed79d3:16:72574373"
        nyt_data_source = urlfetch.fetch(url+api_key)
        nyt_json_content = nyt_data_source.content
        parsed_nyt_dictionary = json.loads(nyt_json_content)
        for i in range(0, len(parsed_nyt_dictionary['response']['docs'])):
            art_headline = parsed_nyt_dictionary['response']['docs'][i]['headline']
            art_lead_para = parsed_nyt_dictionary['response']['docs'][i]['lead_paragraph']
            art_url = parsed_nyt_dictionary['response']['docs'][i]['web_url']
            self.response.write('<html><body><p>%s<br>%s<br>%s</p></body></html>' %(art_headline, art_lead_para, art_url))
        #self.response.write(template.render())


app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
