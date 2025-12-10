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
    images?: string[];
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

/**
 * Get all products with pagination
 */
export const getAllProducts = async (page = 0, size = 20, sort = 'name,asc') => {
    const response = await client.get<Page<Product>>('/products', {
        params: { page, size, sort }
    });
    return response.data;
};

/**
 * Get featured products (first 8 enabled and in-stock products)
 */
export const getFeaturedProducts = async () => {
    const response = await client.get<Product[]>('/products/featured');
    return response.data;
};

/**
 * Get product by ID
 */
export const getProductById = async (id: number) => {
    const response = await client.get<Product>(`/products/${id}`);
    return response.data;
};

/**
 * Get products by category with pagination
 */
export const getProductsByCategory = async (categoryId: number, page = 0, size = 20, sort = 'name,asc') => {
    const response = await client.get<Page<Product>>(`/categories/${categoryId}/products`, {
        params: { page, size, sort }
    });
    return response.data;
};

/**
 * Search products by name
 */
export const searchProducts = async (query: string, page = 0, size = 20, sort = 'name,asc') => {
    const response = await client.get<Page<Product>>('/products/search', {
        params: { query, page, size, sort }
    });
    return response.data;
};

/**
 * Create a new product
 */
export const createProduct = async (product: Omit<Product, 'id' | 'createdTime' | 'updatedTime'>) => {
    const response = await client.post<Product>('/products', product);
    return response.data;
};

/**
 * Update an existing product
 */
export const updateProduct = async (id: number, product: Partial<Product>) => {
    const response = await client.put<Product>(`/products/${id}`, product);
    return response.data;
};

/**
 * Delete a product
 */
export const deleteProduct = async (id: number) => {
    await client.delete(`/products/${id}`);
};
