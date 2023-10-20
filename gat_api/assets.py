import requests

MESSAGE_SIZE = {'err': 'Invalid argument.', 'msg': "'size' must be at most 200."}
# Classe GatCoreAssets: para lidar com operações relacionadas a ativos no GAT
class GatCoreAssets:
    """
    Apontamentos do GAT Core
    """
    headers = {}
    base_url = ""
    asset_types = ['HOST', 'APPLICATION', 'PERSON', 'PROCESS', 'COMPANY', 'CLOUD']
    
    
    def __init__(self, api_key, subdomain):
        """ carrega as variáveis de ambiente
        """
        try:
            self.headers = {
                'Authorization': api_key,
                'Content-Type': 'application/json'
            }
            self.base_url = f'{subdomain}/api/v2/assets'
        except Exception as e:
            print(e)

    # Método para buscar todos os ativos
    def get_all_assets(self, size=None, page=None):
        if(size and size > 200):
            return MESSAGE_SIZE
        if(not size):
            size = 30
        if(not page):
            page = 0
        return requests.get(url=f'{self.base_url}?size={size}&page={page}', headers=self.headers)

    # Método para buscar ativo por id
    def find_asset_by_id(self, key, size=None, page=None):
        if(size and size > 200):
            return MESSAGE_SIZE
        if(not size):
            size = 30
        if(not page):
            page = 0
        
        data = {
            'key': [key]
        }
        return requests.post(url=f'{self.base_url}?size={size}&page={page}', json=data, headers=self.headers)
    
    # Método para buscar ativos através de filtros
    def find_asset(self, data, size=None, page=None):
        if(size and size > 200):
            return MESSAGE_SIZE
        if(not size):
            size = 30
        if(not page):
            page = 0
        return requests.post(url=f'{self.base_url}?size={size}&page={page}', json=data, headers=self.headers)

    # Método para criar um ativo
    def create_asset(self, **kwargs):
        a_type = kwargs.get('type', None)
        if(not a_type or a_type.upper() not in self.asset_types):
            return {'err': 'Missing required information.', 'msg': f"type must be one of: {', '.join(self.asset_types)}"}
        if(not kwargs.get('key', None)):
            return {'err': 'Missing required information.', 'msg': "'key' is required."}
        
        data = {}
        for arg in kwargs:
            data[arg] = kwargs[arg]
        return requests.put(url=self.base_url, headers=self.headers, json=data)