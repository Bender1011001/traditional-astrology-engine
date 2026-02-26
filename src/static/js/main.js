// Main Entry Point
import { initTheme, setupThemeToggle } from './theme.js';
import { updateAuthUI, logout } from './auth.js';
import { initTelemetry } from './telemetry.js';
import { setupForms } from './forms.js';
import { setupTabs } from './ui.js';
import { setupModals } from './modals.js';
// We also need to expose library functions to window as they are called from HTML strings
import './modals.js';

console.log("Loading AstroForge Modules...");

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    setupThemeToggle();
    updateAuthUI();
    initTelemetry();
    setupForms();
    setupTabs();
    setupModals();

    // Initialize specific UI elements
    const libraryBtn = document.getElementById('libraryBtn');
    if (libraryBtn) {
        libraryBtn.addEventListener('click', () => window.openLibraryModal());
    }

    // Expose logout to global for the header link which we modify in js
    window.logout = logout;
});
