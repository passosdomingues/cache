import React from 'react';
import '../styles/ProductCard.css';

interface ProductCardProps {
    id: number;
    name: string;
    price: number;
    imageUrl: string;
    category: string;
}

const ProductCard: React.FC<ProductCardProps> = ({ name, price, imageUrl, category }) => {
    return (
        <div className="product-card">
            <div className="product-image">
                <img src={imageUrl || 'https://via.placeholder.com/300'} alt={name} />
                <span className="product-category-badge">{category}</span>
            </div>
            <div className="product-info">
                <h3 className="product-name">{name}</h3>
                <p className="product-price">${price.toFixed(2)}</p>
                <button className="product-add-btn">Add to Cart</button>
            </div>
        </div>
    );
};

export default ProductCard;
