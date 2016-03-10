from __future__ import absolute_import, division, print_function, unicode_literals

from sqlalchemy import types, Column, Table, ForeignKey, and_, UniqueConstraint

from ckan.lib.base import config
from ckan import model
from ckan.model import Session
from ckan.model import meta
from ckan.model import types as _types
from ckan.model.domain_object import DomainObject

from ckanext.twofactorauth.oath import TOTP
from ckanext.twofactorauth.utils import random_hex, hex_validator

def default_key():
    return random_hex(20)

totp_device_table = Table('twofactorauth_totp_device', meta.metadata,
	Column('id', types.UnicodeText, primary_key=True, default=_types.make_uuid),

	Column('user_id', types.UnicodeText,
		ForeignKey('user.id', onupdate='CASCADE',
			ondelete='CASCADE')),

	# Human readable name of this device
	Column('name', types.UnicodeText),

	#A hex-encoded secret key of up to 40 bytes
	Column('key', types.UnicodeText),

	# Time time step in seconds
	Column('step', types.Integer, default=30),

	# The unix time at to begin counting steps
	Column('t0', types.BigInteger, default=0),

	# The number of digits to expect in a token
	Column('digits', types.Integer, default=6),

	# The number of time steps in the past or future to allow
	Column('tolerance', types.Integer, default=1),

	# The number of time steps the provder is known to deviate from our clock
	Column('drift', types.Integer, default=0),

	# The t value of the last verified token.
	# The next token must be at a higher time step
	Column('last_t', types.BigInteger, default=-1),

	# Is the device ready for user?
	Column('confirmed', types.Boolean, default=True),
)

class TOTPDevice(DomainObject):
	@classmethod
	def get(cls, **kw):
		query = model.Session.query(cls).autoflush(False)
		return query.filter_by(**kw).first()

	@classmethod
	def find(cls, **kw):
		query = model.Session.query(cls).autoflush(False)
		return query.filter_by(**kw)

	@classmethod
	def devices_for_user(cls, user):
		query = model.Session.query(cls).autoFlush(False)
		return query.filter_by(user_id=user, confirmed=True)

## --------------------------------------------------------
## Mapper Stuff

meta.mapper(TOTPDevice, totp_device_table)
