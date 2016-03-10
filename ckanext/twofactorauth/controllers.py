from __future__ import absolute_import, division, print_function, unicode_literals

import os
from binascii import unhexlify
from base64 import b32encode

import pylons.config as config

from ckan import model
from ckan.plugins import toolkit as tk

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
	def _get_context(self):
		context = {'model': model, 'session': model.Session,
				'user': c.user, 'auth_user_obj': c.userobj}

		#context['qr_url'] =

		return context

	def _get_key(self):
		key = random_hex(20).decode('ascii')
		return key

	def setup(self, data=None):
		context = self._get_context()
		data = data or {}

		otpauth_url = get_otpauth_url('admin', random_hex(20).decode('ascii'), issuer='EDX')

		# Make and return QR code
		qrcode_img = qrcode.make(otpauth_url, image_factory=qrcode.image.svg.SvgPathImage)
		with io.BytesIO() as f:
			qrcode_img.save(f)
			data['img'] = f.getvalue()
			f.close()

		# Drop the extra XML header from the svg
		data['img'] = data['img'][data['img'].find('<svg'):]


		vars = {'data': data, 'action': 'index'}

		return tk.render('ckanext/twofactorauth/setup.html',
			extra_vars=vars)
