/**
 * @author Rafael Passos Domingues
 * @lastUpdate 2025 December 10 (Wed)
 * @brief Product list page fetching from API.
 * @us US-2100 List products within a category - Granularity: Page
 */
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import ProductCard from '../components/ProductCard';
import { getProductsByCategory } from '../api/products';
import type { Product, Page } from '../api/products';

const ProductListPage: React.FC = () => {
    const { categoryId } = useParams<{ categoryId: string }>();
    const [pageData, setPageData] = useState<Page<Product> | null>(null);
    const [page, setPage] = useState(0);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    useEffect(() => {
        if (!categoryId) return;

        const loadProducts = async () => {
            setLoading(true);
            try {
                const data = await getProductsByCategory(Number(categoryId), page);
                setPageData(data);
                setError('');
            } catch (err: any) {
                setError('Failed to load products');
                console.error(err);
            } finally {
                setLoading(false);
            }
        };

        loadProducts();
    }, [categoryId, page]);

    const handlePageChange = (newPage: number) => {
        setPage(newPage);
    };

    if (!categoryId) return <div style={{ padding: '2rem' }}>Please select a category to view products.</div>;
    if (loading && !pageData) return <div style={{ padding: '2rem' }}>Loading...</div>;
    if (error) return <div style={{ padding: '2rem', color: 'red' }}>{error}</div>;

    return (
        <div className="product-list-page" style={{ padding: '2rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                <h2>Products</h2>
            </div>

            {pageData && pageData.content.length === 0 && (
                <p>No products found in this category.</p>
            )}

            <div className="product-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: '1.5rem' }}>
                {pageData?.content.map(product => (
                    <ProductCard
                        key={product.id}
                        id={product.id}
                        name={product.name}
                        price={product.price}
                        imageUrl={product.images && product.images.length > 0 ? product.images[0] : ''}
                        category={product.category.name}
                    />
                ))}
            </div>

            {pageData && (pageData.totalPages > 1) && (
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

export default ProductListPage;
