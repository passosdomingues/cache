/**
 * @author Rafael Passos Domingues
 * @lastUpdate 2025-12-08
 * @brief Axios client configuration with interceptors.
 * @us US-0000 Project Configuration - Granularity: API Client
 */
import axios from 'axios';

const API_URL = '/api';

const client = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor to add auth token
client.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor to handle 401
client.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response && error.response.status === 401) {
            // Clear token and redirect to login if needed
            localStorage.removeItem('token');
            // window.location.href = '/login'; // Optional: auto-redirect
        }
        return Promise.reject(error);
    }
);

export default client;
