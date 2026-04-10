import api from './api';

const resumeService = {
    async uploadResumes(files) {
        const formData = new FormData();
        Array.from(files).forEach((file) => {
            formData.append('files', file); 
        });
        
        const response = await api.post('/resumes/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    }
};

export default resumeService;
