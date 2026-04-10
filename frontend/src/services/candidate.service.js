import api from './api';

const candidateService = {
    async triggerRanking(jobId) {
        const response = await api.post(`/candidates/${jobId}/rank`);
        return response.data;
    },
    
    async getRankedResults(jobId) {
        const response = await api.get(`/candidates/${jobId}/results`);
        return response.data;
    }
};

export default candidateService;
