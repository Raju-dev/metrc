from openerp import http
from odoo.http import request
import logging
import threading
_logger = logging.getLogger(__name__)
import requests
import json
from openerp import api
from odoo.modules import registry
from odoo.addons.raju.constants.metrc import *
import base64
import openerp

class NewPage(http.Controller):
    @http.route('/sync-metrc', type="json", auth='public')
    def index(self, metrc_api_key, metrc_user_key, metrc_license):
        ResUser = request.env['res.users'].browse([request.session.uid])
        _logger.debug(ResUser.x_metrc_sync_status)
        dbname = request.env.cr.dbname
        key = base64.b64encode((metrc_api_key+':'+metrc_user_key).encode("utf-8")).decode('utf-8');
        _logger.debug(key)
        response = requests.get(url=METRC_BASE_URL+'/facilities/v1', headers = {'Authorization': 'Basic '+key })
        status = 'failed'
        if response.status_code == 200:
            status = 'success'
            ResUser.write({ "x_metrc_sync_status" : "sent" })
            threaded_calculation = threading.Thread(target=self.sync_metrc_products, args = (request.env, metrc_api_key, metrc_user_key, metrc_license, ResUser.id))
            threaded_calculation.start()
        
        return json.dumps({ 'status': status })

    
    def sync_metrc_products(self, env, metrc_api_key, metrc_user_key, metrc_license, id):
        with openerp.api.Environment.manage():
            with openerp.registry(env.cr.dbname).cursor() as new_cr:
                new_env = api.Environment(new_cr, env.uid, env.context)
                ResCategory = new_env['metrc.categories']

                key = base64.b64encode((metrc_api_key+':'+metrc_user_key).encode("utf-8")).decode('utf-8');
                response = requests.get(url=METRC_BASE_URL+'/items/v1/categories', headers = {'Authorization': 'Basic '+key })
                #content = requests.get(url=url, headers = {""})
                json_content = json.loads(response.text)
                ResCategory = new_env['metrc.categories']
                
                for key in json_content:
                    ResCategory.create({
                        'name' : key.get('Name'),
                        'product_category_type' : key.get('ProductCategoryType'),
                        'quantity_type' : key.get('QuantityType'),
                        'requires_strain' : 0,
                        'requires_item_brand' : 0,
                        'requires_administration_method' : 0,
                        'requires_cbd_percent' : 0,
                        'requires_cbd_content' : 0,
                        'requires_thc_percent' : 0,
                        'requires_thc_content' : 0,
                        'requires_unit_volume' : 0,
                        'requires_unit_weight' : 0,
                        'requires_serving_size' : 0,
                        'require_supply_duration_dates' : 0,
                        'requires_ingredients' : 0,
                        'requires_product_photo' : 0,
                        'can_contain_seeds' : 0,
                        'can_be_remediated' : 0,
                        'user_id': id
                    })
                new_env.cr.commit()

    @http.route('/sync-metrc-status', type="json", auth='public')
    def handler(self):
        ResUser = request.env['res.users'].browse([request.session.uid])
        _logger.debug(ResUser.x_metrc_sync_status)
        return json.dumps({ 'status': ResUser.x_metrc_sync_status })        