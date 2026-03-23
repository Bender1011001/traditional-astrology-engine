/**
 * reading-app.js — B2C Reading Flow
 * 
 * Flow:
 * 1. User fills birth form → submit
 * 2. Free: Calls /api/v1/premium/guest/request → polls → shows full reading (up to IP limit)
 * 3. After IP limit hit: Shows teaser + paywall ($7 Full Reading / $29 Premium)
 * 4. Paid: Redirects to Stripe → returns with session_id → calls /generate-paid → polls → shows full reading
 */

import { apiFetch } from './api.js';

// ─── State ───
let chartPayload = null;
let loadingStartTime = null;
let elapsedTimerInterval = null;

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
        };

        if (!chartPayload.date || !chartPayload.city) {
            shakeForm();
            return;
        }

        // Save for after payment redirect
        localStorage.setItem("ta_chart_payload", JSON.stringify(chartPayload));

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

// ─── Free Reading (Premium Guest) ───
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
                showPaywall();
                return;
            }
            const err = await resp.json().catch(() => ({}));
            throw new Error(err?.detail?.message || err?.detail || "Request failed.");
        }

        const data = await resp.json();
        pollForCompletion(data.task_id, data.free_readings_remaining);
    } catch (err) {
        hideLoading();
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
        } catch (e) {
            console.error("Poll error:", e);
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
        });

        if (!resp.ok) {
            const err = await resp.json().catch(() => ({}));
            throw new Error(err?.detail || "Could not start generation.");
        }

        const data = await resp.json();
        pollForCompletion(data.task_id, -1); // -1 = paid, no limit
    } catch (err) {
        hideLoading();
        showError(err.message);
    }
}

// ─── UI: Show Reading ───
function showReading(result, freeRemaining) {
    const section = document.getElementById("readingSection");
    const content = document.getElementById("readingContent");
    if (!section || !content) return;

    const md = result?.report_markdown || "";
    const html = renderMarkdown(md);
    const traceData = result?.computation_trace || null;

    content.innerHTML = `
        <div class="reading-body">${html}</div>
        ${traceData ? buildTraceSection(traceData) : ''}
        ${buildPostReadingCTA(freeRemaining)}
        ${buildFeedbackWidget()}
    `;

    section.classList.remove("hidden");
    section.scrollIntoView({ behavior: "smooth", block: "start" });

    // Attach feedback handlers
    attachFeedbackHandlers(content);

    // Attach trace interactivity
    if (traceData) {
        attachTraceHandlers(content);
    }
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
                <button class="btn-cta btn-cta-secondary" onclick="window.print()" style="width: auto; margin-top: 1rem;">
                    🖨️ Print / Save as PDF
                </button>
            </div>
        `;
    }

    const freeText = (freeRemaining !== undefined && freeRemaining !== null && freeRemaining >= 0)
        ? `<p style="font-size: 0.8rem; color: var(--text-dim); margin-top: 0.5rem;">Free readings remaining: ${freeRemaining}</p>`
        : "";

    return `
        <div class="unlock-cta">
            <button class="btn-cta btn-cta-secondary" onclick="window.print()" style="width: auto; margin-top: 0; margin-bottom: 1.5rem;">
                🖨️ Print / Save as PDF
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
                <button class="btn-cta" onclick="startCheckout('full_reading')" id="checkoutFullBtn">
                    ✦ Get Full Reading — $7
                </button>
                <span class="btn-or">— or —</span>
                <button class="btn-cta btn-cta-secondary" onclick="startCheckout('premium_audit')" id="checkoutPremiumBtn">
                    Get Premium Deep-Dive — $29
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

    const btn = document.getElementById(tier === "premium_audit" ? "checkoutPremiumBtn" : "checkoutFullBtn");
    if (btn) {
        btn.disabled = true;
        btn.textContent = "Redirecting to payment...";
    }

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
        });

        if (!resp.ok) {
            const err = await resp.json().catch(() => ({}));
            throw new Error(err?.detail || "Checkout failed.");
        }

        const data = await resp.json();
        if (data.url) {
            window.location.href = data.url;
        } else {
            throw new Error("No checkout URL returned.");
        }
    } catch (err) {
        if (btn) {
            btn.disabled = false;
            btn.textContent = tier === "premium_audit" ? "Get Premium Deep-Dive — $29" : "✦ Get Full Reading — $7";
        }
        alert("Checkout error: " + err.message);
    }
};

// ─── UI: Feedback Widget ───
function buildFeedbackWidget() {
    return `
        <div class="feedback-widget">
            <h4>Was this reading accurate?</h4>
            <div class="feedback-buttons">
                <button class="feedback-btn" data-vote="up">👍 Yes, accurate</button>
                <button class="feedback-btn" data-vote="down">👎 Not accurate</button>
            </div>
            <p class="feedback-status"></p>
        </div>
    `;
}

function attachFeedbackHandlers(container) {
    const btns = container.querySelectorAll(".feedback-btn");
    const statusEl = container.querySelector(".feedback-status");
    let submitted = false;

    btns.forEach((btn) => {
        btn.addEventListener("click", async () => {
            if (submitted) return;
            submitted = true;
            btns.forEach((b) => (b.disabled = true));
            const vote = btn.dataset.vote;

            if (statusEl) statusEl.textContent = "Saving...";

            try {
                await apiFetch("/api/v1/reading_feedback", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        reading_hash: hashStr(JSON.stringify(chartPayload || {})),
                        vote: vote,
                        source: "b2c_reading",
                        birth: chartPayload,
                        ts: new Date().toISOString(),
                    }),
                });
                if (statusEl) statusEl.textContent = "Thank you for your feedback!";
            } catch (e) {
                if (statusEl) statusEl.textContent = "Could not save feedback.";
            }
        });
    });
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
        if (elapsedEl) elapsedEl.textContent = `Elapsed: ${secs}s — typically takes 30–60 seconds`;
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
