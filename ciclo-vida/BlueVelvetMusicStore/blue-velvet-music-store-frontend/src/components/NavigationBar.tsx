import React from 'react';
import { useTheme } from '../context/ThemeContext';
import '../styles/NavigationBar.css'; // We will create this

const NavigationBar: React.FC = () => {
    const { theme, toggleTheme } = useTheme();

    return (
        <nav className="navbar">
            <div className="navbar-brand">
                <h1>BlueVelvet</h1>
            </div>
            <div className="navbar-search">
                <input type="text" placeholder="Search for instruments..." />
            </div>
            <div className="navbar-actions">
                <button onClick={toggleTheme} className="theme-toggle" aria-label="Toggle Theme">
                    {theme === 'dark' ? '☀️' : '🌙'}
                </button>
                <div className="user-profile">
                    <span>Login</span>
                </div>
            </div>
        </nav>
    );
};

export default NavigationBar;
