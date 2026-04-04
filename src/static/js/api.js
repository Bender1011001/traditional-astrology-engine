/**
 * Builds a full API URL using the current Base.
 */
export function apiUrl(path) {
    const safePath = String(path || "").startsWith("/") ? path : `/${path || ""}`;
    const base = typeof window !== "undefined" ? window.CAEL_API_BASE : "";
    return `${base}${safePath}`;
}

/**
 * Resilient fetch that uses the global fallback mechanism if available.
 */
export async function apiFetch(path, init) {
    if (typeof window !== "undefined" && window.caelFetchWithFallback) {
        return await window.caelFetchWithFallback(path, init);
    }
    // Fallback for environments where the global script isn't loaded (tests, etc)
    return await fetch(apiUrl(path), init);
}
