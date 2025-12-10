/**
 * @author Rafael Passos Domingues
 * @lastUpdate 2025 December 10 (Wed)
 * @brief API methods for Product management.
 * @us US-2100 List products within a category - Granularity: Frontend API
 */
import client from './client';
import type { Category } from './categories';

export interface Product {
    id: number;
    name: string;
    description?: string;
    price: number;
    enabled: boolean;
    inStock: boolean;
    images: string[];
    category: Category;
    createdTime?: string;
    updatedTime?: string;
}

export interface Page<T> {
    content: T[];
    totalPages: number;
    totalElements: number;
    size: number;
    number: number;
}

export const getProductsByCategory = async (categoryId: number, page = 0, size = 10, sort = 'name,asc') => {
    const response = await client.get<Page<Product>>(`/categories/${categoryId}/products`, {
        params: {
            page,
            size,
            sort
        }
    });
    return response.data;
};
