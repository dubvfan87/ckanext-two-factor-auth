from __future__ import unicode_literals

import logging
import json

from base64 import b64decode, b64encode
from repoze.who.interfaces import IIdentifier, IAuthenticator, IChallenger
from webob import Request, Response
from zope.interface import implements

from ckan.model import User

log = logging.getLogger(__name__)


def make_plugin(**kwargs):
    return TwoStepAuthPlugin(**kwargs)


class TwoFactorAuthPlugin(object):
    '''
    A repoze.who plugin to authenticate with 2 step authentication
    '''

    came_from_field = 'came_from'

    implements(IIdentifier, IChallenger, IAuthenticator)

    def __init__(self):
        return

    def identify(self, environ):
        return True

    def authenticate(self, environ, identity):
        return None
