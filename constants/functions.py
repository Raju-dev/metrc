import requests
from odoo.addons.metrc.constants.metrc import *
import json
import logging
_logger = logging.getLogger(__name__)

def metrc_post(url, api_key, body):
	request_body = json.dumps(body)
	_logger.debug(request_body)
	response = requests.post(url = url, data = request_body, headers = {'Authorization': 'Basic '+api_key, 'Content-type': 'application/json', 'Accept': 'text/plain' })
	_logger.debug("=================================")
	_logger.debug(response.text)
	_logger.debug(response.json())
	_logger.debug("=================================")
	json_content = json.loads(response.text)
	_logger.debug(json_content)
	if response.status_code == 200:
		return { status: 'success' }
	else:
		return { status: 'failed' }