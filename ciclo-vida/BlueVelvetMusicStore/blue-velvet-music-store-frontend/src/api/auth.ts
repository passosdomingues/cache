/**
 * @author Rafael Passos Domingues
 * @lastUpdate 2025-12-08
 * @brief Authentication API service.
 * @us US-1232 Login - Granularity: API Service
 */
import client from './client';

export interface LoginRequest {
    email: string; // Changed from username to email to match Backend
    password?: string;
}

export interface AuthResponse {
    token: string;
    username: string; // OR email
    roles: string[];
}

export const login = async (credentials: LoginRequest): Promise<AuthResponse> => {
    return client.post<AuthResponse>('/auth/signin', credentials).then(res => res.data);
};

export const logout = () => {
    localStorage.removeItem('token');
};

export const getCurrentUser = () => {
    return localStorage.getItem('token');
};
