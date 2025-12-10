/**
 * @author Rafael Passos Domingues
 * @lastUpdate 2025 December 10 (Wed)
 * @brief Shopping cart icon component with item count badge.
 * @us US-0000 E-Commerce Features - Granularity: Component
 */
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useCart } from '../context/CartContext';
import '../styles/CartIcon.css';

const CartIcon: React.FC = () => {
    const navigate = useNavigate();
    const { getItemCount } = useCart();
    const itemCount = getItemCount();

    return (
        <div className="cart-icon-container" onClick={() => navigate('/cart')}>
            <svg
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
            >
                <circle cx="9" cy="21" r="1" />
                <circle cx="20" cy="21" r="1" />
                <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6" />
            </svg>
            {itemCount > 0 && (
                <span className="cart-badge">{itemCount}</span>
            )}
        </div>
    );
};

export default CartIcon;
