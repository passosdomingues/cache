/**
 * @author Rafael Passos Domingues
 * @lastUpdate 2025 December 10 (Wed)
 * @brief Navigation bar component with cart and user menu.
 * @us US-0000 Project Configuration - Granularity: UI Component
 */
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useTheme } from '../context/ThemeContext';
import CartIcon from './CartIcon';
import '../styles/NavigationBar.css';

const NavigationBar: React.FC = () => {
    const { theme, toggleTheme } = useTheme();
    const navigate = useNavigate();

    return (
        <nav className="navbar">
            <div className="navbar-brand" onClick={() => navigate('/')}>
                <h1>BlueVelvet</h1>
            </div>
            <div className="navbar-search">
                <input type="text" placeholder="Search for instruments..." />
            </div>
            <div className="navbar-actions">
                <CartIcon />
                <button onClick={toggleTheme} className="theme-toggle" aria-label="Toggle Theme">
                    {theme === 'dark' ? '☀️' : '🌙'}
                </button>
                <div className="user-profile" onClick={() => navigate('/login')}>
                    <span>Login</span>
                </div>
            </div>
        </nav>
    );
};

export default NavigationBar;
