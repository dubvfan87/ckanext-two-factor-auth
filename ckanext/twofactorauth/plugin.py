from __future__ import unicode_literals

import logging

from ckan import plugins
from ckan.plugins import toolkit as tk

from ckanext.twofactorauth.model import totp_device

log = logging.getLogger(__name__)

class TwoFactorAuthPlugin(plugins.SingletonPlugin):
	plugins.implements(plugins.IConfigurer)
	plugins.implements(plugins.IConfigurable)

	# IConfigurable
	def configure(self, config):
		# Create the tables if they don't exist
		totp_device.totp_device_table.create(checkfirst=True)

	# IConfigurer
	def update_config(self, config_):
		tk.add_template_directory(config_, 'templates')
		tk.add_public_directory(config_, 'public')
