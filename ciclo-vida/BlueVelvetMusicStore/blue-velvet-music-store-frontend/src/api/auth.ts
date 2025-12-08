import client from './client';

export interface LoginRequest {
    username: string;
    password?: string;
}

export interface AuthResponse {
    token: string;
    username: string;
    roles: string[];
}

export const login = async (credentials: LoginRequest): Promise<AuthResponse> => {
    // TODO: Replace with actual endpoint /api/auth/login
    // For now, we simulate a successful login
    // return client.post<AuthResponse>('/auth/login', credentials).then(res => res.data);

    console.log('Simulating login for:', credentials);
    return new Promise((resolve) => {
        setTimeout(() => {
            const fakeToken = "fake-jwt-token-" + Date.now();
            localStorage.setItem('token', fakeToken);
            resolve({
                token: fakeToken,
                username: credentials.username,
                roles: ['ROLE_USER']
            });
        }, 500);
    });
};

export const logout = () => {
    localStorage.removeItem('token');
};

export const getCurrentUser = () => {
    return localStorage.getItem('token');
};
