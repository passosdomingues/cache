/**
 * @author Rafael Passos Domingues
 * @lastUpdate 2025 December 10 (Wed)
 * @brief Custom hook for fetching products from the API.
 * @us US-0000 E-Commerce Features - Granularity: Data Fetching
 */
import { useState, useEffect } from 'react';
import { getAllProducts, getFeaturedProducts, getProductsByCategory, type Product } from '../api/products';

interface UseProductsResult {
    products: Product[];
    loading: boolean;
    error: string | null;
    refetch: () => void;
}

export const useProducts = (categoryId?: number, featured: boolean = false): UseProductsResult => {
    const [products, setProducts] = useState<Product[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchProducts = async () => {
        setLoading(true);
        setError(null);

        try {
            let data: Product[];

            if (featured) {
                data = await getFeaturedProducts();
            } else if (categoryId) {
                const response = await getProductsByCategory(categoryId);
                data = response.content || [];
            } else {
                const response = await getAllProducts();
                data = response.content || [];
            }

            setProducts(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to fetch products');
            console.error('Error fetching products:', err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchProducts();
    }, [categoryId, featured]);

    return {
        products,
        loading,
        error,
        refetch: fetchProducts,
    };
};

// Re-export Product type for convenience
export type { Product };
