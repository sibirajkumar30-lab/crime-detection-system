import axios from 'axios';

const API = axios.create({
    baseURL: process.env.REACT_APP_API_URL || 'http://localhost:5000/api',
    timeout: 30000,
    // Don't set default Content-Type - let Axios handle it based on data type
});

// Request interceptor - Add JWT token to requests
API.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        
        // Only set Content-Type to JSON if not already set and not FormData
        if (!config.headers['Content-Type'] && !(config.data instanceof FormData)) {
            config.headers['Content-Type'] = 'application/json';
        }
        
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor - Handle token refresh
API.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        // If 401 and not already retried, try to refresh token
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            try {
                const refreshToken = localStorage.getItem('refresh_token');
                if (refreshToken) {
                    const response = await axios.post(
                        `${process.env.REACT_APP_API_URL}/auth/refresh`,
                        {},
                        {
                            headers: {
                                Authorization: `Bearer ${refreshToken}`,
                            },
                        }
                    );

                    const { access_token } = response.data;
                    localStorage.setItem('access_token', access_token);

                    originalRequest.headers.Authorization = `Bearer ${access_token}`;
                    return API(originalRequest);
                }
            } catch (refreshError) {
                // Refresh failed, logout user
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                localStorage.removeItem('user');
                window.location.href = '/login';
                return Promise.reject(refreshError);
            }
        }

        return Promise.reject(error);
    }
);

// Admin API endpoints
export const adminAPI = {
    // User Management
    getUsers: (params) => API.get('/admin/users', { params }),
    getUser: (id) => API.get(`/admin/users/${id}`),
    updateUser: (id, data) => API.put(`/admin/users/${id}`, data),
    deactivateUser: (id) => API.post(`/admin/users/${id}/deactivate`),
    activateUser: (id) => API.post(`/admin/users/${id}/activate`),
    
    // Invitation Management
    createInvitation: (data) => API.post('/admin/invitations', data),
    getInvitations: (params) => API.get('/admin/invitations', { params }),
    revokeInvitation: (id) => API.delete(`/admin/invitations/${id}`),
    resendInvitation: (id) => API.post(`/admin/invitations/${id}/resend`),
};

// Auth API endpoints
export const authAPI = {
    login: (data) => API.post('/auth/login', data),
    register: (data) => API.post('/auth/register', data),
    verifyToken: (token) => API.post('/auth/verify-token', { token }),
    logout: () => API.post('/auth/logout'),
    refresh: (refreshToken) => API.post('/auth/refresh', {}, {
        headers: { Authorization: `Bearer ${refreshToken}` }
    }),
    getProfile: () => API.get('/auth/profile'),
    updateProfile: (data) => API.put('/auth/profile', data),
    changePassword: (data) => API.post('/auth/change-password', data),
};

export default API;
