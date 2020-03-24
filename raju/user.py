from openerp import models, fields, api

class FieldsUser(models.Model):
	_inherit = 'res.users'
	x_metrc_sync_status = fields.Char('Metrc sync status')
	x_metrc_api_key = fields.Char('Metrc api key')
	x_metrc_user_key = fields.Char('Metrc user key')
	x_metrc_license = fields.Char('Metrc license')