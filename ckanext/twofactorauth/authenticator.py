import logging

from zope.interface import implements
from repoze.who.interfaces import IAuthenticator

from ckan.model import User

from ckanext.twofactorauth.model.totp_device import TOTPDevice
from ckanext.twofactorauth.model.static_device import StaticDevice
from ckanext.twofactorauth.model.static_token import StaticToken

log = logging.getLogger(__name__)

class TwoFactorAuthenticator(object):
    '''
    A repoze.who plugin to authenticate with 2 factor authentication
    '''
    implements(IAuthenticator)

    def authenticate(self, environ, identity):
        if not ('login' in identity and 'password' in identity):
            return None

        login = identity['login']
        user = User.by_name(login)

        if user is None:
            log.error('Login failed - username %r not found', login)
        elif not user.is_active():
            log.error('Login as %r failed - user isn\'t active', login)
        elif not user.validate_password(identity['password']):
            log.error('Login as %r failed - password not valid', login)
        else:
            # Does this user have any confirmed TOTP devices?
            devices = TOTPDevice.devices_for_user(user.id)

            # If two factor auth is enabled the user must provide a token
            print identity
            if devices and 'token' not in identity:
                log.error('Login failed, token required for two factor auth')
                return None

            return user.name

        return None
