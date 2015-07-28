import urllib
import webapp2
from authomatic import Authomatic
from authomatic.adapters import Webapp2Adapter
import logging
from config import CONFIG
from google.appengine.ext import db
from google.appengine.api import users
import pprint
import twitter
import json
import random
from google.appengine.api import urlfetch
import jinja2
import os

authomatic = Authomatic(config=CONFIG, secret='some random secret string')
jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class LoginGoogleHandler(webapp2.RequestHandler):
    def get(self):
        logging.info("Google login handler")
        template = jinja_environment.get_template('templates/googleloginpage.html')
        self.response.out.write(template.render())

class Login(webapp2.RequestHandler):
    def any(self, provider_name):
        logging.info("logging in -- PROVIDER NAME IS: %s", provider_name)

        result = authomatic.login(Webapp2Adapter(self), provider_name)
        self.response.set_cookie('result', str(result))
        # user = User(result=result)
        # user.put()
        pprint.pprint('RESULT IS %s' % result)

        if result:
            if result.user:
                result.user.update()
                self.response.write('<h1>Hi {0}</h1>'.format(result.user.name))

                # Save the user name and ID to cookies that we can use it in other handlers.
                self.response.set_cookie('user_id', result.user.id)
                self.response.set_cookie('user_name', urllib.quote(result.user.name))

                if result.user.credentials:
                    # Serialize credentials and store it as well.
                    serialized_credentials = result.user.credentials.serialize()
                    self.response.set_cookie('credentials', serialized_credentials)

            elif result.error:
                self.response.set_cookie('error', urllib.quote(result.error.message))

            self.redirect('/')

class Home(webapp2.RequestHandler):
    def get(self):
        logging.info("home (get) handler")
        # Retrieve values from cookies.
        serialized_credentials = self.request.cookies.get('credentials')
        user_id = self.request.cookies.get('user_id')
        user_name = urllib.unquote(self.request.cookies.get('user_name', ''))
        # error = urllib.unquote(self.request.cookies.get('error', ''))
        logging.info("home handler found user_id: %s", user_id)
        # if error:
        #     self.response.write('<p>Damn that error: {0}</p>'.format(error))
        if user_id:
            # self.response.write('<h1>Hi {0}</h1>'.format(user_name))

            if serialized_credentials:
                # Deserialize credentials.
                credentials = authomatic.credentials(serialized_credentials)
                logging.info('CREDENTIALS ARE: %s' % credentials)

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

                if credentials.valid:
                    pass
                else:
                    self.response.write("""
                    <p>
                        Repeat the <b>login procedure</b>to get new credentials.
                    </p>
                    <a href="login/{0}">Refresh</a>
                    """.format(credentials.provider_name))
        else:
            # self.redirect('/')
            template = jinja_environment.get_template('templates/login.html')
            self.response.write(template.render())
            return


        url = "http://api.nytimes.com/svc/search/v2/articlesearch.json?"
        api_key ="api-key=7169254a2f887db9ab1c3c629fed79d3:16:72574373"
        nyt_data_source = urlfetch.fetch(url+api_key)
        nyt_json_content = nyt_data_source.content
        parsed_nyt_dictionary = json.loads(nyt_json_content)
        #not all articles have these 3 things... what do we do?
        articles = []
        for doc in parsed_nyt_dictionary['response']['docs']:
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




        # Create links to the Login handler.
        template = jinja_environment.get_template('templates/mainpage.html')
        self.response.write(template.render({
                                            'articles' : articles,
                                            'name' : format(user_name),
                                            'provider' : format(dict(fb='Facebook', tw='Twitter')[credentials.provider_name]),
                                            'providerslug' : format(credentials.provider_name)
                                        }))


class Refresh(webapp2.RequestHandler):
    def get(self):
        logging.info("refresh (get) handler")
        self.response.write('<a href="..">Home</a>')

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

class Action(webapp2.RequestHandler):
    def any(self, provider_name):
        logging.info("action handler got provider_name %s", provider_name)
        result = authomatic.login(Webapp2Adapter(self), provider_name)
        # result = self.request.cookies.get('result')
        logging.info('RESULT IS: %s' % result)
        serialized_credentials = self.request.cookies.get('credentials')
        user_id = self.request.cookies.get('user_id')

        response = authomatic.access(serialized_credentials,
                                     url='https://api.twitter.com/1.1/statuses/home_timeline.json',
                                     method='GET')
        logging.info('RESPONSE IS: %s' % response)


        if result:
            # If there is result, the login procedure is over and we can write to response.
            self.response.write('<a href="..">Home</a>')

            if result.error:
                # Login procedure finished with an error.
                self.response.write(u'<h2>Damn that error: {}</h2>'.format(result.error.message))


            elif result.user:
                # Hooray, we have the user!

                # OAuth 2.0 and OAuth 1.0a provide only limited user data on login,
                # We need to update the user to get more info.
                if not (result.user.name and result.user.id):
                    result.user.update()

                # Welcome the user.
                self.response.write(u'<h1>Hi {}</h1>'.format(result.user.name))
                self.response.write(u'<h2>Your id is: {}</h2>'.format(result.user.id))
                self.response.write(u'<h2>Your email is: {}</h2>'.format(result.user.email))
                logging.info('CREDENTIALS ARE: %s' % result.user.credentials)
                credentials = result.user.credentials
                logging.info('CREDENTIALS VARIABLE VALUE IS: %s' % credentials)
                # self.response.set_cookie('credentials', credentials)


                # Seems like we're done, but there's more we can do...

                # If there are credentials (only by AuthorizationProvider),
                # we can _access user's protected resources.
                if result.user.credentials:

                    # Each provider has it's specific API.
                    if result.provider.name == 'fb':
                        self.response.write('Your are logged in with Facebook.<br />')

                        # We will access the user's 5 most recent statuses.
                        url = 'https://graph.facebook.com/{}?fields=feed.limit(10)'
                        url = url.format(result.user.id)
                        logging.info("USER ID IS: %s" % result.user.id)

                        # Access user's protected resource.
                        response = result.provider.access(url)

                        if response.status == 200:
                            # Parse response.
                            statuses = response.data.get('feed').get('data')
                            error = response.data.get('error')

                            if error:
                                self.response.write(u'Damn that error: {}!'.format(error))
                            elif statuses:
                                self.response.write('Your 10 most recent statuses:<br />')
                                for message in statuses:

                                    text = message.get('message')
                                    date = message.get('created_time')

                                    self.response.write(u'<h3>{}</h3>'.format(text))
                                    self.response.write(u'Posted on: {}'.format(date))
                        else:
                            self.response.write('Damn that unknown error!<br />')
                            self.response.write(u'Status: {}'.format(response.status))

                    if result.provider.name == 'tw':
                        self.response.write('Your are logged in with Twitter.<br />')

                        # We will get the user's 5 most recent tweets.
                        url = 'https://api.twitter.com/1.1/statuses/home_timeline.json'

                        # You can pass a dictionary of querystring parameters.
                        response = result.provider.access(url, {'count': 10})
                        logging.info('RESPONSE IS: %s' % response)

                        # Parse response.
                        if response.status == 200:
                            logging.info('RESPONSE STATUS IS A-OKAY!')
                            if type(response.data) is list:
                                # Twitter returns the tweets as a JSON list.
                                self.response.write('Your 5 most recent tweets:')
                                # logging.info('RESPONSE DATA IS: %s' % response.data)
                                for tweet in response.data:
                                    text = tweet.get('text')
                                    date = tweet.get('created_at')
                                    name = tweet.get('user').get('name')
                                    media = tweet.get('mediaurl')
                                    logging.info('MEDIA URL IS: %s' % media)
                                    handle = tweet.get('user').get('screen_name')

                                    self.response.write(u'<h3>{0} @{1}</h3>'.format(name, handle))
                                    self.response.write(u'<h4>{}</h4>'.format(text.replace(u'\u2013', '[???]')))
                                    self.response.write(u'Tweeted on: {}'.format(date))

                            elif response.data.get('errors'):
                                self.response.write(u'Damn that error: {}!'.\
                                                    format(response.data.get('errors')))
                        else:
                            self.response.write('Damn that unknown error!<br />')
                            self.response.write(u'Status: {}'.format(response.status))

                    if result.provider.name == 'go':
                        pass

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
        self.response.delete_cookie('user_id')
        self.response.delete_cookie('user_name')
        self.response.delete_cookie('credentials')

        # Redirect home.
        self.redirect('./')

class MainHandler(webapp2.RequestHandler):
    def get(self):
        logging.info("main handler (get)")
        #template = jinja_environment.get_template('templates/news.html')
        #url: http://api.nytimes.com/svc/search/v2/articlesearch.response-format?[q=search term&fq=filter-field:(filter-term)&additional-params=values]&api-key=####
        #base_url = "http://api.nytimes.com/svc/search/v2/articlesearch.response-format?q=sports"
        #search_term =
        url = "http://api.nytimes.com/svc/search/v2/articlesearch.json?"
        api_key ="api-key=7169254a2f887db9ab1c3c629fed79d3:16:72574373"
        nyt_data_source = urlfetch.fetch(url+api_key)
        nyt_json_content = nyt_data_source.content
        parsed_nyt_dictionary = json.loads(nyt_json_content)
        #not all articles have these 3 things... what do we do?
        articles = []
        for doc in parsed_nyt_dictionary['response']['docs']:
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
        template = jinja_environment.get_template('templates/mainpage.html')
        self.response.write(template.render({'articles' : articles}))

class TrialHandler(webapp2.RequestHandler):
    def get(self):
        logging.info("trial handler (get)")
        template = jinja_environment.get_template('templates/mainpage.html')
        self.response.out.write(template.render())


# Create the routes.
ROUTES = [webapp2.Route(r'/login/<:.*>', Login, handler_method='any'),
          webapp2.Route(r'/login', LoginGoogleHandler),
          webapp2.Route(r'/refresh', Refresh),
          webapp2.Route(r'/action/<:.*>', Action, handler_method='any'),
          webapp2.Route(r'/logout', Logout),
          webapp2.Route(r'/', Home)]

# Instantiate the WSGI application.
app = webapp2.WSGIApplication(ROUTES, debug=True)
