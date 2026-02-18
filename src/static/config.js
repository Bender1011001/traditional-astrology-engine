window.CAEL_CONFIG = {
    primaryApiUrl: "https://traditional-astrology.com",
    fallbackApiUrl: "https://astrology-engine-central-7387.azurewebsites.net"
};

(function configureApiBase() {
    if (window.CAEL_API_BASE) return;

    const host = String(window.location.hostname || "").toLowerCase();
    const isLocal = host === "localhost" || host === "127.0.0.1";
    const isFirstParty =
        host === "traditional-astrology.com" ||
        host === "www.traditional-astrology.com" ||
        host.endsWith(".azurewebsites.net");

    if (isLocal || host === "") {
        // Local dev: point to local API server explicitly
        window.CAEL_API_BASE = "http://localhost:8000";
        return;
    }

    if (isFirstParty) {
        // Production app host: call same origin.
        window.CAEL_API_BASE = window.location.origin;
        return;
    }

    // Static host (e.g. GH Pages): use canonical API origin.
    window.CAEL_API_BASE = window.CAEL_CONFIG.primaryApiUrl || window.CAEL_CONFIG.fallbackApiUrl;
})();

(function exposeApiFallbackHelpers() {
    function normalizeBase(base) {
        if (typeof base !== "string") return "";
        return base.trim().replace(/\/+$/, "");
    }

    function getApiBaseCandidates() {
        const host = String(window.location.hostname || "").toLowerCase();
        const isLocal = host === "localhost" || host === "127.0.0.1";
        const configured = normalizeBase(window.CAEL_API_BASE);
        const candidates = [];

        function add(base) {
            const normalized = normalizeBase(base);
            if (!normalized) return;
            if (!candidates.includes(normalized)) candidates.push(normalized);
        }

        if (configured) add(configured);
        add(window.location.origin);
        add(window.CAEL_CONFIG.primaryApiUrl);
        add(window.CAEL_CONFIG.fallbackApiUrl);

        if (isLocal && !candidates.includes("")) {
            candidates.unshift("");
        }
        return candidates;
    }

    function buildApiUrl(base, path) {
        const safePath = String(path || "").startsWith("/") ? path : `/${path || ""}`;
        return base ? `${base}${safePath}` : safePath;
    }

    async function fetchWithFallback(path, init) {
        const bases = getApiBaseCandidates();
        let lastError = null;

        for (let i = 0; i < bases.length; i += 1) {
            const url = buildApiUrl(bases[i], path);
            try {
                return await fetch(url, init);
            } catch (error) {
                lastError = error;
                const message = String((error && error.message) || "");
                const isNetworkError =
                    (error && error.name === "TypeError") ||
                    /failed to fetch|networkerror|load failed/i.test(message);
                if (!isNetworkError || i === bases.length - 1) {
                    throw error;
                }
                console.warn(`[api-fallback] ${url} failed; trying next origin`, error);
            }
        }

        throw lastError || new Error("Network request failed.");
    }

    window.caelGetApiBases = getApiBaseCandidates;
    window.caelBuildApiUrl = function (path) {
        return buildApiUrl(normalizeBase(window.CAEL_API_BASE), path);
    };
    window.caelFetchWithFallback = fetchWithFallback;
})();
