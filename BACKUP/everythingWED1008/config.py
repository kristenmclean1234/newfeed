# config.py

from authomatic.providers import oauth2, oauth1, openid, gaeopenid
import authomatic

CONFIG = {

    'tw': { # Your internal provider name

        # Provider class
        'class_': oauth1.Twitter,

        # Twitter is an AuthorizationProvider so we need to set several other properties too:
        'consumer_key': 'kCh51IOR8BVdmW3Iuf0TpjYD6',
        'consumer_secret': 'p4QsgwRFvBMa9wEMkwpzYRFEPwYc4znupLd4xlBWlFLYZLjOpf',
        'id': authomatic.provider_id()
    },

    'fb': {

        'class_': oauth2.Facebook,

        # Facebook is AuthorizationProvider too.
        'consumer_key': '1596489813951598',
        'consumer_secret': '0bb58a5f081d84e12d28dd1bf6f6f2a1',
        'id': authomatic.provider_id(),

        # We need the "publish_stream" scope to post to users timeline,
        # the "offline_access" scope to be able to refresh credentials,
        # and the other scopes to get user info.
        'scope': ['user_posts'],
    },

    'go': {

        'class_': oauth2.Google,

        'consumer_key': '881600187038-co0kp02bf3ffbfupnnrdes55ko1ued9r.apps.googleusercontent.com',
        'consumer_secret': 'YV_GX-JJkyJXCFC7ZmOW3c2I',
        'id': authomatic.provider_id(),

    },

    'gae_oi': {

        # OpenID provider based on Google App Engine Users API.
        # Works only on GAE and returns only the id and email of a user.
        # Moreover, the id is not available in the development environment!
        'class_': gaeopenid.GAEOpenID,
    },

    'oi': {

        # OpenID provider based on the python-openid library.
        # Works everywhere, is flexible, but requires more resources.
        'class_': openid.OpenID,
        'store': openid.SessionOpenIDStore,
    }
}
