    # THAT'S A WHOLE LOTTA MODULES WOW
from authomatic.adapters import Webapp2Adapter
from authomatic import Authomatic
from config import CONFIG
from google.appengine.api import urlfetch
from google.appengine.api import users
from google.appengine.ext import ndb
import jinja2
import json
import logging
import os
import pprint
import random
import twitter
import urllib
import webapp2

    # JINJA AND AUTHOMATIC
authomatic = Authomatic(config=CONFIG, secret='some random secret string')
jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

    # TAKES CARE OF LOGGING INTO GOOGLE, NOT IN USE CURRENTLY
    # THE PROBLEM IS IT USES JAVASCRIPT INSTEAD OF PYTHON TO GET AND STORE USERNAMES
class LoginGoogleHandler(webapp2.RequestHandler):
    def get(self):
        logging.info("Google login handler")
        template = jinja_environment.get_template('templates/googleloginpage.html')
        self.response.out.write(template.render())

    # CREATES A USER CLASS TO STORE TWITTER AND FACEBOOK CREDENTIALS
    # IN HOPES OF ALLOWING USERS TO LOG INTO BOTH
class Profile(ndb.Model):
    name = ndb.StringProperty(required=False)
    fb_user_name = ndb.StringProperty(required=False)
    fb_user_id = ndb.StringProperty(required=False)
    fb_result = ndb.StringProperty(required=False)
    fb_credentials = ndb.StringProperty(required=False)
    fb_error = ndb.StringProperty(required=False)
    tw_user_name = ndb.StringProperty(required=False)
    tw_user_id = ndb.StringProperty(required=False)
    tw_result = ndb.StringProperty(required=False)
    tw_credentials = ndb.StringProperty(required=False)
    tw_error = ndb.StringProperty(required=False)

    # THE ACTUAL METHOD OF LOGGING IN AND GETTING A USERNAME AND USER ID
    # IT USES RESULT AS A STORAGE FOR IT AND PUTS IT INTO A COOKIE
    # INSTEAD OF COOKIES, PUT IT INTO A DATASTORE

result = {}
serialized_credentials = {}
user_id = {}
user_name = {}

class Login(webapp2.RequestHandler):
    def any(self, provider_name):
        logging.info("logging in -- PROVIDER NAME IS: %s", provider_name)
        Profile.get_by_id
        last_provider = self.request.cookies.get(provider_name)
        global result
        result[provider_name] = authomatic.login(Webapp2Adapter(self), provider_name)
        self.response.set_cookie(str(provider_name) + '_result', str(result[provider_name]))
        self.response.set_cookie(provider_name)

        # user = User(result=result)
        # user.put()
        pprint.pprint('RESULT IS %s' % result[provider_name])

        if result[provider_name]:
            if result[provider_name].user:
                result[provider_name].user.update()
                self.response.write('<h1>Hi {0}</h1>'.format(result[provider_name].user.name))

                # Save the user name and ID to cookies that we can use it in other handlers.
                self.response.set_cookie(str(provider_name) + '_user_id', result[provider_name].user.id)
                self.response.set_cookie(str(provider_name) + '_user_name', urllib.quote(result[provider_name].user.name))
                # profile.fb_userid =
                # prfless

                if result[provider_name].user.credentials:
                    # Serialize credentials and store it as well.
                    serialized_credentials = result[provider_name].user.credentials.serialize()
                    self.response.set_cookie(str(provider_name) + '_credentials', serialized_credentials)

            elif result[provider_name].error:
                self.response.set_cookie(str(provider_name) + '_error', urllib.quote(result[provider_name].error.message))

            self.redirect('/')

def get_article_info(art_dict):
    articles = []
    for doc in art_dict:
        a = {}
        art_headline = doc.get('headline').get('main')
        if art_headline == None:
             art_headline = doc.get('headline').get('print_headline')
        if art_headline == None:
             art_headline = ''
        a['headline'] = art_headline
        art_lead_para = doc.get('lead_paragraph')
        if art_lead_para == None:
            art_lead_para = ''
        a['lead_paragraph'] = art_lead_para
        a['web_url'] = doc.get('web_url')
        articles.append(a)
    return articles



class Home(webapp2.RequestHandler):
    def any(self):
        logging.info("home (get) handler")
        # Retrieve values from cookies.
        global serialized_credentials
        global user_id
        global user_name
        provider_name = 'fb'
        serialized_credentials[provider_name] = self.request.cookies.get(str(provider_name)+'_credentials')
        user_id[provider_name] = self.request.cookies.get(str(provider_name)+ '_user_id')
        user_name[provider_name] = urllib.unquote(self.request.cookies.get(str(provider_name) + '_user_name', ''))
        # error = urllib.unquote(self.request.cookies.get('error', ''))
        logging.info("home handler found user_id: %s", user_id[provider_name])
        # if error:
        #     self.response.write('<p>Damn that error: {0}</p>'.format(error))
        if user_id[provider_name]:
            # self.response.write('<h1>Hi {0}</h1>'.format(user_name))

            if serialized_credentials[provider_name]:
                # Deserialize credentials.
                credentials = {}
                credentials[provider_name] = authomatic.credentials(serialized_credentials[provider_name])
                logging.info('CREDENTIALS ARE: %s' % credentials[provider_name])

                # valid = 'still' if credentials.valid else 'not anymore'
                # expire_soon = 'less' if credentials.expire_soon(60 * 60 * 24) else 'more'
                # remaining = credentials.expire_in
                # expire_on = credentials.expiration_date
                #
                # self.response.write("""
                # <p>
                #     They are <b>{0}</b> valid and
                #     will expire in <b>{1}</b> than one day
                #     (in <b>{2}</b> seconds to be precise).
                #     It will be on <b>{3}</b>.
                # </p>
                # """.format(valid, expire_soon, remaining, expire_on))

                if credentials[provider_name].valid:
                    pass
                else:
                    self.response.write("""
                    <p>
                        Repeat the <b>login procedure</b>to get new credentials.
                    </p>
                    <a href="login/{0}">Refresh</a>
                    """.format(credentials[provider_name].provider_name))
        else:
            # self.redirect('/')
            template = jinja_environment.get_template('templates/login.html')
            self.response.write(template.render())
            return
        logging.info("PROVIDER NAME IS: %s", credentials[provider_name].provider_name)

            #TWITTER & FACEBOOK -----------------------------
        provider_names = {}
        result = {}
        serialized_credentials = {}
        user_id = {}
        provider_names[provider_name] = credentials[provider_name].provider_name
        logging.info("action handler got provider_name %s", provider_names[provider_name])
        result[provider_name] = authomatic.login(Webapp2Adapter(self), provider_names[provider_name])
        logging.info('RESULT IS: %s' % result[provider_name])
        serialized_credentials[provider_name] = self.request.cookies.get(str(provider_name) + '_credentials')
        user_id[provider_name] = self.request.cookies.get(str(provider_name) + '_user_id')
        response = {}
        response[provider_name] = authomatic.access(serialized_credentials[provider_name],
                                     url='https://api.twitter.com/1.1/statuses/home_timeline.json',
                                     method='GET')
        logging.info('RESPONSE IS: %s' % response[provider_name])
        tweets = []
        fstatuses = []
        if result[provider_name]:
            # If there is result, the login procedure is over and we can write to response.
            self.response.write('<a href="..">Home</a>')

            if result[provider_name].error:
                # Login procedure finished with an error.
                self.response.write(u'<h2>Damn that error: {}</h2>'.format(result[provider_name].error.message))


            elif result[provider_name].user:
                # Hooray, we have the user!

                # OAuth 2.0 and OAuth 1.0a provide only limited user data on login,
                # We need to update the user to get more info.
                if not (result[provider_name].user.name and result[provider_name].user.id):
                    result[provider_name].user.update()

                # Welcome the user.
                # self.response.write(u'<h1>Hi {}</h1>'.format(result.user.name))
                # self.response.write(u'<h2>Your id is: {}</h2>'.format(result.user.id))
                # self.response.write(u'<h2>Your email is: {}</h2>'.format(result.user.email))
                logging.info('CREDENTIALS ARE: %s' % result[provider_name].user.credentials)
                credentials[provider_name] = result[provider_name].user.credentials
                logging.info('CREDENTIALS VARIABLE VALUE IS: %s' % credentials[provider_name])
                # self.response.set_cookie('credentials', credentials)

                    # FACEBOOK PRINT STATUSES ---------------
                if 'fb' in result:
                    urlf = 'https://graph.facebook.com/{}?fields=feed.limit(10)'
                    urlf = urlf.format(result['fb'].user.id)
                    logging.info("FACEBOOK USER ID IS: %s" % result['fb'].user.id)

                    # Access user's protected resource.
                    fbresponse = result['fb'].provider.access(urlf)
                    logging.info(fbresponse)
                    if fbresponse.status == 200:
                        # Parse response.
                        statuses = fbresponse.data.get('feed').get('data')
                        error = fbresponse.data.get('error')
                        if error:
                            self.response.write(u'Damn that error: {}!'.format(error))
                        elif statuses:
                            fstatuses = []
                            for message in statuses:
                                s = {}
                                logging.info("MESSAGE FOR FACEBOOK IS: %s", message)
                                text = message.get('message')
                                if text == None:
                                    text = message.get('story')
                                s['text'] = text
                                s['date'] = message.get('created_time')
                                fstatuses.append(s)

                                # text = message.get('message')
                                # date = message.get('created_time')
                    else:
                        self.response.write('Damn that unknown error!<br />')
                        self.response.write(u'Status: {}'.format(response.status))


                # TWITER PRINT TWEETS -------------------------
                urlt = 'https://api.twitter.com/1.1/statuses/home_timeline.json'
                if 'tw' in result:
                    # You can pass a dictionary of querystring parameters.
                    twresponse = result['tw'].provider.access(urlt, {'count': 10})
                    logging.info('TWITTER RESPONSE IS: %s' % twresponse)

                    # Parse response.
                    if twresponse.status == 200:
                        logging.info('RESPONSE STATUS IS A-OKAY!')
                        if type(twresponse.data) is list:
                            # Twitter returns the tweets as a JSON list.
                            # self.response.write('Your 5 most recent tweets:')
                            # logging.info('RESPONSE DATA IS: %s' % response.data)
                            tweets = []
                            for tweet in twresponse.data:
                                t = {}
                                t['text'] = tweet.get('text')
                                t['date'] = tweet.get('created_at')
                                t['name'] = tweet.get('user').get('name')
                                # t['media'] = tweet.get('mediaurl')
                                # logging.info('MEDIA URL IS: %s' % media)
                                t['handle'] = tweet.get('user').get('screen_name')

                                tweets.append(t)

                                # self.response.write(format(name, handle))
                                # self.response.write(format(text.replace(u'\u2013', '[???]')))
                                # self.response.write(format(date))

                                #PUT THESE THREE ENTIRES IN A DICT SO THAT YOU CAN PRINT IT OUT IN HTML

                        elif twresponse.data.get('errors'):
                            self.response.write(u'Damn that error: {}!'.\
                                                format(response.data.get('errors')))
                    else:
                        self.response.write('Damn that unknown error!<br />')
                        self.response.write(u'Status: {}'.format(twresponse.status))



            # NEWS ------------------------------
        url = "http://api.nytimes.com/svc/search/v2/articlesearch.json?"
        api_key ="api-key=7169254a2f887db9ab1c3c629fed79d3:16:72574373"
        nyt_data_source = urlfetch.fetch(url+api_key)
        nyt_json_content = nyt_data_source.content
        parsed_nyt_dictionary = json.loads(nyt_json_content)

        logging.info('STATUSES ARE: %s', fstatuses)

            # RENDER THE TEMPLATE ------------------



        search_term = self.request.get('search_term')
        logging.info(search_term)
        logging.info("hey")
        if search_term == "":
            url =  "http://api.nytimes.com/svc/search/v2/articlesearch.json?"
            api_key ="api-key=7169254a2f887db9ab1c3c629fed79d3:16:72574373"
            nyt_data_source = urlfetch.fetch(url+api_key)
        else:
            url =  "http://api.nytimes.com/svc/search/v2/articlesearch.json?q="
            api_key ="&api-key=7169254a2f887db9ab1c3c629fed79d3:16:72574373"
            nyt_data_source = urlfetch.fetch(url+search_term+api_key)
        nyt_json_content = nyt_data_source.content
        parsed_nyt_dictionary = json.loads(nyt_json_content)
        #template = jinja_environment.get_template('templates/mainpage.html')
        #self.response.write(template.render({'articles' : get_article_info(parsed_nyt_dictionary['response']['docs'])}))
        # Create links to the Login handler.
        template = jinja_environment.get_template('templates/mainpage.html')
        # self.response.write(template.render({'articles' : get_article_info(parsed_nyt_dictionary['response']['docs'])}))
        self.response.write(template.render({
                                            'articles' : get_article_info(parsed_nyt_dictionary['response']['docs']),
                                            'name' : format(user_name[provider_name]),
                                            'provider' : format(dict(fb='Facebook', tw='Twitter')[credentials[provider_name].provider_name]),
                                            'providerslug' : format(credentials[provider_name].provider_name),
                                            'tweets' : tweets,
                                            'statuses' : fstatuses

                                        }))

class Refresh(webapp2.RequestHandler):
    def get(self):
        logging.info("refresh (get) handler")
        self.response.write('<a href="..">Home</a><br>')

        serialized_credentials = self.request.cookies.get('credentials')
        credentials = authomatic.credentials(serialized_credentials)
        old_expiration = credentials.expiration_date

        response = credentials.refresh(force=True)

        if response:
            new_expiration = credentials.expiration_date

            if response.status == 200:
                self.response.write("""
                <p>
                    Credentials were refresshed successfully.
                    Their expiration date was extended from
                    <b>{0}</b> to <b>{0}</b>.
                </p>
                """.format(old_expiration, new_expiration))
            else:
                self.response.write("""
                <p>Refreshment failed!</p>
                <p>Status code: {0}</p>
                <p>Error message:</p>
                <pre>{0}</pre>
                """.format(response.status, response.content))
        else:
            self.response.write('<p>Your credentials don\'t support refreshment!</p>')

        self.response.write('<a href="">Try again!</a>')

# class Action(webapp2.RequestHandler):
#     def any(self, provider_name):
#         logging.info("action handler got provider_name %s", provider_name)
#         result = authomatic.login(Webapp2Adapter(self), provider_name)
#         logging.info('RESULT IS: %s' % result)
#         serialized_credentials = self.request.cookies.get('credentials')
#         user_id = self.request.cookies.get('user_id')
#
#         response = authomatic.access(serialized_credentials,
#                                      url='https://api.twitter.com/1.1/statuses/home_timeline.json',
#                                      method='GET')
#         logging.info('RESPONSE IS: %s' % response)
#
#
#         if result:
#             # If there is result, the login procedure is over and we can write to response.
#             self.response.write('<a href="..">Home</a>')
#
#             if result.error:
#                 # Login procedure finished with an error.
#                 self.response.write(u'<h2>Damn that error: {}</h2>'.format(result.error.message))
#
#
#             elif result.user:
#                 # Hooray, we have the user!
#
#                 # OAuth 2.0 and OAuth 1.0a provide only limited user data on login,
#                 # We need to update the user to get more info.
#                 if not (result.user.name and result.user.id):
#                     result.user.update()
#
#                 # Welcome the user.
#                 self.response.write(u'<h1>Hi {}</h1>'.format(result.user.name))
#                 self.response.write(u'<h2>Your id is: {}</h2>'.format(result.user.id))
#                 self.response.write(u'<h2>Your email is: {}</h2>'.format(result.user.email))
#                 logging.info('CREDENTIALS ARE: %s' % result.user.credentials)
#                 credentials = result.user.credentials
#                 logging.info('CREDENTIALS VARIABLE VALUE IS: %s' % credentials)
#                 # self.response.set_cookie('credentials', credentials)
#
#
#                 # Seems like we're done, but there's more we can do...
#
#                 # If there are credentials (only by AuthorizationProvider),
#                 # we can _access user's protected resources.
#                 if result.user.credentials:
#
#                     # Each provider has it's specific API.
#                     if result.provider.name == 'fb':
#                         self.response.write('Your are logged in with Facebook.<br />')
#
#                         # We will access the user's 5 most recent statuses.
#                         url = 'https://graph.facebook.com/{}?fields=feed.limit(10)'
#                         url = url.format(result.user.id)
#                         logging.info("USER ID IS: %s" % result.user.id)
#
#                         # Access user's protected resource.
#                         response = result.provider.access(url)
#
#                         if response.status == 200:
#                             # Parse response.
#                             statuses = response.data.get('feed').get('data')
#                             error = response.data.get('error')
#
#                             if error:
#                                 self.response.write(u'Damn that error: {}!'.format(error))
#                             elif statuses:
#                                 self.response.write('Your 10 most recent statuses:<br />')
#                                 for message in statuses:
#
#                                     text = message.get('message')
#                                     date = message.get('created_time')
#
#                                     self.response.write(u'<h3>{}</h3>'.format(text))
#                                     self.response.write(u'Posted on: {}'.format(date))
#                         else:
#                             self.response.write('Damn that unknown error!<br />')
#                             self.response.write(u'Status: {}'.format(response.status))
#
#                     if result.provider.name == 'tw':
#                         self.response.write('Your are logged in with Twitter.<br />')
#
#                         # We will get the user's 5 most recent tweets.
#                         url = 'https://api.twitter.com/1.1/statuses/home_timeline.json'
#
#                         # You can pass a dictionary of querystring parameters.
#                         response = result.provider.access(url, {'count': 10})
#                         logging.info('RESPONSE IS: %s' % response)
#
#                         # Parse response.
#                         if response.status == 200:
#                             logging.info('RESPONSE STATUS IS A-OKAY!')
#                             if type(response.data) is list:
#                                 # Twitter returns the tweets as a JSON list.
#                                 self.response.write('Your 5 most recent tweets:')
#                                 # logging.info('RESPONSE DATA IS: %s' % response.data)
#                                 for tweet in response.data:
#                                     text = tweet.get('text')
#                                     date = tweet.get('created_at')
#                                     name = tweet.get('user').get('name')
#                                     media = tweet.get('mediaurl')
#                                     logging.info('MEDIA URL IS: %s' % media)
#                                     handle = tweet.get('user').get('screen_name')
#
#                                     self.response.write(u'<h3>{0} @{1}</h3>'.format(name, handle))
#                                     self.response.write(u'<h4>{}</h4>'.format(text.replace(u'\u2013', '[???]')))
#                                     self.response.write(u'Tweeted on: {}'.format(date))
#
#                             elif response.data.get('errors'):
#                                 self.response.write(u'Damn that error: {}!'.\
#                                                     format(response.data.get('errors')))
#                         else:
#                             self.response.write('Damn that unknown error!<br />')
#                             self.response.write(u'Status: {}'.format(response.status))
#
#                     if result.provider.name == 'go':
#                         pass

    # def post(self, provider_name):
    #     self.response.write('<a href="..">Home</a>')
    #
    #     # Retrieve the message from POST parameters and the values from cookies.
    #     message = self.request.POST.get('message')
    #     serialized_credentials = self.request.cookies.get('credentials')
    #     user_id = self.request.cookies.get('user_id')
    #
    #     if provider_name == 'fb':
    #         # Prepare the URL for Facebook Graph API.
    #         url = 'https://graph.facebook.com/{0}/feed'.format(user_id)
    #
    #         # Access user's protected resource.
    #         response = authomatic.access(serialized_credentials, url,
    #                                      params=dict(message=message),
    #                                      method='POST')
    #
    #         # Parse response.
    #         post_id = response.data.get('id')
    #         error = response.data.get('error')
    #
    #         if error:
    #             self.response.write('<p>Damn that error: {0}!</p>'.format(error))
    #         elif post_id:
    #             self.response.write('<p>You just posted a status with id ' + \
    #                                 '{0} to your Facebook timeline.<p/>'.format(post_id))
    #         else:
    #             self.response.write('<p>Damn that unknown error! Status code: {0}</p>'\
    #                                 .format(response.status))
    #
    #     elif provider_name == 'tw':
    #
    #         response = authomatic.access(serialized_credentials,
    #                                      url='https://api.twitter.com/1.1/statuses/update.json',
    #                                      params=dict(status=message),
    #                                      method='POST')
    #
    #         error = response.data.get('errors')
    #         tweet_id = response.data.get('id')
    #
    #         if error:
    #             self.response.write('<p>Damn that error: {0}!</p>'.format(error))
    #         elif tweet_id:
    #             self.response.write("""
    #             <p>
    #                 You just tweeted a tweet with id {0}.
    #             </p>
    #             """.format(tweet_id))
    #         else:
    #             self.response.write("""
    #             <p>
    #                 Damn that unknown error! Status code: {0}
    #             </p>
    #             """.format(response.status))
    #
    #     # Let the user repeat the action.
    #     self.response.write("""
    #     <form method="post">
    #         <input type="text" name="message" />
    #         <input type="submit" value="Do it again!">
    #     </form>
    #     """)

class Logout(webapp2.RequestHandler):
    def get(self):
        logging.info("logout handler (get)")
        # Delete cookies.
        self.response.delete_cookie('fb_user_id')
        self.response.delete_cookie('fb_user_name')
        self.response.delete_cookie('fb_credentials')
        self.response.delete_cookie('tw_user_id')
        self.response.delete_cookie('tw_user_name')
        self.response.delete_cookie('tw_credentials')

        # Redirect home.
        self.redirect('./')

class TrialHandler(webapp2.RequestHandler):
    def get(self):
        logging.info("trial handler (get)")
        template = jinja_environment.get_template('templates/mainpage.html')
        self.response.out.write(template.render())


# Create the routes.
ROUTES = [webapp2.Route(r'/login/<:.*>', Login, handler_method='any'),
          webapp2.Route(r'/login', LoginGoogleHandler),
          webapp2.Route(r'/refresh', Refresh),
        #   webapp2.Route(r'/action/<:.*>', Action, handler_method='any'),
          webapp2.Route(r'/logout', Logout),
          webapp2.Route(r'/', Home, handler_method='any')]

# Instantiate the WSGI application.
app = webapp2.WSGIApplication(ROUTES, debug=True)
