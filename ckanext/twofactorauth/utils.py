from __future__ import absolute_import, division, print_function, unicode_literals

from binascii import hexlify, unhexlify
from os import urandom

try:
    from urllib.parse import quote, urlencode
except ImportError:
    from urllib import quote, urlencode

from ckan.plugins import toolkit as tk

def hex_validator(length=0):
    """
    Returns a function to be used as a model validator for a hex-encoded
    CharField. This is useful for secret keys of all kinds::

        def key_validator(value):
            return hex_validator(20)(value)

        key = models.CharField(max_length=40, validators=[key_validator], help_text=u'A hex-encoded 20-byte secret key')

    :param int length: If greater than 0, validation will fail unless the
        decoded value is exactly this number of bytes.

    :rtype: function

    >>> hex_validator()('0123456789abcdef')
    >>> hex_validator(8)(b'0123456789abcdef')
    >>> hex_validator()('phlebotinum')          # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    ValidationError: ['phlebotinum is not valid hex-encoded data.']
    >>> hex_validator(9)('0123456789abcdef')    # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    ValidationError: ['0123456789abcdef does not represent exactly 9 bytes.']
    """
    def _validator(value):
        try:
            if isinstance(value, six.text_type):
                value = value.encode()

            unhexlify(value)
        except Exception:
            raise tk.ValidationError('{0} is not valid hex-encoded data.'.format(value))

        if (length > 0) and (len(value) != length * 2):
            raise tk.ValidationError('{0} does not represent exactly {1} bytes.'.format(value, length))

    return _validator


def random_hex(length=20):
    """
    Returns a string of random bytes encoded as hex. This uses
    :func:`os.urandom`, so it should be suitable for generating cryptographic
    keys.

    :param int length: The number of (decoded) bytes to return.

    :returns: A string of hex digits.
    :rtype: str
    """
    return hexlify(urandom(length))

def totp_digits():
    """
    Returns the number of digits for totp tokens. Defaults to 6
    """
    return 6

def get_otpauth_url(accountname, secret, issuer=None, digits=None):
    # For a complete run-through of all the parameters, have a look at the
    # specs at:
    # https://github.com/google/google-authenticator/wiki/Key-Uri-Format

    # quote and urlencode work best with bytes, not unicode strings.
    accountname = accountname.encode('utf8')
    issuer = issuer.encode('utf8') if issuer else None

    label = quote(b': '.join([issuer, accountname]) if issuer else accountname)

    # Ensure that the secret parameter is the FIRST parameter of the URI, this
    # allows Microsoft Authenticator to work.
    query = [
        ('secret', secret),
        ('digits', digits or totp_digits())
    ]

    if issuer:
        query.append(('issuer', issuer))

    return 'otpauth://totp/%s?%s' % (label, urlencode(query))
