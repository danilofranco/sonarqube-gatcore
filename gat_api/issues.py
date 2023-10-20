import requests
    
MESSAGE_SIZE = {'err': 'Invalid argument.', 'msg': "'size' must be at most 200."}
    
class GatCoreIssues:
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
            self.base_url = f'{subdomain}/api/v2/issues'
        except Exception as e:
            print(e)
            
    # Método para buscar todos os apontamentos
    def get_all_issues(self, size=None, page=None):
        if(size and size > 200):
            return MESSAGE_SIZE
        if(not size):
            size = 30
        if(not page):
            page = 0
        return requests.get(url=f'{self.base_url}?size={size}&page={page}', headers=self.headers)
    
    # Método para buscar apontamentos
    def find_issue(self, size=None, page=None, **kwargs):
        if(size and size > 200):
            return MESSAGE_SIZE
        if(not size):
            size = 30
        if(not page):
            page = 0
        data = {}
        for arg in kwargs:
            data[arg] = kwargs[arg]
        return requests.post(url=f'{self.base_url}?size={size}&page={page}', json=data, headers=self.headers)
    
    # Método para criar apontamentos
    def create_issue(self, **kwargs):
        if(not kwargs['title']):
            return {'err': 'Missing required information.', 'msg': "'title' is required."}
        if(not kwargs['asset_id']):
            return {'err': 'Missing required information.', 'msg': "'asset' is required."}
        data = {}
        for arg in kwargs:
            data[arg] = kwargs[arg]
        return requests.put(url=self.base_url, json=data, headers=self.headers)
    
    # Método para atualizar apontamentos
    def update_issue(self, id, **kwargs):
        data = {}
        for arg in kwargs:
            data[arg] = kwargs[arg]
        print(data)
        return requests.patch(url=f'{self.base_url}/{id}', json=data, headers=self.headers)