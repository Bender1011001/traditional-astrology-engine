
const SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
];

const DEFAULT_RENDER_URL = "https://astrology-engine.onrender.com";
if (!window.CAEL_API_BASE && window.location.hostname !== "localhost" && window.location.hostname !== "127.0.0.1") {
    window.CAEL_API_BASE = DEFAULT_RENDER_URL;
}

const API_BASE = window.CAEL_API_BASE || "";
function apiUrl(path) { return `${API_BASE}${path}`; }

// === AUTHENTICATION UI ===
function updateAuthUI() {
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
        // Change to Dashboard
        loginLink.textContent = "DASHBOARD";
        loginLink.href = "profile.html";
        loginLink.className = "help-btn highlight-btn"; // Make it pop
        loginLink.onclick = null;
    } else if (!token && loginLink) {
        // Revert to Login
        loginLink.textContent = "LOG IN";
        loginLink.href = "login.html";
        loginLink.className = "help-btn";
        loginLink.onclick = null;
    }
}

function logout() {
    localStorage.removeItem('cael_auth_token');
    localStorage.removeItem('cael_user');
    localStorage.removeItem('cael_last_request'); // Optional: clear session too?
    location.reload();
}
// =========================

// === TELEMETRY & LOGGING ===
async function logTelemetry(eventType, elementId = null, data = null) {
    try {
        const payload = {
            event_type: eventType,
            element_id: elementId,
            url: window.location.href,
            data: data
        };
        const token = localStorage.getItem('cael_auth_token');
        const headers = { 'Content-Type': 'application/json' };
        if (token) headers['Authorization'] = `Bearer ${token}`;

        // Use sendBeacon if available for better reliability on page unload
        // But sendBeacon doesn't support custom headers easily for Bearer token in some older contexts,
        // so we'll stick to fetch. keepalive: true helps.
        fetch(apiUrl("/api/v1/log/telemetry"), {
            method: 'POST',
            headers: headers,
            body: JSON.stringify(payload),
            keepalive: true
        }).catch(() => { });
    } catch (e) { }
}

// Track Clicks
document.addEventListener('click', (e) => {
    const target = e.target.closest('button, a, .clickable, input[type="submit"], .nav-link');
    if (target) {
        let label = target.innerText ? target.innerText.substring(0, 30) : (target.id || target.className);
        logTelemetry('click', target.id, {
            tag: target.tagName,
            label: label,
            classes: target.className
        });
    }
});

// Track JS Errors
window.addEventListener('error', (e) => {
    logTelemetry('js_error', null, {
        message: e.message,
        filename: e.filename,
        lineno: e.lineno
    });
});
// ==========================
const IS_GH_PAGES = false;
const backendNotice = document.getElementById("backendNotice");
if (backendNotice && IS_GH_PAGES && !API_BASE) {
    backendNotice.classList.remove("hidden");
}

// Help Modal Logic
const helpBtn = document.getElementById("helpBtn");
const modalOverlay = document.getElementById("modalOverlay");
const modalBody = document.getElementById("modalBody");
const modalClose = document.querySelector(".modal-close");
const themeToggle = document.getElementById("themeToggle");

// === DASHBOARD AUTO-LOAD ===
async function checkPendingChart() {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('action') === 'load') {
        const pending = sessionStorage.getItem('cael_pending_chart');
        if (pending) {
            const chart = JSON.parse(pending);
            // Populate form
            if (document.getElementById('date')) document.getElementById('date').value = chart.date || '';
            if (document.getElementById('time')) document.getElementById('time').value = chart.time || '';
            if (document.getElementById('city')) document.getElementById('city').value = chart.city || '';
            if (document.getElementById('state')) document.getElementById('state').value = chart.state || '';
            if (document.getElementById('name')) document.getElementById('name').value = chart.name || '';
            if (document.getElementById('houseSystem')) document.getElementById('houseSystem').value = chart.house_system || 'W';
            if (document.getElementById('currentAge') && chart.age) document.getElementById('currentAge').value = chart.age;

            // Optional: Trigger calculation automatically
            setTimeout(() => {
                const form = document.getElementById('chartForm');
                if (form) form.dispatchEvent(new Event('submit'));
            }, 500);

            sessionStorage.removeItem('cael_pending_chart');
            // Clean URL
            window.history.replaceState({}, document.title, window.location.pathname);
        }
    }
}
window.addEventListener('DOMContentLoaded', checkPendingChart);
// ===========================

const glossaryBtn = document.getElementById("glossaryBtn");
if (glossaryBtn) {
    glossaryBtn.addEventListener("click", async () => {
        modalBody.innerHTML = `<div class="modal-loading">Opening the library...</div>`;
        modalOverlay.classList.remove("hidden");

        try {
            const resp = await fetch(apiUrl("/api/v1/glossary"));
            const glossary = await resp.json();

            let html = `
                <div class="modal-header">
                    <h2>ASTROLOGICAL GLOSSARY</h2>
                    <div class="ornament"></div>
                </div>
                <div class="help-content">
            `;

            for (const [term, def] of Object.entries(glossary)) {
                html += `
                    <div class="help-item">
                        <h3>${escapeHtml(term)}</h3>
                        <p>${escapeHtml(def)}</p>
                    </div>
                `;
            }
            html += `</div>`;
            modalBody.innerHTML = html;
        } catch (err) {
            modalBody.innerHTML = `<p class="error">Failed to load library.</p>`;
        }
    });
}

if (helpBtn) {
    helpBtn.addEventListener("click", () => {
        modalBody.innerHTML = `
            <div class="modal-header">
                <h2>METHOD & TERMS</h2>
                <div class="ornament"></div>
            </div>
            <div class="help-content">
                <div class="help-item">
                    <h3>ALMUTEN FIGURIS</h3>
                    <p>Planet with the highest total dignity from Sun, Moon, Ascendant, Lot of Fortune, and Syzygy. Treated as the primary ruler of the chart.</p>
                </div>
                <div class="help-item">
                    <h3>PERFORMANCE INDEX</h3>
                    <p>A weighted metric of a planet's ability to act. 60% essential dignity (inherent character) + 40% accidental dignity (circumstantial power).</p>
                </div>
                <div class="help-item">
                    <h3>SOVEREIGN (IMPERIAL) vs. CORRUPT</h3>
                    <p><strong>Imperial/Sovereign</strong>: High dignity and accidental power. Strong capacity to act.<br>
                    <strong>Corrupt/Vagabond/Cursed</strong>: Malefic, in detriment, or severely afflicted. Weak or harmful capacity.</p>
                </div>
                <div class="help-item">
                    <h3>CHRONOCRATOR (TIME LORD)</h3>
                    <p>Planet ruling the current period. Annual time lords are assigned by profections.</p>
                </div>
                <div class="help-item">
                    <h3>EPITASIS</h3>
                    <p>Day when the Lord of the Year equals the Lord of the Day. Signs intensified activity.</p>
                </div>
                <div class="help-item">
                    <h3>ZODIACAL RELEASING</h3>
                    <p>Time-lord sequence from the Lots.
                    <br><strong>Level 1:</strong> Long periods (years).
                    <br><strong>Level 2:</strong> Sub-periods (months/years).
                    <br><strong>Loosing of the Bond:</strong> Major pivot in the sequence.</p>
                </div>
            </div>
        `;
        modalOverlay.classList.remove("hidden");
        logEvent("help_open");
    });
}

if (modalClose) {
    modalClose.addEventListener("click", () => {
        modalOverlay.classList.add("hidden");
    });
}

modalOverlay.addEventListener("click", (e) => {
    if (e.target === modalOverlay) {
        modalOverlay.classList.add("hidden");
    }
});

function apiUrl(path) {
    return `${API_BASE}${path}`;
}

function applyTheme(theme) {
    const value = theme === "dark" ? "dark" : "light";
    document.documentElement.setAttribute("data-theme", value);
    if (themeToggle) {
        themeToggle.textContent = value === "dark" ? "LIGHT MODE" : "DARK MODE";
        themeToggle.setAttribute("aria-pressed", value === "dark" ? "true" : "false");
    }
}

function initTheme() {
    const stored = localStorage.getItem("cael_theme");
    if (stored) {
        applyTheme(stored);
        return;
    }
    const prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
    applyTheme(prefersDark ? "dark" : "light");
}

initTheme();
updateAuthUI();

if (themeToggle) {
    themeToggle.addEventListener("click", () => {
        const current = document.documentElement.getAttribute("data-theme") || "light";
        const next = current === "dark" ? "light" : "dark";
        localStorage.setItem("cael_theme", next);
        applyTheme(next);
    });
}

// Pricing Modal Logic
const pricingBtn = document.getElementById("pricingBtn");
const pricingModal = document.getElementById("pricingModal");
const pricingClose = document.getElementById("pricingClose");

if (pricingBtn) {
    pricingBtn.addEventListener("click", () => {
        pricingModal.classList.remove("hidden");
    });
}
if (pricingClose) {
    pricingClose.addEventListener("click", () => {
        pricingModal.classList.add("hidden");
    });
}
if (pricingModal) {
    pricingModal.addEventListener("click", (e) => {
        if (e.target === pricingModal) pricingModal.classList.add("hidden");
    });
}


// Checkout Logic
async function initiateCheckout(tier) {
    const token = localStorage.getItem('cael_auth_token');
    if (!token) {
        window.location.href = "login.html?redirect=pricing";
        return;
    }

    const isAnnual = document.getElementById("billingToggle").checked;

    // Create Checkout Session
    try {
        const resp = await fetch(apiUrl("/api/v1/billing/create-checkout-session"), {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({
                tier: tier,
                annual: isAnnual, // Pass annual flag
                chart_request: {
                    date: "2000-01-01", time: "12:00", city: "Rome", state: "Italy"
                },
                success_url: window.location.origin + "/index.html?session_id={CHECKOUT_SESSION_ID}",
                cancel_url: window.location.origin + "/index.html"
            })
        });

        if (!resp.ok) {
            const err = await resp.json();
            throw new Error(err.detail || "Checkout Failed");
        }

        const data = await resp.json();
        if (data.url) {
            window.location.href = data.url;
        }

    } catch (e) {
        alert("Billing Error: " + e.message);
    }
}

// Developer Portal Logic
async function loadDeveloperData() {
    const token = localStorage.getItem('cael_auth_token');
    if (!token) {
        window.location.href = "login.html?redirect=developer.html";
        return;
    }

    // Load Stats
    try {
        const resp = await fetch(apiUrl("/api/v1/developer/usage"), {
            headers: { "Authorization": `Bearer ${token}` }
        });
        const data = await resp.json();
        if (resp.ok) {
            document.getElementById("planTier").textContent = data.plan_tier.toUpperCase();
            document.getElementById("callsUsed").textContent = data.api_calls_used;
            document.getElementById("quotaLimit").textContent = data.quota || "∞";
        }
    } catch (e) {
        console.error("Failed to load stats", e);
    }

    // Load Keys
    loadApiKeys(token);
}

async function loadApiKeys(token) {
    try {
        const resp = await fetch(apiUrl("/api/v1/developer/keys"), {
            headers: { "Authorization": `Bearer ${token}` }
        });
        const keys = await resp.json();
        const list = document.getElementById("keyList");
        list.innerHTML = "";

        keys.forEach(key => {
            const li = document.createElement("li");
            li.className = "key-item";
            li.innerHTML = `
                <div>
                    <strong>${key.name}</strong>
                    <div class="key-meta">Created: ${new Date(key.created_at).toLocaleDateString()}</div>
                </div>
                <div style="display:flex; align-items:center;">
                    <code style="margin-right:15px; background:#000; padding:2px 5px;">${key.prefix}</code>
                    <button class="danger-btn" onclick="revokeApiKey('${key.id}')">Revoke</button>
                </div>
            `;
            list.appendChild(li);
        });
    } catch (e) {
        console.error("Failed to load keys", e);
    }
}

async function createApiKey() {
    const token = localStorage.getItem('cael_auth_token');
    const name = document.getElementById("newKeyName").value;
    if (!name) return alert("Please name your key");

    try {
        const resp = await fetch(apiUrl("/api/v1/developer/keys"), {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ name: name })
        });

        if (resp.ok) {
            const data = await resp.json();
            document.getElementById("newKeyDisplay").textContent = data.key;
            document.getElementById("keyModal").classList.remove("hidden");
            document.getElementById("newKeyName").value = "";
            loadApiKeys(token); // Refresh list
        } else {
            alert("Failed to create key");
        }
    } catch (e) {
        alert("Error creating key");
    }
}

async function revokeApiKey(keyId) {
    if (!confirm("Are you sure? This cannot be undone.")) return;

    const token = localStorage.getItem('cael_auth_token');
    try {
        await fetch(apiUrl(`/api/v1/developer/keys/${keyId}`), {
            method: "DELETE",
            headers: { "Authorization": `Bearer ${token}` }
        });
        loadApiKeys(token);
    } catch (e) {
        alert("Error revoking key");
    }
}

function closeKeyModal() {
    document.getElementById("keyModal").classList.add("hidden");
}
window.loadDeveloperData = loadDeveloperData;
window.createApiKey = createApiKey;
window.revokeApiKey = revokeApiKey;
window.closeKeyModal = closeKeyModal;
const billingToggle = document.getElementById("billingToggle");
if (billingToggle) {
    billingToggle.addEventListener("change", function () {
        const isAnnual = this.checked;
        const period = isAnnual ? "/yr" : "/mo";

        // Update DOM classes for styling
        document.getElementById("monthlyLabel").classList.toggle("active", !isAnnual);
        document.getElementById("annualLabel").classList.toggle("active", isAnnual);

        // Update Prices
        // Starter: 29/mo -> 290/yr
        // Practitioner: 149/mo -> 1490/yr
        // (Values from seed script)

        if (isAnnual) {
            document.getElementById("price-starter").textContent = "290";
            document.getElementById("price-practitioner").textContent = "1490";
        } else {
            document.getElementById("price-starter").textContent = "29";
            document.getElementById("price-practitioner").textContent = "149";
        }

        document.getElementById("period-starter").textContent = period;
        document.getElementById("period-practitioner").textContent = period;
    });
}

const timeInput = document.getElementById("time");
const timeUnknownToggle = document.getElementById("timeUnknown");
const timeWarning = document.getElementById("timeWarning");
const zodiacSystemSelect = document.getElementById("zodiacSystem");
const ayanamsaGroup = document.getElementById("ayanamsaGroup");

function setTimeUnknownState(isUnknown) {
    if (timeWarning) timeWarning.classList.toggle("hidden", !isUnknown);
    if (timeInput) {
        timeInput.required = !isUnknown;
        if (isUnknown && !timeInput.value) {
            timeInput.value = "12:00";
        }
    }
}

if (timeUnknownToggle) {
    timeUnknownToggle.addEventListener("change", (e) => {
        setTimeUnknownState(e.target.checked);
    });
    setTimeUnknownState(timeUnknownToggle.checked);
}

function updateAyanamsaVisibility() {
    if (!zodiacSystemSelect || !ayanamsaGroup) return;
    const isSidereal = zodiacSystemSelect.value === "sidereal";
    ayanamsaGroup.style.display = isSidereal ? "flex" : "none";
}

if (zodiacSystemSelect) {
    zodiacSystemSelect.addEventListener("change", updateAyanamsaVisibility);
    updateAyanamsaVisibility();
}

const LOG_ENABLED = !IS_GH_PAGES || API_BASE;
const LOG_SESSION_KEY = "cael_session_id";
let _sessionEnded = false;
const _sessionStart = Date.now();

function getSessionId() {
    try {
        const existing = localStorage.getItem(LOG_SESSION_KEY);
        if (existing) return existing;
        const id = (typeof crypto !== "undefined" && crypto.randomUUID) ? crypto.randomUUID() : `sess_${Math.random().toString(36).slice(2)}`;
        localStorage.setItem(LOG_SESSION_KEY, id);
        return id;
    } catch (err) {
        return `sess_${Math.random().toString(36).slice(2)}`;
    }
}

const SESSION_ID = getSessionId();

function logEvent(eventType, payload = {}, options = {}) {
    if (!LOG_ENABLED) return;
    const body = {
        session_id: SESSION_ID,
        event_type: eventType,
        payload,
        ts: new Date().toISOString()
    };
    const url = apiUrl("/api/v1/log/telemetry");
    if (options.beacon && navigator.sendBeacon) {
        try {
            const blob = new Blob([JSON.stringify(body)], { type: "application/json" });
            navigator.sendBeacon(url, blob);
            return;
        } catch (err) {
            // Fallback to fetch
        }
    }
    fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
        keepalive: !!options.beacon
    }).catch(() => { });
}

function endSession(reason) {
    if (_sessionEnded) return;
    _sessionEnded = true;
    const durationMs = Date.now() - _sessionStart;
    logEvent("session_end", { duration_ms: durationMs, reason }, { beacon: true });
}

logEvent("page_view", { path: window.location.pathname, referrer: document.referrer || null });
window.addEventListener("beforeunload", () => endSession("unload"));
document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "hidden") endSession("hidden");
});

function formatLongitude(lon) {
    let signIdx = Math.floor(lon / 30) % 12;
    let degree = lon % 30;
    let d = Math.floor(degree);
    let m = Math.floor((degree - d) * 60);
    return `${d}° ${SIGNS[signIdx]} ${m}'`;
}

function escapeHtml(value) {
    return String(value || "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
}

function formatPlainReading(text) {
    const safe = escapeHtml(text);
    const paragraphs = safe.split(/\n{2,}/).map(p => p.trim()).filter(Boolean);
    if (!paragraphs.length) return "";
    return paragraphs.map(p => `<p>${p.replace(/\n/g, "<br>")}</p>`).join("");
}

function hashString(value) {
    let hash = 5381;
    const str = String(value || "");
    for (let i = 0; i < str.length; i++) {
        hash = ((hash << 5) + hash) + str.charCodeAt(i);
        hash |= 0;
    }
    return `djb2_${Math.abs(hash)}`;
}

// Set default analysis date to today
document.getElementById('analysisDate').value = new Date().toISOString().split('T')[0];

function setLocalDateTime(dateId, timeId) {
    const now = new Date();
    const pad = (v) => String(v).padStart(2, '0');
    const dateVal = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`;
    const timeVal = `${pad(now.getHours())}:${pad(now.getMinutes())}`;
    const dateEl = document.getElementById(dateId);
    const timeEl = document.getElementById(timeId);
    if (dateEl) dateEl.value = dateVal;
    if (timeEl) timeEl.value = timeVal;
}

function setUtcDateTime(dateId, timeId) {
    const iso = new Date().toISOString();
    const dateVal = iso.slice(0, 10);
    const timeVal = iso.slice(11, 16);
    const dateEl = document.getElementById(dateId);
    const timeEl = document.getElementById(timeId);
    if (dateEl) dateEl.value = dateVal;
    if (timeEl) timeEl.value = timeVal;
}

setLocalDateTime('horaryDate', 'horaryTime');
setUtcDateTime('worldDate', 'worldTime');
setUtcDateTime('kairosStartDate');

// Tab Logic
function setActiveTab(btn, allButtons, allPanels, datasetKey, panelSuffix) {
    allButtons.forEach((b) => {
        const isActive = b === btn;
        b.classList.toggle('active', isActive);
        b.setAttribute('aria-selected', isActive ? 'true' : 'false');
        b.setAttribute('tabindex', isActive ? '0' : '-1');
    });
    allPanels.forEach((panel) => panel.classList.remove('active'));
    const targetPanel = document.getElementById(btn.dataset[datasetKey] + panelSuffix);
    if (targetPanel) targetPanel.classList.add('active');
}

const resultTabs = Array.from(document.querySelectorAll('.tab-btn'));
const resultPanels = Array.from(document.querySelectorAll('.tab-content'));
const activeResultTab = resultTabs.find((btn) => btn.classList.contains('active'));
if (activeResultTab) {
    setActiveTab(activeResultTab, resultTabs, resultPanels, 'tab', 'Tab');
}
resultTabs.forEach(btn => {
    btn.addEventListener('click', () => {
        setActiveTab(btn, resultTabs, resultPanels, 'tab', 'Tab');
        logEvent("tab_change", { tab: btn.dataset.tab });
    });
});

document.getElementById('chartForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const btn = document.getElementById('calculateBtn');
    const originalText = btn.querySelector('.btn-text').textContent;
    btn.querySelector('.btn-text').textContent = "RUNNING ANALYSIS...";
    btn.disabled = true;

    const isTimeUnknown = timeUnknownToggle ? timeUnknownToggle.checked : false;
    const timeValue = timeInput ? timeInput.value : "";
    const houseSystemInput = document.getElementById('houseSystem');
    const compareHouseSystemsInput = document.getElementById('compareHouseSystems');
    const ayanamsaSelect = document.getElementById('ayanamsa');
    const timeRangeStartInput = document.getElementById('timeRangeStart');
    const timeRangeEndInput = document.getElementById('timeRangeEnd');
    const timeRangeSamplesInput = document.getElementById('timeRangeSamples');

    // Auth Token
    const token = localStorage.getItem('cael_auth_token');

    const formData = {
        date: document.getElementById('date').value,
        time: isTimeUnknown && !timeValue ? "12:00" : timeValue,
        city: document.getElementById('city').value,
        state: document.getElementById('state').value,
        age: document.getElementById('currentAge').value ? parseInt(document.getElementById('currentAge').value) : null,
        analysis_date: document.getElementById('analysisDate').value || null,
        house_system: houseSystemInput ? houseSystemInput.value : null,
        compare_house_systems: compareHouseSystemsInput ? compareHouseSystemsInput.checked : false,
        zodiac_system: zodiacSystemSelect ? zodiacSystemSelect.value : null,
        ayanamsa: ayanamsaSelect ? ayanamsaSelect.value : null,
        time_range_start: timeRangeStartInput && timeRangeStartInput.value ? timeRangeStartInput.value : null,
        time_range_end: timeRangeEndInput && timeRangeEndInput.value ? timeRangeEndInput.value : null,
        time_range_samples: timeRangeSamplesInput && timeRangeSamplesInput.value ? parseInt(timeRangeSamplesInput.value, 10) : null,
        access_token: token || null // Send token if logged in
    };

    logEvent("chart_request", { form: formData });

    try {
        const response = await fetch(apiUrl('/api/v1/calculate'), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'No response from engine.');
        }

        const result = await response.json();
        logEvent("chart_result", { result });
        renderResults(result);

    } catch (error) {
        logEvent("chart_error", { message: error.message || String(error) });
        alert(error.message);
    } finally {
        btn.querySelector('.btn-text').textContent = originalText;
        btn.disabled = false;
    }
});

const exportCsvBtn = document.getElementById("exportCsvBtn");
if (exportCsvBtn) {
    exportCsvBtn.addEventListener("click", async () => {
        if (!currentResult || !currentResult.forensic_report) {
            alert("No analysis result to export.");
            return;
        }

        try {
            const resp = await fetch(apiUrl("/api/v1/export"), {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ forensic_report: currentResult.forensic_report })
            });
            if (!resp.ok) throw new Error("Export failed");

            const blob = await resp.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = "astrology_export.csv";
            document.body.appendChild(a);
            a.click();
            a.remove();
        } catch (err) {
            alert("Export error: " + err.message);
        }
    });
}

const exportPdfBtn = document.getElementById("exportPdfBtn");
if (exportPdfBtn) {
    exportPdfBtn.addEventListener("click", async () => {
        if (!currentResult) {
            alert("No analysis result to export.");
            return;
        }

        try {
            exportPdfBtn.textContent = "GENERATING PDF...";
            exportPdfBtn.disabled = true;

            const payload = { ...currentResult, format: "pdf" };
            const resp = await fetch(apiUrl("/api/v1/export"), {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            if (!resp.ok) throw new Error("PDF Generation failed");

            const blob = await resp.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = "codex_caelestis_report.pdf";
            document.body.appendChild(a);
            a.click();
            a.remove();
        } catch (err) {
            alert("Export error: " + err.message);
        } finally {
            exportPdfBtn.textContent = "EXPORT AS PDF";
            exportPdfBtn.disabled = false;
        }
    });
}

// City Autocomplete
const cityInput = document.getElementById('city');
const suggestionsBox = document.getElementById('citySuggestions');
let debounceTimer;

cityInput.addEventListener('input', () => {
    clearTimeout(debounceTimer);
    const query = cityInput.value;
    if (query.length < 3) {
        suggestionsBox.style.display = 'none';
        if (cityInput) cityInput.setAttribute('aria-expanded', 'false');
        return;
    }

    debounceTimer = setTimeout(async () => {
        try {
            const resp = await fetch(`https://photon.komoot.io/api/?q=${encodeURIComponent(query)}&limit=5&osm_tag=place:city&osm_tag=place:town`);
            if (!resp.ok) return;
            const data = await resp.json();
            renderSuggestions(data.features || []);
        } catch (err) {
            // Silent fail - autocomplete is non-critical
        }
    }, 300);
});

function renderSuggestions(features) {
    suggestionsBox.innerHTML = '';
    if (!features || features.length === 0) {
        suggestionsBox.style.display = 'none';
        if (cityInput) cityInput.setAttribute('aria-expanded', 'false');
        return;
    }

    features.forEach((f, index) => {
        const item = document.createElement('div');
        item.className = 'suggestion-item';
        item.setAttribute('role', 'option');
        item.id = `city-option-${index}`;
        const city = f.properties.name;
        const state = f.properties.state || f.properties.country;
        item.textContent = `${city}, ${state}`;
        item.onclick = () => {
            cityInput.value = city;
            document.getElementById('state').value = state;
            suggestionsBox.style.display = 'none';
            if (cityInput) cityInput.setAttribute('aria-expanded', 'false');
        };
        suggestionsBox.appendChild(item);
    });
    suggestionsBox.style.display = 'block';
    if (cityInput) cityInput.setAttribute('aria-expanded', 'true');
}

document.addEventListener('click', (e) => {
    if (e.target !== cityInput) {
        suggestionsBox.style.display = 'none';
        if (cityInput) cityInput.setAttribute('aria-expanded', 'false');
    }
});

const oracleContent = document.getElementById('oracleContent');
let oracleFeedbackContext = null;

function resetOracleFeedback(context) {
    oracleFeedbackContext = context || null;
    if (!oracleContent) return;
    const feedback = oracleContent.querySelector('.reading-feedback');
    if (!feedback) return;
    feedback.classList.toggle('hidden', !oracleFeedbackContext);
    feedback.querySelectorAll('.feedback-btn').forEach((btn) => {
        btn.disabled = false;
        btn.classList.remove('selected');
    });
    const status = feedback.querySelector('.feedback-status');
    if (status) status.textContent = '';
    delete feedback.dataset.submitted;
}

if (oracleContent) {
    oracleContent.addEventListener('click', (e) => {
        const btn = e.target.closest('.feedback-btn');
        if (!btn || !oracleFeedbackContext) return;
        const feedback = btn.closest('.reading-feedback');
        if (!feedback || feedback.dataset.submitted === 'true') return;
        const vote = btn.dataset.vote;
        if (!vote) return;

        feedback.dataset.submitted = 'true';
        feedback.querySelectorAll('.feedback-btn').forEach((b) => {
            b.disabled = true;
            b.classList.toggle('selected', b === btn);
        });
        const status = feedback.querySelector('.feedback-status');
        if (status) status.textContent = 'Saving vote...';

        logEvent("reading_feedback", {
            vote,
            source: "plain_reading",
            reading_hash: oracleFeedbackContext.reading_hash,
            birth: oracleFeedbackContext.birth,
            meta: oracleFeedbackContext.meta
        });

        fetch(apiUrl("/api/v1/reading_feedback"), {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                reading_hash: oracleFeedbackContext.reading_hash,
                vote,
                source: "plain_reading",
                birth: oracleFeedbackContext.birth,
                meta: oracleFeedbackContext.meta,
                session_id: SESSION_ID,
                ts: new Date().toISOString()
            })
        }).then(async (resp) => {
            if (!resp.ok) throw new Error("Vote not saved.");
            return resp.json();
        }).then((data) => {
            const counts = data && data.counts ? data.counts : null;
            if (status && counts) {
                status.textContent = `Total votes: ${counts.total} (${counts.up} up / ${counts.down} down)`;
            } else if (status) {
                status.textContent = "Vote saved.";
            }
        }).catch(() => {
            if (status) status.textContent = "Vote recorded. Totals unavailable.";
        });
    });
}

function renderResults(data) {
    const resultsSection = document.getElementById('results');
    resultsSection.classList.remove('results-hidden');

    // 0. Chart Wheel
    renderChartWheel(data);

    // 1. Mundane Context
    const mundaneDiv = document.getElementById('mundaneContext');
    let mundaneHTML = "";
    if (data.forensic_report) {
        let events = data.forensic_report.summary.universal_events.map(e => `[${e.type} in ${e.sign}]`).join(' ');
        let summary = data.forensic_report.summary;
        let dominant = summary.dominant_elements && summary.dominant_elements.length ? summary.dominant_elements[0][0] : 'Unknown';
        mundaneHTML = `
            <div style="display: flex; gap: 2rem; flex-wrap: wrap;">
                <div><strong>LUNAR PHASE:</strong> ${summary.lunar_phase}</div>
                <div><strong>JONES PATTERN:</strong> ${summary.jones_pattern}</div>
                <div><strong>DOMINANT:</strong> ${dominant}</div>
                ${events ? `<div><strong>ECLIPSE:</strong> ${events}</div>` : ''}
            </div>
        `;
        mundaneDiv.innerHTML = mundaneHTML;
        mundaneDiv.style.display = 'block';
    } else {
        mundaneDiv.style.display = 'none';
    }

    renderSummaryExtras(data);
    renderRuleLedger(data);

    // 1a. Soul Guardian
    renderSoulGuardian(data);
    renderVitality(data);
    renderMutualReceptions(data);
    renderPrimaryDirections(data);

    // 1c. Hermetic Lots / Celestial Curia
    renderLots(data);
    renderCelestialWitnesses(data);

    // 1b. Horary Physics / Interactions
    const horarySection = document.getElementById('horaryPhysicsSection');
    const horaryList = document.getElementById('horaryPhysicsList');
    if (data.forensic_report && data.forensic_report.horary_physics) {
        const hp = data.forensic_report.horary_physics;
        horarySection.classList.remove('hidden');
        horaryList.innerHTML = `
            <div class="horary-summary">
                <strong>Significators:</strong> ${hp.significators}
            </div>
            ${hp.interactions.map(i => `
                <div class="horary-item">
                    <span class="horary-condition">${i.condition}</span>
                    <span class="horary-details">${i.details || i.aspect || ''}</span>
                    <span class="horary-status ${i.status.toLowerCase()}">${i.status}</span>
                </div>
            `).join('')}
        `;
        if (hp.interactions.length === 0) {
            horaryList.innerHTML += '<p class="text-muted">No shadow interactions detected between primary significators.</p>';
        }
    } else {
        horarySection.classList.add('hidden');
    }


    // 2. Forensic Grid
    const forensicGrid = document.getElementById('forensicGrid');
    forensicGrid.innerHTML = '';

    if (data.forensic_report) {
        data.forensic_report.planets.forEach(p => {
            const card = document.createElement('div');
            card.className = 'planet-card';

            const pLabel = (p.power_label || "Commoner").toLowerCase();
            const badgeClass = (pLabel.includes('imperial') || pLabel.includes('sovereign')) ? 'badge-sovereign' :
                (pLabel.includes('vagabond') || pLabel.includes('cursed') || pLabel.includes('debilitated')) ? 'badge-corrupt' : 'badge-common';

            let impactsHTML = p.impacts.map(i => `
                <div class="impact-rule">
                    <div class="rule-if">IF ${i.cause}</div>
                    <div class="rule-then">THEN ${i.effect}</div>
                </div>
            `).join('');

            const variantNotes = (p.dignity_conflicts && p.dignity_conflicts.length)
                ? `<div class="variant-note"><strong>Variants:</strong> ${p.dignity_conflicts.join(' | ')}</div>`
                : '';

            const perfIdx = p.performance_index !== undefined ? p.performance_index : 0.5;
            const perfPercent = Math.round(perfIdx * 100);

            card.innerHTML = `
                <div class="card-header">
                    <h3>${p.planet}</h3>
                    <span class="badge ${badgeClass}">${p.power_label}</span>
                </div>
                <div class="card-body">
                    <div class="performance-gauge">
                        <div class="gauge-bar"><span style="width: ${perfPercent}%; background: ${perfIdx > 0.6 ? 'var(--success)' : perfIdx > 0.4 ? 'var(--gold)' : 'var(--danger)'};"></span></div>
                        <div class="gauge-label">PERFORMANCE INDEX: ${perfPercent}%</div>
                    </div>
                    <p><strong>Status:</strong> ${p.sect_status}</p>
                    <p><strong>Position:</strong> ${formatLongitude(p.longitude)}</p>
                    ${p.house_number ? `<p><strong>House:</strong> ${p.house_number}</p>` : ''}
                    <p class="planet-meta"><strong>Solar:</strong> ${p.solar_status || 'UNKNOWN'} | <strong>Medical:</strong> ${p.medical_region || 'Unknown'}</p>
                    ${p.medical_pathology ? `<p class="planet-meta">${p.medical_pathology}</p>` : ''}
                    ${variantNotes}
                    ${impactsHTML}
                    <div class="delineation-snippet">${p.delineation_text}</div>
                </div>
                <div class="card-footer">
                    <button class="view-details" onclick='showDetails(${JSON.stringify(p).replace(/'/g, "&apos;")})'>VIEW RULES</button>
                </div>
            `;
            forensicGrid.appendChild(card);
        });
    }

    // 3. Technical Data
    const analysisJd = data.meta.analysis_jd || data.meta.julian_day;
    const houseSystemMeta = (data.meta && data.meta.house_system) ? data.meta.house_system : null;
    const houseLabel = houseSystemMeta ? `${houseSystemMeta.label} (${houseSystemMeta.code})` : 'Placidus (P)';
    const compareFlag = data.meta && data.meta.compare_house_systems ? 'ON' : 'OFF';
    const zodiacMeta = data.meta && data.meta.zodiac_system ? data.meta.zodiac_system : null;
    const zodiacLabel = zodiacMeta ? escapeHtml(zodiacMeta.label) : 'Tropical';
    const ayanamsaMeta = zodiacMeta && zodiacMeta.ayanamsa ? zodiacMeta.ayanamsa : null;
    const ayanamsaLabel = ayanamsaMeta && ayanamsaMeta.label ? escapeHtml(ayanamsaMeta.label) : null;
    const ayanamsaDeg = ayanamsaMeta && typeof ayanamsaMeta.degrees === 'number'
        ? ayanamsaMeta.degrees.toFixed(4)
        : null;
    const tzAbbrev = data.meta.tz_abbrev ? ` (${data.meta.tz_abbrev})` : '';
    const tzOffsets = (typeof data.meta.utc_offset_hours === 'number')
        ? `UTC ${data.meta.utc_offset_hours >= 0 ? '+' : ''}${data.meta.utc_offset_hours}h` + (typeof data.meta.dst_offset_hours === 'number' ? ` | DST ${data.meta.dst_offset_hours}h` : '')
        : '';
    const tzNote = data.meta.tz_warning ? `<p class="meta-warning">${escapeHtml(data.meta.tz_warning)}</p>` : '';
    document.getElementById('metaInfo').innerHTML = `
        <p><strong>JULIAN DAY:</strong> ${data.meta.julian_day.toFixed(2)}</p>
        <p><strong>ANALYSIS JD:</strong> ${analysisJd.toFixed(2)}</p>
        <p><strong>UTC:</strong> ${data.meta.utc_time || 'Unknown'}</p>
        <p><strong>LATITUDE:</strong> ${data.meta.lat.toFixed(4)} | <strong>LONGITUDE:</strong> ${data.meta.lon.toFixed(4)}</p>
        <p><strong>TIMEZONE:</strong> ${data.meta.timezone}${tzAbbrev}</p>
        ${tzOffsets ? `<p><strong>OFFSET:</strong> ${tzOffsets}</p>` : ''}
        <p><strong>ZODIAC:</strong> ${zodiacLabel}${ayanamsaLabel ? ` | <strong>AYANAMSA:</strong> ${ayanamsaLabel}${ayanamsaDeg ? ` (${ayanamsaDeg}°)` : ''}` : ''}</p>
        <p><strong>HOUSE SYSTEM:</strong> ${houseLabel} | <strong>COMPARE:</strong> ${compareFlag}</p>
        ${tzNote}
    `;

    if (data.angles) {
        const nn = data.planets && data.planets.North_Node ? formatLongitude(data.planets.North_Node.longitude) : 'Unknown';
        const sn = data.planets && data.planets.South_Node ? formatLongitude(data.planets.South_Node.longitude) : 'Unknown';
        document.getElementById('anglesInfo').innerHTML = `
            <p><strong>ASCENDANT:</strong> ${formatLongitude(data.angles.Ascendant)}</p>
            <p><strong>MIDHEAVEN:</strong> ${formatLongitude(data.angles.MC)}</p>
            <p><strong>NORTH NODE:</strong> ${nn}</p>
            <p><strong>SOUTH NODE:</strong> ${sn}</p>
        `;
    } else {
        document.getElementById('anglesInfo').innerHTML = '<p class="placeholder-text">Angles unavailable.</p>';
    }

    // Planets
    let planetHTML = '';
    for (const [name, info] of Object.entries(data.planets)) {
        planetHTML += `
            <div class="item-row">
                <span class="chart-item-name">${name.toUpperCase()}</span>
                <span class="chart-item-val">${formatLongitude(info.longitude)} ${info.is_retrograde ? '(R)' : ''}</span>
            </div>
        `;
    }
    document.getElementById('planetList').innerHTML = planetHTML;

    // Houses
    let houseHTML = '';
    const sortedHouses = Object.entries(data.houses).sort((a, b) => parseInt(a[0]) - parseInt(b[0]));
    for (const [num, lon] of sortedHouses) {
        houseHTML += `
            <div class="item-row">
                <span class="chart-item-name">HOUSE ${num}</span>
                <span class="chart-item-val">${formatLongitude(lon)}</span>
            </div>
        `;
    }
    document.getElementById('houseList').innerHTML = houseHTML;
    renderHouseSystemsComparison(data);
    renderTimeSensitivity(data);
    renderTimeDistribution(data);

    // 4. Prediction
    renderPrediction(data);
    renderAdvancedPrediction(data);

    // 5. Forecast
    renderForecast(data);

    // 6. Medical Check
    initMedicalCheck(data);

    // 7. Daily Output
    renderOracle(data);

    // 8. Fate Timeline
    currentResult = data;
    renderFateTimeline(data, currentLot);

    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function renderHouseSystemsComparison(data) {
    const container = document.getElementById('houseSystemsCompare');
    if (!container) return;

    const housesBySystem = data.houses_by_system || {};
    const errors = data.houses_by_system_errors || {};
    const labels = Object.keys(housesBySystem);
    const errorLabels = Object.keys(errors);

    if (!labels.length && !errorLabels.length) {
        container.innerHTML = '<p class="placeholder-text">Enable "Compare house systems" to see alternative cusps.</p>';
        return;
    }

    const preferredLabel = data.meta && data.meta.house_system ? data.meta.house_system.label : null;
    const orderedLabels = labels.slice().sort((a, b) => {
        if (preferredLabel) {
            if (a === preferredLabel) return -1;
            if (b === preferredLabel) return 1;
        }
        return a.localeCompare(b);
    });

    const cards = [];
    orderedLabels.forEach((label) => {
        const cusps = housesBySystem[label];
        const safeLabel = escapeHtml(label);
        const sortedCusps = Object.entries(cusps || {}).sort((a, b) => parseInt(a[0], 10) - parseInt(b[0], 10));
        const rows = sortedCusps.map(([num, lon]) => `
            <div class="house-system-row">
                <span>H${num}</span>
                <span>${formatLongitude(lon)}</span>
            </div>
        `).join('');
        cards.push(`
            <div class="house-system-card">
                <div class="house-system-title">${safeLabel}</div>
                <div class="house-system-cusps">${rows}</div>
            </div>
        `);
    });

    errorLabels.forEach((label) => {
        const safeLabel = escapeHtml(label);
        cards.push(`
            <div class="house-system-card error">
                <div class="house-system-title">${safeLabel}</div>
                <div class="house-system-error">${escapeHtml(errors[label])}</div>
            </div>
        `);
    });

    container.innerHTML = cards.join('');
}

function renderTimeSensitivity(data) {
    const container = document.getElementById('timeSensitivity');
    if (!container) return;

    const sensitivity = data.time_sensitivity;
    if (!sensitivity) {
        container.innerHTML = '<p class="placeholder-text">Add a time range to see sensitivity analysis.</p>';
        return;
    }

    if (sensitivity.error) {
        container.innerHTML = `<p class="placeholder-text">${escapeHtml(sensitivity.error)}</p>`;
        return;
    }

    const range = sensitivity.range || {};
    const deltas = sensitivity.deltas || {};
    const houseDeltas = deltas.houses || {};
    const sortedHouses = Object.entries(houseDeltas)
        .sort((a, b) => (b[1] || 0) - (a[1] || 0))
        .slice(0, 4)
        .map(([num, diff]) => `H${num}: ${diff}°`);

    const warning = range.warning ? `<div class="time-sensitivity-warning">${escapeHtml(range.warning)}</div>` : '';
    const signFlag = (sensitivity.asc_sign_change || sensitivity.mc_sign_change)
        ? `<div class="time-sensitivity-flag">Sign changes detected in the range.</div>`
        : '';

    container.innerHTML = `
        <div class="time-sensitivity-card">
            <div class="time-sensitivity-title">Time Range</div>
            <div class="time-sensitivity-detail"><strong>Start:</strong> ${escapeHtml(range.start || '')}</div>
            <div class="time-sensitivity-detail"><strong>End:</strong> ${escapeHtml(range.end || '')}</div>
            ${range.minutes !== undefined ? `<div class="time-sensitivity-detail"><strong>Duration:</strong> ${range.minutes} minutes</div>` : ''}
            ${warning}
        </div>
        <div class="time-sensitivity-card">
            <div class="time-sensitivity-title">Key Shifts (°)</div>
            <div class="time-sensitivity-detail">Ascendant: ${deltas.asc ?? '—'}</div>
            <div class="time-sensitivity-detail">Midheaven: ${deltas.mc ?? '—'}</div>
            <div class="time-sensitivity-detail">Moon: ${deltas.moon ?? '—'}</div>
            <div class="time-sensitivity-detail">Sun: ${deltas.sun ?? '—'}</div>
            ${sortedHouses.length ? `<div class="time-sensitivity-detail">Largest house shifts: ${sortedHouses.join(' | ')}</div>` : ''}
            ${signFlag}
        </div>
    `;
}

function renderTimeDistribution(data) {
    const container = document.getElementById('timeDistribution');
    if (!container) return;
    const dist = data.time_range_distribution;
    if (!dist) {
        container.innerHTML = '';
        return;
    }
    if (dist.error) {
        container.innerHTML = `<p class="placeholder-text">${escapeHtml(dist.error)}</p>`;
        return;
    }

    const summary = `
        <div class="time-distribution-summary">
            <strong>Samples:</strong> ${dist.samples || '—'} | <strong>Step:</strong> ${dist.step_minutes || '—'} min
        </div>
    `;

    const cards = [];
    const buildCard = (title, entries) => {
        if (!entries || !entries.length) return '';
        const rows = entries.map(e => `
            <div class="dist-row">
                <span>${escapeHtml(e.label)}</span>
                <span>${e.percent}%</span>
            </div>
            <div class="dist-bar"><span style="width:${e.percent}%;"></span></div>
        `).join('');
        return `
            <div class="time-sensitivity-card dist-card">
                <div class="time-sensitivity-title">${escapeHtml(title)}</div>
                ${rows}
            </div>
        `;
    };

    cards.push(buildCard('Ascendant Sign', dist.asc_sign));
    cards.push(buildCard('Midheaven Sign', dist.mc_sign));
    cards.push(buildCard('Moon Sign', dist.moon_sign));
    cards.push(buildCard('Sun House', dist.sun_house));
    cards.push(buildCard('Moon House', dist.moon_house));

    container.innerHTML = `${summary}<div class="time-distribution-grid">${cards.filter(Boolean).join('')}</div>`;
}

function renderSummaryExtras(data) {
    const lunarCard = document.getElementById('lunarProfileCard');
    const temperamentCard = document.getElementById('temperamentCard');
    const eventsCard = document.getElementById('universalEventsCard');
    const causeCard = document.getElementById('universalCausationCard');

    if (!data.forensic_report || !data.forensic_report.summary) {
        if (lunarCard) lunarCard.innerHTML = `<h4>LUNAR PHASE</h4><p class="placeholder-text">No summary available.</p>`;
        if (temperamentCard) temperamentCard.innerHTML = `<h4>TEMPERAMENT</h4><p class="placeholder-text">No summary available.</p>`;
        if (eventsCard) eventsCard.innerHTML = `<h4>ECLIPSE EVENTS</h4><p class="placeholder-text">No summary available.</p>`;
        if (causeCard) causeCard.innerHTML = `<h4>GLOBAL CAUSATION</h4><p class="placeholder-text">No summary available.</p>`;
        return;
    }

    const summary = data.forensic_report.summary;

    if (lunarCard) {
        let mansionHTML = '';
        if (summary.lunar_mansion) {
            const m = summary.lunar_mansion;
            mansionHTML = `
                <div style="margin-top: 0.5rem; padding-top: 0.5rem; border-top: 1px solid rgba(255,255,255,0.1);">
                    <div style="color: var(--gold); font-weight: bold; font-family: 'Space Mono', monospace;">MANSION ${m.mansion_id}: ${m.name.toUpperCase()}</div>
                    <div style="font-size: 0.8em; margin-top: 0.3rem;">
                         <span style="color: var(--success);">FOR:</span> ${m.intents_good.slice(0, 3).join(', ')}
                    </div>
                    <div style="font-size: 0.8em; margin-top: 0.1rem;">
                         <span style="color: var(--danger);">AVOID:</span> ${m.intents_bad.slice(0, 3).join(', ')}
                    </div>
                </div>
             `;
        }

        lunarCard.innerHTML = `
            <h4>LUNAR PHASE</h4>
            <div class="summary-list">
                <div><strong>YOU ARE IN:</strong> ${summary.lunar_phase}</div>
                <div style="margin-bottom: 0.2rem;">${summary.lunar_phase_profile || 'Profile unavailable.'}</div>
                ${mansionHTML}
            </div>
        `;
    }

    if (temperamentCard) {
        if (summary.temperament) {
            const t = summary.temperament;
            const scores = t.scores || {};
            const net = t.net_balance || {};
            const scoreLine = (Object.keys(scores).length)
                ? `<div><strong>Total:</strong> Hot ${scores.Hot ?? 0}, Cold ${scores.Cold ?? 0}, Moist ${scores.Moist ?? 0}, Dry ${scores.Dry ?? 0}</div>`
                : '';
            const netLine = (Object.keys(net).length)
                ? `<div><strong>Net:</strong> Hot/Cold ${net.Hot_vs_Cold ?? 0}, Moist/Dry ${net.Moist_vs_Dry ?? 0}</div>`
                : '';

            temperamentCard.innerHTML = `
                <h4>TEMPERAMENT</h4>
                <div style="font-size: 0.9em; margin-bottom: 0.5rem; text-transform: uppercase; color: var(--gold);">
                    <strong>YOU ARE: ${t.primary_temperament}</strong>
                </div>
                <div class="summary-list" style="margin-bottom: 0.5rem;">
                    ${scoreLine}
                    ${netLine}
                </div>
                <div class="summary-list" style="max-height: 120px; overflow-y: auto;">
                    ${(t.breakdown || []).map(b => `<div>- ${b}</div>`).join('')}
                </div>
            `;
        } else {
            // Fallback to elements if temperament fails
            const elements = summary.dominant_elements || [];
            temperamentCard.innerHTML = `
                <h4>TEMPERAMENT</h4>
                <div class="summary-list">
                    ${elements.length ? elements.map(([el, count]) => `<div><strong>${el}:</strong> ${count}</div>`).join('') : '<div>No data.</div>'}
                </div>
            `;
        }
    }

    if (eventsCard) {
        const events = summary.universal_events || [];
        eventsCard.innerHTML = `
            <h4>ECLIPSE EVENTS</h4>
            <div class="summary-list">
                ${events.length ? events.map(e => {
            const degree = typeof e.degree === 'number' ? `${e.degree.toFixed(2)}°` : '';
            const duration = typeof e.duration_hours === 'number' ? `${e.duration_hours.toFixed(1)}h` : '';
            return `<div><strong>${e.type}</strong> ${degree} ${e.sign} ${duration ? `(${duration})` : ''}</div>`;
        }).join('') : '<div>No eclipse activity detected.</div>'}
            </div>
        `;
    }

    if (causeCard) {
        const causes = summary.universal_causation_audit || [];
        causeCard.innerHTML = `
            <h4>GLOBAL CAUSATION</h4>
            <div class="summary-list">
                ${causes.length ? causes.map(c => `
                    <div class="summary-item">
                        <div><strong>${c.cause}</strong></div>
                        <div>${c.status}</div>
                        ${c.rule ? `<div>${c.rule}</div>` : ''}
                    </div>
                `).join('') : '<div>No active suspensions in the audit window.</div>'}
            </div>
        `;
    }
}

function renderRuleLedger(data) {
    const ledger = document.getElementById('ruleLedgerList');
    if (!ledger) return;

    const ledgerEntries = data.forensic_report && Array.isArray(data.forensic_report.rule_ledger)
        ? data.forensic_report.rule_ledger
        : [];

    if (!ledgerEntries.length) {
        const fallback = [];
        if (data.forensic_report && Array.isArray(data.forensic_report.planets)) {
            data.forensic_report.planets.forEach(p => {
                (p.impacts || []).forEach(i => {
                    fallback.push({
                        id: `${hashString(`${p.planet}-${i.cause}`)}`,
                        category: "Condition",
                        condition: `${p.planet}: ${i.cause}`,
                        judgment: i.effect,
                        sources: [],
                        confidence: null,
                        conflicts: [],
                        trace: []
                    });
                });
            });
        }
        if (!fallback.length) {
            ledger.innerHTML = '<p class="placeholder-text">Run analysis to generate rule trace.</p>';
            return;
        }
        ledger.innerHTML = fallback.slice(0, 20).map(r => `
            <div class="rule-entry">
                <div class="rule-entry-header">
                    <span class="rule-category">${escapeHtml(r.category)}</span>
                </div>
                <div class="rule-condition">${escapeHtml(r.condition)}</div>
                <div class="rule-judgment">${escapeHtml(r.judgment)}</div>
            </div>
        `).join('');
        return;
    }

    const confidenceLabel = (value) => {
        if (typeof value !== 'number') return { text: '—', className: 'confidence-unknown' };
        if (value >= 80) return { text: 'High', className: 'confidence-high' };
        if (value >= 60) return { text: 'Medium', className: 'confidence-medium' };
        return { text: 'Low', className: 'confidence-low' };
    };

    ledger.innerHTML = ledgerEntries.map(entry => {
        const confidenceInfo = confidenceLabel(entry.confidence);
        const confidenceVal = typeof entry.confidence === 'number' ? `${entry.confidence}%` : '—';
        const sources = Array.isArray(entry.sources) && entry.sources.length
            ? entry.sources.map(s => `<span class="rule-citation">${escapeHtml(s)}</span>`).join(' ')
            : '';
        const conflicts = Array.isArray(entry.conflicts) && entry.conflicts.length
            ? `<div class="rule-conflicts"><strong>Conflicts:</strong> ${entry.conflicts.map(c => escapeHtml(c)).join(' | ')}</div>`
            : '';
        const traceSteps = Array.isArray(entry.trace) && entry.trace.length
            ? `
                <details class="calc-trace">
                    <summary>Calculation trace</summary>
                    <div class="calc-trace-body">
                        ${entry.trace.map(t => `<div>${escapeHtml(t)}</div>`).join('')}
                    </div>
                </details>
            `
            : '';
        const sourceLine = sources ? `<div class="rule-sources">${sources}</div>` : '';

        return `
            <div class="rule-entry" data-rule-id="${escapeHtml(entry.id || '')}">
                <div class="rule-entry-header">
                    <span class="rule-category">${escapeHtml(entry.category || 'Rule')}</span>
                    <span class="rule-confidence ${confidenceInfo.className}">
                        ${confidenceInfo.text} • ${confidenceVal}
                    </span>
                </div>
                <div class="rule-condition">${escapeHtml(entry.condition || '')}</div>
                <div class="rule-judgment">${escapeHtml(entry.judgment || '')}</div>
                ${sourceLine}
                ${conflicts}
                ${traceSteps}
            </div>
        `;
    }).join('');
}

function renderLots(data) {
    const lotsGrid = document.getElementById('lotsGrid');
    if (!lotsGrid) return;

    if (!data.forensic_report || !data.forensic_report.lots) {
        lotsGrid.innerHTML = '<p class="placeholder-text">Lots will appear after calculation.</p>';
        return;
    }

    const lots = data.forensic_report.lots;
    const entries = Object.entries(lots).filter(([, val]) => typeof val === 'number');
    if (!entries.length) {
        lotsGrid.innerHTML = '<p class="placeholder-text">No lot data available.</p>';
        return;
    }

    lotsGrid.innerHTML = entries.map(([name, lon]) => {
        const signIdx = Math.floor(lon / 30) % 12;
        const sign = SIGNS[signIdx];
        return `
            <div class="lot-card">
                <div class="lot-name">${name}</div>
                <div class="lot-value">${formatLongitude(lon)}</div>
                <div class="lot-sign">${sign.toUpperCase()}</div>
            </div>
        `;
    }).join('');
}

function renderCelestialWitnesses(data) {
    const starList = document.getElementById('fixedStarList');
    const nodeList = document.getElementById('nodeList');

    if (starList) {
        const stars = data.forensic_report && data.forensic_report.stars ? data.forensic_report.stars : [];
        const meta = data.forensic_report && data.forensic_report.fixed_star_meta ? data.forensic_report.fixed_star_meta : null;
        const metaHTML = meta ? `
            <div class="witness-meta">
                <div><strong>Catalog:</strong> ${escapeHtml(meta.catalog)}</div>
                <div><strong>Epoch:</strong> ${escapeHtml(meta.epoch)}</div>
                <div><strong>Precession:</strong> ${escapeHtml(meta.precession)}</div>
            </div>
        ` : '';
        if (!stars.length) {
            starList.innerHTML = `${metaHTML}<p class="placeholder-text">No stellar contacts logged.</p>`;
        } else {
            starList.innerHTML = `${metaHTML}${stars.map(s => {
                const starName = s.star_name || s.star || 'Unknown Star';
                const planetName = s.planet_name || s.planet || 'Unknown';
                const contact = s.contact_type || 'Contact';
                const angle = s.angle ? ` (${s.angle})` : '';
                const message = s.message ? `<div>${s.message}</div>` : '';
                return `
                    <div class="witness-item">
                        <strong>${starName}</strong> ${contact} ${planetName}${angle}
                        ${message}
                    </div>
                `;
            }).join('')}`;
        }
    }

    if (nodeList) {
        const nodes = data.forensic_report && data.forensic_report.nodes ? data.forensic_report.nodes : [];
        if (!nodes.length) {
            nodeList.innerHTML = '<p class="placeholder-text">No nodal activations detected.</p>';
        } else {
            nodeList.innerHTML = nodes.map(n => `
                <div class="witness-item">
                    <strong>${n.planet_name}</strong> ${n.node_type} - ${n.metabolic_phase}
                    <div>${n.description}</div>
                </div>
            `).join('');
        }
    }
}

function renderAdvancedPrediction(data) {
    const firdariaDiv = document.getElementById('firdariaInfo');
    const munthaDiv = document.getElementById('munthaInfo');
    const solarReturnDiv = document.getElementById('solarReturnInfo');
    const solarArcDiv = document.getElementById('solarArcInfo');
    const lunarPhaseDiv = document.getElementById('lunarPhaseInfo');

    const adv = data.advanced_prediction;
    if (!adv) {
        const msg = data.advanced_prediction_error || 'Advanced timing unavailable.';
        const placeholder = `<p class="placeholder-text">${msg}</p>`;
        if (firdariaDiv) firdariaDiv.innerHTML = placeholder;
        if (munthaDiv) munthaDiv.innerHTML = '';
        if (solarReturnDiv) solarReturnDiv.innerHTML = placeholder;
        if (solarArcDiv) solarArcDiv.innerHTML = placeholder;
        if (lunarPhaseDiv) lunarPhaseDiv.innerHTML = placeholder;
        return;
    }

    if (firdariaDiv) {
        const f = adv.firdaria || {};
        if (f.error) {
            firdariaDiv.innerHTML = `<p class="placeholder-text">${f.error}</p>`;
        } else {
            firdariaDiv.innerHTML = `
                <div class="tool-result-detail"><strong>YOU ARE IN (MAJOR):</strong> ${f['Major Period']}</div>
                <div class="tool-result-detail"><strong>YOU ARE IN (SUB):</strong> ${f['Sub Period']}</div>
                <div class="tool-result-detail"><strong>MAJOR RANGE:</strong> ${f['Major Start']} to ${f['Major End']}</div>
                <div class="tool-result-detail"><strong>SUB RANGE:</strong> ${f['Sub Start']} to ${f['Sub End']}</div>
                <div class="tool-result-detail"><strong>CURRENT AGE:</strong> ${f['Current Age']}</div>
            `;
        }
    }

    if (munthaDiv) {
        const m = adv.muntha || {};
        munthaDiv.innerHTML = m.sign ? `
            <div class="tool-result-detail"><strong>YOU HAVE (MUNTHA):</strong> ${m.sign} (Age ${m.age})</div>
        ` : '<p class="placeholder-text">Muntha unavailable.</p>';
    }

    if (solarReturnDiv) {
        const sr = adv.solar_return_info || {};
        const natalSun = typeof sr.natal_sun_longitude === 'number' ? formatLongitude(sr.natal_sun_longitude) : 'Unknown';
        solarReturnDiv.innerHTML = sr.return_date ? `
            <div class="tool-result-detail"><strong>SOLAR RETURN:</strong> ${new Date(sr.return_date).toLocaleString()}</div>
            <div class="tool-result-detail"><strong>RETURN JD:</strong> ${sr.return_jd.toFixed ? sr.return_jd.toFixed(4) : sr.return_jd}</div>
            <div class="tool-result-detail"><strong>NATAL SUN:</strong> ${natalSun}</div>
        ` : '<p class="placeholder-text">Solar return unavailable.</p>';
    }

    if (solarArcDiv) {
        const arcs = adv.solar_arcs || [];
        solarArcDiv.innerHTML = arcs.length ? `
            ${arcs.map(a => `<div class="tool-result-detail"><strong>${a.planet}:</strong> ${formatLongitude(a.longitude)}</div>`).join('')}
        ` : '<p class="placeholder-text">Solar arcs unavailable.</p>';
    }

    if (lunarPhaseDiv) {
        const lp = adv.lunar_phase || {};
        lunarPhaseDiv.innerHTML = lp.name ? `
            <div class="tool-result-detail"><strong>LUNAR PHASE:</strong> ${lp.name} (${lp.type || 'Phase'})</div>
            <div class="tool-result-detail">${lp.profile || ''}</div>
        ` : '<p class="placeholder-text">Lunar phase profile unavailable.</p>';
    }

    const transitDiv = document.getElementById('transitInfo');
    if (transitDiv) {
        const transits = adv.transits || [];
        transitDiv.innerHTML = transits.length ? transits.map(t => `
            <div class="tool-result-detail"><strong>${t.transit}</strong> ${t.aspect} ${t.natal_planet} (${t.orb}°)</div>
        `).join('') : '<p class="placeholder-text">No major outer planet transits.</p>';
    }
}

let currentResult = null;
let currentLot = 'Spirit';


// Lot Selector Logic
document.querySelectorAll('.lot-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.lot-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentLot = btn.dataset.lot;
        if (currentResult) renderFateTimeline(currentResult, currentLot);
    });
});

function renderFateTimeline(data, lot) {
    const list = document.getElementById('fateTimelineList');
    const alert = document.getElementById('fateTimelineAlert');
    if (!data.forensic_report) {
        if (alert) {
            alert.innerHTML = `<p class="placeholder-text">Run analysis to calculate time windows.</p>`;
        }
        return;
    }

    const timelineData = lot === 'Spirit' ? data.forensic_report.fate_timeline_spirit : data.forensic_report.fate_timeline_fortune;

    if (!timelineData) {
        list.innerHTML = '<p class="placeholder-text">Time window data unavailable for this Lot.</p>';
        if (alert) {
            alert.innerHTML = `<p class="placeholder-text">No pivots detected for this Lot.</p>`;
        }
        return;
    }

    if (alert) {
        const pivots = [];
        timelineData.forEach(chapter => {
            chapter.paragraphs.forEach(p => {
                if (p.is_pivot) {
                    pivots.push({
                        status: p.status,
                        sign: p.sign,
                        date: p.start_date
                    });
                }
            });
        });

        pivots.sort((a, b) => new Date(`${a.date}T00:00:00`) - new Date(`${b.date}T00:00:00`));
        const today = new Date();
        const nextPivot = pivots.find(p => new Date(`${p.date}T00:00:00`) >= today);
        const pivot = nextPivot || pivots[pivots.length - 1];

        if (pivot) {
            const label = pivot.status === 'Loosing of the Bond' ? 'LOOSING OF THE BOND' : 'FORESHADOWING';
            const tense = nextPivot ? 'On' : 'Most recent';
            alert.innerHTML = `
                <strong>${label}</strong>
                <div>${tense} ${pivot.date}: ${pivot.sign} pivot begins.</div>
            `;
        } else {
            alert.innerHTML = `<p class="placeholder-text">No pivots detected for this Lot.</p>`;
        }
    }

    const now = new Date();
    const nowStr = now.toISOString().split('T')[0];

    list.innerHTML = timelineData.map(chapter => `
        <div class="chapter-block">
            <div class="chapter-header">
                <div class="chapter-title">
                    PERIOD IN ${chapter.sign.toUpperCase()}
                    <span class="chapter-years">${chapter.duration_years} YEARS</span>
                </div>
                <div class="p-dates">${chapter.start_date} to ${chapter.end_date}</div>
            </div>
            <div class="paragraphs-grid">
                ${chapter.paragraphs.map(p => {
        const isActive = nowStr >= p.start_date && nowStr < p.end_date;
        const isLB = p.status === 'Loosing of the Bond';
        const isFore = p.status === 'Foreshadowing';

        return `
                        <div class="paragraph-card ${p.is_pivot ? (isLB ? 'pivot-lb' : 'pivot') : ''}">
                            ${isActive ? '<div class="active-p">PRESENT</div>' : ''}
                            <span class="p-sign">${p.sign}</span>
                            <span class="p-dates">${p.start_date} - ${p.end_date}</span>
                            ${p.status !== 'Normal' ? `<div class="p-status ${isLB ? 'lb' : 'foreshadowing'}">${p.status.toUpperCase()}</div>` : ''}
                        </div>
                    `;
    }).join('')}
            </div>
        </div>
    `).join('');
}

function renderOracle(data) {
    const div = document.getElementById('oracleContent');
    const plainReading = data.plain_reading || (data.forensic_report ? data.forensic_report.plain_reading : null);
    const daily = data.forensic_report ? data.forensic_report.daily_oracle : null;

    if (!plainReading && !daily) {
        div.innerHTML = `<p class="placeholder-text">Run a full nativity to generate a reading.</p>`;
        resetOracleFeedback(null);
        return;
    }

    const feedbackHTML = plainReading ? `
        <div class="reading-feedback">
            <div class="feedback-question">Does this feel accurate?</div>
            <div class="feedback-actions">
                <button type="button" class="feedback-btn" data-vote="up" aria-label="Thumbs up">
                    &#128077;
                </button>
                <button type="button" class="feedback-btn" data-vote="down" aria-label="Thumbs down">
                    &#128078;
                </button>
            </div>
            <div class="feedback-status"></div>
        </div>
    ` : '';

    const plainHTML = plainReading ? `
        <div class="oracle-plain-section">
            <div class="oracle-section-title">PLAIN READING</div>
            <div class="oracle-plain-body">${formatPlainReading(plainReading)}</div>
            ${feedbackHTML}
        </div>
    ` : '';

    const dailyTrace = daily && daily.calculation_steps ? `
        <details class="calc-trace">
            <summary>Daily calculation trace</summary>
            <div class="calc-trace-body">
                <div><strong>Annual:</strong> (${daily.calculation_steps.annual_profection.asc_index} + ${daily.calculation_steps.annual_profection.age}) % 12 = ${daily.calculation_steps.annual_profection.target_index} → ${daily.calculation_steps.annual_profection.result_sign}</div>
                <div><strong>LoY:</strong> domicile(${daily.calculation_steps.lord_of_year.annual_sign}) → ${daily.calculation_steps.lord_of_year.lord_of_year}</div>
                <div><strong>Monthly:</strong> (${daily.calculation_steps.monthly_profection.annual_index} + ${daily.calculation_steps.monthly_profection.month} - 1) % 12 = ${daily.calculation_steps.monthly_profection.target_index} → ${daily.calculation_steps.monthly_profection.result_sign}</div>
                <div><strong>Daily:</strong> steps = floor((${daily.calculation_steps.daily_profection.day} - 1) / ${daily.calculation_steps.daily_profection.rate_days_per_sign.toFixed(3)}) = ${daily.calculation_steps.daily_profection.steps}; (${daily.calculation_steps.daily_profection.monthly_index} + ${daily.calculation_steps.daily_profection.steps}) % 12 = ${daily.calculation_steps.daily_profection.target_index} → ${daily.calculation_steps.daily_profection.result_sign}</div>
                <div><strong>Epitasis:</strong> daily sign = transiting LoY sign (${daily.calculation_steps.epitasis.transiting_loy_sign}); ${daily.calculation_steps.epitasis.matching ? 'MATCH' : 'NO MATCH'}</div>
            </div>
        </details>
    ` : '';

    const dailyHTML = daily ? `
        <div class="oracle-daily-section">
            <div class="oracle-section-title">DAILY OUTPUT</div>
            <div class="oracle-mood-badge">CONDITION: ${daily.mood}</div>
            <h3 class="oracle-title">${daily.title}</h3>
            ${daily.day_lord ? `<div class="oracle-day-lord">DAY LORD: ${daily.day_lord}</div>` : ''}
            <p class="oracle-summary">${daily.summary}</p>
            <div class="oracle-details">
                ${(daily.details || []).map(d => `<div class="oracle-detail-item">${d}</div>`).join('')}
            </div>
            ${daily.secret_key ? `<div class="secret-key-alert">EPITASIS FLAG: ACTIVE</div>` : ''}
            ${dailyTrace}
        </div>
    ` : '';

    div.innerHTML = `${plainHTML}${dailyHTML}`;
    if (plainReading) {
        resetOracleFeedback({
            reading_hash: hashString(plainReading),
            birth: data.meta ? {
                date: data.meta.date,
                time: data.meta.time,
                city: data.meta.city,
                state: data.meta.state
            } : null,
            meta: data.meta || null
        });
    } else {
        resetOracleFeedback(null);
    }
}

function renderSoulGuardian(data) {
    const card = document.getElementById('soulGuardianCard');
    const teamCard = document.getElementById('soulGuardianTeam');
    if (!card || !teamCard) return;

    if (!data.forensic_report || !data.forensic_report.soul_guardian || !data.forensic_report.soul_guardian.almuten) {
        card.innerHTML = `
            <h3>PRIMARY RULER (ALMUTEN FIGURIS)</h3>
            <p class="placeholder-text">Run analysis to compute the primary ruler.</p>
        `;
        teamCard.innerHTML = `
            <h3>SECT ALIGNMENT</h3>
            <p class="placeholder-text">Sect alignment appears after calculation.</p>
        `;
        return;
    }

    const sg = data.forensic_report.soul_guardian;
    const scores = sg.scores || {};
    const sortedScores = Object.entries(scores).sort((a, b) => (b[1].total || 0) - (a[1].total || 0));
    const topScores = sortedScores.slice(0, 5);

    card.innerHTML = `
        <h3>PRIMARY RULER (ALMUTEN FIGURIS)</h3>
        <div class="guardian-title">YOU ARE RULED BY: ${sg.almuten} (Terms of ${sg.term_ruler})</div>
        <div class="guardian-job">${sg.job_description}</div>
        <div class="guardian-meta">Total Score: ${sg.total_score}</div>
        ${sg.prenatal_syzygy_lon ? `<div class="guardian-meta">Prenatal Syzygy: ${formatLongitude(sg.prenatal_syzygy_lon)}</div>` : ''}
        <div class="guardian-scores">
            ${topScores.map(([name, info]) => `
                <div class="guardian-score-item">
                    <span>${name.toUpperCase()}</span>
                    <span>${info.total}</span>
                </div>
            `).join('')}
        </div>
    `;

    const summary = data.forensic_report.summary || {};
    const constructive = summary.constructive_team || [];
    const destructive = summary.destructive_team || [];

    // Planetary Hours
    const ph = summary.planetary_hours || {};
    let hourHTML = '';
    if (ph.hour_ruler) {
        hourHTML = `
            <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.1); font-size: 0.9em;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.3rem;">
                    <span>Day Ruler:</span>
                    <span style="font-weight: bold;">${ph.day_ruler || 'Unknown'}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.3rem;">
                    <span>Hour Ruler:</span>
                    <span style="color: var(--gold); font-weight: bold;">${ph.hour_ruler || 'Unknown'}</span>
                </div>
                <div style="font-size: 0.8em; opacity: 0.7; text-align: right;">${ph.minutes_remaining ? Math.round(ph.minutes_remaining) + ' min left' : ''}</div>
            </div>
        `;
    }

    teamCard.innerHTML = `
        <h3>SECT ALIGNMENT & DAY MASTERY</h3>
        <p class="tool-result-detail">${summary.team_note || ''}</p>
        <div class="tool-result-detail">Constructive Team</div>
        <div class="team-list">
            ${constructive.length ? constructive.map(p => `<span class="team-pill constructive">${p}</span>`).join('') : '<span class="placeholder-text">None</span>'}
        </div>
        <div class="tool-result-detail" style="margin-top: 1rem;">Destructive Team</div>
        <div class="team-list">
            ${destructive.length ? destructive.map(p => `<span class="team-pill destructive">${p}</span>`).join('') : '<span class="placeholder-text">None</span>'}
        </div>
        ${hourHTML}
    `;
}

function renderVitality(data) {
    const card = document.getElementById('vitalityCard');
    if (!card) return;

    if (!data.forensic_report || !data.forensic_report.vitality || !data.forensic_report.vitality.hyleg) {
        card.innerHTML = `
            <h3>VITALITY & LONGEVITY (HYLEG)</h3>
            <p class="placeholder-text">Vitality analysis unavailable.</p>
        `;
        return;
    }

    const v = data.forensic_report.vitality;

    // Create breakdown listing
    const breakdownHTML = v.breakdown ? `
        <div class="vitality-breakdown" style="margin-top: 1rem; font-size: 0.9em; background: rgba(0,0,0,0.3); padding: 0.8rem; border-radius: 4px;">
            <div style="color: var(--gold); margin-bottom: 0.5rem; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 0.25rem;">CALCULATION LOG</div>
            <ul style="list-style: none; padding: 0; margin: 0; max-height: 150px; overflow-y: auto;">
                ${v.breakdown.map(l => `<li style="margin-bottom: 0.25rem;">${l}</li>`).join('')}
            </ul>
        </div>
    ` : '';

    card.innerHTML = `
        <h3>VITALITY & LONGEVITY</h3>
        <div style="display: flex; gap: 2rem; flex-wrap: wrap; margin-bottom: 1rem;">
            <div>
                <span class="tool-result-label">YOU HAVE (HYLEG)</span>
                <div class="tool-result-value">${v.hyleg.replace('Planet', '').replace('Angle', '')}</div>
            </div>
            <div>
                <span class="tool-result-label">YOU HAVE (ALCOCODEN)</span>
                <div class="tool-result-value">${v.alcocoden}</div>
            </div>
            <div>
                <span class="tool-result-label">VITALITY INDEX</span>
                <div class="tool-result-value" style="color: ${v.total_years > 50 ? 'var(--success)' : (v.total_years > 25 ? 'var(--gold)' : 'var(--danger)')};">
                    ${v.total_years.toFixed(1)} YEARS
                </div>
                <div style="font-size: 0.8em; opacity: 0.8; margin-top: 5px; text-transform: uppercase;">${v.vitality_rating || ''}</div>
            </div>
        </div>
        <div class="tool-result-detail">Method: Hyleg and Alcocoden years.</div>
        ${breakdownHTML}
    `;
}

function renderPrimaryDirections(data) {
    const card = document.getElementById('pdCard');
    if (!card) return;

    // Check if we have primary directions data
    const dirs = data.forensic_report ? data.forensic_report.primary_directions : [];
    if (!dirs || dirs.length === 0) {
        card.innerHTML = `
            <h3>PRIMARY DIRECTIONS (PLACIDUS)</h3>
            <p class="placeholder-text">No major directions found in relevant timeframe.</p>
        `;
        return;
    }

    // Sort logic handled in backend, but ensure.
    // Display as a list/timeline
    const listHTML = dirs.map(d => `
        <div class="pd-row" style="display: flex; justify-content: space-between; border-bottom: 1px solid rgba(255,255,255,0.05); padding: 0.5rem 0; font-size: 0.9em;">
            <div style="flex: 2;">
                <span class="pd-promittor" style="color: var(--gold); font-weight: bold;">${d.promittor}</span>
                <span class="pd-aspect" style="opacity: 0.7; margin: 0 0.3rem;">${d.aspect === 'Conjunction' ? 'conj' : d.aspect === 'Opposition' ? 'opp' : d.aspect}</span>
                <span class="pd-significator">${d.significator}</span>
            </div>
            <div style="flex: 1; text-align: right; opacity: 0.8;">
                ${d.years.toFixed(1)} yrs
            </div>
            <div style="flex: 1; text-align: right; font-family: monospace; opacity: 0.6;">
                Arc: ${d.arc.toFixed(1)}°
            </div>
        </div>
    `).join('');

    card.innerHTML = `
        <h3>PRIMARY DIRECTIONS (PLACIDUS)</h3>
        <p style="font-size: 0.8em; opacity: 0.7;">Method: Proportional semi-arc to angles (Asc/MC).</p>
        <div class="pd-list" style="margin-top: 1rem; max-height: 250px; overflow-y: auto;">
             ${listHTML}
        </div>
    `;
}

function renderMutualReceptions(data) {
    // Inject into the Sect/Team card for mutual reception notes.
    const card = document.getElementById('sectTeamCard');
    if (!card) return;

    const summary = data.forensic_report.summary || {};
    const receptions = summary.mutual_receptions || [];

    // Basic styling for reception pills
    const pillStyle = `
        display: inline-block; 
        padding: 0.2rem 0.5rem; 
        background: rgba(255, 215, 0, 0.1); 
        border: 1px solid rgba(255, 215, 0, 0.3); 
        border-radius: 4px; 
        font-size: 0.8em; 
        margin-right: 0.5rem; 
        margin-bottom: 0.3rem; 
        color: var(--gold);
    `;

    let content = '';
    if (receptions.length > 0) {
        content = `
            <div class="tool-result-detail" style="margin-top: 1rem;">MUTUAL RECEPTION</div>
            <div class="reception-list">
                ${receptions.map(r => `
                    <div style="${pillStyle}">
                        <strong>${r.planet_a}</strong> ↔ <strong>${r.planet_b}</strong> 
                        <span style="opacity: 0.7">(${r.type})</span>
                    </div>
                `).join('')}
            </div>
            <div style="font-size: 0.75em; opacity: 0.6; margin-top: 0.2rem;">
                Mutual reception indicates shared rulership.
            </div>
        `;
    } else {
        content = `
            <div class="tool-result-detail" style="margin-top: 1rem;">MUTUAL RECEPTION</div>
            <div style="font-size: 0.8em; opacity: 0.6;">No mutual receptions detected.</div>
        `;
    }

    // Append to existing content of the card
    card.insertAdjacentHTML('beforeend', content);
}

function renderForecast(data) {
    const grid = document.getElementById('forecastGrid');
    if (!data.forensic_forecast) {
        grid.innerHTML = `<p class="placeholder-text">Five-day data unavailable.</p>`;
        return;
    }

    grid.innerHTML = data.forensic_forecast.map(day => `
        <div class="forecast-card ${day.epitasis ? 'epitasis' : ''}">
            <div class="forecast-date">${day.display_date}</div>
            <div class="forecast-lord">
                <div class="lord-icon">${day.chronocrator.charAt(0)}</div>
                <div class="lord-info">
                    <span class="lord-name">${day.chronocrator}</span>
                    <span class="lord-sign">Profection: ${day.profection_sign}</span>
                </div>
            </div>
            <div class="forecast-mood">${day.mood}</div>
            <p class="forecast-summary">${day.summary}</p>
            ${day.medical && day.medical.length > 0 ? `
                <div class="medical-alerts">
                    ${day.medical.map(m => `<div class="medical-alert-item">${m}</div>`).join('')}
                </div>
            ` : ''}
        </div>
    `).join('');
}

function initMedicalCheck(data) {
    const selector = document.getElementById('bodyPartSelect');
    const panel = document.getElementById('surgeryResult');

    const runCheck = async () => {
        const part = selector.value;
        const jd = data.meta.analysis_jd || data.meta.julian_day;

        try {
            const resp = await fetch(apiUrl(`/api/v1/surgery_check?body_part=${part}&jd=${jd}`));
            const res = await resp.json();

            panel.innerHTML = `
                <div class="surgery-status-card ${res.safe ? 'status-safe' : 'status-danger'}">
                    <div class="status-icon">${res.safe ? '✓' : '⚠'}</div>
                    <div class="status-msg">
                        <h4>${res.safe ? 'FAVORABLE' : 'DANGEROUS'}</h4>
                        <p>${res.safe ? 'No major prohibitions found for this operation.' : 'PROHIBITION DETECTED'}</p>
                    </div>
                </div>
                ${res.reasons.length > 0 ? `
                    <div class="surgery-reasons">
                        ${res.reasons.map(r => `<div class="reason-item">✦ ${r}</div>`).join('')}
                    </div>
                ` : ''}
                <div class="medical-meta">
                    <small>Moon: ${res.moon_sign} | Target: ${res.target_body_part}</small>
                </div>
                <div class="medical-footer">
                    <small>${res.historical_context}</small>
                </div>
            `;
        } catch (err) {
            panel.innerHTML = `<p class="error">Medical check failed.</p>`;
        }
    };

    selector.onchange = runCheck;
    runCheck();
}

function renderChartWheel(data) {
    const container = document.getElementById('chartWheelContainer');
    const size = 600;
    const center = size / 2;
    const radius = 250;
    const innerRadius = 160;
    const houseRadius = 120;

    let svg = `<svg viewBox="0 0 ${size} ${size}" class="chart-wheel-svg">
        <defs>
            <radialGradient id="ringGrad" cx="50%" cy="50%" r="50%">
                <stop offset="60%" stop-color="transparent" />
                <stop offset="100%" stop-color="rgba(192, 112, 47, 0.15)" />
            </radialGradient>
            <filter id="glow">
                <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
                <feMerge>
                    <feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/>
                </feMerge>
            </filter>
        </defs>
        
        <!-- Background Rings -->
        <circle cx="${center}" cy="${center}" r="${radius + 30}" fill="none" stroke="var(--gold)" stroke-width="0.5" opacity="0.2" />
        <circle cx="${center}" cy="${center}" r="${radius}" fill="url(#ringGrad)" stroke="var(--gold)" stroke-width="2" />
        <circle cx="${center}" cy="${center}" r="${innerRadius}" fill="none" stroke="var(--gold)" stroke-width="1" />
        <circle cx="${center}" cy="${center}" r="${houseRadius}" fill="none" stroke="var(--gold)" stroke-width="0.5" opacity="0.5" />
    `;

    const offset = data.angles.Ascendant;

    // Draw Signs (Counter-Clockwise)
    for (let i = 0; i < 12; i++) {
        const startEcl = i * 30;
        // Wheel Angle = 180 - (Ecliptic - Ascendant)
        const wheelStart = (180 - (startEcl - offset)) % 360;

        // Division line
        const rad = (wheelStart * Math.PI) / 180;
        const x1 = center + innerRadius * Math.cos(rad);
        const y1 = center + innerRadius * Math.sin(rad);
        const x2 = center + radius * Math.cos(rad);
        const y2 = center + radius * Math.sin(rad);
        svg += `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="var(--gold)" stroke-width="1" opacity="0.4" />`;

        // Sign Label
        const labelAngle = ((wheelStart - 15) * Math.PI) / 180;
        const lx = center + (radius - 20) * Math.cos(labelAngle);
        const ly = center + (radius - 20) * Math.sin(labelAngle);
        svg += `<text x="${lx}" y="${ly}" fill="var(--gold)" font-size="12" font-weight="bold" text-anchor="middle" alignment-baseline="middle" transform="rotate(${wheelStart - 105}, ${lx}, ${ly})" opacity="0.8">${SIGNS[i].substring(0, 3).toUpperCase()}</text>`;
    }

    // Draw Houses
    for (const [num, lon] of Object.entries(data.houses)) {
        const wheelLon = (180 - (lon - offset)) % 360;
        const rad = (wheelLon * Math.PI) / 180;
        const x1 = center + houseRadius * Math.cos(rad);
        const y1 = center + houseRadius * Math.sin(rad);
        const x2 = center + innerRadius * Math.cos(rad);
        const y2 = center + innerRadius * Math.sin(rad);

        svg += `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="var(--purple)" stroke-width="1" opacity="0.5" />`;

        // House Number
        const hLabelAngle = ((wheelLon - 15) * Math.PI) / 180;
        const hx = center + (houseRadius + 15) * Math.cos(hLabelAngle);
        const hy = center + (houseRadius + 15) * Math.sin(hLabelAngle);
        svg += `<text x="${hx}" y="${hy}" fill="var(--purple-light)" font-size="9" text-anchor="middle" opacity="0.6">${num}</text>`;
    }

    // Draw Aspects (Connecting Planets)
    // Simple: draw lines for major aspects
    const planetEntries = Object.entries(data.planets);
    for (let i = 0; i < planetEntries.length; i++) {
        for (let j = i + 1; j < planetEntries.length; j++) {
            const [p1, info1] = planetEntries[i];
            const [p2, info2] = planetEntries[j];
            const diff = Math.abs(info1.longitude - info2.longitude) % 360;
            const dist = diff > 180 ? 360 - diff : diff;

            let color = "";
            let orb = 5;
            if (dist < orb) color = "var(--gold)"; // Conjunction
            else if (Math.abs(dist - 180) < orb) color = "var(--danger)"; // Opposition
            else if (Math.abs(dist - 90) < orb) color = "var(--danger)"; // Square
            else if (Math.abs(dist - 120) < orb) color = "var(--success)"; // Trine
            else if (Math.abs(dist - 60) < orb) color = "var(--success)"; // Sextile

            if (color) {
                const a1 = ((180 - (info1.longitude - offset)) * Math.PI) / 180;
                const a2 = ((180 - (info2.longitude - offset)) * Math.PI) / 180;
                const r = houseRadius - 10;
                svg += `<line x1="${center + r * Math.cos(a1)}" y1="${center + r * Math.sin(a1)}" x2="${center + r * Math.cos(a2)}" y2="${center + r * Math.sin(a2)}" stroke="${color}" stroke-width="0.5" opacity="0.2" />`;
            }
        }
    }

    // Draw Planets
    const PLANET_GLYPHS = {
        "Sun": "☉", "Moon": "☾", "Mercury": "☿", "Venus": "♀", "Mars": "♂",
        "Jupiter": "♃", "Saturn": "♄", "Uranus": "♅", "Neptune": "♆", "Pluto": "♇",
        "North_Node": "☊", "South_Node": "☋"
    };

    planetEntries.forEach(([name, info]) => {
        const wheelDeg = (180 - (info.longitude - offset)) % 360;
        const rad = (wheelDeg * Math.PI) / 180;
        const r = innerRadius - 25;
        const px = center + r * Math.cos(rad);
        const py = center + r * Math.sin(rad);

        svg += `
            <g class="planet-glyph-group" style="cursor: pointer" onclick='showDetailsByPlanet("${name}", ${JSON.stringify(data)})'>
                <circle cx="${px}" cy="${py}" r="14" fill="var(--bg-card)" stroke="var(--gold)" stroke-width="1.5" filter="url(#glow)" />
                <text x="${px}" y="${py}" fill="var(--gold)" font-size="16" text-anchor="middle" alignment-baseline="middle">${PLANET_GLYPHS[name] || name.charAt(0)}</text>
            </g>
        `;
    });

    // Center Earth
    svg += `<circle cx="${center}" cy="${center}" r="15" fill="var(--bg-card)" stroke="var(--gold)" stroke-width="1" />`;
    svg += `<text x="${center}" y="${center}" fill="var(--gold)" font-size="8" text-anchor="middle" alignment-baseline="middle">TERRA</text>`;

    svg += `</svg>`;
    container.innerHTML = svg;
}

window.showDetailsByPlanet = (name, data) => {
    const p = data.forensic_report.planets.find(pl => pl.planet === name);
    if (p) showDetails(p);
};

function renderPrediction(data) {
    const profDiv = document.getElementById('profectionInfo');
    const zrDiv = document.getElementById('zrInfo');

    if (!data.forensic_report || !data.forensic_report.prediction) {
        profDiv.innerHTML = '<p class="placeholder-text">Provide age and analysis date to compute time lords.</p>';
        zrDiv.innerHTML = '<p class="placeholder-text">Full birth data required for zodiacal releasing.</p>';
        return;
    }

    const pred = data.forensic_report.prediction;
    const steps = pred.calculation_steps || null;
    const traceHtml = steps ? `
        <details class="calc-trace">
            <summary>Calculation trace</summary>
            <div class="calc-trace-body">
                <div><strong>Annual:</strong> (${steps.annual_profection.asc_index} + ${steps.annual_profection.age}) % 12 = ${steps.annual_profection.target_index} → ${steps.annual_profection.result_sign}</div>
                <div><strong>LoY:</strong> domicile(${steps.lord_of_year.annual_sign}) → ${steps.lord_of_year.lord_of_year}</div>
                <div><strong>Monthly (continuous):</strong> (${steps.monthly_profection.continuous.annual_index} + ${steps.monthly_profection.continuous.month} - 1) % 12 = ${steps.monthly_profection.continuous.target_index} → ${steps.monthly_profection.continuous.result_sign}</div>
                <div><strong>Monthly (saltatory):</strong> (${steps.monthly_profection.saltatory.asc_index} + ${steps.monthly_profection.saltatory.total_months}) % 12 = ${steps.monthly_profection.saltatory.target_index} → ${steps.monthly_profection.saltatory.result_sign}</div>
                <div><strong>Daily:</strong> steps = floor((${steps.daily_profection.day} - 1) / ${steps.daily_profection.rate_days_per_sign.toFixed(3)}) = ${steps.daily_profection.steps}; (${steps.daily_profection.monthly_index} + ${steps.daily_profection.steps}) % 12 = ${steps.daily_profection.target_index} → ${steps.daily_profection.result_sign}</div>
                <div><strong>Epitasis:</strong> daily sign = transiting LoY sign (${steps.epitasis.transiting_loy_sign || 'Unknown'}) via ${steps.epitasis.source || 'n/a'}; days: ${steps.epitasis.matching_days && steps.epitasis.matching_days.length ? steps.epitasis.matching_days.join(', ') : 'None'}</div>
            </div>
        </details>
    ` : '';
    profDiv.innerHTML = `
        <div class="prediction-item">
            <p><strong>YOU ARE IN (ANNUAL):</strong> ${pred.annual_profection.sign} | Lord: ${pred.annual_profection.lord_of_year}</p>
            <p><strong>YOU ARE IN (MONTHLY):</strong> ${pred.monthly_profection.continuous}</p>
            <p><strong>MONTHLY (SALT):</strong> ${pred.monthly_profection.saltatory || 'Unavailable'}</p>
            <p><strong>YOU ARE IN (DAILY):</strong> ${pred.daily_profection.sign}</p>
            <p><strong>EPITASIS DAYS:</strong> ${pred.epitasis_days && pred.epitasis_days.length ? `Days ${pred.epitasis_days.join(', ')}` : 'None detected'}</p>
        </div>
        ${traceHtml}
    `;

    const zrData = data.forensic_report.zodiacal_releasing;
    if (Array.isArray(zrData)) {
        let zrHTML = '';
        zrData.forEach(p => {
            zrHTML += `
                <div class="zr-period">
                    <div class="zr-period-header">
                        <span>${p.sign}</span>
                        <span style="color:var(--gold)">Level ${p.level}</span>
                    </div>
                    <div class="zr-period-dates">${new Date(p.start).toLocaleDateString()} - ${new Date(p.end).toLocaleDateString()}</div>
                </div>
             `;
        });
        zrDiv.innerHTML = zrHTML;
    } else if (zrData && typeof zrData === 'object') {
        zrDiv.innerHTML = Object.entries(zrData).map(([key, value]) => `
            <div class="zr-period">
                <div class="zr-period-header">
                    <span>${key}</span>
                    <span style="color:var(--gold)">${value}</span>
                </div>
            </div>
        `).join('');
    } else {
        zrDiv.innerHTML = '<p class="placeholder-text">No Zodiacal Releasing data returned.</p>';
    }
}

window.showDetails = (p) => {
    logEvent("view_details", { planet: p.planet, house: p.house_number });
    const modal = document.getElementById('modalOverlay');
    const body = document.getElementById('modalBody');

    const variantSection = (p.dignity_conflicts && p.dignity_conflicts.length) ? `
        <div class="variant-note" style="margin-top: 1rem;">
            <strong>Variants:</strong> ${p.dignity_conflicts.join(' | ')}
        </div>
    ` : '';

    body.innerHTML = `
        <h2 style="font-family: 'Cormorant Garamond', serif; color: var(--gold); margin-bottom: 2rem;">${p.planet} IN THE TWELVE DOMAINS</h2>
        <div class="modal-detail-section">
            <h4 style="color: var(--gold); letter-spacing: 2px;">JUDGMENT OF DIGNITY</h4>
            <p style="margin: 1rem 0;">The planet holds a score of <strong>${p.dignity_score}</strong> in the celestial hierarchy.</p>
            <ul style="list-style: '✦ '; padding-left: 1.5rem; color: var(--text-muted);">
                ${p.dignity_details.map(d => `<li>${d}</li>`).join('')}
            </ul>
            ${variantSection}
        </div>
        <div class="modal-detail-section">
            <h4 style="color: var(--gold); letter-spacing: 2px;">SOLAR CONDITION & MEDICAL</h4>
            <p style="margin: 0.75rem 0;"><strong>Solar Status:</strong> ${p.solar_status || 'Unknown'}</p>
            <p style="margin: 0.75rem 0;"><strong>Medical Region:</strong> ${p.medical_region || 'Unknown'}</p>
            ${p.medical_pathology ? `<p style="margin: 0.75rem 0;"><strong>Pathology:</strong> ${p.medical_pathology}</p>` : ''}
        </div>
        <hr style="border: 0; border-top: 1px solid var(--glass-border); margin: 2rem 0;">
        <div class="modal-detail-section">
            <h4 style="color: var(--gold); letter-spacing: 2px;">RULE TEXT</h4>
            <p style="font-family: 'Sora', sans-serif; font-size: 1.05rem; line-height: 1.7; margin-top: 1rem;">
                ${p.delineation_text}
            </p>
        </div>
        <div class="modal-detail-section" style="margin-top: 2rem;">
            <h4 style="color: var(--gold); letter-spacing: 2px;">HOUSE PLACEMENT: ${p.house_number}</h4>
            <p style="font-family: 'Sora', sans-serif; font-size: 1.05rem; line-height: 1.7; margin-top: 1rem;">
                ${p.house_delineation_text}
            </p>
        </div>
    `;

    modal.classList.remove('hidden');
};

document.querySelector('.modal-close').addEventListener('click', () => {
    document.getElementById('modalOverlay').classList.add('hidden');
});

document.getElementById('modalOverlay').addEventListener('click', (e) => {
    if (e.target.id === 'modalOverlay') {
        document.getElementById('modalOverlay').classList.add('hidden');
    }
});

// Tool Tabs
const toolTabs = Array.from(document.querySelectorAll('.tool-tab-btn'));
const toolPanels = Array.from(document.querySelectorAll('.tool-content'));
const activeToolTab = toolTabs.find((btn) => btn.classList.contains('active'));
if (activeToolTab) {
    setActiveTab(activeToolTab, toolTabs, toolPanels, 'tool', 'Tool');
}
toolTabs.forEach(btn => {
    btn.addEventListener('click', () => {
        setActiveTab(btn, toolTabs, toolPanels, 'tool', 'Tool');
        logEvent("tool_tab_change", { tool: btn.dataset.tool });
    });
});

function renderToolError(containerId, message) {
    const container = document.getElementById(containerId);
    if (container) {
        container.innerHTML = `<p class="placeholder-text">${message}</p>`;
    }
}

// Synastry
document.getElementById('synastryForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
        person_a: {
            date: document.getElementById('synDateA').value,
            time: document.getElementById('synTimeA').value,
            city: document.getElementById('synCityA').value,
            state: document.getElementById('synStateA').value
        },
        person_b: {
            date: document.getElementById('synDateB').value,
            time: document.getElementById('synTimeB').value,
            city: document.getElementById('synCityB').value,
            state: document.getElementById('synStateB').value
        }
    };

    logEvent("tool_request", { tool: "synastry", payload });

    try {
        const resp = await fetch(apiUrl('/api/v1/synastry'), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (!resp.ok) {
            const err = await resp.json();
            throw new Error(err.detail || 'Synastry calculation failed.');
        }
        const result = await resp.json();
        logEvent("tool_result", { tool: "synastry", result });
        renderSynastry(result);
    } catch (err) {
        logEvent("tool_error", { tool: "synastry", message: err.message || String(err) });
        renderToolError('synastryResults', err.message);
    }
});

function renderSynastry(data) {
    const container = document.getElementById('synastryResults');
    const syn = data.synastry;
    if (!syn) {
        renderToolError('synastryResults', 'No synastry data returned.');
        return;
    }

    const dependencies = syn.dependency_audits || [];
    const shared = syn.shared_fate || [];

    container.innerHTML = `
        <div class="tool-result-card">
            <div class="tool-result-title">Overall Assessment</div>
            <div>${syn.overall_assessment}</div>
        </div>
        <div class="tool-result-card">
            <div class="tool-result-title">Dependency Audits</div>
            ${dependencies.length ? dependencies.map(d => `
                <div class="tool-result-detail"><strong>${d.subject} ${d.planet}</strong> on ${d.target} (${d.type})</div>
                <div class="tool-result-detail">${d.delineation}</div>
            `).join('') : '<div class="tool-result-detail">No dependency locks detected.</div>'}
        </div>
        <div class="tool-result-card">
            <div class="tool-result-title">Shared Indicators</div>
            ${shared.length ? shared.map(s => `
                <div class="tool-result-detail"><strong>${s.type}:</strong> ${s.description}</div>
                <div class="tool-result-detail">${s.delineation}</div>
            `).join('') : '<div class="tool-result-detail">No shared indicators detected.</div>'}
        </div>
    `;
}

// Kairos
document.getElementById('kairosForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
        activity: document.getElementById('kairosActivity').value,
        city: document.getElementById('kairosCity').value,
        state: document.getElementById('kairosState').value,
        start_date: document.getElementById('kairosStartDate').value || null,
        hours: parseInt(document.getElementById('kairosHours').value, 10) || 168
    };

    logEvent("tool_request", { tool: "kairos", payload });

    try {
        const resp = await fetch(apiUrl('/api/v1/kairos'), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (!resp.ok) {
            const err = await resp.json();
            throw new Error(err.detail || 'Kairos scan failed.');
        }
        const result = await resp.json();
        logEvent("tool_result", { tool: "kairos", result });
        renderKairos(result);
    } catch (err) {
        logEvent("tool_error", { tool: "kairos", message: err.message || String(err) });
        renderToolError('kairosResults', err.message);
    }
});

function renderKairos(data) {
    const container = document.getElementById('kairosResults');
    const windows = data.best_windows || [];
    if (!windows.length) {
        container.innerHTML = '<p class="placeholder-text">No viable windows found in the scan range.</p>';
        return;
    }

    const query = data.query || {};
    const topSlots = data.raw_top_slots || [];

    const queryHTML = `
        <div class="tool-result-card">
            <div class="tool-result-title">Query</div>
            <div class="tool-result-detail"><strong>Activity:</strong> ${query.activity || 'Unknown'}</div>
            <div class="tool-result-detail"><strong>Location:</strong> ${query.location || 'Unknown'}</div>
            <div class="tool-result-detail"><strong>Start:</strong> ${query.start_time ? new Date(query.start_time).toLocaleString() : 'Unknown'}</div>
            <div class="tool-result-detail"><strong>Range:</strong> ${query.scan_range || 'Unknown'}</div>
        </div>
    `;

    const windowsHTML = windows.map(w => `
        <div class="tool-result-card">
            <div class="tool-result-title">${w.mood} Window</div>
            <div class="tool-result-detail">Start: ${new Date(w.start).toLocaleString()}</div>
            <div class="tool-result-detail">End: ${new Date(w.end).toLocaleString()}</div>
            <div class="tool-result-detail">Duration: ${w.duration_hours} hours</div>
            <div class="tool-result-detail">Peak: ${new Date(w.peak_time).toLocaleString()} (Score ${w.peak_score})</div>
            ${(w.details || []).length ? `<div class="tool-result-detail">${w.details.slice(0, 4).join(' | ')}</div>` : ''}
        </div>
    `).join('');

    const slotsHTML = topSlots.length ? `
        <div class="tool-result-card">
            <div class="tool-result-title">Top Slots</div>
            ${topSlots.slice(0, 6).map(s => `
                <div class="tool-result-detail"><strong>${new Date(s.time).toLocaleString()}</strong> | Score ${s.score} | ${s.mood}</div>
            `).join('')}
        </div>
    ` : '';

    container.innerHTML = `${queryHTML}${windowsHTML}${slotsHTML}`;
}

// Horary Oracle
document.getElementById('horaryForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
        question: document.getElementById('horaryQuestion').value,
        city: document.getElementById('horaryCity').value,
        state: document.getElementById('horaryState').value,
        date: document.getElementById('horaryDate').value || null,
        time: document.getElementById('horaryTime').value || null
    };

    logEvent("tool_request", { tool: "horary", payload });

    try {
        const resp = await fetch(apiUrl('/api/v1/horary'), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (!resp.ok) {
            const err = await resp.json();
            throw new Error(err.detail || 'Horary engine failed.');
        }
        const result = await resp.json();
        logEvent("tool_result", { tool: "horary", result });
        renderHorary(result);
    } catch (err) {
        logEvent("tool_error", { tool: "horary", message: err.message || String(err) });
        renderToolError('horaryResults', err.message);
    }
});

function renderHorary(data) {
    const container = document.getElementById('horaryResults');
    const oracle = data.oracle;
    if (!oracle) {
        renderToolError('horaryResults', 'No horary response returned.');
        return;
    }

    const conditions = oracle.conditions || [];
    const scoreLine = (oracle.total_score !== undefined)
        ? `<div class="tool-result-detail">Score: ${oracle.total_score} (Conditions ${oracle.condition_score}, Strength ${oracle.strength_score})</div>`
        : '';
    const querentVariants = oracle.querent_strength && oracle.querent_strength.variant_notes && oracle.querent_strength.variant_notes.length
        ? ` | Variants: ${oracle.querent_strength.variant_notes.join(' / ')}`
        : '';
    const quesitedVariants = oracle.quesited_strength && oracle.quesited_strength.variant_notes && oracle.quesited_strength.variant_notes.length
        ? ` | Variants: ${oracle.quesited_strength.variant_notes.join(' / ')}`
        : '';

    const strengthCard = (oracle.querent_strength || oracle.quesited_strength) ? `
        <div class="tool-result-card">
            <div class="tool-result-title">Significator Strength</div>
            ${oracle.querent_strength ? `
                <div class="tool-result-detail"><strong>Querent (${oracle.querent_strength.planet}):</strong> ${oracle.querent_strength.total_score} total | Essential ${oracle.querent_strength.essential_score} | Accidental ${oracle.querent_strength.accidental_score} | Sect ${oracle.querent_strength.sect_score} | Nature ${oracle.querent_strength.nature_score} | Hayz ${oracle.querent_strength.hayz_status}${querentVariants}</div>
            ` : ''}
            ${oracle.quesited_strength ? `
                <div class="tool-result-detail"><strong>Quesited (${oracle.quesited_strength.planet}):</strong> ${oracle.quesited_strength.total_score} total | Essential ${oracle.quesited_strength.essential_score} | Accidental ${oracle.quesited_strength.accidental_score} | Sect ${oracle.quesited_strength.sect_score} | Nature ${oracle.quesited_strength.nature_score} | Hayz ${oracle.quesited_strength.hayz_status}${quesitedVariants}</div>
            ` : ''}
        </div>
    ` : '';
    container.innerHTML = `
        <div class="tool-result-card">
            <div class="tool-result-title">Verdict: ${oracle.verdict}</div>
            <div class="tool-result-detail"><strong>Question:</strong> ${oracle.question}</div>
            <div class="tool-result-detail">Querent: ${oracle.querent_ruler} (Asc ${oracle.querent_sign})</div>
            <div class="tool-result-detail">Quesited: ${oracle.quesited_ruler} (House ${oracle.quesited_house} ${oracle.quesited_label}, ${oracle.quesited_sign})</div>
            <div class="tool-result-detail">Weight: ${oracle.verdict_weight}</div>
            ${scoreLine}
            <div class="tool-result-detail">Conditions: ${oracle.positive_count} favorable | ${oracle.negative_count} adverse</div>
        </div>
        <div class="tool-result-card">
            <div class="tool-result-title">Horary Conditions</div>
            ${conditions.length ? conditions.map(c => `
                <div class="tool-result-detail"><strong>${c.condition}</strong>${c.status ? ` (${c.status})` : ''}${formatHoraryCondition(c) ? `: ${formatHoraryCondition(c)}` : ''}</div>
            `).join('') : '<div class="tool-result-detail">No applying contacts detected between significators.</div>'}
        </div>
        ${strengthCard}
    `;
}

function formatHoraryCondition(c) {
    const parts = [];
    if (c.details) parts.push(c.details);
    if (c.aspect) parts.push(`Aspect ${c.aspect}`);
    if (c.via) parts.push(`Via ${c.via}`);
    if (c.from && c.to) parts.push(`${c.from} -> ${c.to}`);
    if (c.collector) parts.push(`Collector ${c.collector}`);
    if (c.p1 && c.p2) parts.push(`${c.p1} + ${c.p2}`);
    if (c.p1_aspect || c.p2_aspect) {
        const aspects = [c.p1_aspect, c.p2_aspect].filter(Boolean).join('/');
        if (aspects) parts.push(aspects);
    }
    if (c.intervener) parts.push(`Intervener ${c.intervener}`);
    if (c.target) parts.push(`Target ${c.target}`);
    if (c.giver && c.receiver) parts.push(`${c.giver} -> ${c.receiver}`);
    if (c.by) parts.push(`By ${Array.isArray(c.by) ? c.by.join(', ') : c.by}`);
    return parts.join(' | ');
}

// World Dashboard
document.getElementById('worldForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
        date: document.getElementById('worldDate').value || null,
        time: document.getElementById('worldTime').value || null
    };

    logEvent("tool_request", { tool: "world", payload });

    try {
        const resp = await fetch(apiUrl('/api/v1/world'), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (!resp.ok) {
            const err = await resp.json();
            throw new Error(err.detail || 'World dashboard failed.');
        }
        const result = await resp.json();
        logEvent("tool_result", { tool: "world", result });
        renderWorld(result);
    } catch (err) {
        logEvent("tool_error", { tool: "world", message: err.message || String(err) });
        renderToolError('worldResults', err.message);
    }
});

// Rectification
document.getElementById('rectificationForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const rectMethods = [];
    const rectAnimodar = document.getElementById('rectMethodAnimodar');
    const rectTrutina = document.getElementById('rectMethodTrutina');
    if (rectAnimodar && rectAnimodar.checked) rectMethods.push('animodar');
    if (rectTrutina && rectTrutina.checked) rectMethods.push('trutina_hermetis');
    if (!rectMethods.length) {
        rectMethods.push('animodar', 'trutina_hermetis');
    }
    const payload = {
        date: document.getElementById('rectDate').value,
        time: document.getElementById('rectTime').value,
        city: document.getElementById('rectCity').value,
        state: document.getElementById('rectState').value,
        rectification_methods: rectMethods
    };

    logEvent("tool_request", { tool: "rectification", payload });

    try {
        const resp = await fetch(apiUrl('/api/v1/rectification'), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (!resp.ok) {
            const err = await resp.json();
            throw new Error(err.detail || 'Rectification failed.');
        }
        const result = await resp.json();
        logEvent("tool_result", { tool: "rectification", result });
        renderRectification(result);
    } catch (err) {
        logEvent("tool_error", { tool: "rectification", message: err.message || String(err) });
        renderToolError('rectificationResults', err.message);
    }
});

function renderWorld(data) {
    const container = document.getElementById('worldResults');
    const stars = data.fixed_star_alerts || [];
    const eclipses = data.eclipses || [];
    const epoch = data.universal_overdrive || [];
    const transits = data.transiting_planets || [];

    let personalHits = [];
    if (currentResult && eclipses.length) {
        const points = [];
        Object.entries(currentResult.planets || {}).forEach(([name, info]) => {
            points.push({ label: name, longitude: info.longitude });
        });
        if (currentResult.angles) {
            points.push({ label: 'Ascendant', longitude: currentResult.angles.Ascendant });
            points.push({ label: 'Midheaven', longitude: currentResult.angles.MC });
        }

        eclipses.forEach(e => {
            points.forEach(p => {
                let diff = Math.abs(e.longitude - p.longitude) % 360;
                if (diff > 180) diff = 360 - diff;
                if (diff <= 3) {
                    personalHits.push(`${p.label} within ${diff.toFixed(1)}° of ${e.type} in ${e.sign}`);
                }
            });
        });
    }

    container.innerHTML = `
        <div class="tool-result-card">
            <div class="tool-result-title">Transiting Planets</div>
            ${transits.length ? transits.map(t => `
                <div class="tool-result-detail"><strong>${t.planet}:</strong> ${formatLongitude(t.longitude)} (${t.sign})${typeof t.speed === 'number' ? ` | Speed ${t.speed}` : ''}</div>
            `).join('') : '<div class="tool-result-detail">Transit list unavailable.</div>'}
        </div>
        <div class="tool-result-card">
            <div class="tool-result-title">Fixed Stars Active</div>
            ${stars.length ? stars.map(s => `
                <div class="tool-result-detail"><strong>${s.star}</strong> conjunct ${s.planet} (orb ${s.orb}°) | ${s.nature}</div>
                ${s.glory ? `<div class="tool-result-detail">Glory: ${s.glory}</div>` : ''}
                ${s.nemesis ? `<div class="tool-result-detail">Nemesis: ${s.nemesis}</div>` : ''}
            `).join('') : '<div class="tool-result-detail">No major fixed star activations at this moment.</div>'}
        </div>
        <div class="tool-result-card">
            <div class="tool-result-title">Eclipse Pressure</div>
            ${eclipses.length ? eclipses.map(e => `
                <div class="tool-result-detail"><strong>${e.type}</strong> at ${e.degree}° ${e.sign} (${e.triplicity})</div>
                ${e.duration_hours ? `<div class="tool-result-detail">Duration: ${e.duration_hours} hours</div>` : ''}
                ${e.affected_regions && e.affected_regions.length ? `<div class="tool-result-detail">Regions: ${e.affected_regions.join(', ')}</div>` : ''}
                ${e.stress_note ? `<div class="tool-result-detail">${e.stress_note}</div>` : ''}
            `).join('') : '<div class="tool-result-detail">No recent eclipses returned for this date.</div>'}
        </div>
        <div class="tool-result-card">
            <div class="tool-result-title">Personal Suspension Checks</div>
            ${personalHits.length ? personalHits.map(h => `<div class="tool-result-detail">${h}</div>`).join('') : '<div class="tool-result-detail">No personal suspensions detected from current eclipses.</div>'}
        </div>
        <div class="tool-result-card">
            <div class="tool-result-title">December 2025 Epoch</div>
            ${epoch.length ? epoch.map(e => `
                <div class="tool-result-detail"><strong>${e.cause}:</strong> ${e.status}</div>
                ${e.rule ? `<div class="tool-result-detail">${e.rule}</div>` : ''}
                ${e.description ? `<div class="tool-result-detail">${e.description}</div>` : ''}
            `).join('') : '<div class="tool-result-detail">No universal overdrive flags for this timestamp.</div>'}
        </div>
        <div class="tool-result-card">
            <div class="tool-result-title">World Note</div>
            <div class="tool-result-detail">${data.note || 'No global note provided.'}</div>
            ${data.timestamp ? `<div class="tool-result-detail">Timestamp: ${data.timestamp}</div>` : ''}
        </div>
    `;
}

function renderRectification(data) {
    const container = document.getElementById('rectificationResults');
    const animodar = data.animodar || [];
    const trutina = data.trutina_hermetis || [];
    const syzygy = data.syzygy || {};
    const meta = data.meta || {};
    const rectMeta = data.rectification_meta || {};
    const methods = rectMeta.computed_methods || [];
    const unsupported = rectMeta.unsupported_methods || [];

    const metaHTML = meta && meta.city ? `
        <div class="tool-result-card">
            <div class="tool-result-title">Chart Context</div>
            <div class="tool-result-detail"><strong>Birth:</strong> ${meta.date} ${meta.time}</div>
            <div class="tool-result-detail"><strong>Location:</strong> ${meta.city}${meta.state ? `, ${meta.state}` : ''}</div>
            <div class="tool-result-detail"><strong>Coordinates:</strong> ${typeof meta.lat === 'number' ? meta.lat.toFixed(4) : meta.lat}, ${typeof meta.lon === 'number' ? meta.lon.toFixed(4) : meta.lon}</div>
        </div>
    ` : '';

    const methodsHTML = (methods.length || unsupported.length) ? `
        <div class="tool-result-card">
            <div class="tool-result-title">Rectification Methods</div>
            <div class="tool-result-detail"><strong>Computed:</strong> ${methods.length ? methods.join(', ') : 'None'}</div>
            ${unsupported.length ? `<div class="tool-result-detail"><strong>Unavailable:</strong> ${unsupported.join(', ')}</div>` : ''}
        </div>
    ` : '';

    const syzygyHTML = syzygy && syzygy.jd ? `
        <div class="tool-result-card">
            <div class="tool-result-title">Prenatal Syzygy</div>
            <div class="tool-result-detail"><strong>Type:</strong> ${syzygy.type}</div>
            <div class="tool-result-detail"><strong>JD:</strong> ${syzygy.jd.toFixed ? syzygy.jd.toFixed(4) : syzygy.jd}</div>
            <div class="tool-result-detail"><strong>Longitude:</strong> ${typeof syzygy.longitude === 'number' ? formatLongitude(syzygy.longitude) : 'Unknown'}</div>
        </div>
    ` : '';

    const animodarHTML = animodar.length ? `
        <div class="tool-result-card">
            <div class="tool-result-title">Animodar (Ptolemaic)</div>
            ${animodar.map(a => `
                <div class="tool-result-detail"><strong>${a.rectifying_planet}</strong> | ${a.suggestion}</div>
                <div class="tool-result-detail">Target Degree: ${a.target_degree.toFixed ? a.target_degree.toFixed(2) : a.target_degree}°</div>
                <div class="tool-result-detail">Difference: ${a.difference.toFixed ? a.difference.toFixed(2) : a.difference}° | Confidence ${a.confidence}%</div>
            `).join('')}
        </div>
    ` : '';

    const trutinaHTML = trutina.length ? `
        <div class="tool-result-card">
            <div class="tool-result-title">Trutina Hermetis</div>
            ${trutina.map(t => `
                <div class="tool-result-detail"><strong>Suggested Asc:</strong> ${formatLongitude(t.suggested_ascendant)}</div>
                <div class="tool-result-detail">Gestation: ${t.gestation_days} days | Confidence ${t.confidence}%</div>
                ${t.conception_date ? `<div class="tool-result-detail">Conception: ${t.conception_date}</div>` : ''}
            `).join('')}
        </div>
    ` : '';

    container.innerHTML = `
        ${metaHTML}
        ${methodsHTML}
        ${syzygyHTML || '<div class="tool-result-card"><div class="tool-result-title">Prenatal Syzygy</div><div class="tool-result-detail">No syzygy found.</div></div>'}
        ${animodarHTML || '<div class="tool-result-card"><div class="tool-result-title">Animodar (Ptolemaic)</div><div class="tool-result-detail">No Animodar results returned.</div></div>'}
        ${trutinaHTML || '<div class="tool-result-card"><div class="tool-result-title">Trutina Hermetis</div><div class="tool-result-detail">No Trutina results returned.</div></div>'}
    `;
}

// ==========================================
// CLIENT-SIDE CHART LIBRARY (LOCALSTORAGE)
// ==========================================

const libraryBtn = document.getElementById('libraryBtn');
const saveChartBtn = document.getElementById('saveChartBtn');
const STORAGE_KEY = 'codex_chart_library';

if (saveChartBtn) {
    saveChartBtn.addEventListener('click', () => {
        if (!currentResult) {
            alert('No chart to save.');
            return;
        }
        saveToLibrary(currentResult);
    });
}

if (libraryBtn) {
    libraryBtn.addEventListener('click', () => {
        openLibraryModal();
    });
}

function getLibrary() {
    try {
        const raw = localStorage.getItem(STORAGE_KEY);
        return raw ? JSON.parse(raw) : [];
    } catch (e) {
        // Silent fail for library parsing
        return [];
    }
}

function saveToLibrary(data) {
    const lib = getLibrary();
    // Create a unique ID or use timestamp
    const id = Date.now().toString();
    const name = prompt("Enter a name for this chart (e.g. 'Napoleon'):", data.meta.name || "Untitled Chart");

    if (!name) return; // User cancelled

    const entry = {
        id: id,
        name: name,
        date: data.meta.date,
        time: data.meta.time,
        city: data.meta.city,
        savedAt: new Date().toISOString(),
        data: data // Store full result
    };

    lib.unshift(entry); // Add to top
    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(lib.slice(0, 50))); // Limit to 50 charts
        alert('Chart saved to library!');
    } catch (e) {
        alert('Storage full or error saving: ' + e.message);
    }
}

function openLibraryModal() {
    const modal = document.getElementById('modalOverlay');
    const body = document.getElementById('modalBody');
    const lib = getLibrary();

    let html = `
        <h2 style="font-family: 'Cormorant Garamond', serif; color: var(--gold); margin-bottom: 1.5rem;">CHART LIBRARY</h2>
        <div class="library-list">
    `;

    if (lib.length === 0) {
        html += `<p class="placeholder-text">Your library is empty. Calculate a chart and click 'Save to Library'.</p>`;
    } else {
        html += lib.map(entry => `
            <div class="library-item" style="border: 1px solid rgba(255,255,255,0.1); padding: 1rem; margin-bottom: 1rem; background: rgba(0,0,0,0.2); display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div style="color: var(--gold); font-weight: bold; font-size: 1.1em;">${escapeHtml(entry.name)}</div>
                    <div style="font-size: 0.85em; opacity: 0.7;">${entry.date} ${entry.time} | ${entry.city}</div>
                </div>
                <div class="library-actions" style="display: flex; gap: 0.5rem;">
                    <button class="help-btn" style="padding: 0.3rem 0.6rem; font-size: 0.8em;" onclick="loadFromLibrary('${entry.id}')">LOAD</button>
                    <button class="help-btn" style="padding: 0.3rem 0.6rem; font-size: 0.8em; border-color: var(--danger); color: var(--danger);" onclick="deleteFromLibrary('${entry.id}')">DEL</button>
                </div>
            </div>
        `).join('');
    }

    html += `</div>`;

    if (lib.length > 0) {
        html += `<div style="margin-top: 1rem; text-align: right; font-size: 0.8em; opacity: 0.5;">Saved locally in your browser.</div>`;
    }

    body.innerHTML = html;
    modal.classList.remove('hidden');
}

window.loadFromLibrary = (id) => {
    const lib = getLibrary();
    const entry = lib.find(e => e.id === id);
    if (entry && entry.data) {
        currentResult = entry.data;
        renderResults(currentResult);
        document.getElementById('modalOverlay').classList.add('hidden');
        logEvent('library_load', { id: id, name: entry.name });
    } else {
        alert('Chart data not found.');
    }
};

window.deleteFromLibrary = (id) => {
    if (!confirm('Are you sure you want to delete this chart?')) return;

    let lib = getLibrary();
    lib = lib.filter(e => e.id !== id);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(lib));
    openLibraryModal(); // Refresh list
};

// Auto-fill from localStorage (Shared with Basic View)
try {
    const savedReq = localStorage.getItem('cael_last_request');
    if (savedReq) {
        const data = JSON.parse(savedReq);
        const dateEl = document.getElementById('date');
        const timeEl = document.getElementById('time');
        const cityEl = document.getElementById('city');
        const stateEl = document.getElementById('state');

        if (dateEl && data.date) dateEl.value = data.date;
        if (cityEl && data.city) cityEl.value = data.city;
        if (stateEl && data.state) stateEl.value = data.state;

        // Handle time slightly more carefully
        if (timeEl && data.time) {
            timeEl.value = data.time;
        }

        // If the saved request implied 'time unknown' (often defaulted to 12:00), 
        // we might check the unknown toggle?
        // Basic View logic: if unknown, value is 12:00. 
        // We'll just set the value for now.
    }
} catch (e) { console.warn('Failed to autoload data', e); }
