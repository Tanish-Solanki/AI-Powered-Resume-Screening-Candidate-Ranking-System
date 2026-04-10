import api from './api';

const authService = {
    async register(userData) {
        const response = await api.post('/auth/register', userData);
        return response.data;
    },
    
    async login(email, password) {
        // FastAPI OAuth2PasswordRequestForm requires x-www-form-urlencoded
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);
        
        const response = await api.post('/auth/login', formData, {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        });
        
        if (response.data.access_token) {
            localStorage.setItem('token', response.data.access_token);
        }
        return response.data;
    },
    
    logout() {
        localStorage.removeItem('token');
        // Let server backend handle optional token blacklisting asynchronously
        api.post('/auth/logout').catch(() => {});
    },
    
    getCurrentToken() {
        return localStorage.getItem('token');
    }
};

export default authService;
