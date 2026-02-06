export function applyTheme(theme) {
    const value = theme === "dark" ? "dark" : "light";
    document.documentElement.setAttribute("data-theme", value);
    const themeToggle = document.getElementById("themeToggle");
    if (themeToggle) {
        themeToggle.textContent = value === "dark" ? "LIGHT MODE" : "DARK MODE";
        themeToggle.setAttribute("aria-pressed", value === "dark" ? "true" : "false");
    }
}

export function initTheme() {
    const stored = localStorage.getItem("cael_theme");
    if (stored) {
        applyTheme(stored);
        return;
    }
    const prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
    applyTheme(prefersDark ? "dark" : "light");
}

export function setupThemeToggle() {
    const themeToggle = document.getElementById("themeToggle");
    if (themeToggle) {
        themeToggle.addEventListener("click", () => {
            const current = document.documentElement.getAttribute("data-theme") || "light";
            const next = current === "dark" ? "light" : "dark";
            localStorage.setItem("cael_theme", next);
            applyTheme(next);
        });
    }
}
