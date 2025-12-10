/**
 * @author Rafael Passos Domingues
 * @lastUpdate 2025 December 10 (Wed)
 * @brief Loading spinner component.
 * @us US-0000 E-Commerce Features - Granularity: Component
 */
import React from 'react';
import '../styles/LoadingSpinner.css';

const LoadingSpinner: React.FC = () => {
    return (
        <div className="loading-spinner-container">
            <div className="loading-spinner"></div>
            <p>Loading...</p>
        </div>
    );
};

export default LoadingSpinner;
