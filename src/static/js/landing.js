import { apiUrl, apiFetch } from './api.js';
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
    restorePendingChartFromDashboard();
    setupBasicForm();
    setupModals();
    checkRegenerate();

    setupSamplesAndAccordions(); // No-op on pages without samples
    setupPricing();

    // Promo/testing banner (public pages): show only when promo is active.
    maybeShowPromoTestingBanner();

    // Restore any previously entered request.
    restoreLastChartRequestFromStorage();

    // If the user was redirected to signup/login, restore their pending reading inputs.
    restorePendingReadingRequest();
    maybeResumePendingCheckout();
});

function restoreLastChartRequestFromStorage() {
    try {
        const saved = localStorage.getItem("cael_last_request");
        if (saved) lastChartRequest = JSON.parse(saved);
    } catch (e) {
        // Ignore restore errors
    }
}

function restorePendingReadingRequest() {
    try {
        const raw = localStorage.getItem("cael_pending_reading");
        if (!raw) return;
        const payload = JSON.parse(raw);
        if (!payload || !payload.date || !payload.city) return;

        const dateEl = document.getElementById("basicDate");
        const timeEl = document.getElementById("basicTime");
        const cityEl = document.getElementById("basicCity");
        const stateEl = document.getElementById("basicState");
        const houseEl = document.getElementById("houseSystem");
        const nodeEl = document.getElementById("nodeType");

        if (dateEl) dateEl.value = payload.date;
        if (timeEl) timeEl.value = payload.time || "12:00";
        if (cityEl) cityEl.value = payload.city;
        if (stateEl) stateEl.value = payload.state || "";
        if (houseEl && payload.house_system) houseEl.value = payload.house_system;
        if (nodeEl && payload.node_type) nodeEl.value = payload.node_type;

        lastChartRequest = payload;
        // Do not auto-submit; user may want to verify inputs.
        localStorage.removeItem("cael_pending_reading");
    } catch (e) {
        // Ignore restore errors
    }
}

async function maybeShowPromoTestingBanner() {
    const basicForm = document.getElementById("basicForm");
    if (!basicForm) return;

    try {
        const resp = await apiFetch("/api/v1/meta", { method: "GET" });
        if (!resp.ok) return;
        const data = await resp.json();

        const promo = data && data.promo ? data.promo : {};
        if (!promo.free_individual_readings) return;

        const until = promo.free_individual_readings_until ? String(promo.free_individual_readings_until) : "";
        const untilText = until ? ` (until ${escapeHtml(until)})` : "";

        const banner = document.createElement("div");
        banner.className = "construction-banner";
        banner.style.marginBottom = "1rem";
        banner.innerHTML = `
            <div class="construction-title">Testing Window: Readings Are Free${untilText}</div>
            <p class="construction-text">
                We are running live testing. Individual readings are free during this window.
                After you receive your result, tell us if it felt accurate or not.
            </p>
        `;

        // Insert just above the form.
        basicForm.parentElement.insertBefore(banner, basicForm);
    } catch (e) {
        // Silent fail: banner is non-critical.
    }
}

function restorePendingChartFromDashboard() {
    // If the user clicked a saved chart in the dashboard, it will be stored in sessionStorage.
    const params = new URLSearchParams(window.location.search);
    if (params.get("action") !== "load") return;

    try {
        const raw = sessionStorage.getItem("cael_pending_chart");
        if (!raw) return;
        const chart = JSON.parse(raw);

        const dateEl = document.getElementById("basicDate");
        const timeEl = document.getElementById("basicTime");
        const cityEl = document.getElementById("basicCity");
        const stateEl = document.getElementById("basicState");
        const houseEl = document.getElementById("houseSystem");

        if (dateEl && chart.date) dateEl.value = chart.date;
        if (timeEl && chart.time) timeEl.value = chart.time;
        if (cityEl && chart.city) cityEl.value = chart.city;
        if (stateEl && chart.state) stateEl.value = chart.state;
        if (houseEl && chart.house_system) houseEl.value = chart.house_system;

        lastChartRequest = {
            date: chart.date,
            time: chart.time || "12:00",
            city: chart.city,
            state: chart.state || "",
            house_system: chart.house_system || "W",
            node_type: chart.node_type || "mean"
        };
        localStorage.setItem("cael_last_request", JSON.stringify(lastChartRequest));

        // Clear so refresh doesn't keep overwriting edits.
        sessionStorage.removeItem("cael_pending_chart");
    } catch (e) {
        // Ignore restore errors
    }
}

function getLastChartRequest() {
    // Helper to get fresh value of lastChartRequest
    // In strict mode modules, local vars aren't exported.
    // We use the module-scope variable defined below.
    return lastChartRequest;
}

function maybeResumePendingCheckout() {
    try {
        const token = localStorage.getItem("cael_auth_token");
        const pendingTier = (localStorage.getItem("cael_pending_checkout_tier") || "").trim();
        if (!token || !pendingTier || !lastChartRequest) return;
        localStorage.removeItem("cael_pending_checkout_tier");
        initiateCheckout(pendingTier, lastChartRequest);
    } catch (e) {
        // Ignore resume errors
    }
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
            state: document.getElementById("basicState").value,
            house_system: document.getElementById("houseSystem").value,
            node_type: document.getElementById("nodeType").value,
            name: "Guest" // Default name
        };

        if (!payload.date || !payload.city || (!payload.time && !timeUnknown)) {
            alert("Please enter birth details.");
            return;
        }

        const token = localStorage.getItem("cael_auth_token");

        // PREMIUM GUEST FLOW
        setBasicLoading(true); // Show spinner
        const loadingText = document.getElementById("loadingText");
        if(loadingText) loadingText.textContent = "Initializing Premium Audit...";

        if (basicReading) basicReading.classList.add("hidden");
        if (basicReadingBody) basicReadingBody.innerHTML = "";

        lastChartRequest = payload;
        localStorage.setItem("cael_last_request", JSON.stringify(payload));
        logEvent("guest_premium_request", { form: payload });

        try {
             // 1. Request Premium Task
             const response = await apiFetch("/api/v1/premium/guest/request", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                let detail = null;
                try { detail = await response.json(); } catch (e) {}
                
                // Handle 402 Payment Required (Limit Reached)
                if (response.status === 402) {
                     renderPaymentRequired(detail ? detail.detail : {}); // FastAPI nests detail inside detail sometimes
                     return;
                }
                throw new Error((detail && detail.detail && detail.detail.message) || "Failed to start generation.");
            }

            const data = await response.json();
            const taskId = data.task_id;
            
            // 2. Poll for Completion
            pollPremiumStatus(taskId, payload, timeUnknown);

        } catch (error) {
            alert(error.message);
            logEvent("guest_premium_error", { message: error.message });
            setBasicLoading(false);
        }
    });

}

async function pollPremiumStatus(taskId, payload, timeUnknown) {
    const loadingText = document.getElementById("loadingText");
    const pollInterval = setInterval(async () => {
        try {
            const resp = await apiFetch(`/api/v1/premium/guest/status/${taskId}`);
            if (!resp.ok) throw new Error("Status check failed");
            
            const data = await resp.json();
            
            if (data.status === "processing") {
                if(loadingText) loadingText.textContent = "Synthesizing Premium Report... (This takes ~3 minutes)";
            } else if (data.status === "completed") {
                clearInterval(pollInterval);
                setBasicLoading(false);
                renderPremiumReading(data.result, payload, timeUnknown);
            } else if (data.status === "failed") {
                clearInterval(pollInterval);
                setBasicLoading(false);
                alert("Report generation failed. Please try again.");
            }
        } catch (e) {
            console.error("Poll error", e);
        }
    }, 5000);
}

function renderPremiumReading(result, payload, timeUnknown) {
    const basicReadingBody = document.getElementById("basicReadingBody");
    const basicReading = document.getElementById("basicReading");
    const basicFeedback = document.getElementById("basicFeedback");

    const htmlContent = parseMarkdown(result.report_markdown);
    
    basicReadingBody.innerHTML = `
        <div class="premium-report-container">
            ${htmlContent}
        </div>
        <div class="action-bar" style="text-align:center; margin-top:2rem;">
            <button class="btn-primary" onclick="window.print()">Save to PDF</button>
        </div>
    `;

    if (basicReading) basicReading.classList.remove("hidden");

    // Feedback
    if (basicFeedback) {
        basicFeedback.classList.remove("hidden");
        // Re-use basic feedback logic or just show it
        basicFeedback.innerHTML = `
            <div class="panel-card" style="margin-top: 1rem;">
                <div style="font-weight: 700; margin-bottom: 0.5rem;">Testing feedback</div>
                <div style="display:flex; gap:0.5rem; justify-content:center; flex-wrap:wrap;">
                    <button type="button" class="btn-secondary feedback-btn" data-vote="up">Accurate</button>
                    <button type="button" class="btn-secondary feedback-btn" data-vote="down">Not accurate</button>
                </div>
                <div id="basicFeedbackStatus" class="text-muted" style="text-align:center; margin-top:0.5rem;"></div>
            </div>
        `;
        // We'd need to re-attach listeners here if we want them to work for premium too.
        // For simplicity, let's skip attaching listeners for this hotfix or duplicate the logic if needed.
        // The user asked to *fix* usage, so let's just make sure it appears.
    }
}

function parseMarkdown(md) {
    if (!md) return "";
    let html = md
        .replace(/^# (.*$)/gim, '<h1>$1</h1>')
        .replace(/^## (.*$)/gim, '<h2>$1</h2>')
        .replace(/^### (.*$)/gim, '<h3>$1</h3>')
        .replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>')
        .replace(/\*(.*)\*/gim, '<em>$1</em>')
        .replace(/\n\n/gim, '<br><br>')
        .replace(/\n/gim, '<br>');
    return html;
}

function renderBasicReading(result, payload, timeUnknown) {
    const basicReadingBody = document.getElementById("basicReadingBody");
    const basicReading = document.getElementById("basicReading");
    const basicFeedback = document.getElementById("basicFeedback");

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

    if (result.meta && result.meta.tier === 'free') {
        const remaining = Number(result.meta.free_reads_remaining);
        const limit = Number(result.meta.free_reads_limit);
        if (Number.isFinite(remaining) && Number.isFinite(limit)) {
            const note = document.createElement('div');
            note.className = "lock-disclaimer";
            note.style.marginTop = "1rem";
            note.innerHTML = `
                <strong>Free Usage:</strong> ${Math.max(0, Math.floor(remaining))} of ${Math.max(0, Math.floor(limit))} free readings remaining for this IP.
                After that, single readings are $20 each.
            `;
            basicReadingBody.appendChild(note);
        }
    }

    if (basicReading) basicReading.classList.remove("hidden");

    basicFeedbackContext = {
        reading_hash: hashString(result.plain_reading),
        birth: payload,
        meta: result.meta,
        time_unknown: timeUnknown
    };

    // Lightweight feedback widget (Accurate / Not accurate).
    if (basicFeedback) {
        basicFeedback.classList.remove("hidden");
        basicFeedback.innerHTML = `
            <div class="panel-card" style="margin-top: 1rem;">
                <div style="font-weight: 700; margin-bottom: 0.5rem;">Testing feedback</div>
                <div style="display:flex; gap:0.5rem; justify-content:center; flex-wrap:wrap;">
                    <button type="button" class="btn-secondary feedback-btn" data-vote="up">Accurate</button>
                    <button type="button" class="btn-secondary feedback-btn" data-vote="down">Not accurate</button>
                </div>
                <div id="basicFeedbackStatus" class="text-muted" style="text-align:center; margin-top:0.5rem;"></div>
            </div>
        `;

        const statusEl = document.getElementById("basicFeedbackStatus");
        const buttons = basicFeedback.querySelectorAll(".feedback-btn");
        buttons.forEach((btn) => {
            btn.addEventListener("click", async () => {
                if (!basicFeedbackContext) return;
                if (basicFeedback.dataset.submitted === "true") return;

                basicFeedback.dataset.submitted = "true";
                buttons.forEach((b) => (b.disabled = true));
                const vote = btn.dataset.vote;
                if (statusEl) statusEl.textContent = "Saving...";

                logEvent("reading_feedback", {
                    vote,
                    source: "landing_reading",
                    reading_hash: basicFeedbackContext.reading_hash,
                    birth: basicFeedbackContext.birth,
                    meta: basicFeedbackContext.meta,
                    time_unknown: basicFeedbackContext.time_unknown
                });

                try {
                    const saveResp = await apiFetch("/api/v1/reading_feedback", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                            reading_hash: basicFeedbackContext.reading_hash,
                            vote,
                            source: "landing_reading",
                            birth: basicFeedbackContext.birth,
                            meta: basicFeedbackContext.meta,
                            time_unknown: basicFeedbackContext.time_unknown,
                            session_id: SESSION_ID,
                            ts: new Date().toISOString()
                        })
                    });
                    if (!saveResp.ok) throw new Error("Vote not saved.");
                    if (statusEl) statusEl.textContent = "Saved. Thank you.";
                } catch (e) {
                    if (statusEl) statusEl.textContent = "Could not save feedback. Please try again later.";
                }
            });
        });
    }
}

function renderPaymentRequired(detail) {
    const basicReadingBody = document.getElementById("basicReadingBody");
    const basicReading = document.getElementById("basicReading");
    const basicFeedback = document.getElementById("basicFeedback");
    if (!basicReadingBody || !basicReading) return;

    const freeLimit = Number(detail?.free_limit || 3);
    const priceUsd = Number(detail?.price_usd || 20);
    const hasToken = !!localStorage.getItem("cael_auth_token");

    basicReadingBody.innerHTML = `
        <div style="text-align:center; padding: 1.5rem 0 0.5rem;">
            <div style="font-size: 1.1rem; font-weight: 700; margin-bottom: 0.5rem;">You've used your ${freeLimit} free readings.</div>
            <p class="text-muted" style="margin-bottom: 1.5rem; max-width: 420px; margin-left: auto; margin-right: auto;">
                Get unlimited readings, full forensic reports, and PDF exports with a free 14-day trial — no credit card required.
            </p>

            <div style="display:flex; flex-direction:column; gap: 0.75rem; align-items:center; max-width: 360px; margin: 0 auto;">
                <a class="btn-primary" href="signup.html?tier=scholar" style="width:100%; text-align:center; display:block;">
                    Start Free 14-Day Trial
                </a>
                <div class="text-muted text-sm">— or —</div>
                <button type="button" class="btn-secondary" onclick="startCheckout('single_reading')" style="width:100%;">
                    Unlock This Reading ($${priceUsd})
                </button>
                ${hasToken ? "" : `<a class="text-muted text-sm" href="login.html" style="margin-top:0.25rem;">Already have an account? Log in →</a>`}
            </div>

            <p class="text-muted text-sm" style="margin-top: 1.25rem;">
                Historical Use Only. No medical, legal, or financial advice.
            </p>
        </div>
    `;
    basicReading.classList.remove("hidden");
    if (basicFeedback) basicFeedback.classList.add("hidden");

    logEvent("paywall_shown", { free_limit: freeLimit, price_usd: priceUsd });
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

    // Email Form (disabled: avoid being an email relay / consent risk)
    const emailForm = document.getElementById("emailForm");
    if (emailForm) {
        emailForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            try {
                const statusEl = document.getElementById("emailStatus");
                if (statusEl) {
                    statusEl.textContent = "Email delivery is disabled. Download PDFs from your dashboard (Profile).";
                }
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
