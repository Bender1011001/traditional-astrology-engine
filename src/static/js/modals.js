import { logEvent } from './telemetry.js';
import { getLibrary, saveToLibrary, deleteFromLibrary } from './library.js';
import { currentResult } from './results-core.js';
import { escapeHtml } from './utils.js';
import { renderResults } from './results-core.js';

export function setupModals() {
    const modalOverlay = document.getElementById('modalOverlay');
    const modalClose = document.querySelector('.modal-close');

    if (modalClose) {
        modalClose.addEventListener('click', () => {
            if (modalOverlay) modalOverlay.classList.add('hidden');
        });
    }

    if (modalOverlay) {
        modalOverlay.addEventListener('click', (e) => {
            if (e.target === modalOverlay) {
                modalOverlay.classList.add('hidden');
            }
        });
    }

    // Help Modal
    const helpBtn = document.getElementById("helpBtn");
    const modalBody = document.getElementById("modalBody");
    if (helpBtn && modalBody && modalOverlay) {
        helpBtn.addEventListener("click", () => {
            modalBody.innerHTML = `
                <div class="modal-header"><h2>METHOD & TERMS</h2><div class="ornament"></div></div>
                <div class="help-content">
                    <div class="help-item"><h3>ALMUTEN FIGURIS</h3><p>Primary ruler of the chart.</p></div>
                </div>
             `;
            modalOverlay.classList.remove("hidden");
            logEvent("help_open");
        });
    }
}

// Global functions needed for onclick handlers in HTML strings
window.showDetails = (p) => {
    logEvent("view_details", { planet: p.planet });
    const modal = document.getElementById('modalOverlay');
    const body = document.getElementById('modalBody');
    if (modal && body) {
        const planetName = escapeHtml(p.planet);
        const delineation = escapeHtml(p.delineation_text);
        body.innerHTML = `
            <h2>${planetName}</h2>
            <p>${delineation}</p>
        `;
        modal.classList.remove('hidden');
    }
};


window.showDetailsByPlanet = (name, data) => {
    // This requires data to be passed or accessed globally
    // The chart renderer passes data JSON stringified in the onclick
    if (data && data.forensic_report && data.forensic_report.planets) {
        const p = data.forensic_report.planets.find(pl => pl.planet === name);
        if (p) window.showDetails(p);
    }
};

window.loadFromLibrary = (id) => {
    const lib = getLibrary();
    const entry = lib.find(e => e.id === id);
    if (entry && entry.data) {
        renderResults(entry.data); // This might cause circular dependency if renderResults imports us? 
        // No, renderResults is in results-core.js. We import it.
        document.getElementById('modalOverlay').classList.add('hidden');
        logEvent('library_load', { id: id, name: entry.name });
    }
};

window.deleteFromLibrary = (id) => {
    deleteFromLibrary(id, () => window.openLibraryModal());
};

window.openLibraryModal = () => {
    const modal = document.getElementById('modalOverlay');
    const body = document.getElementById('modalBody');
    const lib = getLibrary();

    let html = `<h2>CHART LIBRARY</h2><div class="library-list">`;
    if (lib.length === 0) {
        html += `<p>Empty.</p>`;
    } else {
        html += lib.map(entry => `
            <div class="library-item">
                <strong>${escapeHtml(entry.name)}</strong>
                <button onclick="loadFromLibrary('${entry.id}')">LOAD</button>
                <button onclick="deleteFromLibrary('${entry.id}')">DEL</button>
            </div>
        `).join('');
    }
    html += `</div>`;
    body.innerHTML = html;
    if (modal) modal.classList.remove('hidden');
};
