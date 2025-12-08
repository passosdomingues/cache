import React from 'react';


const CategoryListPage: React.FC = () => {
    const categories = ['Guitars', 'Keyboards', 'Drums', 'Microphones', 'Studio Monitors', 'Cables', 'Cases'];

    return (
        <div>
            <h2>Categories</h2>
            <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', marginTop: '1rem' }}>
                {categories.map(cat => (
                    <div
                        key={cat}
                        style={{
                            padding: '2rem',
                            backgroundColor: 'var(--bg-secondary)',
                            borderRadius: 'var(--border-radius)',
                            border: '1px solid var(--border-color)',
                            cursor: 'pointer',
                            minWidth: '200px',
                            textAlign: 'center'
                        }}
                    >
                        <h3 style={{ margin: 0, color: 'var(--accent-color)' }}>{cat}</h3>
                        <p style={{ color: 'var(--text-secondary)' }}>Browse {cat}</p>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default CategoryListPage;
