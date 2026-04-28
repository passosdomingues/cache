# Wikipedia Search Engine

Sistema de busca full-text distribuído utilizando Elasticsearch, Spring Boot e Thymeleaf. O projeto implementa técnicas avançadas de recuperação de informação, incluindo busca booleana, fuzzy matching, destaque de termos (highlighting) e sugestões ortográficas (did you mean).

## Arquitetura do Sistema

O sistema é composto por três camadas principais:
1. **Infraestrutura**: Cluster Elasticsearch 8.x orquestrado via Docker Compose.
2. **Backend**: Aplicação Spring Boot 3.x utilizando o Elasticsearch Java API Client para comunicação via HTTPS.
3. **Frontend**: Interface modular baseada em Thymeleaf e Vanilla JavaScript, seguindo princípios de Atomic Design.

### Tecnologias Utilizadas

| Componente | Tecnologia |
|---|---|
| Engine de Busca | Elasticsearch 8.17 |
| Framework Backend | Spring Boot 3.1.0 |
| SDK de Busca | Elasticsearch Java API Client 8.8.0 |
| Definição de API | OpenAPI 3.0 (OAS) |
| Renderização | Thymeleaf |
| Gerenciamento de Infra | Docker Compose |
| Build Tool | Maven |

## Instalação e Configuração

### Pré-requisitos
* Docker e Docker Compose
* JDK 17 (configurado via Makefile)
* Maven 3.x (via Maven Wrapper)

### Inicialização Rápida

1. **Infraestrutura**:
   Inicie o cluster Elasticsearch e Kibana:
   ```bash
   cd ../docker
   make up
   ```

2. **Build e Execução**:
   Prepare o ambiente e inicie a aplicação:
   ```bash
   cd ../elasticsearch_example-main
   make all
   make run
   ```

3. **Carga de Dados**:
   Popule o índice com o dataset fornecido:
   ```bash
   cd ../datasets
   ./importWiki.sh
   ```

A aplicação estará disponível em `http://localhost:8080/v1/`.

## Funcionalidades Implementadas

### Mecanismo de Busca (Elasticsearch)
* **Busca Booleana**: Combinação de `must` (match compulsório) e `should` (impulsionamento de relevância).
* **Fuzzy Matching**: Tolerância a erros de digitação via `fuzziness: AUTO`.
* **Phrase Boost**: Aumento de score para correspondências exatas de frases.
* **Highlighting**: Geração de fragmentos de conteúdo com marcação HTML para os termos encontrados.
* **Term Suggest**: Motor de sugestão para correção ortográfica em tempo real.

### Interface do Usuário (Frontend)
* **Autocomplete**: Sistema de sugestão assíncrono com debounce para otimização de requisições.
* **Navegação por Teclado**: Suporte completo a atalhos de teclado para seleção de sugestões.
* **Layout Responsivo**: Design adaptável para diferentes resoluções.
* **Acessibilidade**: Implementação de ARIA roles e labels para compatibilidade com leitores de tela.

## Desenvolvimento e Manutenção

### Comandos de Automação (Makefile)
* `make all`: Executa a instalação de dependências e compilação do projeto.
* `make run`: Inicia o servidor Spring Boot.
* `make clean`: Remove artefatos de build e temporários.
* `make test-api`: Executa bateria de testes funcionais via curl.
* `make docs`: Gera documentação técnica e diagramas de arquitetura.

### Documentação da API
O contrato da API está definido em `src/main/resources/api.yml`. A documentação interativa (Swagger UI) pode ser acessada em `/v1/swagger-ui.html` com a aplicação em execução.

## Estrutura de Diretórios
```text
.
├── Makefile                # Orquestração de comandos
├── pom.xml                 # Gerenciamento de dependências Maven
├── src/main/java           # Código-fonte Java (MVC, Services, Domain)
├── src/main/resources      # Configurações, API schema e Templates
└── static/                 # Ativos de frontend (CSS, JS)
```
