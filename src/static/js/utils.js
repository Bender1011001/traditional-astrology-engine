import { SIGNS } from './config.js';

export function escapeHtml(value) {
    return String(value || "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
}

export function formatLongitude(lon) {
    let signIdx = Math.floor(lon / 30) % 12;
    let degree = lon % 30;
    let d = Math.floor(degree);
    let m = Math.floor((degree - d) * 60);
    return `${d}° ${SIGNS[signIdx]} ${m}'`;
}

export function formatPlainReading(text) {
    const safe = escapeHtml(text);
    const paragraphs = safe.split(/\n{2,}/).map(p => p.trim()).filter(Boolean);
    if (!paragraphs.length) return "";
    return paragraphs.map(p => `<p>${p.replace(/\n/g, "<br>")}</p>`).join("");
}

export function hashString(value) {
    let hash = 5381;
    const str = String(value || "");
    for (let i = 0; i < str.length; i++) {
        hash = ((hash << 5) + hash) + str.charCodeAt(i);
        hash |= 0;
    }
    return `djb2_${Math.abs(hash)}`;
}
