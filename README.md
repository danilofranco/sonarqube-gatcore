# Integração SonarQube - GAT Core

Este projeto é uma ferramenta de integração entre o SonarQube e o GAT Core. Ele permite buscar dados de vulnerabilidades e questões de código do SonarQube e enviar esses dados para o GAT Core para análise e gestão de riscos.

## Pré-requisitos

- Python 3.x
- SonarQube ou SonarCloud
- GAT Core

## Instalação

1. Clone este repositório.
2. Instale as dependências do Python com o comando `pip install -r requirements.txt`.
3. Configure as variáveis de ambiente conforme descrito abaixo.

## Configuração de Variáveis de Ambiente

As variáveis de ambiente são usadas para configurar a conexão com o SonarQube e o GAT Core. Estas são as variáveis disponíveis:

```plaintext
# Variáveis para conexão com o GAT Core
GAT_API_KEY="" #chave de api obtida no GAT Core
GAT_SUBDOMAIN="" #url do GAT Core

# Variáveis para captura de dados do Sonarqube
ENABLE_SONARQUBE="true" # "true" ou "false" define se utilizará a integração com o Sonarqube
SONAR_VERSION="community"
SONAR_URL= "https://sonarcloud.io/" #URL do Sonarqube
SONARQUBE_USERNAME="admin" #usuário para autenticação no sonarqube
SONARQUBE_PASSWORD="password" #senha para autenticação no sonarqube
SONARCLOUD_TOKEN="sonarcloud_token" #token para utilização do sonarcloud
SONAR_ORGANIZATION="sonar_organization"
SONAR_PROJECTS="projects" # quais projetos serão importados
SONAR_SEVERITY_RESTRICTION="minor"
SONAR_SAVE_CONTENT="false" # "true" ou "false" para gravar o conteúdo lido num json
```

Guarde estas variáveis em um arquivo .env na raiz do projeto.

##Uso
Execute o script principal com o comando:

```
python main.py
```

O script buscará dados do SonarQube baseado nas configurações fornecidas e enviará os resultados para o GAT Core.

##Contribuição

Contribuições são bem-vindas. Sinta-se à vontade para abrir uma issue ou pull request.