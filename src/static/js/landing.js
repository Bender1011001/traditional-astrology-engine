import { apiUrl } from './api.js';
import { logEvent, SESSION_ID } from './telemetry.js';
import { initTheme, setupThemeToggle, applyTheme } from './theme.js';
import { updateAuthUI, logout } from './auth.js';
import { escapeHtml, formatPlainReading, hashString } from './utils.js';
import { setupPricing, initiateCheckout } from './pricing.js';

// Expose globally for HTML onclicks
window.initiateCheckout = (tier) => initiateCheckout(tier, getLastChartRequest());
window.startCheckout = (tier) => {
    initiateCheckout(tier, getLastChartRequest());
};
window.switchPricing = (tier) => {
    const b2c = document.getElementById('pricingB2C');
    const b2b = document.getElementById('pricingB2B');
    const btnC = document.getElementById('toggleB2C');
    const btnB = document.getElementById('toggleB2B');

    if (tier === 'b2c') {
        b2c?.classList.remove('hidden');
        b2b?.classList.add('hidden');
        btnC?.classList.add('active');
        btnB?.classList.remove('active');
    } else {
        b2c?.classList.add('hidden');
        b2b?.classList.remove('hidden');
        btnC?.classList.remove('active');
        btnB?.classList.add('active');
    }
};

// Expose logout globally
window.logout = logout;

// Backend Notice Logic
const IS_GH_PAGES = false;
const API_BASE = window.CAEL_API_BASE || "";
const backendNotice = document.getElementById("backendNotice");
if (backendNotice && IS_GH_PAGES && !API_BASE) {
    backendNotice.classList.remove("hidden");
}

let lastChartRequest = null;
let basicFeedbackContext = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    setupThemeToggle();
    updateAuthUI();

    // Set Copyright
    const yearEl = document.getElementById("copyrightYear");
    if (yearEl) yearEl.textContent = new Date().getFullYear();

    // Inputs
    setupInputValidation();
    setupUnknownTimeToggle();
    setupBasicForm();
    setupModals();
    checkRegenerate();

    setupSamplesAndAccordions(); // Logic for accordions in index.html
    setupPricing();
    setupPricingToggle();
});

function setupPricingToggle() {
    // This is now handled by switchPricing() via onclick for robustness,
    // but we can keep this for delegating data-target if we use it elsewhere.
    const toggleBtns = document.querySelectorAll('[data-pricing-toggle]');
    toggleBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const target = btn.getAttribute('data-target');
            window.switchPricing(target);
        });
    });
}

function getLastChartRequest() {
    // Helper to get fresh value of lastChartRequest
    // In strict mode modules, local vars aren't exported.
    // We use the module-scope variable defined below.
    return lastChartRequest;
}

function setupInputValidation() {
    document.querySelectorAll('input[required]').forEach(input => {
        input.addEventListener('blur', () => {
            input.style.borderColor = !input.value ? 'var(--danger)' : '';
        });
        input.addEventListener('input', () => {
            if (input.value) input.style.borderColor = '';
        });
    });
}

function setupUnknownTimeToggle() {
    const basicTimeUnknown = document.getElementById("basicTimeUnknown");
    const basicTimeInput = document.getElementById("basicTime");
    const basicTimeWarning = document.getElementById("basicTimeWarning");

    function setBasicTimeUnknownState(isUnknown) {
        if (basicTimeWarning) basicTimeWarning.classList.toggle("hidden", !isUnknown);
        if (basicTimeInput) {
            basicTimeInput.required = !isUnknown;
            if (isUnknown && !basicTimeInput.value) {
                basicTimeInput.value = "12:00";
            }
        }
    }

    if (basicTimeUnknown) {
        basicTimeUnknown.addEventListener("change", (e) => {
            setBasicTimeUnknownState(e.target.checked);
        });
        setBasicTimeUnknownState(basicTimeUnknown.checked);
    }
}

// Loading Animation
let loadingInterval;
const LOADING_MSGS = [
    "Calculating planetary positions...", "Analyzing essential dignities...",
    "Applying traditional techniques...", "Examining Lot of Fortune...",
    "Calculating Almuten Figuris...", "Generating your forensic report..."
];

function setBasicLoading(isLoading) {
    const basicLoading = document.getElementById("basicLoading");
    const basicStartBtn = document.getElementById("basicStartBtn");
    if (!basicLoading || !basicStartBtn) return;

    basicLoading.classList.toggle("hidden", !isLoading);
    basicStartBtn.disabled = isLoading;

    if (loadingInterval) {
        clearInterval(loadingInterval);
        loadingInterval = null;
    }

    const textEl = document.getElementById("loadingText");
    if (isLoading && textEl) {
        let idx = 0;
        textEl.style.opacity = 0;
        textEl.textContent = LOADING_MSGS[0];
        setTimeout(() => textEl.style.opacity = 1, 50);

        loadingInterval = setInterval(() => {
            textEl.style.opacity = 0;
            setTimeout(() => {
                idx = (idx + 1) % LOADING_MSGS.length;
                textEl.textContent = LOADING_MSGS[idx];
                textEl.style.opacity = 1;
            }, 300);
        }, 2000);
    }
}

function setupBasicForm() {
    const basicForm = document.getElementById("basicForm");
    const basicReading = document.getElementById("basicReading");
    const basicReadingBody = document.getElementById("basicReadingBody");
    const basicFeedback = document.getElementById("basicFeedback");
    const basicTimeUnknown = document.getElementById("basicTimeUnknown");
    const basicTimeInput = document.getElementById("basicTime");

    if (!basicForm) return;

    // Load Last Request
    try {
        const saved = localStorage.getItem("cael_last_request");
        if (saved) lastChartRequest = JSON.parse(saved);
    } catch (e) { }

    basicForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const timeUnknown = basicTimeUnknown ? basicTimeUnknown.checked : false;
        const timeValue = basicTimeInput ? basicTimeInput.value : "";

        const payload = {
            date: document.getElementById("basicDate").value,
            time: timeUnknown && !timeValue ? "12:00" : timeValue,
            city: document.getElementById("basicCity").value,
            time: timeUnknown && !timeValue ? "12:00" : timeValue,
            city: document.getElementById("basicCity").value,
            state: document.getElementById("basicState").value,
            house_system: document.getElementById("houseSystem").value,
            node_type: document.getElementById("nodeType").value
        };

        if (!payload.date || !payload.city || (!payload.time && !timeUnknown)) {
            alert("Please enter birth details.");
            return;
        }

        setBasicLoading(true);
        if (basicReading) basicReading.classList.add("hidden");
        if (basicReadingBody) basicReadingBody.innerHTML = "";

        lastChartRequest = payload;
        localStorage.setItem("cael_last_request", JSON.stringify(payload));
        logEvent("basic_chart_request", { form: payload });

        try {
            const response = await fetch(apiUrl("/api/v1/calculate"), {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            if (!response.ok) throw new Error("Processing failed.");

            const result = await response.json();
            logEvent("basic_chart_result", { result });

            if (result.plain_reading) {
                renderBasicReading(result, payload, timeUnknown);
            } else {
                if (basicReadingBody) basicReadingBody.innerHTML = "<p>Reading unavailable.</p>";
                if (basicReading) basicReading.classList.remove("hidden");
            }
        } catch (error) {
            alert(error.message);
            logEvent("basic_chart_error", { message: error.message });
        } finally {
            setBasicLoading(false);
        }
    });
}

function renderBasicReading(result, payload, timeUnknown) {
    const basicReadingBody = document.getElementById("basicReadingBody");
    const basicReading = document.getElementById("basicReading");

    basicReadingBody.innerHTML = formatPlainReading(result.plain_reading);

    // Inject Temperament Bar (simplified for brevity)
    const temp = result.forensic_report?.summary?.temperament;
    if (temp) {
        // ... Similar logic to basic.js ...
        // For now just appending text to save space
        const div = document.createElement('div');
        div.className = "temperament-badge";
        const tempValue = typeof temp === 'string' ? escapeHtml(temp) : (temp.primary_temperament ? escapeHtml(temp.primary_temperament) : 'Unknown');
        div.innerHTML = `<strong>Dominant Temperament:</strong> ${tempValue}`;
        basicReadingBody.prepend(div);
    }

    // Paywall Logic
    if (result.meta && result.meta.tier === 'free') {
        renderPaywallTeaser(basicReadingBody, result);
    }

    if (basicReading) basicReading.classList.remove("hidden");

    basicFeedbackContext = {
        reading_hash: hashString(result.plain_reading),
        birth: payload,
        meta: result.meta,
        time_unknown: timeUnknown
    };
}

function renderPaywallTeaser(container, result) {
    // ... Implement logic similar to basic.js (teaser + modal trigger) ...
    // Using global function exposed or event dispatch
    const ascPhrase = result.angles ? `Ascendant in <span class="redacted-text">HIDDEN</span>` : `Ascendant in <span class="redacted-text">HIDDEN</span>`;

    const div = document.createElement('div');
    div.innerHTML = `
        <div style="margin-top:2rem; padding:1.5rem; background:rgba(192,122,43,0.05); border:1px solid rgba(192,122,43,0.2); border-radius:8px; text-align:center;">
             <p style="color:var(--gold); font-weight:bold;">PREMIUM DATA HIDDEN</p>
             <ul style="list-style:none; padding:0; font-size:0.9em;">
                <li>${ascPhrase}</li>
                <li>Time Lord: <span class="redacted-text">HIDDEN</span></li>
             </ul>
             <button class="btn-primary" onclick="window.openPaywall()">UNLOCK FULL REPORT</button>
        </div>
        <div style="text-align:center; margin-top:1rem;">
            <button class="help-btn" onclick="window.openEmailModal()">SAVE AS PDF 📥</button>
        </div>
    `;
    container.appendChild(div);

    setTimeout(() => window.openPaywall(), 3500);
}

function setupModals() {
    // Paywall Modal
    const paywallModal = document.getElementById("paywallModal");
    const closePaywall = document.getElementById("closePaywall");
    if (closePaywall && paywallModal) {
        closePaywall.addEventListener('click', () => paywallModal.classList.add('hidden'));
    }
    window.openPaywall = () => { if (paywallModal) paywallModal.classList.remove('hidden'); };

    // Email Modal
    const emailModal = document.getElementById("emailModal");
    const closeEmail = document.getElementById("closeEmail");
    if (closeEmail && emailModal) {
        closeEmail.addEventListener('click', () => emailModal.classList.add('hidden'));
    }
    window.openEmailModal = () => { if (emailModal) emailModal.classList.remove('hidden'); };

    // Checkout Logic - DELEGATED to pricing.js
    // window.startCheckout is already defined at top level to use pricing.js
    // window.openPaywall is defined above

    // Email Form
    const emailForm = document.getElementById("emailForm");
    if (emailForm) {
        emailForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById("captureEmail").value;
            try {
                document.getElementById("emailStatus").textContent = "Sending...";
                await fetch(apiUrl("/api/v1/content/email-pdf"), {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ email, chart_data: window.currentChartData, consent: true })
                });
                document.getElementById("emailStatus").textContent = "Sent!";
                setTimeout(() => emailModal.classList.add('hidden'), 2000);
            } catch (e) {
                document.getElementById("emailStatus").textContent = "Error.";
            }
        });
    }
}

async function checkRegenerate() {
    // Logic to handle token params and auto-load
    // ... Copy from basic.js ...
    const params = new URLSearchParams(window.location.search);
    const token = params.get('token');
    if (token) {
        // ... simplistic restore ...
        localStorage.setItem("cael_temp_token", token);
        // Simulate start
    }
}

function setupSamplesAndAccordions() {
    document.querySelectorAll('.sample-toggle').forEach(btn => {
        btn.addEventListener('click', () => {
            const content = btn.nextElementSibling;
            const expanded = btn.getAttribute('aria-expanded') === 'true';
            btn.setAttribute('aria-expanded', !expanded);
            content.classList.toggle('hidden', expanded);
            btn.querySelector('.icon').textContent = expanded ? '+' : '-';
        });
    });
}
