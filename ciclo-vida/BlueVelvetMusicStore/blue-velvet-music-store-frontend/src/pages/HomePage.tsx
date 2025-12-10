/**
 * @author Rafael Passos Domingues
 * @lastUpdate 2025 December 10 (Wed)
 * @brief Home page component with real API integration.
 * @us US-0000 E-Commerce Features - Granularity: Page
 */
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import ProductCard from '../components/ProductCard';
import CategoryBadge from '../components/CategoryBadge';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import { useProducts } from '../hooks/useProducts';
import { useCategories } from '../hooks/useCategories';

const HomePage: React.FC = () => {
    const navigate = useNavigate();
    const [activeCategory, setActiveCategory] = useState<number | null>(null);

    // Fetch featured products or products by category
    const { products, loading: productsLoading, error: productsError, refetch } = useProducts(
        activeCategory || undefined,
        !activeCategory
    );

    // Fetch categories
    const { categories, loading: categoriesLoading } = useCategories(true);

    const handleCategoryClick = (categoryId: number | null) => {
        setActiveCategory(categoryId);
    };

    return (
        <div className="home-page">
            <div className="hero-section" style={{
                marginBottom: '2rem',
                padding: '3rem',
                backgroundColor: 'var(--bg-secondary)',
                borderRadius: 'var(--border-radius)',
                backgroundImage: 'linear-gradient(135deg, rgba(187, 134, 252, 0.1) 0%, rgba(18, 18, 18, 0) 100%)'
            }}>
                <h1 style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>Welcome to Blue Velvet</h1>
                <p style={{ fontSize: '1.2rem', color: 'var(--text-secondary)', maxWidth: '600px' }}>
                    Discover the finest musical instruments and equipment.
                    From vintage guitars to modern synthesizers.
                </p>
                <button
                    onClick={() => navigate('/products')}
                    style={{
                        marginTop: '1.5rem',
                        padding: '0.8rem 2rem',
                        backgroundColor: 'var(--accent-color)',
                        color: '#fff',
                        border: 'none',
                        borderRadius: '25px',
                        fontSize: '1rem',
                        fontWeight: '600',
                        cursor: 'pointer'
                    }}
                >
                    Shop Now
                </button>
            </div>

            {!categoriesLoading && categories.length > 0 && (
                <div style={{ marginBottom: '2rem', display: 'flex', gap: '0.5rem', overflowX: 'auto', paddingBottom: '0.5rem' }}>
                    <CategoryBadge
                        key="all"
                        name="All"
                        active={activeCategory === null}
                        onClick={() => handleCategoryClick(null)}
                    />
                    {categories.map(cat => (
                        <CategoryBadge
                            key={cat.id}
                            name={cat.name}
                            active={activeCategory === cat.id}
                            onClick={() => handleCategoryClick(cat.id)}
                        />
                    ))}
                </div>
            )}

            <h2>{activeCategory ? 'Products' : 'Featured Products'}</h2>

            {productsLoading && <LoadingSpinner />}

            {productsError && <ErrorMessage message={productsError} onRetry={refetch} />}

            {!productsLoading && !productsError && products.length === 0 && (
                <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-secondary)' }}>
                    <p>No products found.</p>
                </div>
            )}

            {!productsLoading && !productsError && products.length > 0 && (
                <div className="product-grid">
                    {products.map(product => (
                        <ProductCard
                            key={product.id}
                            id={product.id}
                            name={product.name}
                            price={product.price}
                            imageUrl={product.images?.[0]}
                            category={product.category.name}
                            inStock={product.inStock}
                        />
                    ))}
                </div>
            )}
        </div>
    );
};

export default HomePage;
