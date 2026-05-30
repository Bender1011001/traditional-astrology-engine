const SVG_W = 960;
const SVG_H = 500;

const LANDMASSES = [
    [
        [-168, 72], [-140, 70], [-124, 58], [-104, 50], [-86, 50], [-70, 45],
        [-58, 52], [-58, 42], [-78, 25], [-97, 18], [-117, 24], [-128, 38],
        [-150, 52], [-168, 60],
    ],
    [
        [-82, 12], [-66, 9], [-49, -5], [-40, -20], [-53, -56], [-68, -54],
        [-76, -35], [-81, -10],
    ],
    [
        [-18, 35], [4, 37], [23, 32], [35, 14], [44, -3], [33, -32],
        [18, -35], [4, -29], [-8, -5], [-17, 18],
    ],
    [
        [-10, 58], [20, 70], [60, 62], [94, 70], [142, 58], [165, 48],
        [146, 32], [108, 20], [86, 8], [60, 22], [44, 12], [28, 32],
        [12, 42], [-4, 41],
    ],
    [
        [44, 28], [65, 24], [80, 8], [78, -4], [60, 6], [50, 16],
    ],
    [
        [112, -12], [154, -10], [154, -36], [134, -44], [114, -34],
    ],
    [
        [-52, 82], [-20, 78], [-26, 62], [-46, 58], [-62, 66],
    ],
    [
        [-180, -70], [-120, -74], [-60, -72], [0, -76], [60, -72], [120, -74],
        [180, -70], [180, -90], [-180, -90],
    ],
];

function project(lon, lat) {
    const x = ((Number(lon) + 180) / 360) * SVG_W;
    const y = ((90 - Number(lat)) / 180) * SVG_H;
    return [x, y];
}

function pointsAttr(points) {
    return points
        .map(([lon, lat]) => project(lon, lat).map((v) => v.toFixed(1)).join(","))
        .join(" ");
}

function linePoints(segment) {
    return segment
        .map((point) => project(point.lon, point.lat).map((v) => v.toFixed(1)).join(","))
        .join(" ");
}

function escapeHtml(value) {
    const div = document.createElement("div");
    div.textContent = value == null ? "" : String(value);
    return div.innerHTML;
}

function strokeWidth(score) {
    const bounded = Math.max(0, Math.min(100, Number(score) || 0));
    return (1.1 + (bounded / 100) * 2.2).toFixed(2);
}

function opacity(score) {
    const bounded = Math.max(0, Math.min(100, Number(score) || 0));
    return (0.42 + (bounded / 100) * 0.48).toFixed(2);
}

function lineSvg(line) {
    const pattern = line.stroke_pattern || (line.stroke === "dashed" ? "7 7" : "");
    const dash = pattern ? ` stroke-dasharray="${escapeHtml(pattern)}"` : "";
    return (line.segments || [])
        .map((segment) => {
            if (!Array.isArray(segment) || segment.length < 2) return "";
            return `
                <polyline
                    class="astro-map-line"
                    points="${linePoints(segment)}"
                    fill="none"
                    stroke="${escapeHtml(line.color || "#d4af37")}"
                    stroke-width="${strokeWidth(line.score)}"
                    stroke-opacity="${opacity(line.score)}"
                    ${dash}
                >
                    <title>${escapeHtml(line.label)}: ${escapeHtml(line.score_label)}. ${escapeHtml(line.interpretation)}</title>
                </polyline>
            `;
        })
        .join("");
}

function markerSvg(target) {
    const [x, y] = project(target.longitude, target.latitude);
    return `
        <g class="astro-map-target" transform="translate(${x.toFixed(1)} ${y.toFixed(1)})">
            <circle r="5.5"></circle>
            <circle r="13"></circle>
            <title>${escapeHtml(target.name)}</title>
        </g>
    `;
}

function mapSvg(data) {
    const graticule = [];
    for (let lon = -150; lon <= 150; lon += 30) {
        const [x] = project(lon, 0);
        graticule.push(`<line x1="${x.toFixed(1)}" y1="18" x2="${x.toFixed(1)}" y2="${SVG_H - 18}" />`);
    }
    for (let lat = -60; lat <= 60; lat += 30) {
        const [, y] = project(0, lat);
        graticule.push(`<line x1="18" y1="${y.toFixed(1)}" x2="${SVG_W - 18}" y2="${y.toFixed(1)}" />`);
    }

    const land = LANDMASSES
        .map((shape) => `<polygon points="${pointsAttr(shape)}" />`)
        .join("");

    const lines = (data.lines || []).map(lineSvg).join("");
    const targets = (data.target_locations || []).map(markerSvg).join("");

    return `
        <svg class="astro-map-svg" viewBox="0 0 ${SVG_W} ${SVG_H}" role="img" aria-label="Astrocartography world map">
            <rect class="astro-map-ocean" x="0" y="0" width="${SVG_W}" height="${SVG_H}" rx="10"></rect>
            <g class="astro-map-graticule">${graticule.join("")}</g>
            <g class="astro-map-land">${land}</g>
            <g class="astro-map-lines">${lines}</g>
            <g class="astro-map-markers">${targets}</g>
        </svg>
    `;
}

function rankedList(data) {
    const items = (data.ranked_lines || []).slice(0, 8);
    if (!items.length) return "";
    return `
        <div class="astro-map-ranked">
            ${items
                .map((line) => `
                    <div class="astro-map-ranked-item">
                        <span class="astro-map-swatch" style="border-color:${escapeHtml(line.color || "#d4af37")}"></span>
                        <div>
                            <div class="astro-map-ranked-title">${escapeHtml(line.label)} <span>${Number(line.score) || 0}/100</span></div>
                            <p>${escapeHtml(line.interpretation)}</p>
                        </div>
                    </div>
                `)
                .join("")}
        </div>
    `;
}

function angleLegend() {
    return `
        <div class="astro-map-angle-legend" aria-label="Line style legend">
            <span><i class="legend-line legend-line-mc"></i>MC</span>
            <span><i class="legend-line legend-line-ic"></i>IC</span>
            <span><i class="legend-line legend-line-asc"></i>ASC</span>
            <span><i class="legend-line legend-line-dsc"></i>DSC</span>
        </div>
    `;
}

function targetList(data) {
    const targets = data.target_locations || [];
    if (!targets.length) return "";
    return `
        <div class="astro-map-targets">
            ${targets
                .map((target) => `
                    <div class="astro-map-target-card">
                        <strong>${escapeHtml(target.name)}</strong>
                        <p>${(target.closest_symbolic_lines || [])
                            .slice(0, 3)
                            .map((hit) => `${escapeHtml(hit.label)} (${escapeHtml(hit.distance_km)} km)`)
                            .join(" | ") || "No close angular lines in the review radius."}</p>
                    </div>
                `)
                .join("")}
        </div>
    `;
}

export function renderAstrocartographyMap(data, container = "astrocartographyMapContainer") {
    const root = typeof container === "string" ? document.getElementById(container) : container;
    if (!root || !data || !Array.isArray(data.lines)) return;

    const houseLabel = data.chart?.house_system?.label || "Whole Sign";
    const confidence = data.chart?.time_confidence === "low_noon_placeholder"
        ? `<p class="astro-map-warning">Birth time unknown: this uses the noon placeholder and should not be treated as precise.</p>`
        : "";

    root.innerHTML = `
        <div class="astro-map-shell">
            ${mapSvg(data)}
            <div class="astro-map-meta">
                <div>
                    <span class="astro-map-kicker">${escapeHtml(data.intent?.label || "General map")}</span>
                    <h3>Strongest chart lines</h3>
                </div>
                <div class="astro-map-badges">
                    <span class="astro-map-band">7 traditional planets</span>
                    <span class="astro-map-band">${escapeHtml(houseLabel)}</span>
                    <span class="astro-map-band">${escapeHtml(data.map?.influence_band_km || 300)} km symbolic band</span>
                </div>
            </div>
            ${angleLegend()}
            ${confidence}
            ${rankedList(data)}
            ${targetList(data)}
        </div>
    `;
}
