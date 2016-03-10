from __future__ import absolute_import, division, print_function, unicode_literals

from sqlalchemy import types, Column, Table, ForeignKey, and_, UniqueConstraint

from ckan.lib.base import config
from ckan import model
from ckan.model import Session
from ckan.model import meta
from ckan.model import types as _types
from ckan.model.domain_object import DomainObject

static_device_table = Table('twofactorauth_static_device', meta.metadata,
	Column('id', types.UnicodeText, primary_key=True, default=_types.make_uuid),

	Column('user_id', types.UnicodeText,
		ForeignKey('user.id', onupdate='CASCADE',
			ondelete='CASCADE')),

	# Human readable name of this device
	Column('name', types.UnicodeText),

	# Is the device ready for user?
	Column('confirmed', types.Boolean, default=True),
)

class StaticDevice(DomainObject):
	@classmethod
	def get(cls, **kw):
		query = model.Session.query(cls).autoflush(False)
		return query.filter_by(**kw).first()

	@classmethod
	def find(cls, **kw):
		query = model.Session.query(cls).autoflush(False)
		return query.filter_by(**kw)

## --------------------------------------------------------
## Mapper Stuff

meta.mapper(StaticDevice, static_device_table)
