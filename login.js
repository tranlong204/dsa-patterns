document.addEventListener('DOMContentLoaded', () => {
    // If already logged in, go to main
    const token = localStorage.getItem('access_token');
    if (token) {
        window.location.href = 'index.html';
        return;
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
            // Get API base from URL params or localStorage; fallback to Render backend
            let base = '';
            const params = new URLSearchParams(window.location.search);
            const apiParam = params.get('api');
            if (apiParam) {
                base = apiParam;
                localStorage.setItem('API_BASE_URL', base);
            } else {
                base = localStorage.getItem('API_BASE_URL') || 'https://dsa-patterns-backend.onrender.com';
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


