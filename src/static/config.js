window.CAEL_CONFIG = {
    primaryApiUrl: "https://traditional-astrology.com",
    fallbackApiUrl: "https://astrology-engine-jknswoor2a-uc.a.run.app",
    signs: [
        "Aries", "Taurus", "Gemini", "Cancer",
        "Leo", "Virgo", "Libra", "Scorpio",
        "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ]
};

(function handleSubdomainRedirect() {
    const host = String(window.location.hostname || "").toLowerCase();
    if (host === "www.traditional-astrology.com") {
        console.warn("Redirecting from www to apex domain to avoid SSL/CORS issues.");
        const newUrl = "https://traditional-astrology.com" + window.location.pathname + window.location.search;
        window.location.replace(newUrl);
    }
})();

(function configureApiBase() {
    if (window.CAEL_API_BASE) return;

    const host = String(window.location.hostname || "").toLowerCase();
    const isLocal = host === "localhost" || host === "127.0.0.1";
    const isFirstParty =
        host === "traditional-astrology.com" ||
        host === "www.traditional-astrology.com" ||
        host.endsWith(".run.app");

    if (isLocal || host === "") {
        // Local dev: point to local API server explicitly
        window.CAEL_API_BASE = "http://127.0.0.1:8000";
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
