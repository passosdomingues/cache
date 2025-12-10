/**
 * @author Rafael Passos Domingues
 * @lastUpdate 2025 December 10 (Wed)
 * @brief API methods for Gift Cards.
 * @us US-0907 Enter gift card information - Granularity: Frontend API
 * @us US-0907 View gift card balance - Granularity: Frontend API
 */
import client from './client';

export interface GiftCard {
    id: number;
    code: string;
    balance: number;
    isActive: boolean;
}

export const getGiftCardBalance = async (code: string) => {
    const response = await client.get<{ code: string; balance: number }>(`/giftcards/${code}/balance`);
    return response.data;
};

export const validateGiftCard = async (code: string) => {
    const response = await client.post<GiftCard>('/giftcards/validate', { code });
    return response.data;
};
