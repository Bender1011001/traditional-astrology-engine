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

    if (isLocal) {
        // Local dev: same-origin API.
        window.CAEL_API_BASE = "";
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
