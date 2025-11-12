# Plano de Ação Detalhado: Gerenciamento de Categorias Bluevelvet Music Store

Este documento apresenta a **Deep Exploration**, a **Análise de Pontos Nodais**, o **Backlog** e o **Plano de Ação de 3 Dias** para a implementação completa do sistema de gerenciamento de categorias da Bluevelvet Music Store, conforme o desafio proposto.

## 1. Deep Exploration e Contexto do Projeto

O repositório `pagliares/category-management-bluevelvet-music-store` serve como ponto de partida para um trabalho de disciplina (Application Lifecycle Management) e fornece o **frontend** em **Vanilla HTML, CSS e JavaScript**, que simula operações CRUD usando o `LocalStorage` do navegador.

O objetivo final é transformar esta simulação em uma **aplicação full-stack** completa, utilizando:
*   **Backend:** Spring Boot (Java).
*   **Banco de Dados:** MySQL ou embarcado (H2/H2DB).
*   **Comunicação:** API RESTful.

O escopo do projeto é o módulo de **Gerenciamento de Categorias** para o administrador da loja.

## 2. Análise de Pontos Nodais (Nodal Points)

Os pontos nodais representam as áreas de maior complexidade, interdependência ou risco no projeto, e onde a maior parte do esforço de desenvolvimento deve ser concentrada.

| Ponto Nodal | Descrição | Impacto e Complexidade | Solução Proposta |
| :--- | :--- | :--- | :--- |
| **Nó 1: Integração Frontend-Backend** | A transição do uso de `LocalStorage` para chamadas a uma API RESTful real (Spring Boot). | **Alto.** Requer a reescrita de todas as funções de persistência do frontend e a criação de todos os *endpoints* REST no backend. | Implementar a camada de `Controller` e `Service` no Spring Boot para cada US (User Story) e adaptar o JavaScript do frontend para usar `fetch()` ou `XMLHttpRequest` para a API. |
| **Nó 2: Segurança (Login/Registro)** | Implementar autenticação e autorização (`Admin` role) para proteger os *endpoints* da API. | **Alto.** É a porta de entrada do sistema. Requer Spring Security. | Configurar Spring Security para JWT (JSON Web Token) ou autenticação baseada em sessão, e garantir que apenas usuários com a *role* `Admin` possam acessar as rotas de gerenciamento de categorias. |
| **Nó 3: Estrutura Hierárquica de Categorias** | O requisito de que categorias podem ter uma `parent_id` (estrutura de árvore). | **Médio/Alto.** Afeta o modelo de dados (entidade `Category`), a lógica de serviço (busca e criação) e a exibição no frontend (listagem e criação). | Modelar a entidade `Category` com um relacionamento `self-referencing` (auto-referência) no Spring Data JPA. Criar lógica de serviço para manipulação da hierarquia. |
| **Nó 4: Paginação, Filtro e Ordenação** | Implementar os requisitos de US-2032 (Dashboard) para paginação (10 por página), ordenação por nome/ID e filtro por nome. | **Médio.** Requer o uso de `PagingAndSortingRepository` ou `JpaRepository` com `Pageable` no Spring Boot. | Utilizar a funcionalidade nativa do Spring Data JPA para lidar com paginação e ordenação de forma eficiente no lado do servidor. |

## 3. Backlog do Projeto (User Stories)

O backlog é baseado nas 11 User Stories (US) fornecidas no `README.md`, priorizadas e agrupadas por funcionalidade.

| Prioridade | ID | Descrição | Módulo |
| :--- | :--- | :--- | :--- |
| **Alta** | US-1232 | Login | Segurança |
| **Alta** | US-1603 | Registrar novos usuários | Segurança |
| **Alta** | US-2032 | Acessar o Dashboard de Gerenciamento de Categorias (Listagem, Paginação, Filtro, Ordenação) | Categorias |
| **Alta** | US-1306 | Criar categoria de produtos | Categorias |
| **Alta** | US-0907 | Listar categorias de produtos (parte do US-2032) | Categorias |
| **Média** | US-1307 | Editar categoria de produtos | Categorias |
| **Média** | US-0904 | Excluir categoria de produtos | Categorias |
| **Baixa** | US-0913 | Ordenar categoria de produtos (parte do US-2032) | Categorias |
| **Baixa** | US-0914 | Filtrar categoria de produtos (parte do US-2032) | Categorias |
| **Baixa** | US-0916 | Exportar categoria de produtos (CSV/JSON) | Categorias |
| **Baixa** | US-2100 | Listar produtos dentro de uma categoria para o comprador online (fora do escopo Admin, mas listado) | Categorias (Opcional) |

***Nota:** O US-2100 será considerado opcional, pois foca no "comprador online" e não no "Administrador", que é o foco principal do trabalho.*

## 4. Plano de Ação de 3 Dias (Implementação Full-Stack)

O plano é estruturado para entregar um **MVP (Minimum Viable Product)** funcional ao final do Dia 2, com a implementação de todas as funcionalidades CRUD básicas, e dedicar o Dia 3 aos requisitos mais complexos e ao polimento final.

### Dia 1: Configuração e Segurança (Nó 2)

**Objetivo:** Configurar o projeto Spring Boot, o banco de dados e implementar a base de segurança (Login/Registro).

| Tarefa | Descrição | US Relacionada | Tempo Estimado |
| :--- | :--- | :--- | :--- |
| **1.1 Setup do Projeto** | Criar projeto Spring Boot (Maven/Gradle), configurar dependências (Web, JPA, H2/MySQL, Lombok, Security). | N/A | 2h |
| **1.2 Modelo de Dados (Usuário)** | Criar entidade `User` e `Role` (Admin, Salesperson, Shipper). Configurar `UserRepository`. | US-1232, US-1603 | 1h |
| **1.3 Serviço de Usuário e Registro** | Implementar `UserService` e `UserController` para `US-1603` (Registro de novos usuários). | US-1603 | 2h |
| **1.4 Configuração de Segurança** | Configurar Spring Security. Implementar `UserDetailsService` e o fluxo de autenticação (Login - `US-1232`). | US-1232 | 3h |
| **1.5 Teste de Conexão** | Testar o registro e login via Postman/cURL para garantir que a segurança básica está funcionando. | US-1232, US-1603 | 1h |
| **Total Estimado Dia 1** | | | **9 horas** |

### Dia 2: CRUD de Categorias (Nós 1, 3 e 4 - Básico)

**Objetivo:** Implementar o modelo de dados de categorias, a API RESTful para CRUD básico e a integração inicial com o frontend.

| Tarefa | Descrição | US Relacionada | Tempo Estimado |
| :--- | :--- | :--- | :--- |
| **2.1 Modelo de Dados (Categoria)** | Criar entidade `Category` com auto-referência (`parent_id`) e campos adicionais (nome, imagem, ativo). | US-1306, Nó 3 | 2h |
| **2.2 Repositório e Serviço de Categoria** | Criar `CategoryRepository` e `CategoryService` com métodos para CRUD. | US-1306, US-0904, US-1307 | 2h |
| **2.3 Controller de Categoria (CRUD)** | Implementar `CategoryController` com *endpoints* REST para: Criar (`US-1306`), Editar (`US-1307`) e Excluir (`US-0904`). | US-1306, US-1307, US-0904 | 3h |
| **2.4 Listagem e Paginação (API)** | Implementar o *endpoint* de listagem com suporte a `Pageable` (Paginação, Ordenação, Filtro - Nó 4). | US-2032, US-0907 | 3h |
| **2.5 Integração Frontend (Básico)** | Adaptar o JavaScript do frontend para chamar os *endpoints* de Listagem e Criação, substituindo o `LocalStorage`. | Nó 1 | 2h |
| **Total Estimado Dia 2** | | | **12 horas** |

### Dia 3: Polimento, Hierarquia e Entrega (Nós 3 e 4 - Avançado)

**Objetivo:** Finalizar a lógica de hierarquia, implementar o filtro/ordenação no frontend, e preparar o código final para entrega.

| Tarefa | Descrição | US Relacionada | Tempo Estimado |
| :--- | :--- | :--- | :--- |
| **3.1 Lógica de Hierarquia** | Refinar o `CategoryService` para lidar com a criação de subcategorias (seleção de `parent_id`) e a busca hierárquica. | US-1306, Nó 3 | 3h |
| **3.2 Frontend: Paginação e Filtro** | Adaptar o frontend para enviar os parâmetros de paginação, ordenação e filtro para a API e renderizar os resultados. | US-2032, Nó 4 | 3h |
| **3.3 Implementação de Exportação** | Adicionar um *endpoint* no `CategoryController` para exportar dados (e.g., para CSV ou JSON - `US-0916`). | US-0916 | 2h |
| **3.4 Testes Finais e Refatoração** | Revisão de código, adição de comentários, e testes de ponta a ponta (end-to-end) de todas as US. | N/A | 2h |
| **3.5 Preparação para Entrega** | Documentação final (instruções de *build* e *run*) e empacotamento do código. | N/A | 1h |
| **Total Estimado Dia 3** | | | **11 horas** |

**Total Geral Estimado:** 32 horas. O plano é ambicioso, mas factível dentro de 3 dias de trabalho intensivo.

## 5. Próxima Fase: Implementação Completa do Código

A próxima fase será a execução deste plano, iniciando com a criação da estrutura do projeto Spring Boot e a implementação da segurança.
