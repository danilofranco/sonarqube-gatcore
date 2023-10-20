import logging
from dotenv import dotenv_values
from datetime import date
from gat_api.assets import GatCoreAssets
from gat_api.issues import GatCoreIssues
from gat_api.root_causes import GatCoreRootCauses

# Carregar as configurações do arquivo .env
config = dotenv_values('.env')

# Configurar o log
logfile = 'logs/' + date.today().strftime('%Y%m%d') + '.log'
logging.basicConfig(filename=logfile, level=logging.INFO)

# Inicializar contadores e constantes
TOTAL_ASSETS_ON_FILE = 0
TOTAL_ISSUES_ON_FILE = 0
ASSETS_CREATED = 0
ASSETS_SKIPPED = 0
ISSUES_CREATED = 0
ISSUES_UPDATED = 0
ISSUES_SKIPPED = 0
ASSETS = {}

# Mapeamento de severidade
SEVERITY = {
    'INFO': 0,
    'MINOR': 1,
    'MAJOR': 3,
    'CRITICAL': 4
}

# Mapeamento de status
STATUS = {
    'OPEN': 'PENDING',
    'WONTFIX': 'ACCEPT',
    'FALSE-POSITIVE': 'NONEXISTENT',
    'FIXED': 'FIXED'
}

# Função para encontrar ou criar um problema baseado nos dados fornecidos
def find_or_create_issue(data, issue_count, comment):
    asset = find_or_create_asset(data, issue_count)
    # Se não foi possível criar ou encontrar o ativo, retorna None
    if asset is None:
        return

    # Se o problema não existe, cria um novo
    if not search_issue(data, asset, issue_count):
        create_issue(data, asset, issue_count, comment)

# Função para criar um ativo no GAT
def create_asset(data, issue_count):
    global ASSETS_CREATED, ASSETS_SKIPPED

    # Preparando os dados do ativo
    asset_data = {
        'type': 'APPLICATION',
        'key': 'https://' + data.get('project') + '.com'
    }

    # Instanciando o objeto GatCoreAssets e criando o ativo
    assets = GatCoreAssets(config.get('GAT_API_KEY'), config.get('GAT_SUBDOMAIN'))
    response = assets.create_asset(**asset_data)

    # Verificando a resposta da API
    if response.status_code == 201:
        ASSETS_CREATED += 1
        new_asset = response.json()
        logging.info({
            'entity': 'asset',
            'issue_count': str(issue_count),
            'type': 'create',
            'result': 'success',
            'asset_id': new_asset['asset_id']
        })
        return new_asset

    # Se a criação do ativo falhar
    ASSETS_SKIPPED += 1
    logging.info({
        'entity': 'asset',
        'issue_count': str(issue_count),
        'type': 'create',
        'result': 'fail',
        'status_code': str(response.status_code)
    })
    return response.status_code

# Função para encontrar ou criar um ativo
def find_or_create_asset(issue, issue_count):
    global ASSETS_SKIPPED

    # Preparando os critérios de pesquisa do ativo
    search_criteria = {
        'type': ['APPLICATION'],
        'key': ['https://' + issue.get('project') + '.com']
    }

    # Pesquisando o ativo
    gat_assets = GatCoreAssets(config.get('GAT_API_KEY'), config.get('GAT_SUBDOMAIN'))
    response = gat_assets.find_asset(search_criteria)

    # Se o ativo for encontrado
    if response.status_code == 200:
        asset = response.json()['content'][0]
        logging.info({
            'entity': 'asset',
            'issue_count': str(issue_count),
            'type': 'found',
            'result': 'success',
            'asset_id': asset['asset_id']
        })
        return asset

    # Se o ativo não for encontrado, tenta criar um novo
    elif response.status_code == 204:
        return create_asset(issue, issue_count)

    # Se não for possível encontrar ou criar o ativo
    ASSETS_SKIPPED += 1
    logging.error('Não foi possível encontrar ou criar o ativo.')
    return None

# Função para encontrar ou criar a causa raiz
# Atualmente, é um placeholder, pois a implementação depende da atualização da API
def find_or_create_root_cause(data):
    gat_root_causes = GatCoreRootCauses(config.get('GAT_API_KEY'), config.get('GAT_SUBDOMAIN'))
    root_causes = gat_root_causes.get_all_root_causes(size=200)
    return root_causes

# Função para pesquisar um problema existente
def search_issue(issue, asset, issue_number):
    global ISSUES_SKIPPED

    # Preparando os critérios de pesquisa do problema
    search_criteria = {
        'title': [issue.get('message')],
        'asset_id': [asset.get('asset_id')]
    }

    # Pesquisando o problema
    issues = GatCoreIssues(config.get('GAT_API_KEY'), config.get('GAT_SUBDOMAIN'))
    response = issues.find_issue(**search_criteria)

    # Se o problema for encontrado, atualiza o seu status
    if response.status_code == 200:
        found_issues = response.json()['content']
        if len(found_issues) != 1:
            ISSUES_SKIPPED += 1
            logging.error('Múltiplos problemas encontrados, não é possível atualizar o status.')
            return True

        issue = found_issues[0]
        issue_id = issue['issue_id']
        data = {
            'vulnerability': {
                'status': 'REOPENED' if issue['vulnerability']['status'] != 'PENDING' else 'PENDING'
            }
        }
        update_issue(issue_id, data, asset['asset_id'], issue_number)
        return True

    return False

# Função para criar um novo problema
def create_issue(data, asset, issue_count, comment):
    global ISSUES_CREATED, ISSUES_SKIPPED, SEVERITY

    # Obtendo a causa raiz
    root_cause = find_or_create_root_cause(data)

    # Preparando os dados do problema
    description = '''Rule: {rule} <br>\
        Component: {component} <br>\
        Line: {line} <br>\
        Hash: {hash} <br>\
        Text Range: {range} <br>\
        '''.format(rule=data.get("rule"), component=data.get('component'), line=data.get("line"), hash=data.get("hash"), range=data.get('textRange'))

    creation_date = data.get('creationDate').split('+')[0]
    vuln_status = status(data.get('resolution')) if data.get('status') == 'RESOLVED' else status(data.get('status'))
    severity = SEVERITY[data.get('severity')]

    issue_data = {
        'title': data.get('message'),
        'source': 'APPSCAN',
        'asset_id': asset.get('asset_id'),
        'severity': severity,
        'description': description,
        'creation_date': creation_date,
        'comment': comment,
        'tags': data.get('tags'),
        'vulnerability': {
            'status': vuln_status,
            'app': {'path': data.get('component')}
        }
    }

    # Criando o problema
    issues = GatCoreIssues(config.get('GAT_API_KEY'), config.get('GAT_SUBDOMAIN'))
    response = issues.create_issue(**issue_data)

    # Verificando a resposta da API
    if response.status_code == 201:
        ISSUES_CREATED += 1
        new_issue = response.json()
        logging.info({
            'entity': 'issue',
            'issue_count': str(issue_count),
            'type': 'create',
            'result': 'success',
            'issue_id': new_issue['issue_id'],
            'asset_id': asset['asset_id']
        })
        return new_issue

    # Se a criação do problema falhar
    ISSUES_SKIPPED += 1
    logging.info({
        'entity': 'issue',
        'issue_count': str(issue_count),
        'type': 'create',
        'result': 'fail',
        'status_code': response.status_code
    })
    return None

# Função para atualizar um problema existente
def update_issue(issue_id, data, asset_id, row_number):
    global ISSUES_UPDATED, ISSUES_SKIPPED

    # Atualizando o problema
    issues = GatCoreIssues(config.get('GAT_API_KEY'), config.get('GAT_SUBDOMAIN'))
    response = issues.update_issue(issue_id, **data)

    # Verificando a resposta da API
    if response.status_code == 201:
        ISSUES_UPDATED += 1
        updated_issue = response.json()
        logging.info({
            'entity': 'issue',
            'row_number': str(row_number),
            'type': 'update',
            'result': 'success',
            'issue_id': updated_issue['issue_id'],
            'asset_id': asset_id
        })
        return updated_issue

    # Se a atualização do problema falhar
    ISSUES_SKIPPED += 1
    logging.info({
        'entity': 'issue',
        'row_number': str(row_number),
        'type': 'update',
        'result': 'fail',
        'status_code': response.status_code
    })
    return None

# Função para mapear o status do problema
def status(data):
    return STATUS.get(data, 'PENDING')
