#Precisa editar

import sys
import subprocess
import pkg_resources
import os
from dotenv import load_dotenv

required = {'requests'}
installed = {pkg.key for pkg in pkg_resources.working_set}
missing = required - installed

if missing:
    print(f'Installing dependencies: {missing}...')
    python = sys.executable
    subprocess.check_call([python, '-m', 'pip', 'install', *missing], stdout=subprocess.DEVNULL)
    print('\nDone!')

import requests

class GatCoreRecommendations:
    """
    Apontamentos do GAT Core
    """
    headers = {}
    base_url = ""
    
    def __init__(self, api_key, subdomain):
        """ carrega as variáveis de ambiente
        """
        try:
            self.headers = {
                'Authorization': api_key,
                'Content-Type': 'application/json'
            }
            self.base_url = f'{subdomain}/api/v1/knowledge-base/recommendations'
        except Exception as e:
            print(e)

    def get_all_recommendations(self, size=None, page=None):
        if(size and size > 200):
            return {'err': 'Invalid argument.', 'msg': "'size' must be at most 200."}
        if(not size):
            size = 30
        if(not page):
            page = 0
        return requests.get(url=f'{self.base_url}?size={size}&page={page}', headers=self.headers)

    def find_recommendation(self, key, size=None, page=None):
        if(size and size > 200):
            return {'err': 'Invalid argument.', 'msg': "'size' must be at most 200."}
        if(not size):
            size = 30
        if(not page):
            page = 0
        
        data = {
            'key': [key]
        }
        return requests.post(url=f'{self.base_url}?size={size}&page={page}', json=data, headers=self.headers)
    
    def create_recommendation(self, **kwargs):        
        data = {}
        for arg in kwargs:
            data[arg] = kwargs[arg]
        return requests.put(url=self.base_url, headers=self.headers, json=data)

    