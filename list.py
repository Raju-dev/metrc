from openerp import http
from odoo.http import request
import logging
import threading
_logger = logging.getLogger(__name__)
import requests
import json
from openerp import api
from odoo.modules import registry
from odoo.addons.metrc.constants.metrc import *
import base64
import openerp
from datetime import datetime
import re

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
                _logger.debug('================ started syncing')
                #Sync metrc categories
                response = requests.get(url=METRC_BASE_URL+'/items/v1/categories', headers = {'Authorization': 'Basic '+api_key })
                json_content = json.loads(response.text)
                ResCategory = new_env['metrc.categories']
                
                for key in json_content:
                    categoryExist = new_env['metrc.categories'].search([('name', '=', key.get('Name'))], limit = 1)
                    if not categoryExist:
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
                    else:
                        categoryExist.write({
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
                _logger.debug('============ metrc rooms')
                #Sync metrc rooms
                response = requests.get(url=METRC_BASE_URL+'/rooms/v1/active?licenseNumber='+metrc_license, headers = {'Authorization': 'Basic '+api_key })
                json_content = json.loads(response.text)
                ResRoom = new_env['metrc.rooms']
                for key in json_content:
                    roomExist = new_env['metrc.rooms'].search([('metrc_id', '=', key.get('Id'))], limit = 1)
                    if not roomExist:
                        ResRoom.create({
                            'metrc_id': key.get('Id'),
                            'name': key.get('Name'),
                            'user_id': id
                        })
                    else:
                        roomExist.write({
                            'metrc_id': key.get('Id'),
                            'name': key.get('Name'),
                            'user_id': id
                        })
                new_env.cr.commit()
                _logger.debug('============ metrc strains')
                #Sync metrc strains
                response = requests.get(url=METRC_BASE_URL+'/strains/v1/active?licenseNumber='+metrc_license, headers = {'Authorization': 'Basic '+api_key })
                json_content = json.loads(response.text)
                ResStrains = new_env['metrc.strains']
                for key in json_content:
                    strainExist = new_env['metrc.strains'].search([('metrc_id', '=', key.get('Id'))], limit = 1)
                    if not strainExist:
                        ResStrains.create({
                            'metrc_id': key.get('Id'),
                            'name': key.get('Name')
                        })
                    else:
                        strainExist.create({
                            'metrc_id': key.get('Id'),
                            'name': key.get('Name')
                        })
                new_env.cr.commit()
                _logger.debug('============ metrc locations')
                #Sync metrc locations
                response = requests.get(url=METRC_BASE_URL+'/locations/v1/active?licenseNumber='+metrc_license, headers = {'Authorization': 'Basic '+api_key })
                json_content = json.loads(response.text)
                ResLocation = new_env['metrc.locations']
                for key in json_content:
                    locationExist = new_env['metrc.locations'].search([('metrc_id', '=', key.get('Id'))], limit = 1)
                    if not locationExist:
                        ResLocation.create({
                            'metrc_id': key.get('Id'),
                            'name': key.get('Name')
                        })
                    else:
                        locationExist.write({
                            'metrc_id': key.get('Id'),
                            'name': key.get('Name')
                        })
                new_env.cr.commit()
                _logger.debug('============ metrc plant btch')
                #Sync metrc plant batches
                response = requests.get(url=METRC_BASE_URL+'/plantbatches/v1/active?licenseNumber='+metrc_license, headers = {'Authorization': 'Basic '+api_key })
                json_content = json.loads(response.text)
                ResPlantBatches = new_env['metrc.plant_batches']
                for key in json_content:
                    batchExist = new_env['metrc.plant_batches'].search([('metrc_id', '=', key.get('Id'))], limit = 1)
                    if not batchExist:
                        ResRoom = new_env['metrc.rooms'].search([('metrc_id','=', key.get('RoomId'))], limit = 1)
                        ResLocation = new_env['metrc.locations'].search([('metrc_id','=', key.get('LocationId'))], limit = 1)
                        ResStrains = new_env['metrc.strains'].search([('metrc_id','=', key.get('StrainId'))], limit = 1)

                        ResPlantBatches.create({
                            'metrc_id': key.get('Id'),
                            'name': key.get('Name'),
                            'type': key.get('Type'),
                            'strain_name': key.get('StrainName'),
                            'room_name': key.get('RoomName'),
                            'count': key.get('Count'),
                            'location_name': key.get('LocationName'), 
                            'strain_id': ResStrains.id,
                            'room_id': ResRoom.id,
                            'location_id': ResLocation.id,
                            'planted_date': key.get('PlantedDate'),
                            'location_type_name': key.get('LocationTypeName')
                        })
                    else:
                        batchExist.write({
                            'metrc_id': key.get('Id'),
                            'name': key.get('Name'),
                            'type': key.get('Type'),
                            'strain_name': key.get('StrainName'),
                            'room_name': key.get('RoomName'),
                            'count': key.get('Count'),
                            'location_name': key.get('LocationName'), 
                            'strain_id': ResStrains.id,
                            'room_id': ResRoom.id,
                            'location_id': ResLocation.id,
                            'planted_date': key.get('PlantedDate'),
                            'location_type_name': key.get('LocationTypeName')
                        })
                new_env.cr.commit()
                _logger.debug('============ metrc plants')

                #Sync vegetative plants
                #response = requests.get(url=METRC_BASE_URL+'/plants/v1/vegetative?licenseNumber='+metrc_license, headers = {'Authorization': 'Basic '+api_key })
                base_url = new_env['ir.config_parameter'].sudo().get_param('web.base.url')
                response = requests.get(url=METRC_BASE_URL+'/plants/v1/vegetative?licenseNumber='+metrc_license+'&&lastModifiedStart=2018-06-11&lastModifiedEnd=', headers = {'Authorization': 'Basic '+api_key })
                json_content = json.loads(response.text)
                ResPlants = new_env['metrc.plants']

                for key in json_content:
                    lastModified = False
                    if key.get('LastModified'):
                        old_string = key.get('LastModified')
                        k = old_string.rfind(":")
                        new_string = old_string[:k] + "" + old_string[k+1:]
                        lastModified = datetime.strptime(new_string, "%Y-%m-%dT%H:%M:%S%z").strftime('%Y-%m-%d %H:%M:%S')
                    ResBatch = new_env['metrc.plant_batches'].search([('metrc_id', '=', key.get('PlantBatchId'))], limit = 1)
                    ResRoom = new_env['metrc.rooms'].search([('metrc_id', '=', key.get('RoomId'))], limit = 1)
                    plantExist = new_env['metrc.plants'].search([('label', '=', key.get('Label'))], limit = 1)
                    
                    plantData = {
                        'label': key.get('Label'),
                        'state': key.get('State'),
                        'growth_phase': key.get('GrowthPhase'),
                        'plant_batch_name': key.get('PlantBatchName'),
                        'plant_batch_type_name': key.get('PlantBatchTypeName'),
                        'strain_id': key.get('StrainId'),
                        'strain_name': key.get('StrainName'),
                        'location_id': key.get('LocationId'),
                        'location_name': key.get('LocationName'),
                        'location_type_name': key.get('LocationTypeName'),
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
                    }

                    if ResBatch:
                        plantData['plant_batch_id'] = ResBatch.id
                    if ResRoom:
                        plantData['room_id'] = ResRoom.id

                    if not plantExist:
                        ResPlants.create(plantData)
                    else:
                        plantExist.write(plantData)

                #Sync vegetative plants
                #response = requests.get(url=METRC_BASE_URL+'/plants/v1/vegetative?licenseNumber='+metrc_license, headers = {'Authorization': 'Basic '+api_key })
                base_url = new_env['ir.config_parameter'].sudo().get_param('web.base.url')
                response = requests.get(url=METRC_BASE_URL+'/plants/v1/vegetative?licenseNumber='+metrc_license, headers = {'Authorization': 'Basic '+api_key })
                json_content = json.loads(response.text)
                ResPlants = new_env['metrc.plants']

                for key in json_content:
                    lastModified = False
                    if key.get('LastModified'):
                        old_string = key.get('LastModified')
                        k = old_string.rfind(":")
                        new_string = old_string[:k] + "" + old_string[k+1:]
                        lastModified = datetime.strptime(new_string, "%Y-%m-%dT%H:%M:%S%z").strftime('%Y-%m-%d %H:%M:%S')
                    ResBatch = new_env['metrc.plant_batches'].search([('metrc_id', '=', key.get('PlantBatchId'))], limit = 1)
                    ResRoom = new_env['metrc.rooms'].search([('metrc_id', '=', key.get('RoomId'))], limit = 1)
                    plantExist = new_env['metrc.plants'].search([('label', '=', key.get('Label'))], limit = 1)
                    
                    plantData = {
                        'label': key.get('Label'),
                        'state': key.get('State'),
                        'growth_phase': key.get('GrowthPhase'),
                        'plant_batch_name': key.get('PlantBatchName'),
                        'plant_batch_type_name': key.get('PlantBatchTypeName'),
                        'strain_id': key.get('StrainId'),
                        'strain_name': key.get('StrainName'),
                        'location_id': key.get('LocationId'),
                        'location_name': key.get('LocationName'),
                        'location_type_name': key.get('LocationTypeName'),
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
                    }

                    if ResBatch:
                        plantData['plant_batch_id'] = ResBatch.id
                    if ResRoom:
                        plantData['room_id'] = ResRoom.id

                    if not plantExist:
                        ResPlants.create(plantData)
                    else:
                        plantExist.write(plantData)

                #Sync flowering plants
                #response = requests.get(url=METRC_BASE_URL+'/plants/v1/vegetative?licenseNumber='+metrc_license, headers = {'Authorization': 'Basic '+api_key })
                base_url = new_env['ir.config_parameter'].sudo().get_param('web.base.url')
                response = requests.get(url=METRC_BASE_URL+'/plants/v1/flowering?licenseNumber='+metrc_license+'&lastModifiedStart=2018-06-11&lastModifiedEnd=', headers = {'Authorization': 'Basic '+api_key })
                json_content = json.loads(response.text)
                ResPlants = new_env['metrc.plants']

                for key in json_content:
                    lastModified = False
                    if key.get('LastModified'):
                        old_string = key.get('LastModified')
                        k = old_string.rfind(":")
                        new_string = old_string[:k] + "" + old_string[k+1:]
                        lastModified = datetime.strptime(new_string, "%Y-%m-%dT%H:%M:%S%z").strftime('%Y-%m-%d %H:%M:%S')
                    ResBatch = new_env['metrc.plant_batches'].search([('metrc_id', '=', key.get('PlantBatchId'))], limit = 1)
                    ResRoom = new_env['metrc.rooms'].search([('metrc_id', '=', key.get('RoomId'))], limit = 1)
                    plantExist = new_env['metrc.plants'].search([('label', '=', key.get('Label'))], limit = 1)
                    _logger.debug('========== label ')
                    _logger.debug(key.get('Label'))
                    plantData = {
                        'label': key.get('Label'),
                        'state': key.get('State'),
                        'growth_phase': key.get('GrowthPhase'),
                        'plant_batch_name': key.get('PlantBatchName'),
                        'plant_batch_type_name': key.get('PlantBatchTypeName'),
                        'strain_id': key.get('StrainId'),
                        'strain_name': key.get('StrainName'),
                        'location_id': key.get('LocationId'),
                        'location_name': key.get('LocationName'),
                        'location_type_name': key.get('LocationTypeName'),
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
                    }

                    if ResBatch:
                        plantData['plant_batch_id'] = ResBatch.id
                    if ResRoom:
                        plantData['room_id'] = ResRoom.id

                    if not plantExist:
                        ResPlants.create(plantData)
                    else:
                        plantExist.write(plantData)

                #Sync flowering plants
                #response = requests.get(url=METRC_BASE_URL+'/plants/v1/vegetative?licenseNumber='+metrc_license, headers = {'Authorization': 'Basic '+api_key })
                base_url = new_env['ir.config_parameter'].sudo().get_param('web.base.url')
                response = requests.get(url=METRC_BASE_URL+'/plants/v1/flowering?licenseNumber='+metrc_license, headers = {'Authorization': 'Basic '+api_key })
                json_content = json.loads(response.text)
                ResPlants = new_env['metrc.plants']

                for key in json_content:
                    lastModified = False
                    if key.get('LastModified'):
                        old_string = key.get('LastModified')
                        k = old_string.rfind(":")
                        new_string = old_string[:k] + "" + old_string[k+1:]
                        lastModified = datetime.strptime(new_string, "%Y-%m-%dT%H:%M:%S%z").strftime('%Y-%m-%d %H:%M:%S')
                    ResBatch = new_env['metrc.plant_batches'].search([('metrc_id', '=', key.get('PlantBatchId'))], limit = 1)
                    ResRoom = new_env['metrc.rooms'].search([('metrc_id', '=', key.get('RoomId'))], limit = 1)
                    plantExist = new_env['metrc.plants'].search([('label', '=', key.get('Label'))], limit = 1)
                    _logger.debug('========== label ')
                    _logger.debug(key.get('Label'))
                    plantData = {
                        'label': key.get('Label'),
                        'state': key.get('State'),
                        'growth_phase': key.get('GrowthPhase'),
                        'plant_batch_name': key.get('PlantBatchName'),
                        'plant_batch_type_name': key.get('PlantBatchTypeName'),
                        'strain_id': key.get('StrainId'),
                        'strain_name': key.get('StrainName'),
                        'location_id': key.get('LocationId'),
                        'location_name': key.get('LocationName'),
                        'location_type_name': key.get('LocationTypeName'),
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
                    }

                    if ResBatch:
                        plantData['plant_batch_id'] = ResBatch.id
                    if ResRoom:
                        plantData['room_id'] = ResRoom.id

                    if not plantExist:
                        ResPlants.create(plantData)
                    else:
                        plantExist.write(plantData)

                _logger.debug('============ metrc plants 224')
                new_env.cr.commit()
                ResUser = new_env['res.users'].browse([id])
                _logger.debug('============ metrc plants 227')
                ResUser.write({ "x_metrc_sync_status" : "synced" })

    @http.route('/sync-metrc-status', type="json", auth='public')
    def handler(self):
        ResUser = request.env['res.users'].browse([request.session.uid])
        _logger.debug(ResUser.x_metrc_sync_status)
        return json.dumps({ 'status': ResUser.x_metrc_sync_status, 'metrc_api_key': ResUser.x_metrc_api_key, 'metrc_user_key': ResUser.x_metrc_user_key, 'metrc_license': ResUser.x_metrc_license })

    @http.route('/get-different-locations', type="http", auth='public')
    def locations(self, _, q):
        locations_list = []
        if q:
            rooms = request.env['metrc.locations'].search([('name', 'like', '%'+q+'%')], limit = 10)
        else:
            rooms = request.env['metrc.locations'].search([], limit = 10)
        for single_room in rooms:
            locations_list.append({ 'id': single_room.id, 'text': single_room.name })
        return json.dumps({ 'result': locations_list, 'user_id': request.session.uid })

    @http.route('/get-different-batches', type="http", auth='public')
    def batches(self, **kwargs):
        values = dict(kwargs)
        sort_fields = ['', 'name', 'strain_name', 'room_name', 'location_name', 'count', 'planted_date'];
        locations_list = []
        totalCount = 0;
        offset = 0
        limit = 10

        if values['start']:
            offset = int(values['start'])

        if values['length']:
            limit = int(values['length'])

        if values['order[0][column]'] and int(values['order[0][column]']) > 0:
            sort_field = sort_fields[int(values['order[0][column]'])]
        else:
            sort_field = 'name'

        if values['order[0][dir]']:
            if values['order[0][dir]'] == 'asc':
                sort_order = 'asc';
            else:
                sort_order = 'desc';
        else:
            sort_order = 'asc'

        order_text = sort_field + ' ' +sort_order

        if values['search[value]']:
            rooms = request.env['metrc.plant_batches'].search([('name', 'like', '%'+values['search[value]']+'%')], limit = limit, offset= offset, order= order_text)
            totalCount = request.env['metrc.plant_batches'].search_count([('name', 'like', '%'+values['search[value]']+'%')])
        else:
            rooms = request.env['metrc.plant_batches'].search([], limit = limit, offset= offset, order= order_text)
            totalCount = request.env['metrc.plant_batches'].search_count([])
        for single_room in rooms:
            single_batch_item = ['', single_room.name]
            if single_room.strain_id:
                single_batch_item.append(single_room.strain_id.name)
            else:
                single_batch_item.append('-')

            if single_room.room_id:
                single_batch_item.append(single_room.room_id.name)
            else:
                single_batch_item.append('-')

            if single_room.location_id:
                single_batch_item.append(single_room.location_id.name)
            else:
                single_batch_item.append('-')

            single_batch_item.append(single_room.count)
            single_batch_item.append(single_room.planted_date)
            #locations_list.append({ 'id': single_room.id, 'text': single_room.name, 'room_id': single_room.room_id.id, 'room_name': single_room.room_name, 'location_id': single_room.location_id.id, 'location_name': single_room.location_name, 'strain_id': single_room.strain_id.id, 'strain_name': single_room.strain_name })
            locations_list.append(single_batch_item)
        return json.dumps({ "recordsTotal": totalCount, "recordsFiltered" : totalCount, 'data': locations_list, 'user_id': request.session.uid })

    @http.route('/get-different-plants', type="http", auth='public')
    def get_plants(self, **kwargs):
        values = dict(kwargs)
        sort_fields = ['', 'label', 'plant_batch_name', 'state', 'growth_phase', 'room_name', 'location_name', 'planted_date'];
        locations_list = []
        totalCount = 0;
        offset = 0
        limit = 10

        if values['start']:
            offset = int(values['start'])

        if values['length']:
            limit = int(values['length'])

        if values['order[0][column]'] and int(values['order[0][column]']) > 0:
            sort_field = sort_fields[int(values['order[0][column]'])]
        else:
            sort_field = 'plant_batch_name'

        if values['order[0][dir]']:
            if values['order[0][dir]'] == 'asc':
                sort_order = 'asc';
            else:
                sort_order = 'desc';
        else:
            sort_order = 'asc'

        order_text = sort_field + ' ' +sort_order

        if values['search[value]']:
            rooms = request.env['metrc.plants'].search([('label', 'like', '%'+values['search[value]']+'%')], limit = limit, offset = offset, order= order_text)
            totalCount = request.env['metrc.plants'].search_count([('label', 'like', '%'+values['search[value]']+'%')])
        else:
            rooms = request.env['metrc.plants'].search([], limit = limit, offset = offset, order= order_text)
            totalCount = request.env['metrc.plants'].search_count([])
        for single_room in rooms:
            single_batch_item = ['', single_room.label]
            if single_room.state:
                single_batch_item.append(single_room.state)
            else:
                single_batch_item.append('-')

            if single_room.plant_batch_name:
                single_batch_item.append(single_room.plant_batch_name)
            else:
                single_batch_item.append('-')

            if single_room.growth_phase:
                single_batch_item.append(single_room.growth_phase)
            else:
                single_batch_item.append('-')

            if single_room.room_name:
                single_batch_item.append(single_room.room_name)
            else:
                single_batch_item.append('-')

            if single_room.location_name:
                single_batch_item.append(single_room.location_name)    
            else:
                single_batch_item.append('-')    
            single_batch_item.append(single_room.planted_date)
            locations_list.append(single_batch_item)
        return json.dumps({ "recordsTotal": totalCount, "recordsFiltered" : totalCount, 'data': locations_list, 'user_id': request.session.uid })

    @http.route('/get-different-rooms', type="http", auth='public')
    def rooms(self, _, q):
        rooms_list = []
        if q:
            rooms = request.env['metrc.rooms'].search([('name', 'like', '%'+q+'%')], limit = 10)
        else:
            rooms = request.env['metrc.rooms'].search([], limit = 10)
        for single_room in rooms:
            rooms_list.append({ 'id': single_room.id, 'text': single_room.name })
        return json.dumps({ 'result': rooms_list, 'user_id': request.session.uid })

    @http.route('/get-different-strains', type="http", auth='public')
    def strains(self, _, q):
        strains_list = []
        if q:
            strains = request.env['metrc.strains'].search([('name', 'like', '%'+q+'%')], limit = 10)
        else:
            strains = request.env['metrc.strains'].search([], limit = 10)
        for single_strain in strains:
            strains_list.append({ 'id': single_strain.id, 'text': single_strain.name })
        return json.dumps({ 'result': strains_list, 'user_id': request.session.uid })

    @http.route('/create-plant-batches', type='json', auth="public")
    def crete_batches(self, batch_name ,batch_type , location ,room ,plant_count ,strain ,planting_date):
        location = request.env['metrc.locations'].search([('id', '=', location)], limit = 1)
        room = request.env['metrc.locations'].search([('id', '=', room)], limit = 1)
        strain = request.env['metrc.strains'].search([('id', '=', strain)], limit = 1)
        user = request.env['res.users'].browse([request.session.uid])

        api_key = base64.b64encode((user.x_metrc_api_key+':'+user.x_metrc_user_key).encode("utf-8")).decode('utf-8');
        url = METRC_BASE_URL+'/plantbatches/v1/createplantings?licenseNumber='+user.x_metrc_license

        request_data = [{
            "Name": batch_name,
            "Type": batch_type,
            "Count": plant_count,
            "Location": location.name,
            "Room": room.name,
            "StrainId": strain.metrc_id,
            "Strain": strain.name,
            "ActualDate": planting_date,
            "LocationId": location.metrc_id,
            "RoomId": room.metrc_id
        }]

        response = requests.post(url, data = json.dumps(request_data), headers = {'Authorization': 'Basic '+api_key, 'Content-Type': 'application/json', 'Accept':'application/json' })
        
        if response.status_code == 200:
            request.env['metrc.plant_batches'].create({
                'name': batch_name,
                'type': batch_type,
                'location_id': location.id,
                'location_name': location.name,
                'room_id': room.id,
                'room_name': room.name,
                'strain_id': strain.id,
                'strain_name': strain.name,
                'count': plant_count,
                'planted_date': planting_date
            })
            return json.dumps({ 'status': 'success' })
        else:
            json_response = json.loads(response.text)
            return json.dumps({ 'status': 'failed', 'error': json_response })

    @http.route('/change-growth-phase', type='json', auth="public")
    def change_growth(self, name, count, starting_tag, change_growth_phase, planting_date, location):
        location = request.env['metrc.locations'].search([('id', '=', location)], limit = 1)
        user = request.env['res.users'].browse([request.session.uid])
        tags = []

        api_key = base64.b64encode((user.x_metrc_api_key+':'+user.x_metrc_user_key).encode("utf-8")).decode('utf-8');
        url = METRC_BASE_URL+'/plantbatches/v1/changegrowthphase?licenseNumber='+user.x_metrc_license

        request_data = [{
            "Name": name,
            "Count": count,
            "StartingTag": starting_tag,
            "GrowthPhase": change_growth_phase,
            "NewLocation": location.name,
            "GrowthDate": planting_date
        }]

        response = requests.post(url, data = json.dumps(request_data), headers = {'Authorization': 'Basic '+api_key, 'Content-Type': 'application/json', 'Accept':'application/json' })
        
        if response.status_code == 200:
            BatchDetail = request.env['metrc.plant_batches'].search([('name', '=', name)], limit = 1)
            totalLeft = BatchDetail.count - int(count)
            BatchDetail.write({ "count": totalLeft })

            last_digits = re.match('.*?([0-9]+)$', starting_tag).group(1)
            
            for i in range(int(count)):
                increased_last_digits = int(last_digits) + i
                next_tag = starting_tag.replace(last_digits, str(increased_last_digits))
                tags.append(next_tag)
                plantData = {
                    'label': next_tag,
                    'state': 'Tracked',
                    'growth_phase': change_growth_phase,
                    'plant_batch_name': name,
                    'plant_batch_type_name': BatchDetail.type,
                    'strain_id': BatchDetail.strain_id,
                    'strain_name': BatchDetail.strain_name,
                    'location_id': BatchDetail.location_id,
                    'location_name': BatchDetail.location_name,
                    'room_name': BatchDetail.room_name,
                    'flowering_date': planting_date
                }
                _logger.debug(plantData)
                request.env['metrc.plants'].create(plantData)
            return json.dumps({ 'status': 'success', 'tags': tags })
        else:
            json_response = json.loads(response.text)
            return json.dumps({ 'status': 'failed', 'error': json_response })

    @http.route('/create-plants', type='json', auth="public")
    def create_plants(self, label ,batch_name ,batch_type ,growth_phase ,location ,room ,plant_count ,strain ,planting_date):
        location = request.env['metrc.locations'].search([('id', '=', location)], limit = 1)
        room = request.env['metrc.locations'].search([('id', '=', room)], limit = 1)
        strain = request.env['metrc.strains'].search([('id', '=', strain)], limit = 1)
        user = request.env['res.users'].browse([request.session.uid])

        api_key = base64.b64encode((user.x_metrc_api_key+':'+user.x_metrc_user_key).encode("utf-8")).decode('utf-8');
        url = METRC_BASE_URL+'/plants/v1/create/plantings?licenseNumber='+user.x_metrc_license

        request_data = [{
            "PlantLabel": label,
            "PlantBatchName": batch_name,
            "PlantBatchType": batch_type,
            "PlantCount": plant_count,
            "LocationName": location.name,
            "RoomName": room.name,
            "StrainId": strain.metrc_id,
            "StrainName": strain.name,
            "ActualDate": planting_date,
            "GrowthPhase": growth_phase,
            "LocationId": location.metrc_id,
            "RoomId": room.metrc_id
        }]

        response = requests.post(url, data = json.dumps(request_data), headers = {'Authorization': 'Basic '+api_key, 'Content-Type': 'application/json', 'Accept':'application/json' })
        _logger.debug(response.text)
        _logger.debug(response.status_code)
        if response.status_code == 200:
            request.env['metrc.plants'].create({
                "label": label,
                "growth_phase": growth_phase,
                "plant_batch_name": batch_name,
                "plant_batch_type_name": plant_count,
                "location_name": location.name,
                "room_name": room.id,
                "strain_name": strain.name,
                "planted_date": planting_date
            });
            return json.dumps({ 'status': 'success' })
        else:
            json_response = json.loads(response.text)
            return json.dumps({ 'status': 'failed', 'error': json_response })