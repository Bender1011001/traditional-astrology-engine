import { renderResults } from './results-core.js';
import { logEvent } from './telemetry.js';
import { escapeHtml } from './utils.js';

const STORAGE_KEY = 'codex_chart_library';
let currentResult = null; // We need to track this shared state?
// Actually, currentResult is used in many places. It should probably be in a state module or passed around.
// For now, let's export a setter/getter or manage it in main.js? 
// The library functions need to load it.

// Let's assume we pass the setCurrentResult callback or similar. 
// Or better, let's keep the library logic pure and handle the UI glue in main.js or modals.js.

export function getLibrary() {
    try {
        const raw = localStorage.getItem(STORAGE_KEY);
        return raw ? JSON.parse(raw) : [];
    } catch (e) {
        return [];
    }
}

export function saveToLibrary(data) {
    const lib = getLibrary();
    const id = Date.now().toString();
    const name = prompt("Enter a name for this chart (e.g. 'Napoleon'):", data.meta.name || "Untitled Chart");

    if (!name) return;

    const entry = {
        id: id,
        name: name,
        date: data.meta.date,
        time: data.meta.time,
        city: data.meta.city,
        savedAt: new Date().toISOString(),
        data: data
    };

    lib.unshift(entry);
    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(lib.slice(0, 50)));
        alert('Chart saved to library!');
    } catch (e) {
        alert('Storage full or error saving: ' + e.message);
    }
}

export function deleteFromLibrary(id, refreshCallback) {
    if (!confirm('Are you sure you want to delete this chart?')) return;

    let lib = getLibrary();
    lib = lib.filter(e => e.id !== id);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(lib));
    if (refreshCallback) refreshCallback();
}
