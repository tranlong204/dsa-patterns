document.addEventListener('DOMContentLoaded', () => {
    // If already logged in, go to main
    // But first verify the token is valid by checking if it's not expired
    const token = localStorage.getItem('access_token');
    if (token) {
        // Try to decode token to check if it's valid (basic check)
        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            const now = Math.floor(Date.now() / 1000);
            // If token is expired or will expire soon, clear it
            if (payload.exp && payload.exp < now) {
                localStorage.removeItem('access_token');
            } else {
                // Token is valid, redirect to main page
                window.location.href = 'index.html';
                return;
            }
        } catch (e) {
            // Token is malformed, clear it
            localStorage.removeItem('access_token');
        }
    }

    const form = document.getElementById('loginForm');
    const errorEl = document.getElementById('error');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        errorEl.textContent = '';

        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value;

        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        try {
            // Get API base from URL params or localStorage; fallback to Lambda API Gateway
            let base = '';
            const params = new URLSearchParams(window.location.search);
            const apiParam = params.get('api');
            if (apiParam) {
                base = apiParam;
                localStorage.setItem('API_BASE_URL', base);
            } else {
                const stored = localStorage.getItem('API_BASE_URL');
                // If stored URL is Render backend, ignore it and use Lambda (migration)
                if (stored && stored.includes('onrender.com')) {
                    console.warn('Detected old Render backend URL in localStorage, clearing it');
                    localStorage.removeItem('API_BASE_URL');
                    base = 'https://5n2tv37eki.execute-api.us-west-1.amazonaws.com/prod';
                } else {
                    base = stored && stored.trim() !== '' ? stored : 'https://5n2tv37eki.execute-api.us-west-1.amazonaws.com/prod';
                }
            }
            const endpoint = (base || '').replace(/\/$/, '') + '/api/auth/login';
            const resp = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: formData.toString()
            });
            if (!resp.ok) {
                const msg = await resp.text();
                throw new Error(msg || 'Login failed');
            }
            const data = await resp.json();
            localStorage.setItem('access_token', data.access_token);
            window.location.href = 'index.html';
        } catch (err) {
            errorEl.textContent = 'Invalid username or password';
        }
    });
});


