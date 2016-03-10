from __future__ import absolute_import, division, print_function, unicode_literals

import logging

from ckan import plugins
from ckan.plugins import toolkit as tk

from ckanext.twofactorauth.model import totp_device, static_device, static_token

log = logging.getLogger(__name__)

class TwoFactorAuthPlugin(plugins.SingletonPlugin):
	plugins.implements(plugins.IConfigurer)
	plugins.implements(plugins.IConfigurable)
	plugins.implements(plugins.IRoutes)

	# IConfigurable
	def configure(self, config):
		# Create the tables if they don't exist
		totp_device.totp_device_table.create(checkfirst=True)
		static_device.static_device_table.create(checkfirst=True)
		static_token.static_token_table.create(checkfirst=True)

	# IConfigurer
	def update_config(self, config_):
		tk.add_template_directory(config_, 'templates')
		tk.add_public_directory(config_, 'public')

	# IRoutes
	def before_map(self, route_map):
		controller = 'ckanext.twofactorauth.controllers:TwoFactorAuthController'

		route_map.connect('twofactorauth_manage',
			'/user/twofactorauth/manage',
			controller=controller,
			action='manage')
		route_map.connect('twofactorauth_setup',
			'/user/twofactorauth/setup',
			controller=controller,
			action='setup')
		route_map.connect('twofactorauth_setup_verify',
			'/user/twofactorauth/setup/verify',
			controller=controller,
			action='setup_verify')

		return route_map

	def after_map(self, route_map):
		return route_map
