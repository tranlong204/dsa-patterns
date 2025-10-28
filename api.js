// API client for backend integration
const API_BASE_URL = 'http://localhost:8000';

class APIClient {
    constructor(baseUrl = API_BASE_URL) {
        this.baseUrl = baseUrl;
        this.userId = this.getOrCreateUserId();
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
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        try {
            const response = await fetch(url, config);
            if (!response.ok) {
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

    // User Progress API
    async getSolvedProblems() {
        return await this.request(`/api/user/${this.userId}/solved`);
    }

    async markProblemSolved(problemId) {
        return await this.request(
            `/api/user/${this.userId}/solved/${problemId}`,
            { method: 'POST' }
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
}

// Initialize API client
const api = new APIClient();

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { APIClient, api };
}

