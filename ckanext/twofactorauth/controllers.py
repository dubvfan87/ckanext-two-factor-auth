from ckan import model
from ckan.plugins import toolkit as tk

c = tk.c

class TwoFactorAuthController(tk.BaseController):
	def _get_context(self):
		return {'model': model, 'session': model.Session,
				'user': c.user, 'auth_user_obj': c.userobj}

	def index(self, data=None):
		context = self._get_context()

		return
