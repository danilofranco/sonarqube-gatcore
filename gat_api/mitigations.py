import os
from dotenv import load_dotenv

MESSAGE_SIZE = {'err': 'Invalid argument.', 'msg': "'size' must be at most 200."}
MESSAGE_ERROR_MISSING = 'Missing required information.'

import requests

load_dotenv()

headers = {
    'Authorization': os.getenv['GAT_API_KEY'],
    'Content-Type': 'application/json'
}

base_url = f'{os.getenv["GAT_SUBDOMAIN"]}/api/v2/assets'

asset_types = ['HOST', 'APPLICATION', 'PERSON', 'PROCESS', 'COMPANY', 'CLOUD']

def get_all_assets(size=None, page=None):
    if(size and size > 200):
        return MESSAGE_SIZE
    if(not size):
        size = 30
    if(not page):
        page = 0
    return requests.get(url=f'{base_url}?size={size}&page={page}', headers=headers)

def find_asset(key, size=None, page=None):
    if(size and size > 200):
        return MESSAGE_SIZE
    if(not size):
        size = 30
    if(not page):
        page = 0
    
    data = {
        'key': [key]
    }
    return requests.post(url=f'{base_url}?size={size}&page={page}', json=data, headers=headers)

def create_asset(**kwargs):
    a_type = kwargs.get('type', None)
    if(not a_type or a_type.upper() not in asset_types):
        return {'err': MESSAGE_ERROR_MISSING, 'msg': f"type must be one of: {', '.join(asset_types)}"}
    if(not kwargs.get(a_type.lower(), None)):
        return {'err': MESSAGE_ERROR_MISSING, 'msg': f'Information about {a_type} is needed.'}
    if(not kwargs.get('key', None)):
        return {'err': MESSAGE_ERROR_MISSING, 'msg': "'key' is required."}
    
    data = {}
    for arg in kwargs:
        data[arg] = kwargs[arg]
    return requests.put(url=base_url, headers=headers, json=data)