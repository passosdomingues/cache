/**
 * @author Rafael Passos Domingues
 * @lastUpdate 2025 December 10 (Wed)
 * @brief Custom hook for fetching categories from the API.
 * @us US-0000 E-Commerce Features - Granularity: Data Fetching
 */
import { useState, useEffect } from 'react';
import { getCategories, type Category } from '../api/categories';

interface UseCategoriesResult {
    categories: Category[];
    loading: boolean;
    error: string | null;
    refetch: () => void;
}

export const useCategories = (enabledOnly: boolean = true): UseCategoriesResult => {
    const [categories, setCategories] = useState<Category[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchCategories = async () => {
        setLoading(true);
        setError(null);

        try {
            const data = await getCategories();
            const filteredData = enabledOnly ? data.filter((cat: Category) => cat.enabled) : data;
            setCategories(filteredData);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to fetch categories');
            console.error('Error fetching categories:', err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchCategories();
    }, [enabledOnly]);

    return {
        categories,
        loading,
        error,
        refetch: fetchCategories,
    };
};

// Re-export Category type for convenience
export type { Category };
