import { useState, useCallback } from 'react';

/**
 * Standard utility hook to wrap async API calls handling loading state and errors elegantly.
 */
export const useApi = (apiFunc) => {
    const [data, setData] = useState(null);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);

    const execute = useCallback(async (...args) => {
        try {
            setLoading(true);
            setError(null);
            const result = await apiFunc(...args);
            setData(result);
            return result;
        } catch (err) {
            setError(err.response?.data?.detail || err.message || 'An unexpected error occurred');
            throw err;
        } finally {
            setLoading(false);
        }
    }, [apiFunc]);

    return { data, error, loading, execute };
};
