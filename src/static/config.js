window.CAEL_CONFIG = {
    renderUrl: "https://astrology-engine.onrender.com"
};

// Auto-configure API Base for GitHub Pages
// Production API configuration
if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
    window.CAEL_API_BASE = window.CAEL_CONFIG.renderUrl;
}
