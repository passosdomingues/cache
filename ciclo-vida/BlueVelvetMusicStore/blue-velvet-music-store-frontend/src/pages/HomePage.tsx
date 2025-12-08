import React, { useState } from 'react';
import ProductCard from '../components/ProductCard';
import CategoryBadge from '../components/CategoryBadge';
import { useNavigate } from 'react-router-dom';

const HomePage: React.FC = () => {
    const navigate = useNavigate();
    const [activeCategory, setActiveCategory] = useState('All');

    // Demo data - later replaced by API call
    const demoProducts = [
        { id: 1, name: 'Fender Stratocaster', price: 1499.00, imageUrl: '', category: 'Guitars' },
        { id: 2, name: 'Gibson Les Paul', price: 2499.00, imageUrl: '', category: 'Guitars' },
        { id: 3, name: 'Yamaha P-125', price: 649.99, imageUrl: '', category: 'Keyboards' },
        { id: 4, name: 'Roland TD-17KV', price: 1199.99, imageUrl: '', category: 'Drums' },
        { id: 5, name: 'Shure SM7B', price: 399.00, imageUrl: '', category: 'Microphones' },
    ];

    const categories = ['All', 'Guitars', 'Keyboards', 'Drums', 'Microphones', 'Accessories'];

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

            <div style={{ marginBottom: '2rem', display: 'flex', gap: '0.5rem', overflowX: 'auto', paddingBottom: '0.5rem' }}>
                {categories.map(cat => (
                    <CategoryBadge
                        key={cat}
                        name={cat}
                        active={activeCategory === cat}
                        onClick={() => setActiveCategory(cat)}
                    />
                ))}
            </div>

            <h2>Featured Products</h2>
            <div className="product-grid">
                {demoProducts.map(product => (
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

export default HomePage;
