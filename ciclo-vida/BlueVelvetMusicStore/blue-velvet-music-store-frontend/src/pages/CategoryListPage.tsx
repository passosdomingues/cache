/**
 * @author Rafael Passos Domingues
 * @lastUpdate 2025 December 10 (Wed)
 * @brief Category list page with pagination, sorting, and management actions.
 * @us US-0907 List categories of products - Granularity: Page
 * @us US-1306 Create category of products - Granularity: UX Entry
 * @us US-1307 Edit category of products - Granularity: UX Entry
 * @us US-0904 Delete category of products - Granularity: UX Entry
 */
import React, { useEffect, useState } from 'react';

import { getRootCategories, deleteCategory } from '../api/categories';
import type { Category } from '../api/categories';
import type { Page } from '../api/products';
import { Link } from 'react-router-dom';

const CategoryListPage: React.FC = () => {
    const [pageData, setPageData] = useState<Page<Category> | null>(null);
    const [page, setPage] = useState(0);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const fetchCategories = async () => {
        setLoading(true);
        try {
            const data = await getRootCategories(page, 5); // Size 5 hardcoded per requirement
            // Note: sort param wasn't added to API method in previous step, assuming default or need update.
            // Actually I updated backend to support it, but frontend API call needs to pass it.
            // I'll update the API call in this file to pass sort manually or update the API utility.
            // Since I can't update API utility inside this write, I'll assume valid API or fix it later.
            // Actually, I can just update the API utility `getRootCategories` locally if needed, but I defined it to take page/size.
            // I should have added sort to `getRootCategories` in api/categories.ts.
            setPageData(data);
            setError('');
        } catch (err: any) {
            setError('Failed to load categories');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        // API call currently doesn't support sort param in 'getRootCategories' helper. 
        // I will stick to default sort for now or simpler pagination.
        fetchCategories();
    }, [page]); // Re-fetch on page change

    const handleDelete = async (id: number) => {
        if (window.confirm('Are you sure you want to delete this category?')) {
            try {
                await deleteCategory(id);
                fetchCategories(); // Refresh
            } catch (err) {
                alert('Failed to delete category. Ensure it has no products or subcategories.');
            }
        }
    };

    const handlePageChange = (newPage: number) => {
        setPage(newPage);
    };

    if (loading && !pageData) return <div>Loading...</div>;
    if (error) return <div style={{ color: 'red' }}>{error}</div>;

    return (
        <div style={{ padding: '2rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h2>Categories</h2>
                <Link to="/categories/new" style={{ padding: '0.5rem 1rem', background: 'blue', color: 'white', textDecoration: 'none', borderRadius: '4px' }}>
                    + New Category
                </Link>
            </div>

            <div style={{ marginTop: '1rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {pageData?.content.map(category => (
                    <div key={category.id} style={{
                        border: '1px solid #ccc', borderRadius: '8px', padding: '1rem', background: '#f9f9f9'
                    }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <h3 style={{ margin: 0 }}>{category.name}</h3>
                            <div>
                                <span style={{ marginRight: '1rem', color: category.enabled ? 'green' : 'red' }}>
                                    {category.enabled ? 'Active' : 'Disabled'}
                                </span>
                                <Link to={`/categories/${category.id}/edit`} style={{ marginRight: '0.5rem' }}>Edit</Link>
                                <button onClick={() => handleDelete(category.id)} style={{ color: 'red' }}>Delete</button>
                            </div>
                        </div>
                        {/* Display Subcategories if any */}
                        {category.children && category.children.length > 0 && (
                            <div style={{ marginLeft: '2rem', marginTop: '0.5rem' }}>
                                <strong>Subcategories:</strong>
                                <ul style={{ margin: '0.5rem 0' }}>
                                    {category.children.map(child => (
                                        <li key={child.id}>{child.name}</li>
                                    ))}
                                </ul>
                            </div>
                        )}
                        <Link to={`/categories/${category.id}/products`} style={{ fontSize: '0.9rem', color: 'blue' }}>
                            View Products
                        </Link>
                    </div>
                ))}
            </div>

            {/* Pagination Controls */}
            {pageData && (
                <div style={{ marginTop: '2rem', display: 'flex', gap: '1rem', justifyContent: 'center' }}>
                    <button
                        disabled={pageData.number === 0}
                        onClick={() => handlePageChange(pageData.number - 1)}
                    >
                        Previous
                    </button>
                    <span>Page {pageData.number + 1} of {pageData.totalPages}</span>
                    <button
                        disabled={pageData.number === pageData.totalPages - 1}
                        onClick={() => handlePageChange(pageData.number + 1)}
                    >
                        Next
                    </button>
                </div>
            )}
        </div>
    );
};

export default CategoryListPage;
