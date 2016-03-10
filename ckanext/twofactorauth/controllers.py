from __future__ import absolute_import, division, print_function, unicode_literals

import os
from binascii import unhexlify
from base64 import b32encode

from pylons import session, config
from pylons.i18n import _

from ckan import model
from ckan.plugins import toolkit as tk

from ckanext.twofactorauth.model.totp_device import TOTPDevice
from ckanext.twofactorauth.utils import random_hex, get_otpauth_url, totp_digits

import io
import qrcode
import qrcode.image.svg

try:
	from urllib.parse import quote, urlencode
except ImportError:
	from urllib import quote, urlencode

c = tk.c

class TwoFactorAuthController(tk.BaseController):
	def __before__(self, action, **env):
		super(TwoFactorAuthController, self).__before__(action, **env)

		try:
			context = {'model': model, 'user': c.user }
			tk.check_access('site_read', context)
		except NotAuthorized:
			tk.abort(401, _('Not authorized to see this page'))

		is_user_setup = self._is_user_setup()

		if not is_user_setup and action not in ['setup', 'setup_verify']:
			tk.redirect_to('twofactorauth_setup')
		elif is_user_setup and action == 'setup':
			tk.redirect_to('twofactorauth_manage')

	def _is_user_setup(self):
		user_id = model.User.by_name(c.user).id
		devices = TOTPDevice.devices_for_user(user_id)
		return len(devices) > 0

	def _get_key(self):
		key = random_hex(20).decode('ascii')
		return key

	def manage(self):
		return tk.render('ckanext/twofactorauth/manage.html')

	def setup(self, data=None, errors=None, error_summary=None):
		data = data or {}

		saved_key = session.get('twofactorauth_saved_key')
		key = saved_key or self._get_key()
		rawkey = unhexlify(key.encode('ascii'))
		b32key = b32encode(rawkey).decode('utf-8')

		# Save these in the session until the verify step is complete
		session['twofactorauth_saved_key'] = key
		session['twofactorauth_saved_b32key'] = b32key
		session.save()

		# Generate a valid otp url to scan
		otpauth_url = get_otpauth_url(c.user, b32key, issuer='Energy Data Exchange (NETL)')

		# Make and return QR code
		qrcode_img = qrcode.make(otpauth_url, image_factory=qrcode.image.svg.SvgPathImage)
		with io.BytesIO() as f:
			qrcode_img.save(f)
			data['img'] = f.getvalue()
			f.close()

		# Drop the extra XML header from the svg
		data['img'] = data['img'][data['img'].find('<svg'):]

		vars = {'data': data, 'errors': errors,
				'error_summary': error_summary, 'action': 'new'}

		return tk.render('ckanext/twofactorauth/setup.html',
			extra_vars=vars)

	def setup_verify(self, data=None, errors=None, error_summary=None):
		data = data or {}

		key = session.get('twofactorauth_saved_key')
		b32key = session.get('twofactorauth_saved_b32key')
		token = tk.request.params.get('token')

		device = TOTPDevice()
		device.name = 'default'
		device.key = key
		device.user_id = model.User.by_name(c.user).id

		verify = device.verify_token(token)

		print(verify)

		vars = {'data': data, 'errors': errors,
				'error_summary': error_summary, 'action': 'new'}

		if not verify:
			vars['errors'] = {
				'token': 'The token you entered is not valid'
			}
			return tk.render('ckanext/twofactorauth/setup.html',
				extra_vars=vars)

		return tk.render('ckanext/twofactorauth/setup_verify.html',
			extra_vars=vars)
