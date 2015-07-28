# main.py

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

def setup_logger(logger):
    logger.setLevel(logging.DEBUG)

    sh = logging.StreamHandler()
    formatter = logging.Formatter(LOG_FORMAT)
    sh.setFormatter(formatter)

    def decorate_emit(fn):
    # add methods we need to the class
        def new(*args):
            levelno = args[0].levelno
            if(levelno >= logging.CRITICAL):
                color = '\x1b[31;1m'
            elif(levelno >= logging.ERROR):
                color = '\x1b[31;1m'
            elif(levelno >= logging.WARNING):
                color = '\x1b[33;1m'
            elif(levelno >= logging.INFO):
                color = '\x1b[32;1m'
            elif(levelno >= logging.DEBUG):
                color = '\x1b[35;1m'
            else:
                color = '\x1b[0m'
            # add colored *** in the beginning of the message
            args[0].msg = "{0}***\x1b[0m {1}".format(color, args[0].msg)

            # new feature i like: bolder each args of message
            args[0].args = tuple('\x1b[1m' + arg + '\x1b[0m' for arg in args[0].args)
            return fn(*args)
        return new
    sh.emit = decorate_emit(sh.emit)
    logger.addHandler(sh)
# Setup Authomatic.
authomatic = Authomatic(config=CONFIG, secret='some random secret string')
class User(db.Model):
    user_name = db.StringProperty(required=True)
    user_id = db.StringProperty(required=True)
    result = db.StringProperty(required=False)
    credentials = db.StringProperty(required=True)
    error = db.StringProperty(required=True)


class Login(webapp2.RequestHandler):
    def any(self, provider_name):

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
        # Create links to the Login handler.
        self.response.write('Login with <a href="login/fb">Facebook</a> or ')
        self.response.write('<a href="login/tw">Twitter</a>')

        # Retrieve values from cookies.
        serialized_credentials = self.request.cookies.get('credentials')
        user_id = self.request.cookies.get('user_id')
        user_name = urllib.unquote(self.request.cookies.get('user_name', ''))
        # error = urllib.unquote(self.request.cookies.get('error', ''))
        #
        # if error:
        #     self.response.write('<p>Damn that error: {0}</p>'.format(error))
        if user_id:
            self.response.write('<h1>Hi {0}</h1>'.format(user_name))

            if serialized_credentials:
                # Deserialize credentials.
                credentials = authomatic.credentials(serialized_credentials)
                logging.info('CREDENTIALS ARE: %s' % credentials)


                self.response.write("""
                <p>
                    You are logged in with <b>{0}</b> and we have your credentials.
                </p>
                """.format(dict(fb='Facebook', tw='Twitter')[credentials.provider_name]))

                valid = 'still' if credentials.valid else 'not anymore'
                expire_soon = 'less' if credentials.expire_soon(60 * 60 * 24) else 'more'
                remaining = credentials.expire_in
                expire_on = credentials.expiration_date

                self.response.write("""
                <p>
                    They are <b>{0}</b> valid and
                    will expire in <b>{1}</b> than one day
                    (in <b>{2}</b> seconds to be precise).
                    It will be on <b>{3}</b>.
                </p>
                """.format(valid, expire_soon, remaining, expire_on))

                if credentials.valid:
                    self.response.write("""
                    <p>We can refresh them while they are valid.</p>
                    <a href="refresh">OK, refresh them!</a>
                    <p>Moreover, we can do powerful stuff with them.</p>
                    <a href="action/{0}">Show me what you can do!</a>
                    """.format(credentials.provider_name))
                else:
                    self.response.write("""
                    <p>
                        Repeat the <b>login procedure</b>to get new credentials.
                    </p>
                    <a href="login/{0}">Refresh</a>
                    """.format(credentials.provider_name))

            self.response.write('<p>We can also log you out.</p>')
            self.response.write('<a href="logout">OK, log me out!</a>')


class Refresh(webapp2.RequestHandler):
    def get(self):
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


        # if provider_name == 'fb':
        #     text = 'post a status on your Facebook timeline'
        # elif provider_name == 'tw':
        #     text = 'tweet'
        #
        # self.response.write("""
        # <a href="..">Home</a>
        # <p>We can {0} on your behalf.</p>
        # <form method="post">
        #     <input type="text" name="message" value="Have you got a bandage?" />
        #     <input type="submit" value="Do it!">
        # </form>
        # """.format(text))



    def post(self, provider_name):
        self.response.write('<a href="..">Home</a>')

        # Retrieve the message from POST parameters and the values from cookies.
        message = self.request.POST.get('message')
        serialized_credentials = self.request.cookies.get('credentials')
        user_id = self.request.cookies.get('user_id')

        if provider_name == 'fb':
            # Prepare the URL for Facebook Graph API.
            url = 'https://graph.facebook.com/{0}/feed'.format(user_id)

            # Access user's protected resource.
            response = authomatic.access(serialized_credentials, url,
                                         params=dict(message=message),
                                         method='POST')

            # Parse response.
            post_id = response.data.get('id')
            error = response.data.get('error')

            if error:
                self.response.write('<p>Damn that error: {0}!</p>'.format(error))
            elif post_id:
                self.response.write('<p>You just posted a status with id ' + \
                                    '{0} to your Facebook timeline.<p/>'.format(post_id))
            else:
                self.response.write('<p>Damn that unknown error! Status code: {0}</p>'\
                                    .format(response.status))

        elif provider_name == 'tw':

            response = authomatic.access(serialized_credentials,
                                         url='https://api.twitter.com/1.1/statuses/update.json',
                                         params=dict(status=message),
                                         method='POST')

            error = response.data.get('errors')
            tweet_id = response.data.get('id')

            if error:
                self.response.write('<p>Damn that error: {0}!</p>'.format(error))
            elif tweet_id:
                self.response.write("""
                <p>
                    You just tweeted a tweet with id {0}.
                </p>
                """.format(tweet_id))
            else:
                self.response.write("""
                <p>
                    Damn that unknown error! Status code: {0}
                </p>
                """.format(response.status))

        # Let the user repeat the action.
        self.response.write("""
        <form method="post">
            <input type="text" name="message" />
            <input type="submit" value="Do it again!">
        </form>
        """)


class Logout(webapp2.RequestHandler):
    def get(self):
        # Delete cookies.
        self.response.delete_cookie('user_id')
        self.response.delete_cookie('user_name')
        self.response.delete_cookie('credentials')

        # Redirect home.
        self.redirect('./')


# Create the routes.
ROUTES = [webapp2.Route(r'/login/<:.*>', Login, handler_method='any'),
          webapp2.Route(r'/refresh', Refresh),
          webapp2.Route(r'/action/<:.*>', Action, handler_method='any'),
          webapp2.Route(r'/logout', Logout),
          webapp2.Route(r'/', Home)]

# Instantiate the WSGI application.
app = webapp2.WSGIApplication(ROUTES, debug=True)
