/**
 * @author Rafael Passos Domingues
 * @lastUpdate 2025 December 10 (Wed)
 * @brief Product card component with add to cart functionality.
 * @us US-0000 E-Commerce Features - Granularity: Component
 */
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCart } from '../context/CartContext';
import '../styles/ProductCard.css';

interface ProductCardProps {
    id: number;
    name: string;
    price: number;
    imageUrl?: string;
    category: string;
    inStock?: boolean;
}

const ProductCard: React.FC<ProductCardProps> = ({ id, name, price, imageUrl, category, inStock = true }) => {
    const navigate = useNavigate();
    const { addToCart } = useCart();
    const [added, setAdded] = useState(false);

    const handleAddToCart = (e: React.MouseEvent) => {
        e.stopPropagation();
        addToCart({ id, name, price, imageUrl, category });
        setAdded(true);
        setTimeout(() => setAdded(false), 2000);
    };

    const handleCardClick = () => {
        navigate(`/products/${id}`);
    };

    return (
        <div className="product-card" onClick={handleCardClick}>
            <div className="product-image">
                <img src={imageUrl || 'https://via.placeholder.com/300x300?text=No+Image'} alt={name} />
                <span className="product-category-badge">{category}</span>
                {!inStock && <span className="out-of-stock-badge">Out of Stock</span>}
            </div>
            <div className="product-info">
                <h3 className="product-name">{name}</h3>
                <p className="product-price">${price.toFixed(2)}</p>
                <button
                    className={`product-add-btn ${added ? 'added' : ''}`}
                    onClick={handleAddToCart}
                    disabled={!inStock}
                >
                    {added ? '✓ Added!' : inStock ? 'Add to Cart' : 'Out of Stock'}
                </button>
            </div>
        </div>
    );
};

export default ProductCard;
