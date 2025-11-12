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

// TODO: add more feature queries here as your schema grows.
