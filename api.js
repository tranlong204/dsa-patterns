// API client for backend integration
// Version: 4 - Fixed double-stringification issue
console.log('[api.js] Loaded version 4 - Fixed double-stringification');

// Determine API base from URL param ?api= or localStorage override, fallback to localhost
(function configureApiBase() {
    try {
        const params = new URLSearchParams(window.location.search);
        const apiParam = params.get('api');
        if (apiParam) {
            localStorage.setItem('API_BASE_URL', apiParam);
        }
    } catch (e) { /* noop */ }
})();

const API_BASE_URL = (function() {
    const stored = localStorage.getItem('API_BASE_URL');
    // If stored URL is Render backend, ignore it and use Lambda (migration)
    if (stored && stored.includes('onrender.com')) {
        console.warn('Detected old Render backend URL in localStorage, clearing it');
        localStorage.removeItem('API_BASE_URL');
        return 'https://5n2tv37eki.execute-api.us-west-1.amazonaws.com/prod';
    }
    return stored && stored.trim() !== '' ? stored : 'https://5n2tv37eki.execute-api.us-west-1.amazonaws.com/prod';
})();

class APIClient {
    constructor(baseUrl = API_BASE_URL) {
        this.baseUrl = baseUrl;
        // Use JWT username (sub) as user_id
        this.userId = this.getJwtUsername() || this.getOrCreateUserId();
    }

    getJwtUsername() {
        try {
            const token = localStorage.getItem('access_token');
            if (!token) return null;
            const parts = token.split('.');
            if (parts.length !== 3) return null;
            const payload = JSON.parse(atob(parts[1].replace(/-/g, '+').replace(/_/g, '/')));
            return payload && payload.sub ? String(payload.sub) : null;
        } catch (e) {
            return null;
        }
    }

    getOrCreateUserId() {
        let userId = localStorage.getItem('userId');
        if (!userId) {
            userId = 'user_' + Date.now();
            localStorage.setItem('userId', userId);
        }
        return userId;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        
        // Build config explicitly to avoid any spreading issues
        const config = {
            method: options.method || 'GET',
            headers: {}
        };
        
        // Copy headers explicitly
        if (options.headers) {
            Object.assign(config.headers, options.headers);
        }

        // Attach Bearer token if available
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }

        // Handle request body - ensure proper JSON encoding
        if (options.body !== undefined) {
            const originalBody = options.body;
            console.log('[request] Original body type:', typeof originalBody, 'value:', typeof originalBody === 'string' ? originalBody.substring(0, 100) : originalBody);
            
            // If body is already a string, check if it's JSON
            if (typeof originalBody === 'string') {
                console.log('[request] Body is string, attempting to parse...');
                try {
                    // Try to parse it - if it's valid JSON, it means it was double-stringified
                    const parsed = JSON.parse(originalBody);
                    console.log('[request] Successfully parsed string body, re-stringifying');
                    // Re-stringify it properly
                    config.body = JSON.stringify(parsed);
                    config.headers['Content-Type'] = 'application/json';
                } catch (e) {
                    console.warn('[request] Body is string but not valid JSON:', e.message);
                    // Not valid JSON, treat as plain text
                    config.body = originalBody;
                    if (!config.headers['Content-Type']) {
                        config.headers['Content-Type'] = 'text/plain';
                    }
                }
            } else if (typeof originalBody === 'object' && !(originalBody instanceof FormData) && !(originalBody instanceof URLSearchParams)) {
                console.log('[request] Body is object, stringifying...');
                // Convert object to JSON string - this is the normal case
                config.body = JSON.stringify(originalBody);
                config.headers['Content-Type'] = 'application/json';
            } else {
                console.log('[request] Body is other type, using as-is');
                // Other types (FormData, URLSearchParams, etc.) - use as-is
                config.body = originalBody;
            }
            
            console.log('[request] Final body type:', typeof config.body, 'Content-Type:', config.headers['Content-Type']);
            console.log('[request] Final body preview:', typeof config.body === 'string' ? config.body.substring(0, 150) : config.body);
        }
        
        // Copy other options (but not body, which we already handled)
        if (options.credentials) config.credentials = options.credentials;
        if (options.mode) config.mode = options.mode;
        if (options.cache) config.cache = options.cache;
        if (options.redirect) config.redirect = options.redirect;
        if (options.referrer) config.referrer = options.referrer;

        try {
            const response = await fetch(url, config);
            if (!response.ok) {
                let errorText;
                try {
                    errorText = await response.text();
                    // Try to parse as JSON for better error message
                    try {
                        const errorJson = JSON.parse(errorText);
                        errorText = errorJson.detail || errorJson.message || errorText;
                    } catch (e) {
                        // Not JSON, use as-is
                    }
                } catch (e) {
                    errorText = `HTTP ${response.status} ${response.statusText}`;
                }
                console.error('API error response:', errorText, 'Status:', response.status);
                if (response.status === 401) {
                    // Clear invalid token
                    localStorage.removeItem('access_token');
                    // Only redirect if not already on login page
                    if (!window.location.pathname.includes('login.html')) {
                        window.location.href = 'login.html';
                    }
                    return;
                }
                throw new Error(errorText || `HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    // Problems API
    async getAllProblems() {
        return await this.request('/api/problems/');
    }

    async getProblemById(id) {
        return await this.request(`/api/problems/${id}`);
    }

    async getProblemsByCategory(category) {
        return await this.request(`/api/problems/by-category/${category}`);
    }

    async createProblem(problemData) {
        // Ensure we pass a plain object, not a string
        let body = problemData;
        if (typeof problemData === 'string') {
            try {
                body = JSON.parse(problemData);
            } catch (e) {
                console.error('Failed to parse problemData as JSON:', e);
                throw new Error('Invalid problem data format');
            }
        }
        
        console.log('createProblem - body type:', typeof body, 'body:', body);
        
        return await this.request('/api/problems/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: body  // Pass as object, request() will stringify it
        });
    }

    async deleteProblem(problemId) {
        return await this.request(`/api/problems/${problemId}`, {
            method: 'DELETE'
        });
    }

    // User Progress API
    async getSolvedProblems() {
        return await this.request(`/api/user/${this.userId}/solved`);
    }

    async markProblemSolved(problemId) {
        // Send user's local date to avoid timezone issues
        const today = new Date();
        const year = today.getFullYear();
        const month = String(today.getMonth() + 1).padStart(2, '0');
        const day = String(today.getDate()).padStart(2, '0');
        const localDate = `${year}-${month}-${day}`;
        
        console.log(`Marking problem ${problemId} as solved with date: ${localDate}`);
        
        return await this.request(
            `/api/user/${this.userId}/solved/${problemId}`,
            { 
                method: 'POST',
                body: { solved_at: localDate }
            }
        );
    }

    async markProblemUnsolved(problemId) {
        return await this.request(
            `/api/user/${this.userId}/solved/${problemId}`,
            { method: 'DELETE' }
        );
    }

    async getStats() {
        return await this.request(`/api/user/${this.userId}/stats`);
    }

    async getCalendarData() {
        return await this.request(`/api/user/${this.userId}/calendar`);
    }

    // Company Tags API
    async listCompanyTags() {
        return await this.request('/api/company-tags/');
    }

    async createCompanyTag(name) {
        return await this.request('/api/company-tags/', { method: 'POST', body: { name } });
    }

    async updateCompanyTag(tagId, name) {
        return await this.request(`/api/company-tags/${tagId}`, { method: 'PUT', body: { name } });
    }

    async deleteCompanyTag(tagId) {
        return await this.request(`/api/company-tags/${tagId}`, { method: 'DELETE' });
    }

    async getProblemCompanyTags(problemId) {
        return await this.request(`/api/company-tags/problem/${problemId}`);
    }

    async setProblemCompanyTags(problemId, tagIds) {
        return await this.request(`/api/company-tags/problem/${problemId}`, { method: 'PUT', body: tagIds });
    }

    async getAllProblemCompanyTags() {
        return await this.request('/api/company-tags/all-problem-tags');
    }

    // Revision API
    async getRevisionList() {
        return await this.request(`/api/user/${this.userId}/revision`);
    }

    async addToRevision(problemId) {
        return await this.request(`/api/user/${this.userId}/revision/${problemId}`, { method: 'POST' });
    }

    async removeFromRevision(problemId) {
        return await this.request(`/api/user/${this.userId}/revision/${problemId}`, { method: 'DELETE' });
    }
}

// Initialize API client
const api = new APIClient();

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { APIClient, api };
}

