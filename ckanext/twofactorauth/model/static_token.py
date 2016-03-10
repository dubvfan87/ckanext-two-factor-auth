from __future__ import absolute_import, division, print_function, unicode_literals

from base64 import b32encode
from os import urandom

from sqlalchemy import types, Column, Table, ForeignKey, and_, UniqueConstraint

from ckan.lib.base import config
from ckan import model
from ckan.model import Session
from ckan.model import meta
from ckan.model import types as _types
from ckan.model.domain_object import DomainObject

static_token_table = Table('twofactorauth_static_token', meta.metadata,
	Column('id', types.UnicodeText, primary_key=True, default=_types.make_uuid),
	Column('user_id', types.UnicodeText,
		ForeignKey('user.id', onupdate='CASCADE',
			ondelete='CASCADE')),
	Column('device_id', types.UnicodeText,
		ForeignKey('twofactorauth_static_device.id', onupdate='CASCADE',
			ondelete='CASCADE')),
	Column('token', types.UnicodeText),
)

class StaticToken(DomainObject):
	@classmethod
	def get(cls, **kw):
		query = model.Session.query(cls).autoflush(False)
		return query.filter_by(**kw).first()

	@classmethod
	def find(cls, **kw):
		query = model.Session.query(cls).autoflush(False)
		return query.filter_by(**kw)

	@classmethod
	def random_token():
		"""
		Returns a new random string that can be used as a static token.

		:rtype: str
		"""
		return b32encode(urandom(5)).lower()

## --------------------------------------------------------
## Mapper Stuff

meta.mapper(StaticToken, static_token_table)
