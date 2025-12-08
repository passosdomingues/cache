import React from 'react';
import '../styles/CategoryBadge.css';

interface CategoryBadgeProps {
    name: string;
    onClick?: () => void;
    active?: boolean;
}

const CategoryBadge: React.FC<CategoryBadgeProps> = ({ name, onClick, active }) => {
    return (
        <span
            className={`category-badge ${active ? 'active' : ''}`}
            onClick={onClick}
        >
            {name}
        </span>
    );
};

export default CategoryBadge;
