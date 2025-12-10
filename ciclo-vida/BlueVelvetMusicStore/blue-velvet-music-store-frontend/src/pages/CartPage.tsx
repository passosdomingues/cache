/**
 * @author Rafael Passos Domingues
 * @lastUpdate 2025 December 10 (Wed)
 * @brief Shopping cart page component.
 * @us US-0000 E-Commerce Features - Granularity: Page
 */
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useCart } from '../context/CartContext';
import '../styles/CartPage.css';

const CartPage: React.FC = () => {
    const navigate = useNavigate();
    const { items, removeFromCart, updateQuantity, getTotal, clearCart } = useCart();

    const handleQuantityChange = (productId: number, newQuantity: number) => {
        if (newQuantity > 0) {
            updateQuantity(productId, newQuantity);
        }
    };

    const subtotal = getTotal();
    const tax = subtotal * 0.08; // 8% tax
    const total = subtotal + tax;

    if (items.length === 0) {
        return (
            <div className="cart-page">
                <h1>Shopping Cart</h1>
                <div className="empty-cart">
                    <div className="empty-cart-icon">🛒</div>
                    <h2>Your cart is empty</h2>
                    <p>Add some amazing instruments to get started!</p>
                    <button className="continue-shopping-btn" onClick={() => navigate('/')}>
                        Continue Shopping
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="cart-page">
            <div className="cart-header">
                <h1>Shopping Cart</h1>
                <button className="clear-cart-btn" onClick={clearCart}>
                    Clear Cart
                </button>
            </div>

            <div className="cart-content">
                <div className="cart-items">
                    {items.map(item => (
                        <div key={item.id} className="cart-item">
                            <img
                                src={item.imageUrl || 'https://via.placeholder.com/100x100?text=No+Image'}
                                alt={item.name}
                                className="cart-item-image"
                            />
                            <div className="cart-item-details">
                                <h3>{item.name}</h3>
                                <p className="cart-item-category">{item.category}</p>
                                <p className="cart-item-price">${item.price.toFixed(2)}</p>
                            </div>
                            <div className="cart-item-quantity">
                                <button
                                    onClick={() => handleQuantityChange(item.id, item.quantity - 1)}
                                    className="quantity-btn"
                                >
                                    -
                                </button>
                                <span className="quantity-value">{item.quantity}</span>
                                <button
                                    onClick={() => handleQuantityChange(item.id, item.quantity + 1)}
                                    className="quantity-btn"
                                >
                                    +
                                </button>
                            </div>
                            <div className="cart-item-total">
                                ${(item.price * item.quantity).toFixed(2)}
                            </div>
                            <button
                                className="remove-item-btn"
                                onClick={() => removeFromCart(item.id)}
                            >
                                ✕
                            </button>
                        </div>
                    ))}
                </div>

                <div className="cart-summary">
                    <h2>Order Summary</h2>
                    <div className="summary-row">
                        <span>Subtotal</span>
                        <span>${subtotal.toFixed(2)}</span>
                    </div>
                    <div className="summary-row">
                        <span>Tax (8%)</span>
                        <span>${tax.toFixed(2)}</span>
                    </div>
                    <div className="summary-divider"></div>
                    <div className="summary-row summary-total">
                        <span>Total</span>
                        <span>${total.toFixed(2)}</span>
                    </div>
                    <button className="checkout-btn">
                        Proceed to Checkout
                    </button>
                    <button className="continue-shopping-btn" onClick={() => navigate('/')}>
                        Continue Shopping
                    </button>
                </div>
            </div>
        </div>
    );
};

export default CartPage;
