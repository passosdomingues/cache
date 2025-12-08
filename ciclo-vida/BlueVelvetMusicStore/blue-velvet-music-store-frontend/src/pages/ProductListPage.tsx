/**
 * @author Rafael Passos Domingues
 * @lastUpdate 2025-12-08
 * @brief Product list page.
 * @us US-2100 List products within a category - Granularity: Page
 */
import React, { useState } from 'react';
import ProductCard from '../components/ProductCard';

const ProductListPage: React.FC = () => {
    const [searchTerm, setSearchTerm] = useState('');

    // Placeholder for now
    const products = [
        { id: 1, name: 'Fender Stratocaster', price: 1499.00, imageUrl: '', category: 'Guitars' },
        { id: 2, name: 'Gibson Les Paul', price: 2499.00, imageUrl: '', category: 'Guitars' },
        { id: 3, name: 'Yamaha P-125', price: 649.99, imageUrl: '', category: 'Keyboards' },
        { id: 4, name: 'Roland TD-17KV', price: 1199.99, imageUrl: '', category: 'Drums' },
    ];

    return (
        <div className="product-list-page">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                <h2>All Products</h2>
                <input
                    type="text"
                    placeholder="Search products..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    style={{
                        padding: '0.6rem 1rem',
                        borderRadius: 'var(--border-radius)',
                        border: '1px solid var(--border-color)',
                        backgroundColor: 'var(--bg-tertiary)',
                        color: 'var(--text-primary)',
                        width: '300px'
                    }}
                />
            </div>

            <div className="product-grid">
                {products.map(product => (
                    <ProductCard
                        key={product.id}
                        id={product.id}
                        name={product.name}
                        price={product.price}
                        imageUrl={product.imageUrl}
                        category={product.category}
                    />
                ))}
            </div>
        </div>
    );
};

export default ProductListPage;
