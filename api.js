// API client for backend integration
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
    return stored && stored.trim() !== '' ? stored : 'https://dsa-patterns-backend.onrender.com';
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
        const config = {
            method: options.method || 'GET',
            headers: {
                ...(options.headers || {})
            },
            ...options
        };

        // Attach Bearer token if available
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }

        // Only set JSON content-type when sending a JSON body
        if (config.body !== undefined) {
            if (typeof config.body === 'object' && !(config.body instanceof FormData) && !(config.body instanceof URLSearchParams)) {
                config.body = JSON.stringify(config.body);
                config.headers['Content-Type'] = config.headers['Content-Type'] || 'application/json';
            }
        }

        try {
            const response = await fetch(url, config);
            if (!response.ok) {
                const errorText = await response.text();
                console.error('API error response:', errorText);
                if (response.status === 401) {
                    window.location.href = 'login.html';
                    return;
                }
                throw new Error(`HTTP error! status: ${response.status}`);
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
        return await this.request('/api/problems/', {
            method: 'POST',
            body: JSON.stringify(problemData)
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

