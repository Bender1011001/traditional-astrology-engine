/**
 * reading-app.js — B2C Reading Flow
 *
 * Flow:
 * 1. User fills birth form → submit
 * 2. Free: Calls /api/v1/premium/guest/request → polls → shows free reading
 * 3. Upsell: $69 Complete Analysis via guest Stripe checkout (no account).
 *    Return URL /?paid=true&session_id=... → POST /api/v1/guest/generate-paid
 *    → poll /api/v1/guest/task-status/{id} → render + PDF emailed.
 * 4. Feedback: visitor can rate the reading, send a comment, and optionally tip
 */

import { apiFetch } from './api.js';
import { trackPurchase } from './config.js';
import { renderAstrocartographyMap } from './astrocartography-map.js';
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
        // Analytics must never interrupt chart generation.
    }
}

function authHeaders(extra = {}) {
    const headers = { ...extra };
    try {
        const token = localStorage.getItem("access_token");
        if (token) headers.Authorization = `Bearer ${token}`;
    } catch (_) {
        // Private browsing/storage issues should not block the reading flow.
    }
    return headers;
}

function hasPrintableReading() {
    const section = document.getElementById("readingSection");
    const content = document.getElementById("readingContent");
    return Boolean(
        section &&
        content &&
        !section.classList.contains("hidden") &&
        content.textContent.trim().length > 0
    );
}

function setReadingPrintMode(active) {
    document.body.classList.toggle(
        "printing-reading",
        Boolean(active && hasPrintableReading())
    );
}

window.addEventListener("beforeprint", () => setReadingPrintMode(true));
window.addEventListener("afterprint", () => setReadingPrintMode(false));

window.printReading = function () {
    trackConversionEvent("print_save_pdf");
    setReadingPrintMode(true);
    window.print();
};

const SHARE_READING_TITLE = "My Traditional Astrology Reading";
const SHARE_READING_TEXT = "I just generated a free traditional astrology reading with sect, houses, lots, fixed stars, and timing. You can make yours here:";
const SHARE_READING_FALLBACK_URL = "https://traditional-astrology.com/#get-reading";
const SUPPORT_TIP_AMOUNTS = [
    { amountCents: 500, label: "$5" },
    { amountCents: 1100, label: "$11" },
    { amountCents: 2500, label: "$25" },
];
const PREMIUM_PRICE_LABEL = "$69";

function getReadingShareUrl(medium) {
    try {
        const origin = window.location.origin && window.location.origin !== "null"
            ? window.location.origin
            : "https://traditional-astrology.com";
        if (!medium) return `${origin}/#get-reading`;
        return `${origin}/?utm_source=share&utm_medium=${encodeURIComponent(medium)}&utm_campaign=reading_share#get-reading`;
    } catch (_) {
        return SHARE_READING_FALLBACK_URL;
    }
}

function getPersonalizedShareText() {
    const summary = currentReadingContext?.meta?.chart_summary || {};
    const sun = summary.sun_sign;
    const moon = summary.moon_sign;
    const rising = summary.rising_sign;
    if (sun && moon && rising) {
        return `${sun} Sun, ${moon} Moon, ${rising} Rising — I just got a free traditional astrology reading and it's surprisingly detailed. Get yours:`;
    }
    if (sun) {
        return `${sun} Sun — I just got a free traditional astrology reading and it's surprisingly detailed. Get yours:`;
    }
    return SHARE_READING_TEXT;
}

function getReadingSharePayload(medium) {
    return {
        title: SHARE_READING_TITLE,
        text: getPersonalizedShareText(),
        url: getReadingShareUrl(medium),
    };
}

function setShareStatus(button, message) {
    const host = button?.closest(".reading-share-actions, .chart-actions, .share-nudge");
    const status = host?.querySelector("[data-share-status]");
    if (!status) {
        temporarilyLabelButton(button, "Copied");
        return;
    }

    status.textContent = message;
    clearTimeout(status.dataset.clearTimer);
    const timer = window.setTimeout(() => {
        status.textContent = "";
    }, 3200);
    status.dataset.clearTimer = String(timer);
}

function temporarilyLabelButton(button, label) {
    if (!button) return;
    const original = button.textContent;
    button.textContent = label;
    window.setTimeout(() => {
        button.textContent = original;
    }, 1800);
}

async function writeClipboardText(text) {
    if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
        return;
    }

    const textarea = document.createElement("textarea");
    textarea.value = text;
    textarea.setAttribute("readonly", "");
    textarea.style.position = "fixed";
    textarea.style.left = "-9999px";
    textarea.style.top = "0";
    document.body.appendChild(textarea);
    textarea.select();
    try {
        const copied = document.execCommand("copy");
        if (!copied) throw new Error("Copy command failed.");
    } finally {
        textarea.remove();
    }
}

async function copyReadingShareText(button) {
    const payload = getReadingSharePayload("copy");
    await writeClipboardText(`${payload.text}\n${payload.url}`);
    setShareStatus(button, "Share text copied.");
    temporarilyLabelButton(button, "Copied");
    trackConversionEvent("reading_share_copy");
}

async function shareReading(button) {
    const payload = getReadingSharePayload("native");
    if (navigator.share) {
        try {
            await navigator.share(payload);
            setShareStatus(button, "Share sheet opened.");
            trackConversionEvent("reading_share_native");
            return;
        } catch (err) {
            if (err?.name === "AbortError") return;
        }
    }

    await copyReadingShareText(button);
}

function openPlatformShare(platform) {
    const text = getPersonalizedShareText();
    const url = getReadingShareUrl(platform);
    const encoded = encodeURIComponent(text + "\n" + url);
    const encodedUrl = encodeURIComponent(url);
    const encodedText = encodeURIComponent(text);
    let shareUrl = "";

    switch (platform) {
        case "twitter":
            shareUrl = `https://x.com/intent/tweet?text=${encodedText}&url=${encodedUrl}`;
            break;
        case "facebook":
            shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodedUrl}`;
            break;
        case "whatsapp":
            shareUrl = `https://wa.me/?text=${encoded}`;
            break;
        case "reddit":
            shareUrl = `https://reddit.com/submit?url=${encodedUrl}&title=${encodeURIComponent(SHARE_READING_TITLE)}`;
            break;
        default:
            return;
    }

    trackConversionEvent("reading_share_platform", { platform });
    window.open(shareUrl, "_blank", "noopener,noreferrer,width=600,height=500");
}

function buildShareNudge() {
    const summary = currentReadingContext?.meta?.chart_summary || {};
    const sun = summary.sun_sign;
    const personalNote = sun
        ? `Your ${escapeHtml(sun)} Sun reading is ready to share.`
        : "Your reading is ready to share.";

    return `
        <div class="share-nudge" id="shareNudge">
            <div class="share-nudge-inner">
                <h3 class="share-nudge-title">Know someone who'd find this interesting?</h3>
                <p class="share-nudge-sub">${personalNote} The free reading takes a minute — no account needed.</p>
                <div class="share-platform-buttons">
                    <button type="button" class="share-platform-btn share-twitter" onclick="openPlatformShare('twitter')" aria-label="Share on Twitter/X">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
                        <span>Twitter / X</span>
                    </button>
                    <button type="button" class="share-platform-btn share-facebook" onclick="openPlatformShare('facebook')" aria-label="Share on Facebook">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>
                        <span>Facebook</span>
                    </button>
                    <button type="button" class="share-platform-btn share-whatsapp" onclick="openPlatformShare('whatsapp')" aria-label="Share on WhatsApp">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
                        <span>WhatsApp</span>
                    </button>
                    <button type="button" class="share-platform-btn share-reddit" onclick="openPlatformShare('reddit')" aria-label="Share on Reddit">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0zm5.01 4.744c.688 0 1.25.561 1.25 1.249a1.25 1.25 0 0 1-2.498.056l-2.597-.547-.8 3.747c1.824.07 3.48.632 4.674 1.488.308-.309.73-.491 1.207-.491.968 0 1.754.786 1.754 1.754 0 .716-.435 1.333-1.01 1.614a3.111 3.111 0 0 1 .042.52c0 2.694-3.13 4.87-7.004 4.87-3.874 0-7.004-2.176-7.004-4.87 0-.183.015-.366.043-.534A1.748 1.748 0 0 1 4.028 12c0-.968.786-1.754 1.754-1.754.463 0 .898.196 1.207.49 1.207-.883 2.878-1.43 4.744-1.487l.885-4.182a.342.342 0 0 1 .14-.197.35.35 0 0 1 .238-.042l2.906.617a1.214 1.214 0 0 1 1.108-.701zM9.25 12C8.561 12 8 12.562 8 13.25c0 .687.561 1.248 1.25 1.248.687 0 1.248-.561 1.248-1.249 0-.688-.561-1.249-1.249-1.249zm5.5 0c-.687 0-1.248.561-1.248 1.25 0 .687.561 1.248 1.249 1.248.688 0 1.249-.561 1.249-1.249 0-.687-.562-1.249-1.25-1.249zm-5.466 3.99a.327.327 0 0 0-.231.094.33.33 0 0 0 0 .463c.842.842 2.484.913 2.961.913.477 0 2.105-.056 2.961-.913a.361.361 0 0 0 .029-.463.33.33 0 0 0-.464 0c-.547.533-1.684.73-2.512.73-.828 0-1.979-.196-2.512-.73a.326.326 0 0 0-.232-.095z"/></svg>
                        <span>Reddit</span>
                    </button>
                </div>
                <div class="share-nudge-alt">
                    <button type="button" class="btn-cta btn-cta-secondary share-nudge-copy" data-reading-share-action="copy">
                        Copy Share Link
                    </button>
                    <p class="reading-share-status" data-share-status aria-live="polite"></p>
                </div>
            </div>
        </div>
    `;
}

window.openPlatformShare = openPlatformShare;

function setupReadingShareHandlers() {
    document.addEventListener("click", async (event) => {
        const target = event.target instanceof Element ? event.target : null;
        const button = target?.closest("[data-reading-share-action]");
        if (!button) return;

        event.preventDefault();
        const action = button.dataset.readingShareAction || "share";
        button.disabled = true;
        try {
            if (action === "copy") {
                await copyReadingShareText(button);
            } else {
                await shareReading(button);
            }
        } catch (err) {
            setShareStatus(button, "Could not copy. Use your browser address bar.");
            trackConversionEvent("reading_share_error", { error: String(err.message || err) });
        } finally {
            button.disabled = false;
        }
    });
}

function showSupportReturnNotice() {
    let params;
    try {
        params = new URLSearchParams(window.location.search || "");
    } catch (_) {
        return;
    }

    const isTipThanks = params.get("tip") === "thanks";
    const isMonthlyThanks = params.get("supporter") === "monthly";
    if (!isTipThanks && !isMonthlyThanks) return;

    const formCard = document.getElementById("chartFormCard");
    const host = formCard?.parentElement || document.getElementById("get-reading");
    if (!host || document.getElementById("supportReturnNotice")) return;

    const notice = document.createElement("div");
    notice.id = "supportReturnNotice";
    notice.className = "support-return-notice";
    notice.innerHTML = `
        <strong>Thank you for supporting the free report.</strong>
        <span>${isMonthlyThanks ? "Your monthly support helps keep this full traditional reading available to everyone." : "Your tip helps pay for chart calculation, report generation, and source research."}</span>
    `;
    host.insertBefore(notice, formCard || host.firstChild);
    trackConversionEvent(isMonthlyThanks ? "monthly_support_success" : "tip_success");
}

// ─── Loading Messages ───
const LOADING_MSGS = [
    "Validating your birth data...",
    "Calculating planetary positions from the Swiss Ephemeris...",
    "Building the forensic audit payload...",
    "Writing the complete LLM report...",
    "Synthesizing sect, dignities, lots, and timing...",
    "Checking safety language and report quality...",
    "Saving your chart record...",
    "Rendering your free reading...",
];

const LOADING_DETAILS = [
    "Checking date, time, and location before the engine starts.",
    "The chart math is deterministic: same birth data, same chart.",
    "The LLM receives the full structured chart payload used for the complete report.",
    "This can take a few minutes. The moving bars mean the browser is still polling.",
    "The report is being written from the calculated chart data, not a generic template.",
    "The customer-facing body is checked before it is shown.",
    "Persisting the result so feedback and owner readback still work.",
    "Finalizing the browser view.",
];

// ─── DOM Ready ───
document.addEventListener("DOMContentLoaded", () => {
    setupForm();
    setupTimeUnknownToggle();
    setupReadingShareHandlers();
    setupSupportCheckoutHandlers();
    showSupportReturnNotice();
    handlePaidReturn();

    // Export & Share Handlers
    const exportPdfBtn = document.getElementById('exportPdfBtn');

    if (exportPdfBtn) {
        exportPdfBtn.addEventListener('click', () => {
            printReading();
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
        const dateInput = document.getElementById("birthDate");
        const cityInput = document.getElementById("birthCity");

        // ── Validation: block submit until required fields are complete ──
        const missing = [];
        if (!dateInput?.value) missing.push([dateInput, "your date of birth"]);
        if (!timeUnknown && !timeInput?.value) missing.push([timeInput, "your time of birth (or check “I don’t know my birth time”)"]);
        if (!cityInput?.value.trim()) missing.push([cityInput, "your city of birth"]);

        // clear any prior invalid marks
        [dateInput, timeInput, cityInput].forEach(el => el && el.setAttribute("aria-invalid", "false"));

        if (missing.length) {
            missing.forEach(([el]) => el && el.setAttribute("aria-invalid", "true"));
            showFormError("Please enter " + missing.map(m => m[1]).join(", ") + ".");
            (missing[0][0])?.focus();
            shakeForm();
            return;
        }
        clearFormError();

        const latVal = document.getElementById("birthLat")?.value;
        const lonVal = document.getElementById("birthLon")?.value;

        chartPayload = {
            date: dateInput.value,
            time: timeUnknown && !timeInput?.value ? "12:00" : (timeInput?.value || "12:00"),
            city: cityInput.value.trim(),
            state: document.getElementById("birthState")?.value || "",
            name: "Guest",
            time_unknown: Boolean(timeUnknown),
        };
        // If a city was picked from suggestions, pass exact coordinates so the
        // server skips geocoding (faster, and never fails on an ambiguous name).
        if (latVal && lonVal) {
            chartPayload.latitude = parseFloat(latVal);
            chartPayload.longitude = parseFloat(lonVal);
        }

        // Save so report feedback and browser refreshes can preserve context.
        localStorage.setItem("ta_chart_payload", JSON.stringify(chartPayload));

        trackConversionEvent("free_chart_submit");
        showLoading();
        await requestFreeReading(chartPayload);
    });

    setupCityAutocomplete();
}

// ─── Inline form-error helpers ───
function showFormError(msg) {
    const el = document.getElementById("formError");
    if (!el) return;
    el.textContent = msg;
    el.hidden = false;
}
function clearFormError() {
    const el = document.getElementById("formError");
    if (!el) return;
    el.textContent = "";
    el.hidden = true;
}

// ─── City Autocomplete (Open-Meteo geocoding, free, no key) ───
function setupCityAutocomplete() {
    const input = document.getElementById("birthCity");
    const list = document.getElementById("citySuggestions");
    const stateInput = document.getElementById("birthState");
    const latInput = document.getElementById("birthLat");
    const lonInput = document.getElementById("birthLon");
    if (!input || !list) return;

    let debounceTimer = null;
    let activeIdx = -1;
    let items = [];

    const closeList = () => {
        list.hidden = true;
        list.innerHTML = "";
        input.setAttribute("aria-expanded", "false");
        activeIdx = -1;
        items = [];
    };

    const fmtSub = (r) => [r.admin1, r.country].filter(Boolean).join(", ");

    const choose = (r) => {
        input.value = r.name;
        if (stateInput) stateInput.value = r.admin1 || r.country || "";
        if (latInput) latInput.value = r.latitude;
        if (lonInput) lonInput.value = r.longitude;
        input.setAttribute("aria-invalid", "false");
        clearFormError();
        closeList();
    };

    const render = () => {
        if (!items.length) { closeList(); return; }
        list.innerHTML = items.map((r, i) =>
            `<li role="option" data-i="${i}" class="${i === activeIdx ? "active" : ""}">${escapeHtml(r.name)}<span class="city-sub">${escapeHtml(fmtSub(r))}</span></li>`
        ).join("");
        list.hidden = false;
        input.setAttribute("aria-expanded", "true");
    };

    // Photon (komoot) geocoder — free, no key, and already allow-listed in our CSP.
    const search = async (q) => {
        try {
            const url = `https://photon.komoot.io/api/?q=${encodeURIComponent(q)}&limit=8&lang=en`;
            const resp = await fetch(url);
            if (!resp.ok) return;
            const data = await resp.json();
            const feats = Array.isArray(data.features) ? data.features : [];
            const seen = new Set();
            items = [];
            for (const f of feats) {
                const p = f.properties || {};
                const coords = (f.geometry || {}).coordinates || [];
                // Only settlements make sense as a birthplace.
                const isPlace = p.osm_key === "place" ||
                    ["city", "town", "village", "hamlet", "municipality"].includes(p.type);
                const name = p.name || p.city;
                if (!isPlace || !name || coords.length < 2) continue;
                const admin1 = p.state || p.county || "";
                const key = `${name}|${admin1}|${p.country || ""}`;
                if (seen.has(key)) continue;
                seen.add(key);
                items.push({
                    name,
                    admin1,
                    country: p.country || "",
                    latitude: coords[1],
                    longitude: coords[0],
                });
                if (items.length >= 6) break;
            }
            activeIdx = -1;
            render();
        } catch (_) { /* network hiccup — silently skip suggestions */ }
    };

    input.addEventListener("input", () => {
        // Typing invalidates any previously selected coordinates.
        if (latInput) latInput.value = "";
        if (lonInput) lonInput.value = "";
        const q = input.value.trim();
        clearTimeout(debounceTimer);
        if (q.length < 2) { closeList(); return; }
        debounceTimer = setTimeout(() => search(q), 250);
    });

    input.addEventListener("keydown", (e) => {
        if (list.hidden || !items.length) return;
        if (e.key === "ArrowDown") { e.preventDefault(); activeIdx = (activeIdx + 1) % items.length; render(); }
        else if (e.key === "ArrowUp") { e.preventDefault(); activeIdx = (activeIdx - 1 + items.length) % items.length; render(); }
        else if (e.key === "Enter" && activeIdx >= 0) { e.preventDefault(); choose(items[activeIdx]); }
        else if (e.key === "Escape") { closeList(); }
    });

    list.addEventListener("mousedown", (e) => {
        const li = e.target.closest("li[data-i]");
        if (!li) return;
        e.preventDefault();
        choose(items[parseInt(li.dataset.i, 10)]);
    });

    document.addEventListener("click", (e) => {
        if (!list.hidden && !e.target.closest(".city-autocomplete")) closeList();
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

// ─── Premium ($69 Complete Analysis) Checkout ───────────────────────────────

function getStoredChartPayload() {
    if (chartPayload?.date && chartPayload?.city) return chartPayload;
    try {
        const stored = JSON.parse(localStorage.getItem("ta_chart_payload") || "null");
        if (stored?.date && stored?.city) {
            chartPayload = stored;
            return stored;
        }
    } catch (_) {
        // Ignore storage parse issues; the form is still available.
    }
    return null;
}

function buildPremiumUpsell() {
    return `
        <div class="premium-bottom-banner" id="premiumUpsell">
            <div class="premium-bottom-banner-inner">
                <span class="premium-trial-badge">✦ GO DEEPER</span>
                <h3 class="premium-bottom-title">The Complete Astrological Analysis — ${PREMIUM_PRICE_LABEL}</h3>
                <p class="premium-bottom-sub">
                    Your free reading is a single pass over the chart. The Complete Analysis runs six
                    deep synthesis passes: 20+ pages covering advanced timing (annual profections,
                    firdaria, Zodiacal Releasing), all five dignity levels, Arabic lots, fixed star
                    contacts, humoral temperament, and a personalized 10-year forecast.
                </p>
                <p class="premium-bottom-sub" style="margin-top:0.5rem;">
                    No account needed. The PDF is emailed to you after checkout, and the full reading
                    also renders right here in your browser.
                </p>
                <button class="btn-cta" type="button" data-premium-checkout data-default-label="Get the Complete Analysis — ${PREMIUM_PRICE_LABEL}" style="width:auto; margin-top:1rem;">
                    ✦ Get the Complete Analysis — ${PREMIUM_PRICE_LABEL}
                </button>
                <p class="premium-bottom-sub" style="margin-top:0.75rem; font-size:0.8rem;">
                    One-time payment. No subscription. If anything goes wrong with delivery,
                    you keep the reading and get your money back.
                </p>
                <p class="reading-support-status" data-premium-status aria-live="polite"></p>
            </div>
        </div>
    `;
}

async function startPremiumCheckout(button, statusEl = null) {
    const payload = getStoredChartPayload();
    if (!payload) {
        if (statusEl) statusEl.textContent = "Generate your free reading first so we have your birth details.";
        return;
    }

    if (button) {
        button.disabled = true;
        button.textContent = "Opening secure checkout...";
    }
    if (statusEl) statusEl.textContent = "Opening Stripe checkout...";
    trackConversionEvent("premium_checkout_click", { tier: "premium_audit" });

    try {
        const qs = new URLSearchParams({
            tier: "premium_audit",
            date: payload.date,
            time: payload.time || "12:00",
            city: payload.city,
            state: payload.state || "",
            name: payload.name || "Guest",
        });
        const resp = await apiFetch(`/api/v1/guest/checkout?${qs.toString()}`, {
            method: "POST",
            headers: authHeaders({ "Content-Type": "application/json" }),
            body: "{}",
        });
        if (!resp.ok) {
            const err = await resp.json().catch(() => ({}));
            throw new Error(err?.detail || "Could not open checkout.");
        }
        const data = await resp.json();
        if (!data.url) throw new Error("No checkout URL returned.");
        trackConversionEvent("premium_checkout_redirect", { tier: "premium_audit" });
        window.location.href = data.url;
    } catch (err) {
        if (button) {
            button.disabled = false;
            button.textContent = button.dataset.defaultLabel || `Get the Complete Analysis — ${PREMIUM_PRICE_LABEL}`;
        }
        trackConversionEvent("premium_checkout_error", { error: String(err.message || err) });
        if (statusEl) statusEl.textContent = "Could not open checkout. Please try again.";
    }
}

// ─── Paid Return: /?paid=true&session_id=... ────────────────────────────────

function handlePaidReturn() {
    let params;
    try {
        params = new URLSearchParams(window.location.search || "");
    } catch (_) {
        return;
    }
    if (params.get("paid") !== "true") return;
    const sessionId = params.get("session_id");
    if (!sessionId) return;

    getStoredChartPayload();
    showLoading();
    updateLoadingMessage("Confirming your payment...", "Verifying the Stripe checkout session.");
    updateLoadingProgress(0, 6);

    startPaidGeneration(sessionId);
}

async function startPaidGeneration(sessionId) {
    try {
        const resp = await apiFetch(
            `/api/v1/guest/generate-paid?session_id=${encodeURIComponent(sessionId)}`,
            {
                method: "POST",
                headers: authHeaders({ "Content-Type": "application/json" }),
                body: "{}",
            }
        );
        if (!resp.ok) {
            const err = await resp.json().catch(() => ({}));
            throw new Error(err?.detail || "Could not start your paid reading.");
        }
        const data = await resp.json();
        if (data.purchase) trackPurchase(data.purchase);
        trackConversionEvent("paid_generation_started", { tier: data.tier || "premium_audit" });
        updateLoadingMessage(
            "Writing your Complete Analysis...",
            "Six deep synthesis passes — this usually takes several minutes. Your PDF will also be emailed."
        );
        updateLoadingProgress(3, 15);
        pollForPaidCompletion(data.task_id);
    } catch (err) {
        hideLoading();
        trackConversionEvent("paid_generation_start_error", { error: String(err.message || err) });
        showError(
            "Your payment went through, but we could not start the report automatically. " +
            "Refresh this page to retry — your order is safe and this step can be repeated. " +
            "If it keeps failing, email support@traditional-astrology.com with your checkout email: " +
            "you will get your reading, and a refund if we can't deliver it promptly."
        );
    }
}

function pollForPaidCompletion(taskId) {
    let attempts = 0;
    const maxAttempts = 360; // 30 minutes at 5s intervals — 6 LLM passes take a while

    const interval = setInterval(async () => {
        attempts++;
        const pct = Math.min(92, 15 + Math.floor((attempts / maxAttempts) * 77));
        const stageIndex = Math.min(LOADING_MSGS.length - 2, 3 + Math.floor((attempts / 60) * 3));
        updateLoadingMessage(
            PREMIUM_LOADING_MSGS[attempts % PREMIUM_LOADING_MSGS.length],
            "Your PDF will be emailed to your checkout address even if you close this page."
        );
        updateLoadingProgress(stageIndex, pct);

        if (attempts >= maxAttempts) {
            clearInterval(interval);
            hideLoading();
            showError(
                "The report is taking longer than expected. Don't worry — generation continues in the " +
                "background and the PDF will be emailed to your checkout address. If nothing arrives " +
                "within an hour, email support@traditional-astrology.com."
            );
            return;
        }

        try {
            const resp = await apiFetch(`/api/v1/guest/task-status/${taskId}`);
            if (!resp.ok) return;
            const data = await resp.json();

            if (data.status === "completed") {
                clearInterval(interval);
                updateLoadingProgress(7, 100);
                hideLoading();
                trackConversionEvent("paid_generation_completed", { tier: data.result?.tier || "premium_audit" });
                showPaidReading(data.result);
            } else if (data.status === "failed") {
                clearInterval(interval);
                hideLoading();
                trackConversionEvent("paid_generation_failed");
                showError(
                    "Report generation hit an error. We have been alerted automatically and will " +
                    "regenerate and email your reading. If you don't hear from us within a few hours, " +
                    "email support@traditional-astrology.com — you keep the reading and get a refund " +
                    "if we can't make it right."
                );
            }
        } catch (_) {
            // Suppressed: non-critical poll error; retry next interval
        }
    }, 5000);
}

function showPaidReading(result) {
    const section = document.getElementById("readingSection");
    const content = document.getElementById("readingContent");
    if (!section || !content) return;

    const md = result?.report_markdown || "";
    const html = renderMarkdown(md);
    const traceData = result?.computation_trace || null;
    currentReadingContext = {
        chart_event_id: result?.chart_event_id || null,
        reading_hash: result?.reading_hash || hashStr(JSON.stringify({ chartPayload, md })),
        source: "b2c_paid_reading",
        birth: chartPayload,
        meta: result?.meta || {},
        time_unknown: Boolean(chartPayload?.time_unknown),
    };

    content.innerHTML = `
        <div class="premium-trial-top-banner premium-trial-top-banner--complete" role="status">
            <div class="premium-trial-banner-inner">
                <span class="premium-trial-badge">✦ COMPLETE ANALYSIS</span>
                <p class="premium-trial-headline">
                    Thank you for your purchase. Your <strong>Complete Astrological Analysis</strong> is ready below.
                </p>
                <p class="premium-trial-sub">
                    A PDF copy is on its way to the email you used at checkout. Anything wrong?
                    Email support@traditional-astrology.com — you keep the reading and get your money back.
                </p>
            </div>
        </div>
        <div class="reading-body">${html}</div>
        ${traceData ? buildTraceSection(traceData) : ''}
        <div class="unlock-cta">
            <div class="unlock-buttons">
                <button class="btn-cta btn-cta-secondary" onclick="printReading()" style="width: 100%; margin-top: 0;">
                    Print / Save as PDF
                </button>
                ${buildReadingShareActions()}
            </div>
        </div>
        ${buildFeedbackWidget("paid")}
    `;

    section.classList.remove("hidden");
    section.scrollIntoView({ behavior: "smooth", block: "start" });

    attachFeedbackHandlers(content, "paid");
    const chartActions = document.getElementById("chartActions");
    if (chartActions) chartActions.classList.remove("hidden");
    if (traceData) attachTraceHandlers(content);
}

// ─── Free Reading (Instant) ───
async function requestFreeReading(payload) {
    try {
        const resp = await apiFetch("/api/v1/premium/guest/request", {
            method: "POST",
            headers: authHeaders({ "Content-Type": "application/json" }),
            body: JSON.stringify(payload),
        });

        if (!resp.ok) {
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

        // LLM-backed complete free flow — poll for completion
        if (data.task_id) {
            trackConversionEvent("free_chart_generation_started", {
                chart_event_id: data.chart_event_id,
                tier: data.tier || "free_chart",
            });
            updateLoadingMessage("Writing the complete LLM report...", LOADING_DETAILS[3]);
            updateLoadingProgress(3, 18);
            pollForCompletion(
                data.task_id,
                data.free_readings_remaining,
                data.chart_event_id,
                data.tier || "free_chart"
            );
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
function pollForCompletion(taskId, freeRemaining, chartEventId = null, tier = "free_chart") {
    let msgIdx = 0;
    let attempts = 0;
    const maxAttempts = 144; // 12 minutes at 5s intervals

    const interval = setInterval(async () => {
        attempts++;
        const stageIndex = Math.min(
            LOADING_MSGS.length - 2,
            Math.floor((attempts / maxAttempts) * (LOADING_MSGS.length + 2))
        );
        const pct = Math.min(92, 18 + Math.floor((attempts / maxAttempts) * 74));
        updateLoadingMessage(
            LOADING_MSGS[stageIndex],
            LOADING_DETAILS[stageIndex]
        );
        updateLoadingProgress(stageIndex, pct);
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
                const processingStage = Math.max(stageIndex, 4);
                updateLoadingMessage(
                    LOADING_MSGS[processingStage],
                    LOADING_DETAILS[processingStage]
                );
                updateLoadingProgress(processingStage, Math.max(pct, 35));
            } else if (data.status === "completed") {
                clearInterval(interval);
                updateLoadingMessage("Rendering your free reading...", LOADING_DETAILS[7]);
                updateLoadingProgress(7, 100);
                hideLoading();
                trackConversionEvent("free_chart_success", {
                    free_readings_remaining: freeRemaining,
                    chart_event_id: data.result?.chart_event_id || chartEventId,
                    tier: data.result?.tier || tier,
                });
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
        ${buildShareNudge()}
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

    const astroDataEl = content.querySelector('#astrocartographyData');
    if (astroDataEl) {
        try {
            const astroData = JSON.parse(astroDataEl.textContent);
            renderAstrocartographyMap(astroData);
        } catch (e) {
            console.warn('Astrocartography map render failed:', e);
        }
    }

    section.classList.remove("hidden");
    section.scrollIntoView({ behavior: "smooth", block: "start" });

    // Attach feedback & action handlers
    attachFeedbackHandlers(content, "free");
    const chartActions = document.getElementById("chartActions");
    if (chartActions) chartActions.classList.remove("hidden");

    // The current free chart flow uses complete report generation directly, so
    // there is no second background add-on job to start here.
}

// ─── Retired Free Complete Add-On Bridge ────────────────────────────────────
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
            headers: authHeaders({ "Content-Type": "application/json" }),
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
        console.warn("Retired free report add-on kickoff failed (non-critical):", err);
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

// ─── Retired Free Premium Add-On Polling ────────────────────────────────────
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

function buildReadingShareActions() {
    return `
        <div class="reading-share-actions" aria-label="Share this reading">
            <button type="button" class="btn-cta btn-cta-secondary" data-reading-share-action="share">
                Share Reading
            </button>
            <button type="button" class="btn-cta btn-cta-secondary reading-copy-btn" data-reading-share-action="copy">
                Copy Link
            </button>
            <div class="share-inline-platforms">
                <button type="button" class="share-icon-btn" onclick="openPlatformShare('twitter')" aria-label="Share on X" title="Share on X">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
                </button>
                <button type="button" class="share-icon-btn" onclick="openPlatformShare('facebook')" aria-label="Share on Facebook" title="Share on Facebook">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>
                </button>
                <button type="button" class="share-icon-btn" onclick="openPlatformShare('whatsapp')" aria-label="Share on WhatsApp" title="Share on WhatsApp">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
                </button>
            </div>
            <p class="reading-share-status" data-share-status aria-live="polite"></p>
        </div>
    `;
}

function buildInstantConversionBar(freeRemaining) {
    return `
        <div class="result-conversion-bar" aria-label="Free reading actions">
            <div class="result-conversion-copy">
                <div class="result-conversion-kicker">Your free reading</div>
                <h2>Your traditional astrology reading is ready.</h2>
                <p>Calculated from your real chart: sect, dignities, houses, lots, fixed stars, and classical interpretation.</p>
                <div class="result-conversion-meta">
                    <span>No account or email required</span>
                    <span>Generate another chart whenever you want</span>
                    <span>Free reading stays free</span>
                </div>
                <p class="feedback-reassurance" style="margin:0.85rem 0 0; max-width:none; text-align:left;"><strong>Feedback matters:</strong> use the Good/Bad buttons and comment box at the bottom to tell us how accurate the reading felt.</p>
                <div class="result-conversion-support" id="support-the-work">
                    <p><strong>Want the full depth?</strong> The Complete Astrological Analysis (${PREMIUM_PRICE_LABEL}, one-time) runs six synthesis passes: 20+ pages with advanced timing, all dignity levels, and a 10-year forecast. PDF emailed, no account needed.</p>
                    <div class="result-support-actions">
                        <button class="support-action-btn support-action-primary" type="button" data-premium-checkout data-default-label="Get the Complete Analysis — ${PREMIUM_PRICE_LABEL}">Get the Complete Analysis — ${PREMIUM_PRICE_LABEL}</button>
                    </div>
                    <p class="reading-support-status" data-premium-status aria-live="polite"></p>
                </div>
            </div>
            <div class="result-conversion-actions">
                ${buildReadingShareActions()}
                <button class="btn-cta btn-cta-secondary" onclick="printReading()" data-default-label="Print / Save PDF">
                    Print / Save PDF
                </button>
            </div>
        </div>
    `;
}

// ─── UI: Show Reading (Markdown, polled) ───
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
        source: "b2c_free_chart",
        birth: chartPayload,
        meta: result?.meta || {},
        time_unknown: Boolean(chartPayload?.time_unknown),
    };

    content.innerHTML = `
        ${buildInstantConversionBar(freeRemaining)}
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
    return `
        ${buildPremiumUpsell()}
        <div class="unlock-cta">
            <div class="unlock-buttons">
                <button class="btn-cta btn-cta-secondary" onclick="printReading()" style="width: 100%; margin-top: 0;">
                    Print / Save as PDF
                </button>
                ${buildReadingShareActions()}
            </div>
            <p style="font-size: 0.8rem; color: var(--text-dim); margin-top: 0.5rem;">You can generate another free reading whenever you want.</p>
        </div>
        ${buildShareNudge()}
    `;
}

// ─── UI: Feedback Widget ───
function buildFeedbackWidget(source) {
    const widgetId = source === "premium_trial" ? "premiumFeedbackWidget" : "freeFeedbackWidget";

    const label = source === "premium_trial"
        ? "How accurate did the reading feel?"
        : "How accurate did this chart reading feel?";
    return `
        <div class="feedback-widget" id="${widgetId}">
            <h4>${label}</h4>
            <div class="feedback-buttons">
                <button class="feedback-btn" data-vote="good" aria-label="Thumbs up - good reading">👍 Good</button>
                <button class="feedback-btn" data-vote="bad" aria-label="Thumbs down - bad reading">👎 Bad</button>
            </div>
            <div class="feedback-comment-wrap" style="display:block; margin-top: 1rem;">
                <textarea
                    class="feedback-comment-textarea"
                    placeholder="What felt accurate or off? Your note emails us and helps improve the rules."
                    rows="3"
                    maxlength="1000"
                    aria-label="Optional feedback comment"
                ></textarea>
                <button class="feedback-submit-btn" type="button">Send Feedback</button>
            </div>
            <p class="feedback-status"></p>
            ${source === "paid" ? "" : buildInlineTipBox()}
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

    attachTipHandlers(widget);

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
            if (submitted) return;
            if (!chosenVote) {
                if (statusEl) statusEl.textContent = "Choose Good or Bad first, then send the comment.";
                return;
            }
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
                const supportBox = widget.querySelector(".inline-tip-box");
                if (supportBox) {
                    supportBox.classList.add("inline-tip-box-highlight");
                    trackConversionEvent("tip_prompt_after_feedback", { source: source || "b2c_reading" });
                }
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

// ─── Retired Free Premium Add-On UI Builders ───
function buildPremiumTrialTopBanner() {
    return `
        <div class="premium-trial-top-banner" role="status" aria-live="polite">
            <div class="premium-trial-banner-inner">
                <span class="premium-trial-badge">✦ GENERATING</span>
                <p class="premium-trial-headline">
                    Your <strong>free LLM chart</strong> is generating.
                </p>
                <p class="premium-trial-sub">
                    The free chart now uses complete report generation directly.
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
                    Your <strong>free LLM chart</strong> is complete. Scroll down to read it.
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
                    <h3 class="premium-loading-title">Complete Analysis Generating</h3>
                    <p class="premium-loading-subtitle">Best-tier LLM analysis in progress &mdash; usually a few minutes</p>
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
                <span class="premium-reading-badge">✦ COMPLETE REPORT</span>
                <h2 class="premium-reading-title">Your Complete Traditional Astrology Analysis</h2>
                <p class="premium-reading-subtitle">Complete traditional report generation for this chart</p>
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
                <span class="premium-trial-badge">✦ FULL REPORT INCLUDED</span>
                <h3 class="premium-bottom-title">Keep a copy of the full report</h3>
                <p class="premium-bottom-sub">
                    This is the complete traditional astrology reading for this chart.
                    Use your browser print dialog to save it for later.
                </p>
                <button class="btn-cta btn-cta-secondary" onclick="printReading()" style="width:auto; margin-top:1rem;">
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
            <p class="email-capture-sub">We'll email you a copy of this reading &mdash; no spam. The free report does not require email; email is useful for delivery and support.</p>
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
    updateLoadingMessage(LOADING_MSGS[0], LOADING_DETAILS[0]);

    const readingSection = document.getElementById("readingSection");
    if (readingSection) readingSection.classList.add("hidden");

    // Reset progress bar
    const fill = document.getElementById("loadingProgressFill");
    if (fill) fill.style.width = "4%";

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
        const mins = Math.floor(secs / 60);
        const s = secs % 60;
        const elapsed = mins > 0 ? `${mins}m ${String(s).padStart(2, "0")}s` : `${s}s`;
        if (elapsedEl) elapsedEl.textContent = `Elapsed: ${elapsed} · still working`;
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

function updateLoadingMessage(msg, detail = null) {
    const el = document.getElementById("loadingMessage");
    if (el) {
        el.style.opacity = "0";
        setTimeout(() => {
            el.textContent = msg;
            el.style.opacity = "1";
        }, 200);
    }
    if (detail) {
        const detailEl = document.getElementById("loadingDetail");
        if (detailEl) detailEl.textContent = detail;
    }
}

function buildInlineTipBox() {
    const presetButtons = SUPPORT_TIP_AMOUNTS.map((tip) => (
        `<button class="tip-preset-btn" type="button" data-tip-amount="${tip.amountCents}" data-default-label="${tip.label} tip">${tip.label}</button>`
    )).join("");

    return `
        <div class="inline-tip-box">
            <h4>Keep the free reading free</h4>
            <p>If the reading helped, you can leave a one-time tip. The free reading is already yours either way.</p>
            <p class="inline-tip-impact">Tips pay for chart calculation, report generation, and source research.</p>
            <div class="inline-tip-actions" aria-label="Suggested tip amounts">
                ${presetButtons}
            </div>
            <form class="custom-tip-form" novalidate>
                <label class="custom-tip-label" for="customTipAmount">Tip amount</label>
                <div class="custom-tip-row">
                    <span class="custom-tip-prefix">$</span>
                    <input
                        id="customTipAmount"
                        class="custom-tip-input"
                        type="number"
                        min="1"
                        max="500"
                        step="0.01"
                        value="5"
                        inputmode="decimal"
                        aria-label="Tip amount in dollars"
                    />
                    <button class="feedback-submit-btn tip-submit-btn" type="submit" data-default-label="Tip">Tip</button>
                </div>
                <p class="tip-status" aria-live="polite"></p>
            </form>
        </div>
    `;
}

function attachTipHandlers(container) {
    const form = container.querySelector(".custom-tip-form");
    const tipBox = container.querySelector(".inline-tip-box");
    if (tipBox && !tipBox.dataset.impressionTracked) {
        tipBox.dataset.impressionTracked = "1";
        trackConversionEvent("tip_impression");
    }
    if (!form) return;

    const input = form.querySelector(".custom-tip-input");
    const button = form.querySelector(".tip-submit-btn");
    const status = form.querySelector(".tip-status");

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const dollars = Number(input?.value);
        if (!Number.isFinite(dollars) || dollars < 1) {
            if (status) status.textContent = "Enter an amount of at least $1.";
            return;
        }
        if (dollars > 500) {
            if (status) status.textContent = "Please keep the tip at $500 or less.";
            return;
        }

        const amountCents = Math.round(dollars * 100);
        await startTip(amountCents, button ? [button] : [], status);
    });
}

function setupSupportCheckoutHandlers() {
    document.addEventListener("click", async (event) => {
        const target = event.target instanceof Element ? event.target : null;
        const tipButton = target?.closest("[data-tip-amount]");
        const premiumButton = target?.closest("[data-premium-checkout]");
        const button = tipButton || premiumButton;
        if (!button) return;

        event.preventDefault();
        const host = button.closest(".inline-tip-box, .result-conversion-support, .premium-bottom-banner");
        const status = host?.querySelector(".tip-status, [data-support-status], [data-premium-status]") || null;

        if (tipButton) {
            const amountCents = Number(tipButton.dataset.tipAmount);
            await startTip(amountCents, [tipButton], status);
            return;
        }

        await startPremiumCheckout(premiumButton, status);
    });
}

async function startTip(amountCents, buttons = [], statusEl = null) {
    const amount = Number(amountCents);
    if (!Number.isFinite(amount) || amount < 100 || amount > 50000) {
        if (statusEl) statusEl.textContent = "Choose a valid tip amount.";
        return;
    }

    buttons.forEach((btn) => {
        btn.disabled = true;
        btn.textContent = "Opening...";
    });
    if (statusEl) statusEl.textContent = "Opening secure tip page...";
    trackConversionEvent("tip_click", { amount_cents: amount });

    try {
        const resp = await apiFetch(`/api/v1/guest/tip?amount_cents=${encodeURIComponent(String(amount))}`, {
            method: "POST",
            headers: authHeaders({ "Content-Type": "application/json" }),
            body: "{}",
        });
        if (!resp.ok) {
            const err = await resp.json().catch(() => ({}));
            throw new Error(err?.detail || "Could not start tip page.");
        }
        const data = await resp.json();
        if (!data.url) throw new Error("No tip URL returned.");
        trackConversionEvent("tip_redirect", { amount_cents: amount });
        window.location.href = data.url;
    } catch (err) {
        buttons.forEach((btn) => {
            btn.disabled = false;
            btn.textContent = btn.dataset.defaultLabel || "Tip";
        });
        trackConversionEvent("tip_error", { amount_cents: amount, error: String(err.message || err) });
        if (statusEl) statusEl.textContent = "Could not open tip page. Please try again.";
    }
}

function updateLoadingProgress(stepIndex, percent = null) {
    const totalSteps = LOADING_MSGS.length;
    const pct = percent === null
        ? Math.min(((stepIndex + 1) / totalSteps) * 100, 95)
        : Math.max(0, Math.min(Number(percent), 100));
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
