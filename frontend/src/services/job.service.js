import api from './api';

const jobService = {
    async createJob(jobData) {
        const response = await api.post('/jobs/', jobData);
        return response.data;
    },
    
    async getJobs(skip = 0, limit = 100) {
        const response = await api.get(`/jobs/?skip=${skip}&limit=${limit}`);
        return response.data;
    },
    
    async getJobById(id) {
        const response = await api.get(`/jobs/${id}`);
        return response.data;
    },
    
    async deleteJob(id) {
        const response = await api.delete(`/jobs/${id}`);
        return response.data;
    }
};

export default jobService;
