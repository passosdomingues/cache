# Bluevelvet Category Management System - Guia de Implementação

## 📋 Visão Geral

Este é um sistema full-stack completo de gerenciamento de categorias para a Bluevelvet Music Store, desenvolvido em **3 dias** com as seguintes tecnologias:

### Stack Tecnológico

**Backend:**
- Node.js + Express
- tRPC (Type-safe RPC framework)
- MySQL Database
- Drizzle ORM
- Autenticação OAuth (Manus)

**Frontend:**
- React 19
- Tailwind CSS 4
- TypeScript
- Wouter (Routing)
- Sonner (Toast notifications)

## 🎯 User Stories Implementadas

| ID | Descrição | Status |
|---|---|---|
| US-1232 | Login | ✅ Implementado |
| US-1603 | Registrar novos usuários | ✅ Implementado |
| US-2032 | Acessar Dashboard de Categorias | ✅ Implementado |
| US-1306 | Criar categoria de produtos | ✅ Implementado |
| US-0907 | Listar categorias de produtos | ✅ Implementado |
| US-1307 | Editar categoria de produtos | ✅ Implementado |
| US-0904 | Deletar categoria de produtos | ✅ Implementado |
| US-0913 | Ordenar categorias | ✅ Implementado |
| US-0914 | Filtrar categorias | ✅ Implementado |
| US-0916 | Exportar categorias | ⏳ Futuro |
| US-2100 | Listar produtos para comprador | ⏳ Futuro |

## 🏗️ Arquitetura

### Estrutura de Diretórios

```
bluevelvet-category-manager/
├── client/                          # Frontend React
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Home.tsx            # Página inicial
│   │   │   ├── CategoriesDashboard.tsx  # Dashboard principal
│   │   │   └── NotFound.tsx
│   │   ├── components/              # Componentes reutilizáveis
│   │   ├── lib/
│   │   │   └── trpc.ts             # Cliente tRPC
│   │   ├── App.tsx                 # Roteamento
│   │   └── main.tsx
│   └── public/                      # Ativos estáticos
├── server/                          # Backend Express
│   ├── routers.ts                  # Definição de procedures tRPC
│   ├── db.ts                       # Query helpers
│   └── _core/                      # Framework interno
├── drizzle/                         # Migrações e schema
│   ├── schema.ts                   # Definição de tabelas
│   └── migrations/
├── seed-categories.mjs             # Script de seed
└── package.json
```

### Modelo de Dados

#### Tabela: `users`
```sql
CREATE TABLE users (
  id INT PRIMARY KEY AUTO_INCREMENT,
  openId VARCHAR(64) UNIQUE NOT NULL,
  name TEXT,
  email VARCHAR(320),
  loginMethod VARCHAR(64),
  role ENUM('user', 'admin') DEFAULT 'user' NOT NULL,
  createdAt TIMESTAMP DEFAULT NOW(),
  updatedAt TIMESTAMP DEFAULT NOW() ON UPDATE NOW(),
  lastSignedIn TIMESTAMP DEFAULT NOW()
);
```

#### Tabela: `categories`
```sql
CREATE TABLE categories (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(255) UNIQUE NOT NULL,
  description TEXT,
  imageFileName VARCHAR(255),
  parentId INT,
  isActive INT DEFAULT 1,
  createdAt TIMESTAMP DEFAULT NOW(),
  updatedAt TIMESTAMP DEFAULT NOW() ON UPDATE NOW(),
  FOREIGN KEY (parentId) REFERENCES categories(id) ON DELETE CASCADE
);
```

## 🔌 API REST (tRPC)

### Procedures de Categorias

#### 1. Listar Categorias
```typescript
trpc.categories.list.useQuery({
  skip: 0,
  take: 10,
  search: "",
  sortBy: "name",  // "name" | "id" | "createdAt"
  sortOrder: "asc" // "asc" | "desc"
})
```

**Resposta:**
```json
{
  "categories": [
    {
      "id": 1,
      "name": "T-Shirts",
      "description": "Camisetas de banda e artistas",
      "imageFileName": "tshirts.jpg",
      "parentId": null,
      "isActive": 1,
      "createdAt": "2025-11-07T15:00:00Z",
      "updatedAt": "2025-11-07T15:00:00Z"
    }
  ],
  "total": 14
}
```

#### 2. Obter Categoria por ID
```typescript
trpc.categories.getById.useQuery({ id: 1 })
```

#### 3. Criar Categoria
```typescript
trpc.categories.create.useMutation({
  name: "Amplifiers",
  description: "Amplificadores de guitarra",
  imageFileName: "amplifiers.jpg",
  parentId: undefined,  // Opcional
  isActive: 1
})
```

#### 4. Atualizar Categoria
```typescript
trpc.categories.update.useMutation({
  id: 1,
  name: "T-Shirts Updated",
  description: "Nova descrição",
  isActive: 1
})
```

#### 5. Deletar Categoria
```typescript
trpc.categories.delete.useMutation({ id: 1 })
```

#### 6. Obter Categorias Raiz
```typescript
trpc.categories.getRoots.useQuery()
```

#### 7. Obter Subcategorias
```typescript
trpc.categories.getSubcategories.useQuery({ parentId: 1 })
```

## 🚀 Como Executar

### Pré-requisitos
- Node.js 22+
- MySQL 8.0+ (ou H2 embarcado)
- npm ou pnpm

### Instalação

1. **Clonar o repositório**
```bash
git clone <repo-url>
cd bluevelvet-category-manager
```

2. **Instalar dependências**
```bash
pnpm install
```

3. **Configurar variáveis de ambiente**
As variáveis de ambiente já estão configuradas no sistema Manus:
- DATABASE_URL
- JWT_SECRET
- OAUTH_SERVER_URL
- VITE_APP_TITLE
- VITE_APP_LOGO

4. **Executar migrações do banco de dados**
```bash
pnpm db:push
```

5. **Popular o banco com dados de exemplo**
```bash
node seed-categories.mjs
```

6. **Iniciar o servidor de desenvolvimento**
```bash
pnpm dev
```

O aplicativo estará disponível em `http://localhost:3000`

## 📊 Dados de Exemplo

O script `seed-categories.mjs` popula o banco com:

**10 Categorias Raiz:**
- T-Shirts
- Vinyl
- CD
- MP3
- Books
- Acoustic Guitar
- Electric Guitar
- Bass
- Drums
- Keyboards

**3 Subcategorias (filhas de T-Shirts):**
- Metal T-Shirts
- Rock T-Shirts
- Pop T-Shirts

## 🔐 Segurança

- **Autenticação:** OAuth integrado (Manus)
- **Autorização:** Role-based access control (Admin, User)
- **Proteção de Rotas:** Procedures protegidas com `protectedProcedure`
- **Validação:** Zod schema validation em todas as inputs
- **CORS:** Configurado para ambiente de produção

## 🎨 Interface do Usuário

### Página Inicial (`/`)
- Apresentação do sistema
- Links para login e dashboard
- Lista de recursos disponíveis

### Dashboard de Categorias (`/categories`)
- **Busca:** Filtrar categorias por nome em tempo real
- **Ordenação:** Por nome, ID ou data de criação
- **Paginação:** 10 categorias por página
- **CRUD Completo:**
  - Criar nova categoria (modal)
  - Editar categoria (modal)
  - Deletar categoria (com confirmação)
- **Status Visual:** Indicador de categoria ativa/inativa
- **Hierarquia:** Suporte a categorias pai/filho

## 📝 Exemplo de Uso - Frontend

```typescript
import { trpc } from "@/lib/trpc";

export function CategoryList() {
  const [page, setPage] = useState(0);
  
  const { data, isLoading } = trpc.categories.list.useQuery({
    skip: page * 10,
    take: 10,
    search: "",
    sortBy: "name",
    sortOrder: "asc"
  });

  const createMutation = trpc.categories.create.useMutation({
    onSuccess: () => {
      utils.categories.list.invalidate();
    }
  });

  const handleCreate = () => {
    createMutation.mutate({
      name: "Nova Categoria",
      description: "Descrição",
      imageFileName: "image.jpg",
      isActive: 1
    });
  };

  return (
    <div>
      {isLoading ? <Spinner /> : (
        <table>
          {data?.categories.map(cat => (
            <tr key={cat.id}>
              <td>{cat.name}</td>
              <td>{cat.description}</td>
            </tr>
          ))}
        </table>
      )}
      <button onClick={handleCreate}>Criar</button>
    </div>
  );
}
```

## 🧪 Testes

### Testes Manuais Realizados
- ✅ Login e autenticação
- ✅ Listagem de categorias com paginação
- ✅ Busca por nome
- ✅ Ordenação (nome, ID, data)
- ✅ Criação de categoria (Amplifiers)
- ✅ Edição de categoria
- ✅ Exclusão de categoria
- ✅ Hierarquia (categorias pai/filho)
- ✅ Responsividade em dispositivos móveis

### Próximos Passos para Testes
- [ ] Testes unitários com Vitest
- [ ] Testes de integração E2E
- [ ] Testes de carga e performance
- [ ] Testes de segurança (OWASP)

## 📦 Deployment

### Opções de Deployment

1. **Manus Platform (Recomendado)**
```bash
# Clicar no botão "Publish" na interface do Manus
# Após criar um checkpoint
```

2. **Docker**
```bash
docker build -t bluevelvet-categories .
docker run -p 3000:3000 bluevelvet-categories
```

3. **Heroku**
```bash
heroku create bluevelvet-categories
git push heroku main
```

## 🔄 Fluxo de Desenvolvimento Futuro

### Melhorias Imediatas
- [ ] Upload de imagens para S3
- [ ] Exportação de categorias (CSV/JSON)
- [ ] Testes automatizados
- [ ] Validação de unicidade de nome
- [ ] Cache no frontend

### Recursos Avançados
- [ ] Módulo de produtos
- [ ] Relatórios e analytics
- [ ] Integração com API de pagamento
- [ ] Notificações em tempo real
- [ ] Suporte a múltiplos idiomas

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique a documentação de tRPC: https://trpc.io/docs
2. Consulte a documentação de Drizzle: https://orm.drizzle.team
3. Revise os exemplos no código-fonte

## 📄 Licença

MIT License - Veja LICENSE para detalhes

---

**Desenvolvido em 3 dias | Bluevelvet Music Store | 2025**
