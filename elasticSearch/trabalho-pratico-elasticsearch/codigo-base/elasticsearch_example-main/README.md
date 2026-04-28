# Elasticsearch Search API

Este é um projeto exemplo de uma aplicação Spring Boot que utiliza o **Elasticsearch Java API Client** para realizar buscas em um índice do Elasticsearch. A API é definida utilizando o padrão OpenAPI (Swagger).

## 🚀 Tecnologias Utilizadas

*   **Java 17**
*   **Spring Boot 3.1.0**
*   **Elasticsearch Java Client 8.8.0**
*   **OpenAPI Generator** (para geração de interfaces e modelos a partir do `api.yml`)
*   **Maven**

## 📋 Pré-requisitos

*   JDK 17 instalado.
*   Instância do Elasticsearch rodando localmente (padrão esperado: `https://localhost:9200`).
*   Índice chamado `wikipedia` criado no Elasticsearch com o campo `content`.

## 🛠️ Configuração do Elasticsearch

A conexão com o Elasticsearch é configurada na classe `EsClient.java`. Atualmente, ela está configurada para:
*   **Host:** `https://localhost:9200`
*   **Usuário:** `elastic`
*   **Senha:** `user123`
*   **SSL:** Configurado para ignorar certificados não confiáveis (apenas para ambiente de desenvolvimento).

## 📂 Estrutura da API

A definição da API está localizada em `src/main/resources/api.yml`.

### Endpoint de Busca
`GET /search`

**Parâmetros:**
*   `query` (string, obrigatório): O termo de busca a ser enviado ao campo `content` do Elasticsearch.
*   `page` (integer, opcional): O número da página de resultados (padrão: `1`).

**Exemplo de uso:**
```bash
curl "http://localhost:8080/search?query=computador&page=1"
```

## ⚙️ Como Executar

1.  Compile o projeto para gerar as classes a partir do OpenAPI:
    ```bash
    ./mvnw compile
    ```

2.  Execute a aplicação:
    ```bash
    ./mvnw spring-boot:run
    ```

A aplicação estará disponível em `http://localhost:8080`.

## 📝 Detalhes da Implementação

*   **Geração de Código:** O plugin `openapi-generator-maven-plugin` gera a interface `SearchApi` e o modelo `Result` automaticamente.
*   **Controlador:** `SearchController` implementa a interface gerada e delega a lógica para o `SearchService`.
*   **Serviço:** `SearchService` processa os resultados do Elasticsearch e limpa o conteúdo (removendo tags HTML e caracteres especiais).
*   **Paginação:** O cálculo do offset (`from`) é feito no `EsClient` seguindo a fórmula `(page - 1) * 10`.
