from settings import *
import logging

SITE_ID = 4
SITE_NAME = 'mirosubs-adam'


# socialauth-related
OPENID_REDIRECT_NEXT = '/accounts/openid/done/'
 
OPENID_SREG = {"requred": "nickname, email", "optional":"postcode, country", "policy_url": ""}
OPENID_AX = [{"type_uri": "email", "count": 1, "required": False, "alias": "email"}, {"type_uri": "fullname", "count":1 , "required": False, "alias": "fullname"}]
 
TWITTER_CONSUMER_KEY = 'GRcOIZyWRM0XxluS6flA'
TWITTER_CONSUMER_SECRET = '4BSIzc524xOV9edjyXgJiae1krY7TEmG38K7tKohc'

FACEBOOK_API_KEY = ''
FACEBOOK_API_SECRET = ''
 
AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend',
                           'socialauth.auth_backends.OpenIdBackend',
                           'socialauth.auth_backends.TwitterBackend',
                           'socialauth.auth_backends.FacebookBackend',
                           )
