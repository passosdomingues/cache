/**
 * @author Rafael Passos Domingues
 * @lastUpdate 2025 December 10 (Wed)
 * @brief API methods for Category management.
 * @us US-1306 Create category of products - Granularity: Frontend API
 * @us US-1307 Edit category of products - Granularity: Frontend API
 * @us US-0904 Delete category of products - Granularity: Frontend API
 */
import client from './client';
import type { Page } from './products'; // Reusing Page definition

export interface Category {
    id: number;
    name: string;
    imageFileName?: string;
    enabled: boolean;
    parent?: { id: number; name: string };
    children?: Category[];
}

export const getCategories = async () => {
    const response = await client.get<Category[]>('/categories/public');
    return response.data;
};

export const getRootCategories = async (page = 0, size = 5) => {
    const response = await client.get<Page<Category>>('/categories/public/roots', {
        params: { page, size }
    });
    return response.data;
};

export const getCategory = async (id: number) => {
    const response = await client.get<Category>(`/categories/public/${id}`);
    return response.data;
};

export const createCategory = async (data: FormData) => {
    const response = await client.post<Category>('/categories', data, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    return response.data;
};

export const updateCategory = async (id: number, data: FormData) => {
    const response = await client.put<Category>(`/categories/${id}`, data, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    return response.data;
};

export const deleteCategory = async (id: number) => {
    await client.delete(`/categories/${id}`);
};

export const toggleCategory = async (id: number) => {
    await client.patch(`/categories/${id}/toggle`);
};
