/**
 * reading-app.js — B2C Reading Flow
 * 
 * Flow:
 * 1. User fills birth form → submit
 * 2. Free: Calls /api/v1/premium/guest/request → polls → shows full reading (up to IP limit)
 * 3. After visitor limit hit: Shows teaser + paywall ($25 Full Reading / $69 Premium)
 * 4. Paid: Redirects to Stripe → returns with session_id → calls /generate-paid → polls → shows full reading
 */

import { apiFetch } from './api.js';
import { renderChartWheel } from './chart-graphics.js';

// ─── State ───
let chartPayload = null;
let currentReadingContext = null;
let loadingStartTime = null;
let elapsedTimerInterval = null;

function trackConversionEvent(eventName, params = {}) {
    try {
        if (typeof window.gtag === "function") {
            window.gtag("event", eventName, {
                event_category: "reading_funnel",
                ...params,
            });
        }
    } catch (_) {
        // Analytics must never interrupt chart generation or checkout.
    }
}

window.printReading = function () {
    trackConversionEvent("print_save_pdf");
    window.print();
};

// ─── Loading Messages ───
const LOADING_MSGS = [
    "Locating your birth coordinates...",
    "Calculating planetary positions from the Swiss Ephemeris...",
    "Determining sect — day chart or night chart...",
    "Scoring essential dignities...",
    "Computing the Lot of Fortune...",
    "Analyzing mutual receptions...",
    "Running annual profections...",
    "Synthesizing your personal reading...",
];

// ─── DOM Ready ───
document.addEventListener("DOMContentLoaded", () => {
    setupForm();
    setupTimeUnknownToggle();
    checkForPaidReturn();

    // Export & Share Handlers
    const exportPdfBtn = document.getElementById('exportPdfBtn');
    const shareChartBtn = document.getElementById('shareChartBtn');

    if (exportPdfBtn) {
        exportPdfBtn.addEventListener('click', () => {
            printReading();
        });
    }

    if (shareChartBtn) {
        shareChartBtn.addEventListener('click', async () => {
            const chartUrl = window.location.href;
            if (navigator.share) {
                try {
                    await navigator.share({
                        title: 'My Traditional Astrology Chart',
                        text: 'Check out my classical astrology reading!',
                        url: chartUrl
                    });
                } catch (err) {
                    console.log('Share error:', err);
                }
            } else {
                navigator.clipboard.writeText(chartUrl).then(() => {
                    const originalText = shareChartBtn.textContent;
                    shareChartBtn.textContent = '✦ Copied to Clipboard!';
                    setTimeout(() => { shareChartBtn.textContent = originalText; }, 2000);
                });
            }
        });
    }
});

// ─── Form Setup ───
function setupForm() {
    const form = document.getElementById("chartForm");
    if (!form) return;

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const timeUnknown = document.getElementById("timeUnknown")?.checked;
        const timeInput = document.getElementById("birthTime");

        chartPayload = {
            date: document.getElementById("birthDate").value,
            time: timeUnknown && !timeInput?.value ? "12:00" : (timeInput?.value || "12:00"),
            city: document.getElementById("birthCity").value,
            state: document.getElementById("birthState")?.value || "",
            name: "Guest",
            time_unknown: Boolean(timeUnknown),
        };

        if (!chartPayload.date || !chartPayload.city) {
            shakeForm();
            return;
        }

        // Save for after payment redirect
        localStorage.setItem("ta_chart_payload", JSON.stringify(chartPayload));

        trackConversionEvent("free_chart_submit");
        showLoading();
        await requestFreeReading(chartPayload);
    });
}

function setupTimeUnknownToggle() {
    const checkbox = document.getElementById("timeUnknown");
    const timeInput = document.getElementById("birthTime");
    if (!checkbox || !timeInput) return;

    checkbox.addEventListener("change", () => {
        timeInput.required = !checkbox.checked;
        if (checkbox.checked && !timeInput.value) {
            timeInput.value = "12:00";
        }
    });
}

function shakeForm() {
    const card = document.getElementById("chartFormCard");
    if (!card) return;
    card.style.animation = "none";
    requestAnimationFrame(() => {
        card.style.animation = "shake 0.4s ease-out";
    });
}

// ─── Free Reading (Instant) ───
async function requestFreeReading(payload) {
    try {
        const resp = await apiFetch("/api/v1/premium/guest/request", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        if (!resp.ok) {
            if (resp.status === 402) {
                // Free limit reached — show paywall
                hideLoading();
                trackConversionEvent("free_chart_paywall", { reason: "visitor_limit" });
                showPaywall();
                return;
            }
            const err = await resp.json().catch(() => ({}));
            let msg = "Request failed.";
            if (Array.isArray(err?.detail)) {
                msg = err.detail.map(d => `${d.loc ? d.loc.slice(-1)[0] : 'field'}: ${d.msg}`).join("; ");
            } else if (typeof err?.detail === "string") {
                msg = err.detail;
            } else if (err?.detail?.message) {
                msg = err.detail.message;
            }
            throw new Error(msg);
        }

        const data = await resp.json();

        // Instant free reading (new flow) — no polling needed
        if (data.instant && data.reading_html) {
            hideLoading();
            trackConversionEvent("free_chart_success", {
                free_readings_remaining: data.free_readings_remaining,
                chart_event_id: data.chart_event_id,
            });
            showFreeReading(
                data.reading_html,
                data.free_readings_remaining,
                data.chart_event_id,
                data.reading_hash,
                data.chart_summary
            );
            return;
        }

        // Legacy/paid flow — poll for completion
        if (data.task_id) {
            pollForCompletion(data.task_id, data.free_readings_remaining);
            return;
        }

        throw new Error("Unexpected response format.");
    } catch (err) {
        hideLoading();
        trackConversionEvent("free_chart_error", { error: String(err.message || err) });
        showError(err.message);
    }
}

// ─── Polling ───
function pollForCompletion(taskId, freeRemaining) {
    let msgIdx = 0;
    let attempts = 0;
    const maxAttempts = 120; // 10 minutes at 5s intervals

    const interval = setInterval(async () => {
        attempts++;
        updateLoadingMessage(LOADING_MSGS[msgIdx % LOADING_MSGS.length]);
        updateLoadingProgress(msgIdx % LOADING_MSGS.length);
        msgIdx++;

        if (attempts >= maxAttempts) {
            clearInterval(interval);
            hideLoading();
            showError("Generation timed out. Please try again.");
            return;
        }

        try {
            const resp = await apiFetch(`/api/v1/premium/guest/status/${taskId}`);
            if (!resp.ok) return;

            const data = await resp.json();

            if (data.status === "processing") {
                updateLoadingMessage("Synthesizing your personal reading...");
            } else if (data.status === "completed") {
                clearInterval(interval);
                hideLoading();
                showReading(data.result, freeRemaining);
            } else if (data.status === "failed") {
                clearInterval(interval);
                hideLoading();
                showError("Generation failed. Please try again.");
            }
        } catch (_) {
            // Suppressed: non-critical poll error; retry will occur next interval
        }
    }, 5000);
}

// ─── Post-Payment Return ───
function checkForPaidReturn() {
    const params = new URLSearchParams(window.location.search);
    const isPaid = params.get("paid") === "true";
    const sessionId = params.get("session_id");

    if (!isPaid || !sessionId) return;

    // Clean URL
    window.history.replaceState({}, document.title, "/");
    trackConversionEvent("paid_return");

    // Restore chart data
    try {
        chartPayload = JSON.parse(localStorage.getItem("ta_chart_payload"));
    } catch (e) {
        chartPayload = null;
    }

    // Trigger paid generation
    showLoading();
    updateLoadingMessage("Payment confirmed! Generating your premium reading...");
    generatePaidReading(sessionId);
}

async function generatePaidReading(sessionId) {
    try {
        const resp = await apiFetch(`/api/v1/guest/generate-paid?session_id=${encodeURIComponent(sessionId)}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: "{}",
        });

        if (!resp.ok) {
            const err = await resp.json().catch(() => ({}));
            throw new Error(err?.detail || "Could not start generation.");
        }

        const data = await resp.json();
        trackConversionEvent("paid_generation_started", { tier: data.tier || "unknown" });
        pollForCompletion(data.task_id, -1); // -1 = paid, no limit
    } catch (err) {
        hideLoading();
        trackConversionEvent("paid_generation_error", { error: String(err.message || err) });
        showError(err.message);
    }
}

// ─── UI: Show Free Reading (HTML, instant) ───
function showFreeReading(readingHtml, freeRemaining, chartEventId, readingHash, chartSummary) {
    const section = document.getElementById("readingSection");
    const content = document.getElementById("readingContent");
    if (!section || !content) return;

    currentReadingContext = {
        chart_event_id: chartEventId || null,
        reading_hash: readingHash || hashStr(JSON.stringify({ chartPayload, readingHtml })),
        source: "b2c_free_chart",
        birth: chartPayload,
        meta: {
            chart_summary: chartSummary || {},
            free_readings_remaining: freeRemaining,
        },
        time_unknown: Boolean(chartPayload?.time_unknown),
    };

    content.innerHTML = `
        ${buildInstantConversionBar(freeRemaining)}
        ${readingHtml}
        ${buildFeedbackWidget("free")}
    `;

    // Render the natal chart wheel if data is embedded in the reading HTML
    const wheelDataEl = content.querySelector('#chartWheelData');
    if (wheelDataEl) {
        try {
            const wheelData = JSON.parse(wheelDataEl.textContent);
            renderChartWheel(wheelData);
        } catch (e) {
            console.warn('Chart wheel render failed:', e);
        }
    }

    section.classList.remove("hidden");
    section.scrollIntoView({ behavior: "smooth", block: "start" });

    // Attach feedback & action handlers
    attachFeedbackHandlers(content, "free");
    const chartActions = document.getElementById("chartActions");
    if (chartActions) chartActions.classList.remove("hidden");

    // Kick off the free LLM premium trial simultaneously in the background
    kickOffFreePremiumTrial(chartPayload, chartEventId);
}

// ─── Free Premium Trial — Background LLM Kickoff ───────────────────────────
async function kickOffFreePremiumTrial(payload, chartEventId) {
    const content = document.getElementById("readingContent");
    if (!content) return;

    // Insert the top announcement banner at the very top of reading content
    const topBannerEl = document.createElement("div");
    topBannerEl.id = "premiumTrialTopBanner";
    topBannerEl.innerHTML = buildPremiumTrialTopBanner();
    content.insertAdjacentElement("afterbegin", topBannerEl);

    // Append the loading section below all existing content
    const loadingEl = document.createElement("div");
    loadingEl.id = "premiumTrialSection";
    loadingEl.innerHTML = buildPremiumLoadingSection();
    content.appendChild(loadingEl);

    try {
        const resp = await apiFetch("/api/v1/premium/free-trial/request", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        if (!resp.ok) {
            _hidePremiumTrialSection();
            return;
        }

        const data = await resp.json();

        if (data.status === "limit_reached") {
            _hidePremiumTrialSection();
            _hidePremiumTopBanner();
            trackConversionEvent("premium_trial_limit_reached");
            return;
        }

        if (data.status === "started" && data.task_id) {
            trackConversionEvent("premium_trial_started");
            pollForFreePremium(data.task_id, chartEventId);
            return;
        }

        _hidePremiumTrialSection();
    } catch (err) {
        _hidePremiumTrialSection();
        console.warn("Free premium trial kickoff failed (non-critical):", err);
    }
}

function _hidePremiumTrialSection() {
    const el = document.getElementById("premiumTrialSection");
    if (el) el.remove();
}

function _hidePremiumTopBanner() {
    const el = document.getElementById("premiumTrialTopBanner");
    if (el) el.remove();
}

// ─── Free Premium Trial — Polling ───────────────────────────────────────────
const PREMIUM_LOADING_MSGS = [
    "Calculating your full planetary picture...",
    "Analyzing sect, dignities, and mutual receptions...",
    "Mapping the annual profection year...",
    "Interpreting your Lot of Fortune...",
    "Synthesizing the firdaria time-lord sequence...",
    "Correlating fixed star influences...",
    "Drafting your forecast narrative...",
    "Finalizing your 10-year timeline...",
    "Running final editorial pass...",
    "Almost there — polishing the last sections...",
];

function pollForFreePremium(taskId, chartEventId) {
    let msgIdx = 0;
    let attempts = 0;
    const maxAttempts = 70; // ~5.8 min at 5s intervals

    const interval = setInterval(async () => {
        attempts++;
        _updatePremiumLoadingMessage(
            PREMIUM_LOADING_MSGS[msgIdx % PREMIUM_LOADING_MSGS.length],
            attempts,
            maxAttempts
        );
        msgIdx++;

        if (attempts >= maxAttempts) {
            clearInterval(interval);
            _hidePremiumTrialSection();
            _hidePremiumTopBanner();
            trackConversionEvent("premium_trial_timeout");
            return;
        }

        try {
            const resp = await apiFetch(`/api/v1/premium/guest/status/${taskId}`);
            if (!resp.ok) return;

            const data = await resp.json();

            if (data.status === "completed" && data.result) {
                clearInterval(interval);
                _renderFreePremiumResult(data.result, chartEventId);
                trackConversionEvent("premium_trial_completed");
            } else if (data.status === "failed") {
                clearInterval(interval);
                _hidePremiumTrialSection();
                _hidePremiumTopBanner();
                trackConversionEvent("premium_trial_failed");
            }
        } catch (_) {
            // Suppress poll errors; retry next interval
        }
    }, 5000);
}

function _updatePremiumLoadingMessage(msg, attempts, maxAttempts) {
    const msgEl = document.getElementById("premiumLoadingMsg");
    if (msgEl) {
        msgEl.style.opacity = "0";
        setTimeout(() => {
            msgEl.textContent = msg;
            msgEl.style.opacity = "1";
        }, 200);
    }
    const bar = document.getElementById("premiumLoadingBar");
    if (bar) {
        const pct = Math.min((attempts / maxAttempts) * 90, 90);
        bar.style.width = pct + "%";
    }
    const elapsed = document.getElementById("premiumLoadingElapsed");
    if (elapsed) {
        const secs = attempts * 5;
        const mins = Math.floor(secs / 60);
        const s = secs % 60;
        elapsed.textContent = mins > 0 ? `${mins}m ${s}s` : `${s}s`;
    }
}

function _renderFreePremiumResult(result, chartEventId) {
    const section = document.getElementById("premiumTrialSection");
    if (!section) return;

    const md = result?.report_markdown || "";
    const html = renderMarkdown(md);

    section.innerHTML = buildRenderedPremiumSection(html, chartEventId);

    // Update the top banner to reflect completion
    const topBanner = document.getElementById("premiumTrialTopBanner");
    if (topBanner) {
        topBanner.innerHTML = buildPremiumTrialTopBannerComplete();
    }

    section.scrollIntoView({ behavior: "smooth", block: "start" });

    attachFeedbackHandlers(section, "premium_trial");
    attachEmailCaptureHandler(section, chartEventId);
}

function buildInstantConversionBar(freeRemaining) {
    const remainingText = Number.isFinite(Number(freeRemaining)) && Number(freeRemaining) >= 0
        ? `<span>${Number(freeRemaining)} free chart${Number(freeRemaining) === 1 ? "" : "s"} left today</span>`
        : "";

    return `
        <div class="result-conversion-bar" aria-label="Full reading purchase options">
            <div class="result-conversion-copy">
                <div class="result-conversion-kicker">Chart generated</div>
                <h2>Unlock the complete reading while this chart is loaded.</h2>
                <p>Save the free preview as a PDF, or unlock houses, lots, fixed stars, time-lord periods, and the full forecast.</p>
                <div class="result-conversion-meta">
                    <span>No account</span>
                    <span>Stripe checkout</span>
                    ${remainingText}
                </div>
            </div>
            <div class="result-conversion-actions">
                <button class="btn-cta" onclick="startCheckout('full_reading')" id="checkoutFullTopBtn" data-default-label="Full Reading — $25">
                    Full Reading — $25
                </button>
                <button class="btn-cta btn-cta-secondary" onclick="startCheckout('premium_audit')" id="checkoutPremiumTopBtn" data-default-label="Complete Analysis — $69">
                    Complete Analysis — $69
                </button>
                <button class="btn-cta btn-cta-secondary" onclick="printReading()" data-default-label="Print / Save Preview PDF">
                    Print / Save Preview PDF
                </button>
            </div>
        </div>
    `;
}

// ─── UI: Show Paid Reading (Markdown, polled) ───
function showReading(result, freeRemaining) {
    const section = document.getElementById("readingSection");
    const content = document.getElementById("readingContent");
    if (!section || !content) return;

    const md = result?.report_markdown || "";
    const html = renderMarkdown(md);
    const traceData = result?.computation_trace || null;
    currentReadingContext = {
        chart_event_id: result?.chart_event_id || null,
        reading_hash: result?.reading_hash || result?.meta?.chart_hash || hashStr(JSON.stringify({ chartPayload, md })),
        source: freeRemaining < 0 ? "b2c_paid_reading" : "b2c_reading",
        birth: chartPayload,
        meta: result?.meta || {},
        time_unknown: Boolean(chartPayload?.time_unknown),
    };

    content.innerHTML = `
        <div class="reading-body">${html}</div>
        ${traceData ? buildTraceSection(traceData) : ''}
        ${buildPostReadingCTA(freeRemaining)}
        ${buildFeedbackWidget("free")}
    `;

    section.classList.remove("hidden");
    section.scrollIntoView({ behavior: "smooth", block: "start" });

    attachFeedbackHandlers(content, "free");
    const chartActions = document.getElementById("chartActions");
    if (chartActions) chartActions.classList.remove("hidden");

    if (traceData) attachTraceHandlers(content);
}

// ─── Computation Trace Renderer ───
function buildTraceSection(traceData) {
    if (!traceData || !traceData.steps || traceData.steps.length === 0) return '';

    const categories = traceData.categories || [];
    const steps = traceData.steps || [];

    const categoriesHtml = categories.map(cat => {
        const catSteps = steps.filter(s => s.category === cat);
        const catId = cat.replace(/[\W_]+/g, '-').toLowerCase();

        // Group by subsection
        const subsections = {};
        catSteps.forEach(s => {
            const key = s.subsection || '__main__';
            if (!subsections[key]) subsections[key] = [];
            subsections[key].push(s);
        });

        let stepsHtml = '';
        for (const [subKey, subSteps] of Object.entries(subsections)) {
            if (subKey !== '__main__') {
                stepsHtml += `<h4 class="trace-subsection-header">${escapeHtml(subKey)}</h4>`;
            }
            subSteps.forEach(s => {
                const inputsRows = Object.entries(s.inputs || {})
                    .map(([k, v]) => `<tr><td class="trace-input-key">${escapeHtml(k)}</td><td class="trace-input-val">${escapeHtml(String(v))}</td></tr>`)
                    .join('');
                
                const notesHtml = s.notes 
                    ? `<div class="trace-step-notes"><strong>📝 Note:</strong> ${escapeHtml(s.notes)}</div>` 
                    : '';

                stepsHtml += `
                    <div class="trace-step-card">
                        <div class="trace-step-header" onclick="this.parentElement.classList.toggle('trace-expanded')">
                            <span class="trace-step-num">Step ${s.step}</span>
                            <span class="trace-step-technique">${escapeHtml(s.technique)}</span>
                            <span class="trace-step-result-badge">${escapeHtml(String(s.result || ''))}</span>
                            <span class="trace-step-chevron">▸</span>
                        </div>
                        <div class="trace-step-body">
                            <div class="trace-section">
                                <div class="trace-label">📥 Inputs</div>
                                <table class="trace-inputs-table">${inputsRows}</table>
                            </div>
                            <div class="trace-section">
                                <div class="trace-label">📜 Rule</div>
                                <div class="trace-rule-text">${escapeHtml(s.rule || '')}</div>
                                <div class="trace-source-tag">— ${escapeHtml(s.source || '')}</div>
                            </div>
                            <div class="trace-section">
                                <div class="trace-label">🔢 Calculation</div>
                                <div class="trace-calc-text">${escapeHtml(s.calculation || '')}</div>
                            </div>
                            <div class="trace-section trace-result-section">
                                <div class="trace-label">✅ Result</div>
                                <div class="trace-result-text">${escapeHtml(String(s.result || ''))}</div>
                            </div>
                            ${notesHtml}
                        </div>
                    </div>
                `;
            });
        }

        return `
            <div class="trace-category-block" id="trace-${catId}">
                <h3 class="trace-category-title" onclick="this.classList.toggle('trace-collapsed'); this.nextElementSibling.classList.toggle('trace-hidden')">
                    <span class="trace-collapse-icon">▼</span>
                    ${escapeHtml(cat)}
                    <span class="trace-step-count">${catSteps.length} step${catSteps.length !== 1 ? 's' : ''}</span>
                </h3>
                <div class="trace-category-body trace-hidden">
                    ${stepsHtml}
                </div>
            </div>
        `;
    }).join('');

    // Build TOC
    const tocItems = categories.map(cat => {
        const catId = cat.replace(/[\W_]+/g, '-').toLowerCase();
        const count = steps.filter(s => s.category === cat).length;
        return `<li><a href="#trace-${catId}" onclick="event.preventDefault(); const el = document.getElementById('trace-${catId}'); el.scrollIntoView({behavior:'smooth'}); const title = el.querySelector('.trace-category-title'); if(title.classList.contains('trace-collapsed')){title.click();}">${escapeHtml(cat)}</a> <span class="trace-toc-count">(${count})</span></li>`;
    }).join('');

    return `
        <div class="trace-container" id="traceContainer">
            <div class="trace-header" onclick="document.getElementById('traceBody').classList.toggle('trace-hidden'); this.classList.toggle('trace-open')">
                <div class="trace-header-left">
                    <span class="trace-header-icon">⚙</span>
                    <div>
                        <h2 class="trace-header-title">Show Our Work</h2>
                        <p class="trace-header-subtitle">${traceData.total_steps} computation steps · ${categories.length} categories · ${Math.round(traceData.elapsed_ms || 0)}ms</p>
                    </div>
                </div>
                <span class="trace-header-chevron">▸</span>
            </div>
            <div class="trace-body trace-hidden" id="traceBody">
                <div class="trace-controls">
                    <input type="text" class="trace-search" id="traceSearch" placeholder="Search steps... (e.g. Sun, Domicile, Fortune)" oninput="filterTraceSteps(this.value)">
                    <div class="trace-buttons">
                        <button class="trace-btn" onclick="expandAllTrace()">Expand All</button>
                        <button class="trace-btn" onclick="collapseAllTrace()">Collapse All</button>
                    </div>
                </div>
                <div class="trace-toc">
                    <h4>Categories</h4>
                    <ul>${tocItems}</ul>
                </div>
                ${categoriesHtml}
                <div class="trace-footer">
                    <p>All calculations use pre-1700 traditional methods. Sources cited per step.</p>
                    <p>Historical Use Only. Not medical, financial, or legal advice.</p>
                </div>
            </div>
        </div>
    `;
}

function attachTraceHandlers(container) {
    // Search is handled via inline oninput — no additional setup needed
}

window.filterTraceSteps = function(query) {
    const q = query.toLowerCase().trim();
    document.querySelectorAll('.trace-step-card').forEach(card => {
        if (!q) {
            card.style.display = '';
            return;
        }
        const text = card.textContent.toLowerCase();
        card.style.display = text.includes(q) ? '' : 'none';
    });
    // Auto-expand categories with visible steps
    if (q) {
        document.querySelectorAll('.trace-category-block').forEach(block => {
            const visible = block.querySelectorAll('.trace-step-card:not([style*="display: none"])');
            const title = block.querySelector('.trace-category-title');
            const body = block.querySelector('.trace-category-body');
            if (visible.length > 0) {
                title.classList.remove('trace-collapsed');
                body.classList.remove('trace-hidden');
            } else {
                title.classList.add('trace-collapsed');
                body.classList.add('trace-hidden');
            }
        });
    }
};

window.expandAllTrace = function() {
    document.querySelectorAll('.trace-category-title').forEach(el => {
        el.classList.remove('trace-collapsed');
        el.nextElementSibling.classList.remove('trace-hidden');
    });
};

window.collapseAllTrace = function() {
    document.querySelectorAll('.trace-category-title').forEach(el => {
        el.classList.add('trace-collapsed');
        el.nextElementSibling.classList.add('trace-hidden');
    });
};

function buildPostReadingCTA(freeRemaining) {
    // If paid or free remaining is negative (paid), don't show paywall
    if (freeRemaining < 0) {
        return `
            <div class="unlock-cta" style="border-top: 1px solid var(--border); padding-top: 2rem; margin-top: 2rem;">
                <h3>Your Premium Reading is Complete</h3>
                <p>You can print this page or use your browser's "Save as PDF" to keep a copy.</p>
                <button class="btn-cta btn-cta-secondary" onclick="printReading()" style="width: auto; margin-top: 1rem;">
                    Print / Save as PDF
                </button>
            </div>
        `;
    }

    const freeText = (freeRemaining !== undefined && freeRemaining !== null && freeRemaining >= 0)
        ? `<p style="font-size: 0.8rem; color: var(--text-dim); margin-top: 0.5rem;">Free readings remaining: ${freeRemaining}</p>`
        : "";

    return `
        <div class="unlock-cta">
            <button class="btn-cta btn-cta-secondary" onclick="printReading()" style="width: auto; margin-top: 0; margin-bottom: 1.5rem;">
                Print / Save as PDF
            </button>
            ${freeText}
        </div>
    `;
}

// ─── UI: Show Paywall ───
function showPaywall() {
    const section = document.getElementById("readingSection");
    const content = document.getElementById("readingContent");
    if (!section || !content) return;

    content.innerHTML = `
        <div style="text-align: center; padding: 2rem 0;">
            <div style="font-size: 2.5rem; margin-bottom: 1rem;">✦</div>
            <h2 style="font-family: var(--font-display); font-size: 1.6rem; color: var(--gold); margin-bottom: 0.75rem;">
                You've Used Your Free Readings
            </h2>
            <p style="color: var(--text-muted); max-width: 420px; margin: 0 auto 2rem; line-height: 1.75;">
                You've reached the free reading limit. Unlock your complete natal chart reading
                with a one-time payment — no account or subscription needed.
            </p>
            <div class="unlock-buttons">
                <button class="btn-cta" onclick="startCheckout('full_reading')" id="checkoutFullBtn" data-default-label="✦ Get Full Reading — $25">
                    ✦ Get Full Reading — $25
                </button>
                <span class="btn-or">— or —</span>
                <button class="btn-cta btn-cta-secondary" onclick="startCheckout('premium_audit')" id="checkoutPremiumBtn" data-default-label="Get Premium Deep-Dive — $69">
                    Get Premium Deep-Dive — $69
                </button>
                <p style="font-size: 0.78rem; color: var(--text-dim); margin-top: 0.5rem;">
                    Secure payment via Stripe. No account required.
                </p>
            </div>
        </div>
    `;

    section.classList.remove("hidden");
    section.scrollIntoView({ behavior: "smooth" });
}

// ─── Stripe Checkout ───
window.startCheckout = async function (tier) {
    if (!chartPayload) {
        alert("Please enter your birth details first.");
        return;
    }

    const buttons = getCheckoutButtons(tier);
    buttons.forEach((btn) => {
        btn.disabled = true;
        btn.textContent = "Redirecting to payment...";
    });
    trackConversionEvent("checkout_click", { tier });

    try {
        const params = new URLSearchParams({
            tier: tier,
            date: chartPayload.date,
            time: chartPayload.time,
            city: chartPayload.city,
            state: chartPayload.state || "",
            name: chartPayload.name || "Guest",
        });

        const resp = await apiFetch(`/api/v1/guest/checkout?${params.toString()}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: "{}",
        });

        if (!resp.ok) {
            const err = await resp.json().catch(() => ({}));
            throw new Error(err?.detail || "Checkout failed.");
        }

        const data = await resp.json();
        if (data.url) {
            trackConversionEvent("checkout_redirect", { tier });
            window.location.href = data.url;
        } else {
            throw new Error("No checkout URL returned.");
        }
    } catch (err) {
        buttons.forEach((btn) => {
            btn.disabled = false;
            btn.textContent = btn.dataset.defaultLabel || (tier === "premium_audit" ? "Get Premium Deep-Dive — $69" : "✦ Get Full Reading — $25");
        });
        trackConversionEvent("checkout_error", { tier, error: String(err.message || err) });
        alert("Checkout error: " + err.message);
    }
};

function getCheckoutButtons(tier) {
    const selectors = tier === "premium_audit"
        ? ["#checkoutPremiumBtn", "#checkoutPremiumTopBtn"]
        : ["#checkoutFullBtn", "#checkoutFullTopBtn"];
    return selectors
        .map((selector) => document.querySelector(selector))
        .filter(Boolean);
}

// ─── UI: Feedback Widget ───
function buildFeedbackWidget(source) {
    const widgetId = source === "premium_trial" ? "premiumFeedbackWidget" : "freeFeedbackWidget";

    const label = source === "premium_trial"
        ? "Was the premium reading helpful?"
        : "Was this chart reading good or bad?";
    return `
        <div class="feedback-widget" id="${widgetId}">
            <h4>${label}</h4>
            <div class="feedback-buttons">
                <button class="feedback-btn" data-vote="good" aria-label="Thumbs up - good reading">👍 Good</button>
                <button class="feedback-btn" data-vote="bad" aria-label="Thumbs down - bad reading">👎 Bad</button>
            </div>
            <div class="feedback-comment-wrap" style="display:none; margin-top: 1rem;">
                <textarea
                    class="feedback-comment-textarea"
                    placeholder="Any feedback is appreciated (optional)..."
                    rows="3"
                    maxlength="1000"
                    aria-label="Optional feedback comment"
                ></textarea>
                <button class="feedback-submit-btn" type="button">Send Feedback</button>
            </div>
            <p class="feedback-status"></p>
        </div>
    `;
}

function attachFeedbackHandlers(container, source) {
    const widget = container.querySelector(".feedback-widget");
    if (!widget) return;

    const btns = widget.querySelectorAll(".feedback-btn");
    const statusEl = widget.querySelector(".feedback-status");
    const commentWrap = widget.querySelector(".feedback-comment-wrap");
    const commentTextarea = widget.querySelector(".feedback-comment-textarea");
    const submitBtn = widget.querySelector(".feedback-submit-btn");
    let chosenVote = null;
    let submitted = false;

    btns.forEach((btn) => {
        btn.addEventListener("click", () => {
            if (submitted) return;
            btns.forEach((b) => b.classList.remove("selected"));
            btn.classList.add("selected");
            chosenVote = btn.dataset.vote;
            // Show comment box after a vote
            if (commentWrap) commentWrap.style.display = "block";
            trackConversionEvent("reading_feedback_vote", { vote: chosenVote, source: source || "b2c_reading" });
        });
    });

    if (submitBtn) {
        submitBtn.addEventListener("click", async () => {
            if (submitted || !chosenVote) return;
            submitted = true;
            btns.forEach((b) => (b.disabled = true));
            if (submitBtn) submitBtn.disabled = true;

            const comment = (commentTextarea?.value || "").trim();
            const context = currentReadingContext || {};
            const readingHash = context.reading_hash || hashStr(JSON.stringify(chartPayload || {}));

            if (statusEl) statusEl.textContent = "Saving...";

            try {
                const resp = await apiFetch("/api/v1/reading_feedback", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        reading_hash: readingHash,
                        vote: chosenVote,
                        source: source || "b2c_reading",
                        chart_event_id: context.chart_event_id || null,
                        birth: context.birth || chartPayload,
                        meta: context.meta || {},
                        time_unknown: Boolean(context.time_unknown),
                        comment: comment || null,
                        ts: new Date().toISOString(),
                    }),
                });
                if (!resp.ok) throw new Error("Feedback save failed.");
                if (statusEl) statusEl.textContent = "✓ Thank you for your feedback!";
                if (commentWrap) commentWrap.style.display = "none";
            } catch (e) {
                submitted = false;
                if (submitBtn) submitBtn.disabled = false;
                if (statusEl) statusEl.textContent = "Could not save feedback — please try again.";
            }
        });
    }
}

// ─── Email Capture Handler ───
function attachEmailCaptureHandler(container, chartEventId) {
    const form = container.querySelector(".email-capture-form");
    const input = container.querySelector(".email-capture-input");
    const btn = container.querySelector(".email-capture-btn");
    const status = container.querySelector(".email-capture-status");
    if (!form || !input || !btn) return;

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const email = (input.value || "").trim();
        if (!email || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
            if (status) { status.textContent = "Please enter a valid email address."; status.style.color = "var(--danger)"; }
            return;
        }

        btn.disabled = true;
        btn.textContent = "Sending...";
        trackConversionEvent("email_capture_submit");

        try {
            const resp = await apiFetch("/api/v1/premium/email-reading", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    email,
                    chart_event_id: chartEventId || null,
                    name: chartPayload?.name || "Guest",
                }),
            });
            if (!resp.ok) throw new Error("Submission failed.");
            if (status) { status.textContent = "✓ Got it! We'll be in touch."; status.style.color = "var(--gold)"; }
            btn.textContent = "Sent ✓";
            input.disabled = true;
        } catch (err) {
            btn.disabled = false;
            btn.textContent = "Send Me a Copy";
            if (status) { status.textContent = "Error — please try again."; status.style.color = "var(--danger)"; }
        }
    });
}

// ─── Premium Trial UI Builders ───
function buildPremiumTrialTopBanner() {
    return `
        <div class="premium-trial-top-banner" role="status" aria-live="polite">
            <div class="premium-trial-banner-inner">
                <span class="premium-trial-badge">✦ LIMITED TIME</span>
                <p class="premium-trial-headline">
                    Your <strong>full premium reading</strong> is generating in the background &mdash; completely free.
                </p>
                <p class="premium-trial-sub">
                    This is the <strong>$25 report</strong>. It takes up to 5 minutes. Read your chart below while you wait — we'll load it right here when it's ready.
                </p>
            </div>
        </div>
    `;
}

function buildPremiumTrialTopBannerComplete() {
    return `
        <div class="premium-trial-top-banner premium-trial-top-banner--complete" role="status">
            <div class="premium-trial-banner-inner">
                <span class="premium-trial-badge">✦ READY</span>
                <p class="premium-trial-headline">
                    Your <strong>premium reading</strong> is complete. Scroll down to read it.
                </p>
            </div>
        </div>
    `;
}

function buildPremiumLoadingSection() {
    return `
        <div class="premium-loading-section">
            <div class="premium-loading-header">
                <div class="premium-loading-orb"></div>
                <div>
                    <h3 class="premium-loading-title">Premium Reading Generating</h3>
                    <p class="premium-loading-subtitle">Multi-stage LLM analysis in progress &mdash; this takes up to 5 minutes</p>
                </div>
            </div>
            <div class="premium-loading-progress-track">
                <div class="premium-loading-progress-fill" id="premiumLoadingBar"></div>
            </div>
            <p class="premium-loading-msg" id="premiumLoadingMsg">Calculating your full planetary picture...</p>
            <p class="premium-loading-elapsed">Elapsed: <span id="premiumLoadingElapsed">0s</span></p>
        </div>
    `;
}

function buildRenderedPremiumSection(html, chartEventId) {
    return `
        <div class="premium-reading-section">
            <div class="premium-reading-header">
                <span class="premium-reading-badge">✦ PREMIUM READING</span>
                <h2 class="premium-reading-title">Your Full Traditional Astrology Report</h2>
                <p class="premium-reading-subtitle">LLM-generated multi-stage analysis &mdash; normally $25</p>
                <button class="btn-cta btn-cta-secondary" onclick="printReading()" style="width:auto; margin-top:0.75rem;">
                    Print / Save as PDF
                </button>
            </div>
            <div class="premium-reading-body reading-body">${html}</div>
            ${buildPremiumBottomBanner()}
            ${buildEmailCapture()}
            ${buildFeedbackWidget("premium_trial")}
        </div>
    `;
}

function buildPremiumBottomBanner() {
    return `
        <div class="premium-bottom-banner">
            <div class="premium-bottom-banner-inner">
                <span class="premium-trial-badge">✦ LIMITED TIME OFFER</span>
                <h3 class="premium-bottom-title">This report is normally $25.</h3>
                <p class="premium-bottom-sub">
                    We're sharing the full reading free while we gather feedback from real users.
                    If it resonated with you, share it with someone who might benefit.
                </p>
                <button class="btn-cta" onclick="printReading()" style="width:auto;">
                    Print / Save PDF
                </button>
            </div>
        </div>
    `;
}

function buildEmailCapture() {
    return `
        <div class="email-capture-block">
            <h4 class="email-capture-title">Want a copy sent to your inbox?</h4>
            <p class="email-capture-sub">We'll email you a copy of this reading &mdash; no spam, no account required.</p>
            <form class="email-capture-form" novalidate>
                <div class="email-capture-row">
                    <input
                        type="email"
                        class="email-capture-input"
                        placeholder="your@email.com"
                        autocomplete="email"
                        aria-label="Your email address"
                        required
                    />
                    <button type="submit" class="email-capture-btn">Send Me a Copy</button>
                </div>
                <p class="email-capture-status"></p>
            </form>
        </div>
    `;
}

// ─── UI: Loading State ───
function showLoading() {
    const btn = document.getElementById("submitBtn");
    if (btn) {
        btn.disabled = true;
        const btnText = btn.querySelector(".btn-text");
        const btnLoading = btn.querySelector(".btn-loading");
        if (btnText) btnText.classList.add("hidden");
        if (btnLoading) btnLoading.classList.remove("hidden");
    }

    const loadingSection = document.getElementById("loadingSection");
    if (loadingSection) loadingSection.classList.remove("hidden");

    const readingSection = document.getElementById("readingSection");
    if (readingSection) readingSection.classList.add("hidden");

    // Reset progress bar
    const fill = document.getElementById("loadingProgressFill");
    if (fill) fill.style.width = "0%";

    // Reset step indicators
    document.querySelectorAll(".loading-step").forEach((el, i) => {
        el.classList.remove("active", "complete");
        if (i === 0) el.classList.add("active");
    });

    // Start elapsed timer
    loadingStartTime = Date.now();
    const elapsedEl = document.getElementById("loadingElapsed");
    if (elapsedTimerInterval) clearInterval(elapsedTimerInterval);
    elapsedTimerInterval = setInterval(() => {
        const secs = Math.floor((Date.now() - loadingStartTime) / 1000);
        if (elapsedEl) elapsedEl.textContent = `Calculating your chart... ${secs}s`;
    }, 1000);

    // Scroll to loading
    loadingSection?.scrollIntoView({ behavior: "smooth" });
}

function hideLoading() {
    const btn = document.getElementById("submitBtn");
    if (btn) {
        btn.disabled = false;
        const btnText = btn.querySelector(".btn-text");
        const btnLoading = btn.querySelector(".btn-loading");
        if (btnText) btnText.classList.remove("hidden");
        if (btnLoading) btnLoading.classList.add("hidden");
    }

    const loadingSection = document.getElementById("loadingSection");
    if (loadingSection) loadingSection.classList.add("hidden");

    // Stop elapsed timer
    if (elapsedTimerInterval) {
        clearInterval(elapsedTimerInterval);
        elapsedTimerInterval = null;
    }
}

function updateLoadingMessage(msg) {
    const el = document.getElementById("loadingMessage");
    if (el) {
        el.style.opacity = "0";
        setTimeout(() => {
            el.textContent = msg;
            el.style.opacity = "1";
        }, 200);
    }
}

function updateLoadingProgress(stepIndex) {
    const totalSteps = LOADING_MSGS.length;
    const pct = Math.min(((stepIndex + 1) / totalSteps) * 100, 95); // Cap at 95% until complete
    const fill = document.getElementById("loadingProgressFill");
    if (fill) fill.style.width = pct + "%";

    // Update step indicators
    document.querySelectorAll(".loading-step").forEach((el, i) => {
        el.classList.remove("active", "complete");
        if (i < stepIndex) el.classList.add("complete");
        else if (i === stepIndex) el.classList.add("active");
    });
}

// ─── UI: Error ───
function showError(msg) {
    const section = document.getElementById("readingSection");
    const content = document.getElementById("readingContent");
    if (!section || !content) {
        alert(msg);
        return;
    }

    content.innerHTML = `
        <div style="text-align: center; padding: 2rem;">
            <div style="font-size: 2rem; margin-bottom: 1rem;">⚠️</div>
            <h3 style="color: var(--danger); margin-bottom: 0.75rem;">Something went wrong</h3>
            <p style="color: var(--text-muted);">${escapeHtml(msg)}</p>
            <button class="btn-cta btn-cta-secondary" onclick="location.reload()" style="margin-top: 1.5rem; width: auto;">
                Try Again
            </button>
        </div>
    `;

    section.classList.remove("hidden");
}

// ─── Markdown Renderer ───
function renderMarkdown(md) {
    if (!md) return "<p>No reading content available.</p>";

    let html = md
        // Headers
        .replace(/^#### (.*$)/gim, '<h4>$1</h4>')
        .replace(/^### (.*$)/gim, '<h3>$1</h3>')
        .replace(/^## (.*$)/gim, '<h2>$1</h2>')
        .replace(/^# (.*$)/gim, '<h1>$1</h1>')
        // Horizontal rules
        .replace(/^---$/gim, '<hr>')
        // Bold & italic
        .replace(/\*\*\*(.*?)\*\*\*/gim, '<strong><em>$1</em></strong>')
        .replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/gim, '<em>$1</em>')
        // Code blocks (simple)
        .replace(/```[\s\S]*?```/gim, (match) => {
            const code = match.replace(/```\w*\n?/g, '').replace(/```/g, '');
            return `<pre style="background:rgba(0,0,0,0.3);padding:1rem;border-radius:8px;overflow-x:auto;font-size:0.85rem;"><code>${escapeHtml(code)}</code></pre>`;
        })
        // Inline code
        .replace(/`(.*?)`/gim, '<code style="background:rgba(255,255,255,0.06);padding:0.15em 0.4em;border-radius:4px;font-size:0.9em;">$1</code>')
        // Unordered lists
        .replace(/^\s*[-*] (.*$)/gim, '<li>$1</li>')
        // Tables (basic)
        .replace(/^\|(.+)\|$/gim, (match) => {
            const cells = match.split('|').filter(c => c.trim());
            if (cells.every(c => /^[\s-:]+$/.test(c))) return ''; // separator row
            const isHeader = false; // simplified
            const tag = 'td';
            const row = cells.map(c => `<${tag}>${c.trim()}</${tag}>`).join('');
            return `<tr>${row}</tr>`;
        })
        // Paragraphs
        .replace(/\n\n/gim, '</p><p>')
        .replace(/\n/gim, '<br>');

    // Wrap in paragraph
    html = '<p>' + html + '</p>';

    // Clean up empty paragraphs and fix list wrapping
    html = html.replace(/<p><\/p>/g, '');
    html = html.replace(/(<li>.*?<\/li>)/gs, (match) => `<ul>${match}</ul>`);
    html = html.replace(/<\/ul><ul>/g, '');

    // Wrap table rows
    html = html.replace(/(<tr>.*?<\/tr>)/gs, (match) => `<table>${match}</table>`);
    html = html.replace(/<\/table><table>/g, '');

    return html;
}

// ─── Utilities ───
function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str || "";
    return div.innerHTML;
}

function hashStr(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        const char = str.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash |= 0;
    }
    return String(Math.abs(hash));
}
