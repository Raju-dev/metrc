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
from datetime import datetime

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
            ResUser.write({ "x_metrc_sync_status" : "sent", "x_metrc_api_key": metrc_api_key, "x_metrc_user_key": metrc_user_key, "x_metrc_license": metrc_license })
            threaded_calculation = threading.Thread(target=self.sync_metrc_products, args = (request.env, metrc_api_key, metrc_user_key, metrc_license, ResUser.id))
            threaded_calculation.start()
        
        return json.dumps({ 'status': status })

    
    def sync_metrc_products(self, env, metrc_api_key, metrc_user_key, metrc_license, id):
        with openerp.api.Environment.manage():
            with openerp.registry(env.cr.dbname).cursor() as new_cr:
                new_env = api.Environment(new_cr, env.uid, env.context)
                ResCategory = new_env['metrc.categories']

                api_key = base64.b64encode((metrc_api_key+':'+metrc_user_key).encode("utf-8")).decode('utf-8');
                
                #Sync metrc categories
                response = requests.get(url=METRC_BASE_URL+'/items/v1/categories', headers = {'Authorization': 'Basic '+api_key })
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
                
                #Sync metrc rooms
                response = requests.get(url=METRC_BASE_URL+'/rooms/v1/active?licenseNumber='+metrc_license, headers = {'Authorization': 'Basic '+api_key })
                json_content = json.loads(response.text)
                ResRoom = new_env['metrc.rooms']
                for key in json_content:
                    ResRoom.create({
                        'metrc_id': key.get('Id'),
                        'name': key.get('Name'),
                        'user_id': id
                    })
                new_env.cr.commit()
                #Sync metrc plants
                #response = requests.get(url=METRC_BASE_URL+'/plants/v1/vegetative?licenseNumber='+metrc_license, headers = {'Authorization': 'Basic '+api_key })
                base_url = new_env['ir.config_parameter'].sudo().get_param('web.base.url')
                response = requests.get(url=base_url+'/raju/static/json/plants.json', headers = {'Authorization': 'Basic '+api_key })
                json_content = json.loads(response.text)
                ResPlants = new_env['metrc.plants']

                for key in json_content:
                    lastModified = False
                    if key.get('LastModified'):
                        old_string = key.get('LastModified')
                        k = old_string.rfind(":")
                        new_string = old_string[:k] + "" + old_string[k+1:]
                        lastModified = datetime.strptime(new_string, "%Y-%m-%dT%H:%M:%S%z").strftime('%Y-%m-%d %H:%M:%S')
                   
                    ResRoom = new_env['metrc.rooms'].search([('metrc_id','=',21102)], limit = 1)
                    ResPlants.create({
                        'label': key.get('Label'),
                        'state': key.get('State'),
                        'growth_phase': key.get('GrowthPhase'),
                        'plant_batch_id': key.get('PlantBatchId'),
                        'plant_batch_name': key.get('PlantBatchName'),
                        'plant_batch_type_name': key.get('PlantBatchTypeName'),
                        'strain_id': key.get('StrainId'),
                        'strain_name': key.get('StrainName'),
                        'location_id': key.get('LocationId'),
                        'location_name': key.get('LocationName'),
                        'location_type_name': key.get('LocationTypeName'),
                        'room_id': ResRoom.id,
                        'room_name': key.get('RoomName'),
                        'patient_license_number': key.get('PatientLicenseNumber'),
                        'harvest_id': key.get('HarvestId'),
                        'harvested_unit_of_weight_name': key.get('HarvestUnitOfWeightName'),
                        'harvested_unit_of_weight_abbreviation': key.get('HarvestedUnitOfWeightAbbreviation'),
                        'harvested_wet_weight': key.get('HarvestedWetWeight'),
                        'harvest_count': key.get('HarvestCount'),
                        'is_on_hold': key.get('IsOnHold'),
                        'planted_date': key.get('PlantedDate'),
                        'vegetative_date': key.get('VegetativeDate'),
                        'flowering_date': key.get('FloweringDate'),
                        'harvested_date': key.get('HarvestedDate'),
                        'destroyed_date': key.get('DestroyedDate'),
                        'destroyed_note': key.get('DestroyedNote'),
                        'destroyed_by_user_name': key.get('DestroyedByUserName'),
                        'last_modified': lastModified
                    })
                new_env.cr.commit()
                ResUser = new_env['res.users'].browse([id])
                ResUser.write({ "x_metrc_sync_status" : "synced" })

    @http.route('/sync-metrc-status', type="json", auth='public')
    def handler(self):
        ResUser = request.env['res.users'].browse([request.session.uid])
        _logger.debug(ResUser.x_metrc_sync_status)
        return json.dumps({ 'status': ResUser.x_metrc_sync_status, 'metrc_api_key': ResUser.x_metrc_api_key, 'metrc_user_key': ResUser.x_metrc_user_key, 'metrc_license': ResUser.x_metrc_license })        