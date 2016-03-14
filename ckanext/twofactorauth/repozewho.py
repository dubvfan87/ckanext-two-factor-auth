from urlparse import urlparse, urlunparse
from urllib import urlencode
try:
    from urlparse import parse_qs
except ImportError:#pragma: no cover
    from cgi import parse_qs

from webob import Request
# TODO: Stop using Paste; we already started using WebOb
from webob.exc import HTTPFound, HTTPUnauthorized
from paste.request import construct_url, parse_dict_querystring, parse_formvars
from zope.interface import implements

from repoze.who.interfaces import IChallenger, IIdentifier

__all__ = ['TwoFactorAuthPlugin']

class TwoFactorAuthPlugin(object):
    implements(IIdentifier)

    def __init__(self, rememberer_name):
        self.rememberer_name = rememberer_name

    # IIdentifier
    def identify(self, environ):
        credentials = {
            'token': 'TEST TOKEN'
        }
        return credentials

    # IIdentifier
    def remember(self, environ, identity):
        rememberer = self._get_rememberer(environ)
        return rememberer.remember(environ, identity)

    # IIdentifier
    def forget(self, environ, identity):
        rememberer = self._get_rememberer(environ)
        return rememberer.forget(environ, identity)

    def _get_rememberer(self, environ):
        rememberer = environ['repoze.who.plugins'][self.rememberer_name]
        return rememberer
