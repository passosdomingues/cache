/**
 * @author Rafael Passos Domingues
 * @lastUpdate 2025 December 10 (Wed)
 * @brief Form for creating and editing categories.
 * @us US-1306 Create category of products - Granularity: Page
 * @us US-1307 Edit category of products - Granularity: Page
 */
import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { createCategory, updateCategory, getCategory, getCategories } from '../api/categories';
import type { Category } from '../api/categories';

const CategoryFormPage: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const isEdit = !!id;

    const [name, setName] = useState('');
    const [parentId, setParentId] = useState<string>('');
    const [enabled, setEnabled] = useState(true);
    const [image, setImage] = useState<File | null>(null);
    const [categories, setCategories] = useState<Category[]>([]);
    const [error, setError] = useState('');

    useEffect(() => {
        // Load all categories for parent selection
        getCategories().then(setCategories).catch(console.error);

        if (isEdit) {
            getCategory(Number(id)).then(cat => {
                setName(cat.name);
                setParentId(cat.parent?.id.toString() || '');
                setEnabled(cat.enabled);
            }).catch(err => {
                setError('Failed to load category details');
                console.error(err);
            });
        }
    }, [id, isEdit]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        const formData = new FormData();
        formData.append('name', name);
        if (parentId) formData.append('parentId', parentId);
        formData.append('enabled', String(enabled));
        if (image) formData.append('image', image);

        try {
            if (isEdit) {
                await updateCategory(Number(id), formData);
            } else {
                await createCategory(formData);
            }
            navigate('/categories');
        } catch (err: any) {
            setError(err.response?.data?.message || 'Failed to save category');
        }
    };

    return (
        <div style={{ padding: '2rem', maxWidth: '600px' }}>
            <h2>{isEdit ? 'Edit Category' : 'New Category'}</h2>
            {error && <div style={{ color: 'red', marginBottom: '1rem' }}>{error}</div>}

            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div>
                    <label>Name</label>
                    <input
                        type="text"
                        value={name}
                        onChange={e => setName(e.target.value)}
                        required
                        style={{ width: '100%', padding: '0.5rem' }}
                    />
                </div>

                <div>
                    <label>Parent Category</label>
                    <select
                        value={parentId}
                        onChange={e => setParentId(e.target.value)}
                        style={{ width: '100%', padding: '0.5rem' }}
                    >
                        <option value="">None (Root Category)</option>
                        {categories.filter(c => c.id !== Number(id)).map(c => (
                            <option key={c.id} value={c.id}>{c.name}</option>
                        ))}
                    </select>
                </div>

                <div>
                    <label>
                        <input
                            type="checkbox"
                            checked={enabled}
                            onChange={e => setEnabled(e.target.checked)}
                        />
                        {' '}Active
                    </label>
                </div>

                <div>
                    <label>Image</label>
                    <input
                        type="file"
                        accept="image/*"
                        onChange={e => setImage(e.target.files ? e.target.files[0] : null)}
                    />
                </div>

                <div style={{ marginTop: '1rem' }}>
                    <button type="submit" style={{ padding: '0.5rem 1rem', background: 'blue', color: 'white', border: 'none', borderRadius: '4px' }}>
                        Save
                    </button>
                    <button
                        type="button"
                        onClick={() => navigate('/categories')}
                        style={{ marginLeft: '1rem', padding: '0.5rem 1rem' }}
                    >
                        Cancel
                    </button>
                </div>
            </form>
        </div>
    );
};

export default CategoryFormPage;
