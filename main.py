import json
import sys
import logging
from datetime import date, datetime
from sonarqube import SonarQubeClient, SonarCloudClient
from dotenv import dotenv_values
import traceback

import sonar_core_controller as sc

# Constantes
LOGS_DIRECTORY = 'logs/'
CONTENT_DIRECTORY = 'content/'
ISSUES_FILE_PREFIX = 'sonarqube-'
ISSUES_FILE_EXTENSION = '.json'

def configurar_logging():
    logfile = f'{LOGS_DIRECTORY}{date.today().strftime("%Y%m%d")}.log'
    logging.basicConfig(filename=logfile, encoding='utf-8', level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

def carregar_configuracao():
    config = dotenv_values('.env')
    sonar_url = config.get('SONAR_URL')
    sonar_version = config.get('SONAR_VERSION')

    if sonar_version == 'cloud':
        sonar_token = config.get('SONARCLOUD_TOKEN')  
        sonar = SonarCloudClient(sonarcloud_url=sonar_url, token=sonar_token)
    elif sonar_version == 'community':
        sonar_username = config.get('SONARQUBE_USERNAME')
        sonar_password = config.get('SONARQUBE_PASSWORD')
        sonar = SonarQubeClient(sonarqube_url=sonar_url, username=sonar_username, password=sonar_password)

    projects = config.get('SONAR_PROJECTS').split(",")
    return sonar, projects, config  # Retornar também a variável config

def salvar_issues_em_json(issues, config):
    if str(config.get("SONAR_SAVE_CONTENT")).lower() == "true":
        json_file = f'{CONTENT_DIRECTORY}{ISSUES_FILE_PREFIX}{datetime.now().strftime("%Y%m%d %H%M%S")}{ISSUES_FILE_EXTENSION}'
        with open(json_file, 'w') as json_data:
            json.dump(issues, json_data)    
            
def obter_issues_completas(sonar, project):
    issues_info = sonar.issues.search_issues(componentKeys=project)
    issues = issues_info.get('issues', [])  # Obtém a lista de issues do retorno
    return issues

def processar_issue(sonar, issue, issue_count):
    start_line = issue.get('textRange', {}).get('startLine', None)
    end_line = issue.get('textRange', {}).get('endLine', None)
    
    if start_line is not None and end_line is not None:
        component_key = issue.get('component')
        comment = ""
        #if sonar_version == "cloud":
        #    source_code = sonar.sources.get_source_code(key=component_key, from_line=start_line, to_line=end_line)
        #    comment = str(source_code["sources"][0]).replace('"', '\\"').replace("'", "\'")
        sc.find_or_create_issue(issue, issue_count, comment)
    else:
        logging.warning(f"Issue não possui informações de textRange: {issue}")

def my_progress(count, total, status=''):
    bar_len = 60
    fille_len = int(round(bar_len * count / float(total)))
    bar = '=' * fille_len + '-' * (bar_len - fille_len)

    sys.stdout.write(f'[{bar}] {count} out of {total}    {status}\r')
    sys.stdout.flush()

def main():
    try:
        configurar_logging()
        sonar, projects, config = carregar_configuracao()  # Receber a configuração

        for project in projects:
            logging.info(f"Iniciando importação do projeto {project}")
            
            issue_details = obter_issues_completas(sonar, project)
            print(issue_details)
            TOTAL_ISSUES_ON_FILE = len(issue_details)
            issue_count = 0
            salvar_issues_em_json(issue_details, config)  # Passar a configuração

            for issue in issue_details:
                my_progress(issue_count, TOTAL_ISSUES_ON_FILE)
                processar_issue(sonar, issue, issue_count)  # Passar o objeto sonar
                issue_count += 1

    except Exception as e:
        traceback.print_exc()
        logging.error(str(e))   

if __name__ == '__main__':
    main()
