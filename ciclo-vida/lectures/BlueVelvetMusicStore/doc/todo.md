# Bluevelvet Category Manager - TODO

## Dia 1: Configuração e Segurança

- [x] 1.1 Setup do Projeto (Dependências Spring Boot, JPA, Security)
- [x] 1.2 Modelo de Dados (User, Role)
- [x] 1.3 Serviço de Usuário e Registro (US-1603)
- [x] 1.4 Configuração de Segurança e Login (US-1232)
- [x] 1.5 Teste de Conexão (Postman/cURL)

## Dia 2: CRUD de Categorias (MVP)

- [x] 2.1 Modelo de Dados (Category com auto-referência)
- [x] 2.2 Repositório e Serviço de Categoria
- [x] 2.3 Controller de Categoria (CRUD - US-1306, US-1307, US-0904)
- [x] 2.4 Listagem e Paginação (API - US-2032, US-0907)
- [x] 2.5 Integração Frontend (Básico)

## Dia 3: Polimento e Entrega

- [x] 3.1 Lógica de Hierarquia (Subcategorias)
- [x] 3.2 Frontend: Paginação, Filtro e Ordenação
- [ ] 3.3 Implementação de Exportação (US-0916)
- [x] 3.4 Testes Finais e Refatoração
- [ ] 3.5 Preparação para Entrega

## Bugs e Melhorias Futuras

- [ ] Adicionar validação de unicidade de nome de categoria
- [ ] Implementar upload de imagens para S3
- [ ] Adicionar exportação de categorias em CSV/JSON
- [ ] Melhorar tratamento de erros no frontend
- [ ] Adicionar testes unitários e de integração
- [ ] Implementar cache de categorias no frontend
- [ ] Adicionar suporte a múltiplos idiomas

## Features Implementadas

- [x] Projeto inicializado com tRPC + Express + React + Tailwind
- [x] Banco de dados configurado (MySQL)
- [x] Autenticação Manus OAuth integrada
- [x] Schema base de usuários criado
- [x] Schema de categorias criado com auto-referência (parentId)
- [x] API REST completa para CRUD de categorias
- [x] Dashboard de categorias com interface React
- [x] Paginação, busca e ordenação implementadas
- [x] Banco de dados populado com categorias de exemplo
- [x] Página inicial com navegação
