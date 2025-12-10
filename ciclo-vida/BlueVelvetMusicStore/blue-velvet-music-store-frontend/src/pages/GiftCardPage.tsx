/**
 * @author Rafael Passos Domingues
 * @lastUpdate 2025 December 10 (Wed)
 * @brief Page to manage Gift Cards (Check balance).
 * @us US-0907 Enter gift card information - Granularity: Page
 * @us US-0907 View gift card balance - Granularity: Page
 */
import React, { useState } from 'react';
import { getGiftCardBalance } from '../api/giftcards';

const GiftCardPage: React.FC = () => {
    const [code, setCode] = useState('');
    const [balanceData, setBalanceData] = useState<{ code: string, balance: number } | null>(null);
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleCheckBalance = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setBalanceData(null);
        setLoading(true);

        try {
            const data = await getGiftCardBalance(code);
            setBalanceData(data);
        } catch (err: any) {
            setError(err.response?.data?.message || 'Invalid Gift Card Code');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ padding: '2rem', maxWidth: '500px' }}>
            <h2>Gift Cards</h2>
            <p>Enter your gift card code to check the balance.</p>

            <form onSubmit={handleCheckBalance} style={{ display: 'flex', gap: '0.5rem', marginBottom: '2rem' }}>
                <input
                    type="text"
                    value={code}
                    onChange={e => setCode(e.target.value)}
                    placeholder="Enter Code (e.g. ABCD-1234)"
                    required
                    style={{ flex: 1, padding: '0.5rem' }}
                />
                <button type="submit" disabled={loading} style={{ padding: '0.5rem 1rem', background: 'green', color: 'white', border: 'none' }}>
                    {loading ? 'Checking...' : 'Check Balance'}
                </button>
            </form>

            {error && <div style={{ color: 'red', marginTop: '1rem' }}>{error}</div>}

            {balanceData && (
                <div style={{ marginTop: '2rem', padding: '1rem', border: '2px solid green', borderRadius: '8px', textAlign: 'center' }}>
                    <h3>Balance Available</h3>
                    <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'green' }}>
                        ${balanceData.balance.toFixed(2)}
                    </div>
                    <p>Code: {balanceData.code}</p>
                </div>
            )}
        </div>
    );
};

export default GiftCardPage;
