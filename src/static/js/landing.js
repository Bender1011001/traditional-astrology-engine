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

    // If the user was redirected to signup/login, restore their pending reading inputs.
    restorePendingReadingRequest();
});

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
        const resp = await fetch(apiUrl("/api/v1/meta"), { method: "GET" });
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
                We are running live testing. Individual readings will be free for a limited time, but you still need an account.
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
            node_type: document.getElementById("nodeType").value
        };

        if (!payload.date || !payload.city || (!payload.time && !timeUnknown)) {
            alert("Please enter birth details.");
            return;
        }

        // Account required for readings.
        const token = localStorage.getItem("cael_auth_token");
        if (!token) {
            // Persist the request so signup/login can resume.
            try {
                localStorage.setItem("cael_pending_reading", JSON.stringify(payload));
                localStorage.setItem("cael_last_request", JSON.stringify(payload));
                localStorage.setItem("cael_post_auth_redirect", window.location.href);
            } catch (e) { }
            window.location.href = "signup.html?reason=reading";
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
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
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

    // Upgrade CTA for free/demo users (skip during promo unlock).
    if (result.meta && result.meta.tier === 'free' && !result.meta.promo_unlocked) {
        renderUpgradeCta(basicReadingBody);
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
                    const saveResp = await fetch(apiUrl("/api/v1/reading_feedback"), {
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

function renderUpgradeCta(container) {
    const div = document.createElement('div');
    div.innerHTML = `
        <div class="lock-disclaimer" style="margin-top: 1.5rem;">
            <strong>Practitioner Access:</strong>
            Create an account to start a no-card trial (14 days) and unlock the full deterministic outputs, exports, and API access.
            <div class="hero-actions" style="justify-content:center; margin-top: 1rem;">
                <a class="btn-primary" href="signup.html?plan=practitioner">Start Practitioner Trial</a>
                <a class="btn-secondary" href="signup.html?plan=studio">Start Studio Trial</a>
                <a class="btn-secondary" href="profile.html">Go to Dashboard</a>
            </div>
        </div>
    `;
    container.appendChild(div);
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
