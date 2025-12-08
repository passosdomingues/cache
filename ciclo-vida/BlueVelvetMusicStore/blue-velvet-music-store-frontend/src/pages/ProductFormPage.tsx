import React, { useState } from 'react';

const ProductFormPage: React.FC = () => {
    const [name, setName] = useState('');
    const [description, setDescription] = useState('');
    const [price, setPrice] = useState('');
    const [category, setCategory] = useState('');
    const [image, setImage] = useState<File | null>(null);

    const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setImage(e.target.files[0]);
        }
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        const formData = new FormData();
        formData.append('name', name);
        formData.append('description', description);
        formData.append('price', price);
        formData.append('category', category);
        if (image) {
            formData.append('image', image);
        }

        console.log('Submitting product:', formData);
        // TODO: content-type multipart/form-data
    };

    return (
        <div className="product-form-page" style={{ maxWidth: '600px', margin: '0 auto' }}>
            <h2>Create New Product</h2>
            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>

                <div>
                    <label style={{ display: 'block', marginBottom: '0.5rem' }}>Product Name</label>
                    <input
                        type="text"
                        value={name}
                        onChange={e => setName(e.target.value)}
                        className="form-input"
                        style={{ width: '100%', padding: '0.8rem', borderRadius: '8px', border: '1px solid var(--border-color)', background: 'var(--bg-tertiary)', color: 'var(--text-primary)' }}
                        required
                    />
                </div>

                <div>
                    <label style={{ display: 'block', marginBottom: '0.5rem' }}>Category</label>
                    <select
                        value={category}
                        onChange={e => setCategory(e.target.value)}
                        className="form-input"
                        style={{ width: '100%', padding: '0.8rem', borderRadius: '8px', border: '1px solid var(--border-color)', background: 'var(--bg-tertiary)', color: 'var(--text-primary)' }}
                        required
                    >
                        <option value="">Select Category</option>
                        <option value="Guitars">Guitars</option>
                        <option value="Keyboards">Keyboards</option>
                        <option value="Drums">Drums</option>
                    </select>
                </div>

                <div>
                    <label style={{ display: 'block', marginBottom: '0.5rem' }}>Price</label>
                    <input
                        type="number"
                        value={price}
                        onChange={e => setPrice(e.target.value)}
                        className="form-input"
                        style={{ width: '100%', padding: '0.8rem', borderRadius: '8px', border: '1px solid var(--border-color)', background: 'var(--bg-tertiary)', color: 'var(--text-primary)' }}
                        required
                        step="0.01"
                    />
                </div>

                <div>
                    <label style={{ display: 'block', marginBottom: '0.5rem' }}>Description</label>
                    <textarea
                        value={description}
                        onChange={e => setDescription(e.target.value)}
                        className="form-input"
                        style={{ width: '100%', padding: '0.8rem', borderRadius: '8px', border: '1px solid var(--border-color)', background: 'var(--bg-tertiary)', color: 'var(--text-primary)', minHeight: '100px' }}
                        required
                    />
                </div>

                <div>
                    <label style={{ display: 'block', marginBottom: '0.5rem' }}>Product Image</label>
                    <input
                        type="file"
                        onChange={handleImageChange}
                        accept="image/*"
                        style={{ color: 'var(--text-secondary)' }}
                    />
                </div>

                <button
                    type="submit"
                    style={{
                        marginTop: '1rem',
                        padding: '1rem',
                        background: 'var(--accent-color)',
                        color: '#fff',
                        border: 'none',
                        borderRadius: '8px',
                        cursor: 'pointer',
                        fontWeight: 'bold'
                    }}
                >
                    Save Product
                </button>
            </form>
        </div>
    );
};

export default ProductFormPage;
