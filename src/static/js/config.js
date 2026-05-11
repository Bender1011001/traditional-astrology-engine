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

function purchaseStorageKey(transactionId) {
    return `ta_purchase_tracked_${transactionId}`;
}

function storageHasKey(key) {
    try {
        return window.localStorage.getItem(key) === "1";
    } catch (_) {
        try {
            return window.sessionStorage.getItem(key) === "1";
        } catch (__) {
            return false;
        }
    }
}

function storageSetKey(key) {
    try {
        window.localStorage.setItem(key, "1");
        return;
    } catch (_) {
        try {
            window.sessionStorage.setItem(key, "1");
        } catch (__) {
            // No persistent storage available; the purchase event was still sent.
        }
    }
}

function normalizePurchasePayload(purchase) {
    if (!purchase || typeof purchase !== "object") return null;

    const transactionId = String(
        purchase.transaction_id || purchase.session_id || purchase.order_id || ""
    ).trim();
    if (!transactionId) return null;

    const amountCents = Number(purchase.amount_cents);
    const rawValue = Number(purchase.value);
    const value = Number.isFinite(rawValue)
        ? rawValue
        : (Number.isFinite(amountCents) ? amountCents / 100 : 0);
    const currency = String(purchase.currency || "USD").trim().toUpperCase();
    const tier = String(purchase.tier || "unknown").trim() || "unknown";
    const items = Array.isArray(purchase.items) && purchase.items.length > 0
        ? purchase.items
        : [{
            item_id: tier,
            item_name: "Traditional Astrology Purchase",
            item_category: "paid_reading",
            price: value,
            quantity: 1,
        }];

    return {
        transaction_id: transactionId,
        value,
        currency,
        items,
        tier,
        order_id: purchase.order_id || transactionId,
    };
}

export function trackPurchase(purchase) {
    try {
        if (typeof window.gtag !== "function") return false;
        const payload = normalizePurchasePayload(purchase);
        if (!payload) return false;

        const key = purchaseStorageKey(payload.transaction_id);
        if (storageHasKey(key)) return false;

        window.gtag("event", "purchase", payload);
        storageSetKey(key);
        return true;
    } catch (_) {
        return false;
    }
}
