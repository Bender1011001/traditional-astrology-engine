import { SIGNS } from './config.js';

/**
 * Escape HTML special characters to prevent XSS attacks.
 * Use this for ALL user-provided or API-provided data.
 */
export function escapeHtml(value) {
    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
}

/**
 * Safe HTML template tag - automatically escapes interpolated values.
 * Usage: safeHTML`<div>${userInput}</div>` 
 * This is the preferred way to build HTML with dynamic data.
 */
export function safeHTML(strings, ...values) {
    return strings.reduce((result, str, i) => {
        const value = i < values.length ? escapeHtml(values[i]) : '';
        return result + str + value;
    }, '');
}

/**
 * Sanitize an object's string values recursively for safe HTML insertion.
 * Returns a new object with all string values escaped.
 */
export function sanitizeData(obj) {
    if (typeof obj === 'string') return escapeHtml(obj);
    if (typeof obj !== 'object' || obj === null) return obj;
    if (Array.isArray(obj)) return obj.map(sanitizeData);
    const result = {};
    for (const [key, value] of Object.entries(obj)) {
        result[key] = sanitizeData(value);
    }
    return result;
}


export function formatLongitude(lon) {
    let signIdx = Math.floor(lon / 30) % 12;
    let degree = lon % 30;
    let d = Math.floor(degree);
    let m = Math.floor((degree - d) * 60);
    return `${d}° ${SIGNS[signIdx]} ${m}'`;
}

export function renderMarkdown(text) {
    if (!text) return "";

    // 1. Protection: Basic escaping of < and > (except those we might want to allow if any)
    let html = text.replace(/</g, "&lt;").replace(/>/g, "&gt;");

    // 2. Headers (### Header)
    html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
    html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
    html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');

    // 3. Bold (**bold**)
    html = html.replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>');

    // 4. Lists (- item)
    html = html.replace(/^\- (.*$)/gim, '<li>$1</li>');
    // Wrap lists in <ul>
    // This is a bit tricky with regex only, but we can do a simple version:
    // If a line starts with <li> and previous didn't, or vice-versa.
    // For simplicity in Vanilla, we can just let it stay as <li> which browser handles okay-ish
    // or we can wrap the whole block.

    // 5. Horizontal Rules (---)
    html = html.replace(/^---$/gim, '<hr class="ornament">');

    // 6. Blockquotes (> quote)
    html = html.replace(/^> (.*$)/gim, '<blockquote style="border-left: 2px solid var(--gold); padding-left: 1rem; margin-left: 0; font-style: italic;">$1</blockquote>');

    // 7. Paragraphs & Line breaks
    // Double newlines to <p>
    const chunks = html.split(/\n\s*\n/);
    return chunks.map(chunk => {
        if (chunk.includes('<h') || chunk.includes('<hr') || chunk.includes('<li') || chunk.includes('<blockquote')) {
            return chunk;
        }
        return `<p>${chunk.replace(/\n/g, "<br>")}</p>`;
    }).join("");
}

export function formatPlainReading(text) {
    return renderMarkdown(text);
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
