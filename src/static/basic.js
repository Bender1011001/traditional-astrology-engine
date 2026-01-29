const API_BASE = window.CAEL_API_BASE || "";
const IS_GH_PAGES = window.location.hostname.endsWith("github.io");
const backendNotice = document.getElementById("backendNotice");
if (backendNotice && IS_GH_PAGES && !API_BASE) {
    backendNotice.classList.remove("hidden");
}

const LOG_ENABLED = !IS_GH_PAGES || API_BASE;
const LOG_SESSION_KEY = "cael_session_id";
let _sessionEnded = false;
const _sessionStart = Date.now();
const themeToggle = document.getElementById("themeToggle");

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

if (themeToggle) {
    themeToggle.addEventListener("click", () => {
        const current = document.documentElement.getAttribute("data-theme") || "light";
        const next = current === "dark" ? "light" : "dark";
        localStorage.setItem("cael_theme", next);
        applyTheme(next);
    });
}

function logEvent(eventType, payload = {}, options = {}) {
    if (!LOG_ENABLED) return;
    const body = {
        session_id: SESSION_ID,
        event_type: eventType,
        payload,
        ts: new Date().toISOString()
    };
    const url = apiUrl("/api/log_event");
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

function escapeHtml(value) {
    return String(value || "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/\"/g, "&quot;")
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

const basicForm = document.getElementById("basicForm");
const basicLoading = document.getElementById("basicLoading");
const basicReading = document.getElementById("basicReading");
const basicReadingBody = document.getElementById("basicReadingBody");
const basicStartBtn = document.getElementById("basicStartBtn");
const basicTimeInput = document.getElementById("basicTime");
const basicTimeUnknown = document.getElementById("basicTimeUnknown");
const basicTimeWarning = document.getElementById("basicTimeWarning");
const basicFeedback = document.getElementById("basicFeedback");
const basicFeedbackStatus = document.getElementById("basicFeedbackStatus");
let basicFeedbackContext = null;
let lastChartRequest = null; // Store for checkout

// Load last request from storage if available
try {
    const saved = localStorage.getItem("cael_last_request");
    if (saved) lastChartRequest = JSON.parse(saved);
} catch (e) { }


// Paywall Elements
const paywallModal = document.getElementById("paywallModal");
const closePaywallBtn = document.getElementById("closePaywall");

if (closePaywallBtn && paywallModal) {
    closePaywallBtn.addEventListener("click", () => {
        paywallModal.classList.add("hidden");
    });
    // Close on click outside
    paywallModal.addEventListener("click", (e) => {
        if (e.target === paywallModal) {
            paywallModal.classList.add("hidden");
        }
    });
}

window.startCheckout = async function (tier) {
    if (!lastChartRequest) {
        alert("Please generate a chart first.");
        return;
    }

    const btn = document.querySelector(`button[onclick="window.startCheckout('${tier}')"]`);
    const originalText = btn ? btn.innerText : "";
    if (btn) {
        btn.innerText = "PROCESSING...";
        btn.disabled = true;
    }

    try {
        const payload = {
            tier: tier,
            chart_request: lastChartRequest,
            success_url: window.location.origin + "/success.html",
            cancel_url: window.location.href
        };

        const response = await fetch(apiUrl("/api/create-checkout"), {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Checkout failed");
        }

        const data = await response.json();
        if (data.checkout_url) {
            window.location.href = data.checkout_url;
        } else {
            throw new Error("No checkout URL returned");
        }
    } catch (err) {
        alert("Payment initialization failed: " + err.message);
        if (btn) {
            btn.innerText = originalText;
            btn.disabled = false;
        }
    }
};


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

function resetBasicFeedback(context) {
    basicFeedbackContext = context || null;
    if (!basicFeedback) return;
    basicFeedback.classList.toggle("hidden", !basicFeedbackContext);
    if (basicFeedbackStatus) basicFeedbackStatus.textContent = "";
    basicFeedback.querySelectorAll(".feedback-btn").forEach((btn) => {
        btn.disabled = false;
        btn.classList.remove("selected");
    });
    delete basicFeedback.dataset.submitted;
}

if (basicFeedback) {
    basicFeedback.addEventListener("click", (e) => {
        const btn = e.target.closest(".feedback-btn");
        if (!btn || !basicFeedbackContext) return;
        if (basicFeedback.dataset.submitted === "true") return;
        const vote = btn.dataset.vote;
        if (!vote) return;

        basicFeedback.dataset.submitted = "true";
        basicFeedback.querySelectorAll(".feedback-btn").forEach((b) => {
            b.disabled = true;
            b.classList.toggle("selected", b === btn);
        });
        if (basicFeedbackStatus) basicFeedbackStatus.textContent = "Saving vote...";

        logEvent("reading_feedback", {
            vote,
            source: "basic_reading",
            reading_hash: basicFeedbackContext.reading_hash,
            birth: basicFeedbackContext.birth,
            meta: basicFeedbackContext.meta,
            time_unknown: basicFeedbackContext.time_unknown
        });

        fetch(apiUrl("/api/reading_feedback"), {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                reading_hash: basicFeedbackContext.reading_hash,
                vote,
                source: "basic_reading",
                birth: basicFeedbackContext.birth,
                meta: basicFeedbackContext.meta,
                time_unknown: basicFeedbackContext.time_unknown,
                session_id: SESSION_ID,
                ts: new Date().toISOString()
            })
        }).then(async (resp) => {
            if (!resp.ok) throw new Error("Vote not saved.");
            return resp.json();
        }).then((data) => {
            const counts = data && data.counts ? data.counts : null;
            if (basicFeedbackStatus && counts) {
                basicFeedbackStatus.textContent = `Total votes: ${counts.total} (${counts.up} up / ${counts.down} down)`;
            } else if (basicFeedbackStatus) {
                basicFeedbackStatus.textContent = "Vote saved.";
            }
        }).catch(() => {
            if (basicFeedbackStatus) basicFeedbackStatus.textContent = "Vote recorded. Totals unavailable.";
        });
    });
}

function setBasicLoading(isLoading) {
    if (!basicLoading || !basicStartBtn) return;
    basicLoading.classList.toggle("hidden", !isLoading);
    basicStartBtn.disabled = isLoading;
}

if (basicForm) {
    basicForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const timeUnknown = basicTimeUnknown ? basicTimeUnknown.checked : false;
        const timeValue = basicTimeInput ? basicTimeInput.value : "";
        const payload = {
            date: document.getElementById("basicDate").value,
            time: timeUnknown && !timeValue ? "12:00" : timeValue,
            city: document.getElementById("basicCity").value,
            state: document.getElementById("basicState").value
        };

        if (!payload.date || !payload.city || (!payload.time && !timeUnknown)) {
            alert("Please enter your birth date, time, and city.");
            return;
        }

        setBasicLoading(true);
        if (basicReading) basicReading.classList.add("hidden");
        if (basicReadingBody) basicReadingBody.innerHTML = "";
        resetBasicFeedback(null);



        // Store for checkout
        lastChartRequest = payload;
        localStorage.setItem("cael_last_request", JSON.stringify(payload));


        logEvent("basic_chart_request", { form: payload });


        try {
            const response = await fetch(apiUrl("/api/calculate"), {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.detail || "No response from engine.");
            }

            const result = await response.json();
            logEvent("basic_chart_result", { result });

            const reading = result.plain_reading || "";
            if (reading) {
                if (basicReadingBody) {
                    basicReadingBody.innerHTML = formatPlainReading(reading);
                    // Append upgrade teaser if free
                    if (result.meta && result.meta.tier === 'free') {
                        const teaser = document.createElement("div");
                        teaser.className = "reading-teaser";
                        teaser.innerHTML = `
                            <hr class="ornament" style="margin: 2rem auto; width: 60px;">
                            <p style="text-align: center; color: var(--gold); font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase;">
                                Reading Truncated
                            </p>
                            <div style="text-align: center; margin-top: 1.5rem;">
                                <button class="btn-primary" style="max-width: 300px;" onclick="document.getElementById('paywallModal').classList.remove('hidden')">
                                    UNLOCK FULL REPORT
                                </button>
                            </div>
                        `;
                        basicReadingBody.appendChild(teaser);

                        // Show modal automatically after a slight delay
                        setTimeout(() => {
                            if (paywallModal) paywallModal.classList.remove("hidden");
                        }, 2500);
                    }
                }
                if (basicReading) basicReading.classList.remove("hidden");
                resetBasicFeedback({
                    reading_hash: hashString(reading),
                    birth: payload,
                    meta: result.meta || null,
                    time_unknown: timeUnknown
                });
            } else {
                if (basicReadingBody) basicReadingBody.innerHTML = "<p>Reading unavailable. Please try again.</p>";
                if (basicReading) basicReading.classList.remove("hidden");
                resetBasicFeedback(null);
            }

        } catch (error) {
            logEvent("basic_chart_error", { message: error.message || String(error) });
            alert(error.message);
        } finally {
            setBasicLoading(false);
        }
    });
}

// Auto-Regenerate Check
async function checkRegenerate() {
    const params = new URLSearchParams(window.location.search);
    if (params.get('action') === 'regenerate') {
        // Load request
        try {
            const saved = localStorage.getItem('cael_last_request');
            if (saved) lastChartRequest = JSON.parse(saved);
        } catch (e) { }

        if (lastChartRequest) {
            // Check if we have a token for this request?
            // Since we don't have the hash yet, we can check localStorage keys or just assume content
            // However, success.html passes nothing about the token, it stores it in localStorage under the hash.
            // We need the hash.
            // Let's rely on success.html logic which stored the token.
            // But basic.js needs to find it.

            // HACK: Iterate localStorage to find a recent token?
            // OR: Calculate hash here? We implemented helper for hash but not sha256.
            // Wait, we can iterate all keys starting with cael_token_

            let foundToken = null;
            for (let i = 0; i < localStorage.length; i++) {
                const key = localStorage.key(i);
                if (key.startsWith('cael_token_')) {
                    // Use the most recent one? Or just any?
                    // Ideally we check timestamp but we didn't store it.
                    foundToken = localStorage.getItem(key);
                    // For MVP we assume the last action was this purchase.
                    break;
                }
            }

            if (foundToken) {
                lastChartRequest.access_token = foundToken;

                // Pre-fill form
                if (document.getElementById('basicDate')) document.getElementById('basicDate').value = lastChartRequest.date;
                if (document.getElementById('basicTime')) document.getElementById('basicTime').value = lastChartRequest.time;
                if (document.getElementById('basicCity')) document.getElementById('basicCity').value = lastChartRequest.city;
                if (document.getElementById('basicState')) document.getElementById('basicState').value = lastChartRequest.state;

                // Auto-click if button exists
                const btn = document.getElementById('basicStartBtn');
                if (btn) {
                    // small delay to ensure UI is ready
                    setTimeout(() => btn.click(), 500);
                }

                // Clean URL
                window.history.replaceState({}, document.title, window.location.pathname);
            }
        }
    }
}
checkRegenerate();


// City Autocomplete Logic
const basicCityInput = document.getElementById('basicCity');
const basicSuggestionsBox = document.getElementById('basicCitySuggestions');
let basicDebounceTimer;

if (basicCityInput && basicSuggestionsBox) {
    basicCityInput.addEventListener('input', () => {
        clearTimeout(basicDebounceTimer);
        const query = basicCityInput.value;
        if (query.length < 3) {
            basicSuggestionsBox.style.display = 'none';
            basicCityInput.setAttribute('aria-expanded', 'false');
            return;
        }

        basicDebounceTimer = setTimeout(async () => {
            try {
                const resp = await fetch('https://photon.komoot.io/api/?q=' + encodeURIComponent(query) + '&limit=5&osm_tag=place:city&osm_tag=place:town');
                if (!resp.ok) return;
                const data = await resp.json();
                renderBasicSuggestions(data.features || []);
            } catch (err) {
                console.error('Autocomplete error', err);
            }
        }, 300);
    });

    document.addEventListener('click', (e) => {
        if (e.target !== basicCityInput) {
            basicSuggestionsBox.style.display = 'none';
            if (basicCityInput) basicCityInput.setAttribute('aria-expanded', 'false');
        }
    });
}

function renderBasicSuggestions(features) {
    if (!basicSuggestionsBox) return;
    basicSuggestionsBox.innerHTML = '';
    
    if (!features || features.length === 0) {
        basicSuggestionsBox.style.display = 'none';
        if (basicCityInput) basicCityInput.setAttribute('aria-expanded', 'false');
        return;
    }

    features.forEach((f, index) => {
        const item = document.createElement('div');
        item.className = 'suggestion-item';
        item.setAttribute('role', 'option');
        item.id = 'city-option-' + index;
        
        const city = f.properties.name;
        const state = f.properties.state || f.properties.country;
        const country = f.properties.country;
        
        let label = city;
        if (state) label += ', ' + state;
        if (country && country !== state) label += ', ' + country;

        item.textContent = label;
        
        item.onclick = () => {
            basicCityInput.value = city;
            const stateInput = document.getElementById('basicState');
            if (stateInput && state) {
                stateInput.value = state;
            }
            
            basicSuggestionsBox.style.display = 'none';
            basicCityInput.setAttribute('aria-expanded', 'false');
        };
        basicSuggestionsBox.appendChild(item);
    });
    basicSuggestionsBox.style.display = 'block';
    if (basicCityInput) basicCityInput.setAttribute('aria-expanded', 'true');
}

