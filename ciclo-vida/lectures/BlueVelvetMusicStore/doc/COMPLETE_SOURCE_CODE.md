# Bluevelvet Category Manager - Código-Fonte Completo

## 📁 Estrutura de Arquivos

Este documento contém o código-fonte completo de todos os arquivos principais do projeto.

---

## 1. Schema do Banco de Dados

### `drizzle/schema.ts`

```typescript
import { int, mysqlEnum, mysqlTable, text, timestamp, varchar } from "drizzle-orm/mysql-core";

/**
 * Core user table backing auth flow.
 * Extend this file with additional tables as your product grows.
 * Columns use camelCase to match both database fields and generated types.
 */
export const users = mysqlTable("users", {
  /**
   * Surrogate primary key. Auto-incremented numeric value managed by the database.
   * Use this for relations between tables.
   */
  id: int("id").autoincrement().primaryKey(),
  /** Manus OAuth identifier (openId) returned from the OAuth callback. Unique per user. */
  openId: varchar("openId", { length: 64 }).notNull().unique(),
  name: text("name"),
  email: varchar("email", { length: 320 }),
  loginMethod: varchar("loginMethod", { length: 64 }),
  role: mysqlEnum("role", ["user", "admin"]).default("user").notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
  lastSignedIn: timestamp("lastSignedIn").defaultNow().notNull(),
});

export type User = typeof users.$inferSelect;
export type InsertUser = typeof users.$inferInsert;

/**
 * Categories table for Bluevelvet Music Store.
 * Supports hierarchical categories (parent-child relationship).
 * parent_id is null for root categories.
 */
export const categories = mysqlTable("categories", {
  id: int("id").autoincrement().primaryKey(),
  name: varchar("name", { length: 255 }).notNull().unique(),
  description: text("description"),
  imageFileName: varchar("imageFileName", { length: 255 }),
  parentId: int("parentId"),
  isActive: int("isActive").default(1).notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
});

export type Category = typeof categories.$inferSelect;
export type InsertCategory = typeof categories.$inferInsert;
```

---

## 2. Camada de Banco de Dados

### `server/db.ts`

```typescript
import { eq, like, asc, desc, sql, isNull } from "drizzle-orm";
import { drizzle } from "drizzle-orm/mysql2";
import { InsertUser, users, categories, InsertCategory } from "../drizzle/schema";
import { ENV } from './_core/env';

let _db: ReturnType<typeof drizzle> | null = null;

// Lazily create the drizzle instance so local tooling can run without a DB.
export async function getDb() {
  if (!_db && process.env.DATABASE_URL) {
    try {
      _db = drizzle(process.env.DATABASE_URL);
    } catch (error) {
      console.warn("[Database] Failed to connect:", error);
      _db = null;
    }
  }
  return _db;
}

export async function upsertUser(user: InsertUser): Promise<void> {
  if (!user.openId) {
    throw new Error("User openId is required for upsert");
  }

  const db = await getDb();
  if (!db) {
    console.warn("[Database] Cannot upsert user: database not available");
    return;
  }

  try {
    const values: InsertUser = {
      openId: user.openId,
    };
    const updateSet: Record<string, unknown> = {};

    const textFields = ["name", "email", "loginMethod"] as const;
    type TextField = (typeof textFields)[number];

    const assignNullable = (field: TextField) => {
      const value = user[field];
      if (value === undefined) return;
      const normalized = value ?? null;
      values[field] = normalized;
      updateSet[field] = normalized;
    };

    textFields.forEach(assignNullable);

    if (user.lastSignedIn !== undefined) {
      values.lastSignedIn = user.lastSignedIn;
      updateSet.lastSignedIn = user.lastSignedIn;
    }
    if (user.role !== undefined) {
      values.role = user.role;
      updateSet.role = user.role;
    } else if (user.openId === ENV.ownerOpenId) {
      values.role = 'admin';
      updateSet.role = 'admin';
    }

    if (!values.lastSignedIn) {
      values.lastSignedIn = new Date();
    }

    if (Object.keys(updateSet).length === 0) {
      updateSet.lastSignedIn = new Date();
    }

    await db.insert(users).values(values).onDuplicateKeyUpdate({
      set: updateSet,
    });
  } catch (error) {
    console.error("[Database] Failed to upsert user:", error);
    throw error;
  }
}

export async function getUserByOpenId(openId: string) {
  const db = await getDb();
  if (!db) {
    console.warn("[Database] Cannot get user: database not available");
    return undefined;
  }

  const result = await db.select().from(users).where(eq(users.openId, openId)).limit(1);

  return result.length > 0 ? result[0] : undefined;
}

/**
 * Get all categories with optional filtering and pagination
 */
export async function getCategories({
  skip = 0,
  take = 10,
  search = "",
  sortBy = "name",
  sortOrder = "asc",
}: {
  skip?: number;
  take?: number;
  search?: string;
  sortBy?: "name" | "id" | "createdAt";
  sortOrder?: "asc" | "desc";
} = {}) {
  const db = await getDb();
  if (!db) {
    console.warn("[Database] Cannot get categories: database not available");
    return { categories: [], total: 0 };
  }

  try {
    // Build query with search filter
    const whereCondition = search ? like(categories.name, `%${search}%`) : undefined;
    
    // Get total count
    const countResult = await db
      .select({ count: sql<number>`COUNT(*)` })
      .from(categories)
      .where(whereCondition || sql`1=1`);
    const total = countResult[0]?.count as number || 0;

    // Get paginated results
    const orderColumn = sortBy === "id" ? categories.id : sortBy === "createdAt" ? categories.createdAt : categories.name;
    const orderDirection = sortOrder === "asc" ? asc(orderColumn) : desc(orderColumn);

    const result = await db
      .select()
      .from(categories)
      .where(whereCondition || sql`1=1`)
      .orderBy(orderDirection)
      .limit(take)
      .offset(skip);

    return { categories: result, total };
  } catch (error) {
    console.error("[Database] Failed to get categories:", error);
    throw error;
  }
}

/**
 * Get a single category by ID
 */
export async function getCategoryById(id: number) {
  const db = await getDb();
  if (!db) {
    console.warn("[Database] Cannot get category: database not available");
    return undefined;
  }

  try {
    const result = await db
      .select()
      .from(categories)
      .where(eq(categories.id, id))
      .limit(1);
    return result.length > 0 ? result[0] : undefined;
  } catch (error) {
    console.error("[Database] Failed to get category:", error);
    throw error;
  }
}

/**
 * Create a new category
 */
export async function createCategory(data: InsertCategory) {
  const db = await getDb();
  if (!db) {
    console.warn("[Database] Cannot create category: database not available");
    return undefined;
  }

  try {
    const result = await db.insert(categories).values(data);
    const categoryId = (result as any).insertId;
    return getCategoryById(Number(categoryId));
  } catch (error) {
    console.error("[Database] Failed to create category:", error);
    throw error;
  }
}

/**
 * Update a category
 */
export async function updateCategory(id: number, data: Partial<InsertCategory>) {
  const db = await getDb();
  if (!db) {
    console.warn("[Database] Cannot update category: database not available");
    return undefined;
  }

  try {
    await db.update(categories).set(data).where(eq(categories.id, id));
    return getCategoryById(id);
  } catch (error) {
    console.error("[Database] Failed to update category:", error);
    throw error;
  }
}

/**
 * Delete a category
 */
export async function deleteCategory(id: number) {
  const db = await getDb();
  if (!db) {
    console.warn("[Database] Cannot delete category: database not available");
    return false;
  }

  try {
    await db.delete(categories).where(eq(categories.id, id));
    return true;
  } catch (error) {
    console.error("[Database] Failed to delete category:", error);
    throw error;
  }
}

/**
 * Get all root categories (no parent)
 */
export async function getRootCategories() {
  const db = await getDb();
  if (!db) {
    console.warn("[Database] Cannot get root categories: database not available");
    return [];
  }

  try {
    const result = await db
      .select()
      .from(categories)
      .where(isNull(categories.parentId))
      .orderBy(asc(categories.name));
    return result;
  } catch (error) {
    console.error("[Database] Failed to get root categories:", error);
    throw error;
  }
}

/**
 * Get subcategories of a parent category
 */
export async function getSubcategories(parentId: number) {
  const db = await getDb();
  if (!db) {
    console.warn("[Database] Cannot get subcategories: database not available");
    return [];
  }

  try {
    const result = await db
      .select()
      .from(categories)
      .where(eq(categories.parentId, parentId))
      .orderBy(asc(categories.name));
    return result;
  } catch (error) {
    console.error("[Database] Failed to get subcategories:", error);
    throw error;
  }
}
```

---

## 3. API tRPC Routers

### `server/routers.ts`

```typescript
import { COOKIE_NAME } from "@shared/const";
import { getSessionCookieOptions } from "./_core/cookies";
import { systemRouter } from "./_core/systemRouter";
import { publicProcedure, protectedProcedure, router } from "./_core/trpc";
import { z } from "zod";
import {
  getCategories,
  getCategoryById,
  createCategory,
  updateCategory,
  deleteCategory,
  getRootCategories,
  getSubcategories,
} from "./db";

export const appRouter = router({
  system: systemRouter,
  auth: router({
    me: publicProcedure.query(opts => opts.ctx.user),
    logout: publicProcedure.mutation(({ ctx }) => {
      const cookieOptions = getSessionCookieOptions(ctx.req);
      ctx.res.clearCookie(COOKIE_NAME, { ...cookieOptions, maxAge: -1 });
      return {
        success: true,
      } as const;
    }),
  }),

  categories: router({
    list: protectedProcedure
      .input(
        z.object({
          skip: z.number().int().nonnegative().default(0),
          take: z.number().int().positive().default(10),
          search: z.string().default(""),
          sortBy: z.enum(["name", "id", "createdAt"]).default("name"),
          sortOrder: z.enum(["asc", "desc"]).default("asc"),
        })
      )
      .query(async ({ input }) => {
        return getCategories({
          skip: input.skip,
          take: input.take,
          search: input.search,
          sortBy: input.sortBy,
          sortOrder: input.sortOrder,
        });
      }),

    getById: protectedProcedure
      .input(z.object({ id: z.number().int().positive() }))
      .query(async ({ input }) => {
        return getCategoryById(input.id);
      }),

    create: protectedProcedure
      .input(
        z.object({
          name: z.string().min(1).max(255),
          description: z.string().optional(),
          imageFileName: z.string().optional(),
          parentId: z.number().int().positive().optional(),
          isActive: z.number().int().default(1),
        })
      )
      .mutation(async ({ input }) => {
        return createCategory({
          name: input.name,
          description: input.description || null,
          imageFileName: input.imageFileName || null,
          parentId: input.parentId || null,
          isActive: input.isActive,
        });
      }),

    update: protectedProcedure
      .input(
        z.object({
          id: z.number().int().positive(),
          name: z.string().min(1).max(255).optional(),
          description: z.string().optional(),
          imageFileName: z.string().optional(),
          parentId: z.number().int().positive().optional(),
          isActive: z.number().int().optional(),
        })
      )
      .mutation(async ({ input }) => {
        const { id, ...updateData } = input;
        return updateCategory(id, updateData);
      }),

    delete: protectedProcedure
      .input(z.object({ id: z.number().int().positive() }))
      .mutation(async ({ input }) => {
        return deleteCategory(input.id);
      }),

    getRoots: protectedProcedure.query(async () => {
      return getRootCategories();
    }),

    getSubcategories: protectedProcedure
      .input(z.object({ parentId: z.number().int().positive() }))
      .query(async ({ input }) => {
        return getSubcategories(input.parentId);
      }),
  }),
});

export type AppRouter = typeof appRouter;
```

---

## 4. Frontend - Roteamento

### `client/src/App.tsx`

```typescript
import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import NotFound from "@/pages/NotFound";
import CategoriesDashboard from "@/pages/CategoriesDashboard";
import { Route, Switch } from "wouter";
import ErrorBoundary from "./components/ErrorBoundary";
import { ThemeProvider } from "./contexts/ThemeContext";
import Home from "./pages/Home";

function Router() {
  return (
    <Switch>
      <Route path={"/"} component={Home} />
      <Route path={"/categories"} component={CategoriesDashboard} />
      <Route path={"/404"} component={NotFound} />
      {/* Final fallback route */}
      <Route component={NotFound} />
    </Switch>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider
        defaultTheme="light"
      >
        <TooltipProvider>
          <Toaster />
          <Router />
        </TooltipProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;
```

---

## 5. Frontend - Cliente tRPC

### `client/src/lib/trpc.ts`

```typescript
import { createTRPCReact } from "@trpc/react-query";
import type { AppRouter } from "../../../server/routers";

export const trpc = createTRPCReact<AppRouter>();
```

---

## 6. Frontend - Página Inicial

### `client/src/pages/Home.tsx`

```typescript
import { useAuth } from "@/_core/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Loader2 } from "lucide-react";
import { APP_LOGO, APP_TITLE, getLoginUrl } from "@/const";
import { useLocation } from "wouter";

export default function Home() {
  const { user, loading, isAuthenticated, logout } = useAuth();
  const [, navigate] = useLocation();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            {APP_LOGO && <img src={APP_LOGO} alt={APP_TITLE} className="h-8 w-8" />}
            <h1 className="text-xl font-bold text-gray-900">{APP_TITLE}</h1>
          </div>
          <div className="flex items-center gap-4">
            {isAuthenticated ? (
              <>
                <span className="text-sm text-gray-600">
                  {user?.name} ({user?.role})
                </span>
                <Button variant="outline" size="sm" onClick={logout}>
                  Logout
                </Button>
              </>
            ) : (
              <Button size="sm" onClick={() => window.location.href = getLoginUrl()}>
                Login
              </Button>
            )}
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Bluevelvet Music Store
          </h2>
          <p className="text-xl text-gray-600 mb-8">
            Sistema de Gerenciamento de Categorias
          </p>
        </div>

        {isAuthenticated ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card className="p-8 hover:shadow-lg transition-shadow">
              <h3 className="text-2xl font-bold mb-4 text-gray-900">
                Gerenciar Categorias
              </h3>
              <p className="text-gray-600 mb-6">
                Acesse o dashboard para criar, editar, deletar e gerenciar todas as categorias de produtos da loja.
              </p>
              <Button
                className="w-full"
                onClick={() => navigate("/categories")}
              >
                Ir para Dashboard
              </Button>
            </Card>

            <Card className="p-8 hover:shadow-lg transition-shadow">
              <h3 className="text-2xl font-bold mb-4 text-gray-900">
                Recursos
              </h3>
              <ul className="space-y-3 text-gray-600 mb-6">
                <li className="flex items-center gap-2">
                  <span className="text-blue-600">✓</span>
                  Criar categorias e subcategorias
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-blue-600">✓</span>
                  Editar informações de categorias
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-blue-600">✓</span>
                  Deletar categorias
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-blue-600">✓</span>
                  Buscar e filtrar categorias
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-blue-600">✓</span>
                  Paginação e ordenação
                </li>
              </ul>
            </Card>
          </div>
        ) : (
          <Card className="p-8 text-center max-w-md mx-auto">
            <h3 className="text-2xl font-bold mb-4 text-gray-900">
              Bem-vindo!
            </h3>
            <p className="text-gray-600 mb-6">
              Faça login para acessar o sistema de gerenciamento de categorias.
            </p>
            <Button
              className="w-full"
              onClick={() => window.location.href = getLoginUrl()}
            >
              Fazer Login
            </Button>
          </Card>
        )}
      </main>

      <footer className="bg-white border-t mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 text-center text-gray-600">
          <p>&copy; 2025 Bluevelvet Music Store. Todos os direitos reservados.</p>
        </div>
      </footer>
    </div>
  );
}
```

---

## 7. Script de Seed do Banco de Dados

### `seed-categories.mjs`

```javascript
import mysql from 'mysql2/promise';
import dotenv from 'dotenv';

dotenv.config();

const connection = await mysql.createConnection(process.env.DATABASE_URL);

// Sample categories data
const categories = [
  { name: 'T-Shirts', description: 'Camisetas de banda e artistas', imageFileName: 'tshirts.jpg', parentId: null, isActive: 1 },
  { name: 'Vinyl', description: 'Discos de vinil clássicos e modernos', imageFileName: 'vinyl.jpg', parentId: null, isActive: 1 },
  { name: 'CD', description: 'Discos compactos de música', imageFileName: 'cd.jpg', parentId: null, isActive: 1 },
  { name: 'MP3', description: 'Arquivos de áudio digital', imageFileName: 'mp3.jpg', parentId: null, isActive: 1 },
  { name: 'Books', description: 'Livros sobre música e artistas', imageFileName: 'books.jpg', parentId: null, isActive: 1 },
  { name: 'Acoustic Guitar', description: 'Violões acústicos', imageFileName: 'acoustic-guitar.jpg', parentId: null, isActive: 1 },
  { name: 'Electric Guitar', description: 'Violões elétricos', imageFileName: 'electric-guitar.jpg', parentId: null, isActive: 1 },
  { name: 'Bass', description: 'Baixos e contrabaixos', imageFileName: 'bass.jpg', parentId: null, isActive: 1 },
  { name: 'Drums', description: 'Baterias e percussão', imageFileName: 'drums.jpg', parentId: null, isActive: 1 },
  { name: 'Keyboards', description: 'Teclados e sintetizadores', imageFileName: 'keyboards.jpg', parentId: null, isActive: 1 },
];

try {
  // Clear existing categories
  await connection.execute('DELETE FROM categories');
  console.log('Tabela de categorias limpa');

  // Insert categories
  for (const category of categories) {
    await connection.execute(
      'INSERT INTO categories (name, description, imageFileName, parentId, isActive, createdAt, updatedAt) VALUES (?, ?, ?, ?, ?, NOW(), NOW())',
      [category.name, category.description, category.imageFileName, category.parentId, category.isActive]
    );
  }

  console.log(`✓ ${categories.length} categorias inseridas com sucesso!`);

  // Get the first category ID to create a subcategory
  const [rows] = await connection.execute('SELECT id FROM categories WHERE name = ? LIMIT 1', ['T-Shirts']);
  if (rows.length > 0) {
    const parentId = rows[0].id;
    
    // Insert subcategories
    const subcategories = [
      { name: 'Metal T-Shirts', description: 'Camisetas de bandas de metal', imageFileName: 'metal-tshirts.jpg', parentId },
      { name: 'Rock T-Shirts', description: 'Camisetas de bandas de rock', imageFileName: 'rock-tshirts.jpg', parentId },
      { name: 'Pop T-Shirts', description: 'Camisetas de artistas pop', imageFileName: 'pop-tshirts.jpg', parentId },
    ];

    for (const subcategory of subcategories) {
      await connection.execute(
        'INSERT INTO categories (name, description, imageFileName, parentId, isActive, createdAt, updatedAt) VALUES (?, ?, ?, ?, ?, NOW(), NOW())',
        [subcategory.name, subcategory.description, subcategory.imageFileName, subcategory.parentId, 1]
      );
    }

    console.log(`✓ ${subcategories.length} subcategorias inseridas com sucesso!`);
  }

  console.log('\n✓ Banco de dados populado com sucesso!');
} catch (error) {
  console.error('Erro ao popular o banco de dados:', error);
  process.exit(1);
} finally {
  await connection.end();
}
```

---

## 📝 Notas Importantes

1. **Autenticação:** O sistema usa OAuth do Manus. Usuários são automaticamente sincronizados no banco de dados.

2. **Hierarquia de Categorias:** O campo `parentId` permite criar subcategorias. Se `parentId` for `null`, é uma categoria raiz.

3. **Validação:** Todos os inputs são validados com Zod no backend antes de serem processados.

4. **Type Safety:** O tRPC garante type safety end-to-end entre frontend e backend.

5. **Paginação:** A listagem de categorias usa paginação com 10 itens por página por padrão.

6. **Busca:** A busca é case-insensitive e busca por substring no nome da categoria.

---

**Desenvolvido em 3 dias | Bluevelvet Music Store | 2025**
