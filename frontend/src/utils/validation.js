/**
 * Reusable RegEx evaluation bounds and form checks enforcing robust security directly inside user client.
 */

export const isValidEmail = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
};

export const isValidPassword = (password) => {
    // Requires min 8 chars
    return password && password.length >= 8;
};

export const validateJobDescription = (data) => {
    const errors = {};
    if (!data.title || data.title.length < 3) {
        errors.title = "Title must be at least 3 characters long.";
    }
    if (!data.description || data.description.length < 10) {
        errors.description = "Description highly detailed mapping at least 10 characters.";
    }
    return {
        isValid: Object.keys(errors).length === 0,
        errors
    };
};
