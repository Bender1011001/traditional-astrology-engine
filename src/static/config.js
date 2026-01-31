window.CAEL_CONFIG = {
    renderUrl: "https://astrology-engine.onrender.com"
};

// Auto-configure API Base for GitHub Pages
if (window.location.hostname.endsWith("github.io")) {
    window.CAEL_API_BASE = window.CAEL_CONFIG.renderUrl;
    console.log("Environment: Production (GitHub Pages). Connected to Render Backend.");
} else {
    console.log("Environment: Local/Development. Expecting backend on same host or proxy.");
}
