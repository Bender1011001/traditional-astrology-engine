export function updateAuthUI() {
    const token = localStorage.getItem('cael_auth_token');
    const userJson = localStorage.getItem('cael_user');
    const nav = document.querySelector('.header-actions');
    if (!nav) return;

    // Find login link
    let loginLink = nav.querySelector('a[href="login.html"]');
    if (!loginLink) {
        // Might already be transformed to logout
        loginLink = nav.querySelector('.logout-btn-nav');
    }

    if (token && loginLink) {
        // Change to Logout
        let userEmail = "";
        try {
            if (userJson) {
                const user = JSON.parse(userJson);
                userEmail = user.email ? user.email.split('@')[0].toUpperCase() : "";
            }
        } catch (e) { }

        loginLink.textContent = userEmail ? `LOG OUT (${userEmail})` : "LOG OUT";
        loginLink.href = "#";
        loginLink.className = "help-btn logout-btn-nav";
        loginLink.onclick = (e) => {
            e.preventDefault();
            logout();
        };
    } else if (!token && loginLink && loginLink.classList.contains('logout-btn-nav')) {
        // Revert to Login (if logout happened in another tab/action)
        loginLink.textContent = "LOG IN";
        loginLink.href = "login.html";
        loginLink.className = "help-btn";
        loginLink.onclick = null;
    }
}

export function logout() {
    localStorage.removeItem('cael_auth_token');
    localStorage.removeItem('cael_user');
    localStorage.removeItem('cael_last_request');
    location.reload();
}
