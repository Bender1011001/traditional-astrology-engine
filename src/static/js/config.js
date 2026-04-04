export const SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
];

const DEFAULT_API_URL = "https://traditional-astrology.com";

if (!window.CAEL_API_BASE && window.location.hostname !== "localhost" && window.location.hostname !== "127.0.0.1") {
    window.CAEL_API_BASE = DEFAULT_API_URL;
}

export const API_BASE = window.CAEL_API_BASE || "";

/**
 * Safe event tracking wrapper. Sends to GA4 via gtag if available.
 * @param {string} eventName - The event name (e.g. "horary_success")
 * @param {object} [params] - Optional event parameters
 */
export function trackEvent(eventName, params) {
    try {
        if (typeof window.gtag === "function") {
            window.gtag("event", eventName, params || {});
        }
    } catch (_) {
        // Silently swallow — analytics should never break the app
    }
}
