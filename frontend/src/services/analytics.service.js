import api from './api';

const analyticsService = {
    async getDashboardStats() {
        const response = await api.get('/analytics/dashboard');
        return response.data;
    },
    
    async getCandidateOverview() {
        const response = await api.get('/analytics/candidates-overview');
        return response.data;
    }
};

export default analyticsService;
