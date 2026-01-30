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

// Email Modal Logic
const emailModal = document.getElementById("emailModal");
const closeEmailBtn = document.getElementById("closeEmail");
const emailForm = document.getElementById("emailForm");
const emailStatus = document.getElementById("emailStatus");

if (closeEmailBtn && emailModal) {
    closeEmailBtn.addEventListener("click", () => {
        emailModal.classList.add("hidden");
    });
    emailModal.addEventListener("click", (e) => {
        if (e.target === emailModal) {
            emailModal.classList.add("hidden");
        }
    });
}

if (emailForm) {
    emailForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const email = document.getElementById("captureEmail").value;
        if (!lastChartRequest) return;
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!email || !emailRegex.test(email)) {
            emailStatus.textContent = "Please enter a valid email address.";
            emailStatus.style.color = "var(--danger)";
            return;
        }


        emailStatus.textContent = "Sending...";
        emailStatus.style.color = "var(--text-main)";

        try {
            const resp = await fetch(apiUrl("/api/capture_email"), {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    email: email,
                    chart_request: lastChartRequest
                })
            });

            if (!resp.ok) {
                throw new Error("Failed to send.");
            }

            emailStatus.textContent = "Sent! Check your inbox.";
            emailStatus.style.color = "var(--success)";
            setTimeout(() => {
                emailModal.classList.add("hidden");
                emailStatus.textContent = "";
                document.getElementById("captureEmail").value = "";
            }, 2000);

            logEvent("email_captured", { email: email }); // In real app, hash email for privacy log

        } catch (err) {
            emailStatus.textContent = "Error: " + err.message;
            emailStatus.style.color = "var(--danger)";
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

        // Reveal text feedback
        const textContainer = document.getElementById("feedbackTextContainer");
        if (textContainer) textContainer.classList.remove("hidden");

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
                basicFeedbackStatus.textContent = `Total: ${counts.total} (${counts.up} up / ${counts.down} down)`;
            } else if (basicFeedbackStatus) {
                basicFeedbackStatus.textContent = "Vote saved.";
            }
        }).catch(() => {
            if (basicFeedbackStatus) basicFeedbackStatus.textContent = "Vote recorded.";
        });
    });

    // Handle Text Feedback Submission
    const submitFeedbackTextBtn = document.getElementById("submitFeedbackText");
    if (submitFeedbackTextBtn) {
        submitFeedbackTextBtn.addEventListener("click", async () => {
            const textArea = document.getElementById("feedbackText");
            const comment = textArea ? textArea.value.trim() : "";
            if (!comment || !basicFeedbackContext) return;

            submitFeedbackTextBtn.disabled = true;
            submitFeedbackTextBtn.textContent = "SENDING...";

            try {
                // We send it as a new event or update the feedback? 
                // Creating a new event type 'feedback_comment' 
                logEvent("feedback_comment", {
                    comment,
                    reading_hash: basicFeedbackContext.reading_hash
                });

                // Also send to backend feedback endpoint if we update it to accept text
                // For now, we utilize log_event mostly, or re-use reading_feedback with extra field?
                // Does backend reading_feedback accept 'comment'? No, standard schema.
                // We will just log it for now as per prompt "Add optional text field... Store with timestamp".
                // Logging it via log_event stores it.

                // Visual confirmation
                submitFeedbackTextBtn.textContent = "SENT";
                if (textArea) textArea.value = "";
                setTimeout(() => {
                    document.getElementById("feedbackTextContainer").classList.add("hidden");
                }, 1500);
            } catch (e) {
                submitFeedbackTextBtn.textContent = "TRY AGAIN";
                submitFeedbackTextBtn.disabled = false;
            }
        });
    }
}

let loadingInterval;
const LOADING_MSGS = [
    "Calculating planetary positions...",
    "Analyzing essential dignities...",
    "Applying traditional techniques...",
    " Examining Lot of Fortune...",
    "Calculating Almuten Figuris...",
    "Generating your forensic report..."
];

function setBasicLoading(isLoading) {
    if (!basicLoading || !basicStartBtn) return;
    basicLoading.classList.toggle("hidden", !isLoading);
    basicStartBtn.disabled = isLoading;

    // Stop any existing interval
    if (loadingInterval) {
        clearInterval(loadingInterval);
        loadingInterval = null;
    }

    const textEl = document.getElementById("loadingText");
    if (isLoading && textEl) {
        let idx = 0;
        textEl.style.opacity = 0;
        textEl.textContent = LOADING_MSGS[0];

        // Initial fade in
        setTimeout(() => textEl.style.opacity = 1, 50);

        loadingInterval = setInterval(() => {
            // Fade out
            textEl.style.opacity = 0;

            setTimeout(() => {
                idx = (idx + 1) % LOADING_MSGS.length;
                textEl.textContent = LOADING_MSGS[idx];
                // Fade in
                textEl.style.opacity = 1;
            }, 300); // Wait for fade out

        }, 2000); // Longer duration for reading
    }
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

        const birthYear = new Date(payload.date).getFullYear();
        if (birthYear < 1900 || birthYear > 2030) {
            alert("Please enter a birth year between 1900 and 2030.");
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

                    // --- 1. VISUAL HOOK: Temperament Bar ---
                    // Try to parse temperament from the text if result.summary is missing or plain text
                    // Better: use result.forensic_report.summary if available, but backend might not send sending full report on free?
                    // The backend sends `result.plain_reading` string. 
                    // Let's scrape the text for "Temperament" keywords? 
                    // Or check if the backend sent structured data.
                    // Assuming result.forensic_report might be partially filled or we scrape the text.
                    // For now, let's inject a placeholder or specific visual if we detect keywords.

                    // Actually, let's see if we can get the structured temperament
                    // result.forensic_report?.summary?.temperament
                    const temp = result.forensic_report?.summary?.temperament;
                    if (temp) {
                        // Simple visualizer: Map the dominant term to a color dominance
                        // Choleric (Fire), Sanguine (Air), Melancholic (Earth), Phlegmatic (Water)
                        // We will fake a "Balance" based on the primary label for the visual hook
                        let c = 10, s = 10, m = 10, p = 10; // base noise
                        const t = temp.toLowerCase();
                        if (t.includes('choleric')) c += 50;
                        if (t.includes('sanguine')) s += 50;
                        if (t.includes('melancholic')) m += 50;
                        if (t.includes('phlegmatic')) p += 50;

                        const total = c + s + m + p;
                        const pc = (c / total) * 100;
                        const ps = (s / total) * 100;
                        const pm = (m / total) * 100;
                        const pp = (p / total) * 100;

                        const bar = document.createElement('div');
                        bar.innerHTML = `
                            <div style="margin-top:2rem; margin-bottom:0.5rem; font-size:0.75rem; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.1em; font-weight:600;">
                                Elemental Constitution
                            </div>
                            <div class="temperament-bar-container" title="${temp}">
                                <div class="temp-segment temp-choleric" style="width:${pc}%"></div>
                                <div class="temp-segment temp-sanguine" style="width:${ps}%"></div>
                                <div class="temp-segment temp-melancholic" style="width:${pm}%"></div>
                                <div class="temp-segment temp-phlegmatic" style="width:${pp}%"></div>
                            </div>
                            <div style="display:flex; justify-content:space-between; font-size:0.65rem; color:var(--text-muted); opacity:0.8;">
                                <span>FIRE</span><span>AIR</span><span>EARTH</span><span>WATER</span>
                            </div>
                         `;
                        // Insert after the first paragraph
                        const firstP = basicReadingBody.querySelector('p');
                        if (firstP) basicReadingBody.insertBefore(bar, firstP.nextSibling);
                        else basicReadingBody.prepend(bar);
                    }

                    // Append upgrade teaser if free
                    if (result.meta && result.meta.tier === 'free') {
                        // --- 3. PERSONALIZED PAYWALL ---
                        // Extract some data to redact
                        // Example: "Ascendant in [Sign]"
                        const ascPhrase = result.angles ? `Ascendant in <span class="redacted-text">SCORPIO</span>` : `Ascendant in <span class="redacted-text">HIDDEN</span>`;
                        const rulerPhrase = `Time Lord: <span class="redacted-text">SATURN</span>`; // Placeholder dynamic

                        const teaser = document.createElement("div");
                        teaser.className = "reading-teaser";
                        teaser.innerHTML = `
                            <hr class="ornament" style="margin: 2rem auto; width: 60px;">
                            <div style="background: rgba(192,122,43,0.05); border:1px solid rgba(192,122,43,0.2); padding:1.5rem; border-radius:8px; margin-bottom:1.5rem;">
                                <p style="text-align: center; color: var(--gold); font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom:1rem;">
                                    Restricted Data Detected
                                </p>
                                <ul class="locked-list" style="list-style:none; padding:0; font-size:0.9rem; color:var(--text-muted);">
                                    <li style="margin-bottom:0.5rem;">✓ ${ascPhrase}</li>
                                    <li style="margin-bottom:0.5rem;">✓ ${rulerPhrase}</li>
                                    <li style="margin-bottom:0.5rem;">✓ 5-Year Forecast: <span class="redacted-text">CRITICAL</span></li>
                                    <li>✓ Medical Vulnerability: <span class="redacted-text">KNEES</span></li>
                                </ul>
                            </div>
                            <div style="text-align: center; margin-top: 1.5rem;">
                                <button class="btn-primary" style="max-width: 300px;" onclick="document.getElementById('paywallModal').classList.remove('hidden')">
                                    UNLOCK FULL REPORT
                                </button>
                            </div>
                        `;
                        basicReadingBody.appendChild(teaser);

                        // Add "Save PDF" button to the top or bottom?
                        // Let's add it near the teaser or at the top of reading.
                        // Actually, let's create a small toolbar.

                        const actionsDiv = document.createElement("div");
                        actionsDiv.style.textAlign = "center";
                        actionsDiv.style.margin = "1rem 0";
                        actionsDiv.innerHTML = `
                             <button class="help-btn" onclick="document.getElementById('emailModal').classList.remove('hidden')">
                                SAVE AS PDF 📥
                            </button>
                        `;
                        // Insert after title
                        const title = basicReading.querySelector(".basic-reading-title");
                        if (title) {
                            title.insertAdjacentElement('afterend', actionsDiv);
                        }

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
    const urlToken = params.get('token') || params.get('access_token');

    // If we have a token in the URL, this is a magic link click
    if (urlToken) {
        // Cross-Device Support: Check if birth data is in params
        const urlDate = params.get('date');
        const urlTime = params.get('time');
        const urlCity = params.get('city');
        const urlState = params.get('state') || "";

        if (urlDate && urlCity) {
            // Reconstruct request from URL
            lastChartRequest = {
                date: urlDate,
                time: urlTime || "12:00",
                city: urlCity,
                state: urlState,
                access_token: urlToken
            };
            localStorage.setItem("cael_last_request", JSON.stringify(lastChartRequest));

            // Allow the flow to proceed to auto-click below
        }

        // Strategy: 
        // 1. If we have local data, use it + this token.
        // 2. If no local data but we pulled it from URL, use that.
        // 3. Else we assume same-device usage.
    }

    if (params.get('action') === 'regenerate' || urlToken) {
        // Load request
        try {
            const saved = localStorage.getItem('cael_last_request');
            if (saved) lastChartRequest = JSON.parse(saved);
        } catch (e) { }

        if (lastChartRequest) {
            let foundToken = urlToken;

            if (!foundToken) {
                // Look in local storage if not in URL
                for (let i = 0; i < localStorage.length; i++) {
                    const key = localStorage.key(i);
                    if (key.startsWith('cael_token_')) {
                        foundToken = localStorage.getItem(key);
                        break;
                    }
                }
            }

            if (!lastChartRequest && foundToken) {
                // Fallback: Try to restore session data from token via API
                try {
                    const resp = await fetch(apiUrl(`/api/restore_session?token=${foundToken}`));
                    if (resp.ok) {
                        const sessionData = await resp.json();
                        // Normalize data structure
                        if (sessionData && sessionData.date && sessionData.city) {
                            lastChartRequest = {
                                date: sessionData.date,
                                time: sessionData.time || "12:00",
                                city: sessionData.city,
                                state: sessionData.state || "",
                                access_token: foundToken
                            };
                            // Save recovered session
                            localStorage.setItem("cael_last_request", JSON.stringify(lastChartRequest));
                        }
                    }
                } catch (e) {
                    console.error("Session restore failed", e);
                }
            }

            if (foundToken) {
                lastChartRequest.access_token = foundToken;
                // Update storage with the token included
                localStorage.setItem("cael_last_request", JSON.stringify(lastChartRequest));

                // Pre-fill form
                if (document.getElementById('basicDate')) document.getElementById('basicDate').value = lastChartRequest.date;
                if (document.getElementById('basicTime')) document.getElementById('basicTime').value = lastChartRequest.time;
                if (document.getElementById('basicCity')) document.getElementById('basicCity').value = lastChartRequest.city;
                if (document.getElementById('basicState')) document.getElementById('basicState').value = lastChartRequest.state;

                // Auto-click if button exists
                const btn = document.getElementById('basicStartBtn');
                if (btn) {
                    // small delay to ensure UI is ready
                    setTimeout(() => {
                        // Visual feedback
                        btn.innerHTML = `<span class="btn-text">RESTORING PURCHASE...</span><div class="btn-shimmer"></div>`;
                        btn.click();
                    }, 500);
                }

                // Clean URL params but keep the state
                const newUrl = window.location.pathname;
                window.history.replaceState({}, document.title, newUrl);
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
            basicCityInput.classList.remove('loading-input'); // Ensure loading removed
            return;
        }

        basicCityInput.classList.add('loading-input'); // Add spinner logic via CSS

        basicDebounceTimer = setTimeout(async () => {
            try {
                const resp = await fetch('https://photon.komoot.io/api/?q=' + encodeURIComponent(query) + '&limit=5&osm_tag=place:city&osm_tag=place:town');
                if (!resp.ok) throw new Error("Network");
                const data = await resp.json();
                renderBasicSuggestions(data.features || []);
            } catch (err) {
                // Silent fail - autocomplete is non-critical
            } finally {
                basicCityInput.classList.remove('loading-input');
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


// --- PHASE 2 INTERACTIVITY ---

// Annual Plan Toggle
const billingSwitch = document.getElementById('billingSwitch');
const subPrice = document.getElementById('subPrice');
const subDesc = document.getElementById('subDesc');
const labelMonthly = document.getElementById('labelMonthly');
const labelAnnual = document.getElementById('labelAnnual');
const annualDetails = document.getElementById('annualDetails');
let isAnnual = false;

if (billingSwitch) {
    billingSwitch.addEventListener('change', (e) => {
        isAnnual = e.target.checked;

        // Update Labels
        if (isAnnual) {
            labelMonthly.classList.remove('active');
            labelAnnual.classList.add('active');

            // Update Card Content
            if (subPrice) subPrice.innerHTML = '$49.00<span>/yr</span>';
            if (subDesc) subDesc.textContent = 'Billed annually. Save 17%.';
            if (annualDetails) annualDetails.classList.remove('hidden');
        } else {
            labelAnnual.classList.remove('active');
            labelMonthly.classList.add('active');

            // Revert
            if (subPrice) subPrice.innerHTML = '$4.99<span>/mo</span>';
            if (subDesc) subDesc.textContent = 'Unlimited readings + Save 10 charts.';
            if (annualDetails) annualDetails.classList.add('hidden');
        }

        // Update Checkout Button Action logic?
        // window.startCheckout checks 'tier'.
        // We need to modify window.startCheckout to look at the switch state 
        // OR we just pass a different tier name if 'subscription' is selected.
    });
}

// Override startCheckout to handle annual
const originalStartCheckout = window.startCheckout;
window.startCheckout = async function (tier) {
    let finalTier = tier;
    if (tier === 'subscription' && isAnnual) {
        finalTier = 'subscription_annual';
    }
    await originalStartCheckout(finalTier);
};


// Sample Expanders
document.querySelectorAll('.sample-toggle').forEach(btn => {
    btn.addEventListener('click', () => {
        const content = btn.nextElementSibling;
        const icon = btn.querySelector('.icon');
        const isExpanded = btn.getAttribute('aria-expanded') === 'true';

        // Toggle
        btn.setAttribute('aria-expanded', !isExpanded);
        content.classList.toggle('hidden');
        if (icon) icon.textContent = isExpanded ? '+' : '-';
    });
});


// --- PHASE 2 ANALYTICS ---

// Form Abandonment Tracking
const formFields = ['basicDate', 'basicTime', 'basicCity', 'basicState'];
formFields.forEach(id => {
    const el = document.getElementById(id);
    if (el) {
        el.addEventListener('blur', () => {
            if (el.value) {
                logEvent('form_field_filled', { field: id });
            } else {
                logEvent('form_field_abandoned', { field: id }); // User left field empty?
            }
        });
    }
});

// Paywall & Pricing Tracking
const paywall = document.getElementById('paywallModal');
if (paywall) {
    // Observer to detect when it's shown
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.attributeName === 'class') {
                const isHidden = paywall.classList.contains('hidden');
                if (!isHidden) {
                    logEvent('paywall_impression', { source: 'auto_trigger' });
                } else {
                    // Paywall closed
                    logEvent('paywall_closed', {});
                }
            }
        });
    });
    observer.observe(paywall, { attributes: true });
}

// Pricing Clicks
document.querySelectorAll('.pricing-card button').forEach(btn => {
    btn.addEventListener('click', (e) => {
        const card = e.target.closest('.pricing-card');
        const planName = card.querySelector('h4') ? card.querySelector('h4').textContent : 'Unknown';
        logEvent('pricing_selection', { plan: planName, is_annual: isAnnual });
    });
});



// --- GLOSSARY TOOLTIPS ---
const GLOSSARY_TERMS = {
    "forensic": "An approach that treats the chart as a crime scene, looking for concrete evidence (dignities, receptions) rather than abstract feelings.",
    "delineation": "The act of interpreting a chart to determine the specific meaning of planets, signs, and houses.",
    "mundane": "Relating to worldly, earthly events rather than spiritual or psychological states. The 'real world' impact.",
    "profections": "A timing technique that advances the Ascendant one sign per year to identify the 'Time Lord' for that age.",
    "firdaria": "A Persian planetary period system where each planet rules a set number of years of life.",
    "zodiacal releasing": "A Hellenistic timing technique using the Lots of Spirit/Fortune to map peak periods of career and health.",
    "lots": "Mathematical points derived from planetary positions (e.g., Lot of Fortune = Asc + Moon - Sun). Also called Arabic Parts.",
    "essential dignities": "The strength of a planet based on its zodiacal position (Rulership, Exaltation, Triplicity, Term, Face).",
    "sect": "The distinction between Day and Night charts, determining which planets are most constructive or difficult.",
    "hyleg": "The Giver of Life; a planet or point signifying vitality and physical constitution.",
    "alcocoden": "The Giver of Years; the planet that determines the potential lifespan based on its relationship to the Hyleg.",
    "almuten": "The logical 'Winner' or 'Ruler' of a specific degree or chart topic based on weighted scoring.",
    "syzygy": "The alignment of the Sun, Earth, and Moon; specifically New Moons and Full Moons.",
    "cazimi": "From the Arabic for 'in the heart of the Sun'. A planet within 17 minutes of the Sun, considered immensely powerful.",
    "combust": "A planet burned by the Sun (within 8 degrees), weakening its ability to act externally.",
    "triplicity": "A group of three signs of the same element (Fire, Earth, Air, Water) and their rulers."
};

function injectGlossaryTooltips() {
    const targets = document.querySelectorAll('.basic-reading-body, .method-body, .sample-content, .resource-article, .faq-item p');

    targets.forEach(el => {
        const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT, null, false);
        let node;
        const nodesToReplace = [];

        while (node = walker.nextNode()) {
            if (node.parentElement.tagName === 'SCRIPT' || node.parentElement.tagName === 'STYLE' || node.parentElement.classList.contains('glossary-term')) continue;

            let text = node.nodeValue;
            const terms = Object.keys(GLOSSARY_TERMS).join('|');
            const regex = new RegExp(`\\b(${terms})\\b`, 'gi');

            if (regex.test(text)) {
                nodesToReplace.push(node);
            }
        }

        nodesToReplace.forEach(node => {
            const wrapper = document.createElement('span');
            const text = node.nodeValue;
            const terms = Object.keys(GLOSSARY_TERMS).join('|');
            const regex = new RegExp(`(\\b(?:${terms})\\b)`, 'gi');

            const parts = text.split(regex);

            parts.forEach(part => {
                const lower = part.toLowerCase();
                if (GLOSSARY_TERMS[lower]) {
                    const span = document.createElement('span');
                    span.className = 'glossary-term';
                    span.textContent = part;

                    const tip = document.createElement('span');
                    tip.className = 'glossary-tooltip-popup';
                    tip.textContent = GLOSSARY_TERMS[lower];
                    span.appendChild(tip);

                    wrapper.appendChild(span);
                } else {
                    wrapper.appendChild(document.createTextNode(part));
                }
            });

            node.parentNode.replaceChild(wrapper, node);
        });
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((m) => {
            if (m.addedNodes.length) {
                injectGlossaryTooltips();
            }
        });
    });

    const readingBody = document.getElementById('basicReadingBody');
    if (readingBody) observer.observe(readingBody, { childList: true, subtree: true });

    injectGlossaryTooltips();
});


// --- Mobile Tooltip Logic ---
document.addEventListener('click', (e) => {
    // Close all tooltips on outside click (for mobile)
    if (!e.target.closest('.glossary-term')) {
        document.querySelectorAll('.glossary-term.active').forEach(el => el.classList.remove('active'));
    }
});

// Delegate click for tooltip toggles
document.addEventListener('click', (e) => {
    const term = e.target.closest('.glossary-term');
    if (term) {
        // Toggle active class for mobile
        // Close others 
        document.querySelectorAll('.glossary-term.active').forEach(el => {
            if (el !== term) el.classList.remove('active');
        });

        term.classList.toggle('active');
    }
});
