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
        key = base64.b64encode((metrc_api_key+':'+metrc_user_key).encode("utf-8")).decode('utf-8');
        response = requests.get(url=METRC_BASE_URL+'/items/v1/categories', headers = {'Authorization': 'Basic '+key })
        #content = requests.get(url=url, headers = {""})
        json_content = json.loads(response.text)
        ResCategory = env['metrc.categories']
        
        for key in json_content:
            data = {
                'display_name' : key.get('Name'),
                'name': key.get('Name'),
                'product_category_type' : key.get('ProductCategoryType'),
                'quantity_type' : key.get('QuantityType')
            }
            if key.get('RequiresStrain') == 'True':
                data['requires_strain'] = 1
            else:
                data['requires_strain'] = 0

            if key.get('RequiresItemBrand') == 'True':
                data['requires_item_brand'] = 1
            else:
                data['requires_item_brand'] = 0

            if key.get('RequiresAdministrationMethod') == 'True':
                data['requires_administration_method'] = 1
            else:
                data['requires_administration_method'] = 0

            if key.get('RequiresUnitCbdPercent') == 'True':
                data['requires_cbd_percent'] = 1
            else:
                data['requires_cbd_percent'] = 0

            if key.get('RequiresUnitCbdContent') == 'True':
                data['requires_cbd_content'] = 1
            else:
                data['requires_cbd_content'] = 0

            if key.get('RequiresUnitThcPercent') == 'True':
                data['requires_thc_percent'] = 1
            else:
                data['requires_thc_percent'] = 0

            if key.get('RequiresUnitThcContent') == 'True':
                data['requires_thc_content'] = 1
            else:
                data['requires_thc_content'] = 0

            if key.get('RequiresUnitVolume') == 'True':
                data['requires_unit_volume'] = 1
            else:
                data['requires_unit_volume'] = 0

            if key.get('RequiresUnitWeight') == 'True':
                data['requires_unit_weight'] = 1
            else:
                data['requires_unit_weight'] = 0

            if key.get('RequiresServingSize') == 'True':
                data['requires_serving_size'] = 1
            else:
                data['requires_serving_size'] = 0

            if key.get('RequiresSupplyDurationDays') == 'True':
                data['require_supply_duration_dates'] = 1
            else:
                data['require_supply_duration_dates'] = 0

            if key.get('RequiresIngredients') == 'True':
                data['requires_ingredients'] = 1
            else:
                data['requires_ingredients'] = 0

            if key.get('RequiresProductPhoto') == 'True':
                data['requires_product_photo'] = 1
            else:
                data['requires_product_photo'] = 0

            if key.get('CanContainSeeds') == 'True':
                data['can_contain_seeds'] = 1
            else:
                data['can_contain_seeds'] = 0

            if key.get('CanBeRemediated') == 'True':
                data['can_be_remediated'] = 1
            else:
                data['can_be_remediated'] = 0
            data['user_id'] = id
            data['create_date'] = '2012-10-10'
            _logger.debug(data)
            ResCategory.create({
                'name': 'ame'
                })
        env.cr.commit()