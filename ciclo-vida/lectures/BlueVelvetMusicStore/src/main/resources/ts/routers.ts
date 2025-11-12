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
