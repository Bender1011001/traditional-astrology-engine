import { apiUrl } from './api.js';

const IS_GH_PAGES = window.location.hostname.endsWith("github.io");
const LOG_ENABLED = !IS_GH_PAGES || (window.CAEL_API_BASE || "");
const LOG_SESSION_KEY = "cael_session_id";
let _sessionEnded = false;
const _sessionStart = Date.now();

export function getSessionId() {
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

export const SESSION_ID = getSessionId();

export function logEvent(eventType, payload = {}, options = {}) {
    if (!LOG_ENABLED) return;
    const body = {
        event_type: eventType,
        element_id: payload.element_id || null,
        url: window.location.href,
        data: {
            ...payload,
            session_id: SESSION_ID,
            ts: new Date().toISOString()
        }
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

export async function logTelemetry(eventType, elementId = null, data = null) {
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

        fetch(apiUrl("/api/log/telemetry"), {
            method: 'POST',
            headers: headers,
            body: JSON.stringify(payload),
            keepalive: true
        }).catch(() => { });
    } catch (e) { }
}

export function endSession(reason) {
    if (_sessionEnded) return;
    _sessionEnded = true;
    const durationMs = Date.now() - _sessionStart;
    logEvent("session_end", { duration_ms: durationMs, reason }, { beacon: true });
}

// Initialize global telemetry listeners
export function initTelemetry() {
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

    logEvent("page_view", { path: window.location.pathname, referrer: document.referrer || null });
    window.addEventListener("beforeunload", () => endSession("unload"));
    document.addEventListener("visibilitychange", () => {
        if (document.visibilityState === "hidden") endSession("hidden");
    });
}
