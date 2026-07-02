import { SIGNS } from './config.js';

const SIGN_GLYPHS = {
    Aries: "♈",
    Taurus: "♉",
    Gemini: "♊",
    Cancer: "♋",
    Leo: "♌",
    Virgo: "♍",
    Libra: "♎",
    Scorpio: "♏",
    Sagittarius: "♐",
    Capricorn: "♑",
    Aquarius: "♒",
    Pisces: "♓",
};

const PLANET_GLYPHS = {
    Sun: "☉",
    Moon: "☽",
    Mercury: "☿",
    Venus: "♀",
    Mars: "♂",
    Jupiter: "♃",
    Saturn: "♄",
};

const TRADITIONAL_PLANETS = new Set(["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]);

const ROMAN_HOUSES = {
    1: "I",
    2: "II",
    3: "III",
    4: "IV",
    5: "V",
    6: "VI",
    7: "VII",
    8: "VIII",
    9: "IX",
    10: "X",
    11: "XI",
    12: "XII",
};

const ASPECTS = [
    { angle: 0, orb: 6, className: "conjunction" },
    { angle: 60, orb: 4, className: "sextile" },
    { angle: 90, orb: 5, className: "square" },
    { angle: 120, orb: 5, className: "trine" },
    { angle: 180, orb: 6, className: "opposition" },
];

function escapeSvg(value) {
    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
}

function normalizeDeg(value) {
    const n = Number(value) || 0;
    return ((n % 360) + 360) % 360;
}

function wheelAngle(longitude, ascendant) {
    return normalizeDeg(180 - (normalizeDeg(longitude) - normalizeDeg(ascendant)));
}

function polarPoint(center, radius, angleDeg) {
    const rad = (angleDeg * Math.PI) / 180;
    return {
        x: center + radius * Math.cos(rad),
        y: center + radius * Math.sin(rad),
    };
}

function describeArc(center, innerRadius, outerRadius, startAngle, endAngle) {
    const startOuter = polarPoint(center, outerRadius, startAngle);
    const endOuter = polarPoint(center, outerRadius, endAngle);
    const startInner = polarPoint(center, innerRadius, endAngle);
    const endInner = polarPoint(center, innerRadius, startAngle);
    const largeArc = Math.abs(endAngle - startAngle) > 180 ? 1 : 0;

    return [
        `M ${startOuter.x.toFixed(2)} ${startOuter.y.toFixed(2)}`,
        `A ${outerRadius} ${outerRadius} 0 ${largeArc} 1 ${endOuter.x.toFixed(2)} ${endOuter.y.toFixed(2)}`,
        `L ${startInner.x.toFixed(2)} ${startInner.y.toFixed(2)}`,
        `A ${innerRadius} ${innerRadius} 0 ${largeArc} 0 ${endInner.x.toFixed(2)} ${endInner.y.toFixed(2)}`,
        "Z",
    ].join(" ");
}

function zodiacPosition(longitude) {
    const lon = normalizeDeg(longitude);
    const signIndex = Math.floor(lon / 30);
    const signName = SIGNS[signIndex] || "";
    const signLon = lon % 30;
    const degree = Math.floor(signLon);
    const minute = Math.round((signLon - degree) * 60);
    const normalizedDegree = minute === 60 ? degree + 1 : degree;
    const normalizedMinute = minute === 60 ? 0 : minute;
    return `${normalizedDegree}°${String(normalizedMinute).padStart(2, "0")}′ ${SIGN_GLYPHS[signName] || signName}`;
}

function midpointLongitude(start, end) {
    const distance = normalizeDeg(end - start);
    return normalizeDeg(start + distance / 2);
}

function matchingAspect(distance) {
    return ASPECTS.find((aspect) => Math.abs(distance - aspect.angle) <= aspect.orb);
}

function distributedPlanetAngles(planetEntries, ascendant) {
    // Spread label angles so planet glyphs never overlap. Works on the wheel's
    // angular axis (0-360, screen space). Clusters are pushed apart symmetrically
    // around their centre, then relaxed over several passes — so a tight stack of
    // planets (e.g. three in one sign) fans out evenly instead of piling to one side.
    const minSpacing = 15; // degrees of arc between adjacent labels
    const positioned = planetEntries
        .map(([name, info]) => ({
            name,
            ideal: wheelAngle(info.longitude, ascendant),
            angle: wheelAngle(info.longitude, ascendant),
        }))
        .sort((a, b) => a.angle - b.angle);

    const n = positioned.length;
    if (n <= 1) {
        return new Map(positioned.map((p) => [p.name, normalizeDeg(p.angle)]));
    }

    // Relaxation passes: push overlapping neighbours apart in both directions,
    // gently pull each label back toward its true (ideal) position each pass.
    for (let pass = 0; pass < 60; pass++) {
        let moved = false;
        for (let i = 0; i < n; i++) {
            const a = positioned[i];
            const b = positioned[(i + 1) % n];
            let gap = b.angle - a.angle;
            if (i === n - 1) gap += 360; // wrap-around pair
            if (gap < minSpacing) {
                const push = (minSpacing - gap) / 2;
                a.angle -= push;
                b.angle += push;
                moved = true;
            }
        }
        // Light spring back toward ideal so labels stay near their real degree.
        for (const p of positioned) {
            const diff = ((p.ideal - p.angle + 540) % 360) - 180;
            p.angle += diff * 0.05;
        }
        if (!moved) break;
    }

    return new Map(positioned.map((p) => [p.name, normalizeDeg(p.angle)]));
}

function renderRingLabel(svg, label, x, y, className, extra = "") {
    svg.push(
        `<text class="${className}" x="${x.toFixed(2)}" y="${y.toFixed(2)}" text-anchor="middle" dominant-baseline="middle" ${extra}>${escapeSvg(label)}</text>`
    );
}

export function renderChartWheel(data) {
    const container = document.getElementById('chartWheelContainer');
    if (!container || !data?.planets || !data?.houses || !data?.angles) return;

    const size = 720;
    const center = size / 2;
    const outerRadius = 330;
    const zodiacOuter = 308;
    const zodiacInner = 248;
    const houseOuter = 240;
    const houseInner = 126;
    const aspectRadius = 104;
    const planetPointRadius = 232;
    const planetLabelRadius = 198;
    const ascendant = normalizeDeg(data.angles.Ascendant);
    const houses = data.houses || {};
    const planetEntries = Object.entries(data.planets)
        .filter(([name, info]) => TRADITIONAL_PLANETS.has(name) && info && info.longitude !== undefined && info.longitude !== null)
        .sort((a, b) => normalizeDeg(a[1].longitude) - normalizeDeg(b[1].longitude));
    const labelAngles = distributedPlanetAngles(planetEntries, ascendant);

    const svg = [
        `<svg viewBox="0 0 ${size} ${size}" class="chart-wheel-svg" role="img" aria-label="Traditional astrology natal chart wheel">`,
        `<defs>
            <radialGradient id="chartPaperGlow" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stop-color="rgba(252,244,218,0.08)" />
                <stop offset="64%" stop-color="rgba(252,244,218,0.025)" />
                <stop offset="100%" stop-color="rgba(201,168,76,0.16)" />
            </radialGradient>
            <filter id="wheelTextShadow" x="-20%" y="-20%" width="140%" height="140%">
                <feDropShadow dx="0" dy="1" stdDeviation="1.4" flood-color="#05050b" flood-opacity="0.75" />
            </filter>
        </defs>`,
        `<rect x="18" y="18" width="${size - 36}" height="${size - 36}" rx="18" class="chart-wheel-plate" />`,
        `<circle cx="${center}" cy="${center}" r="${outerRadius}" class="chart-wheel-outer-halo" />`,
        `<circle cx="${center}" cy="${center}" r="${zodiacOuter}" class="chart-wheel-zodiac-backdrop" />`,
    ];

    // Zodiac ring.
    for (let i = 0; i < 12; i++) {
        const startLon = i * 30;
        const endLon = startLon + 30;
        const startAngle = wheelAngle(startLon, ascendant);
        const endAngle = wheelAngle(endLon, ascendant);
        const signName = SIGNS[i];
        const labelPoint = polarPoint(center, 278, wheelAngle(startLon + 15, ascendant));
        svg.push(
            `<path d="${describeArc(center, zodiacInner, zodiacOuter, endAngle, startAngle)}" class="zodiac-slice zodiac-slice-${i % 2}" />`
        );
        renderRingLabel(
            svg,
            SIGN_GLYPHS[signName] || signName.slice(0, 3),
            labelPoint.x,
            labelPoint.y,
            "zodiac-glyph",
            `transform="rotate(${wheelAngle(startLon + 15, ascendant) + 90}, ${labelPoint.x.toFixed(2)}, ${labelPoint.y.toFixed(2)})"`
        );
    }

    // Degree ticks and sign boundaries.
    for (let degree = 0; degree < 360; degree += 5) {
        const angle = wheelAngle(degree, ascendant);
        const isSignBoundary = degree % 30 === 0;
        const isDecan = degree % 10 === 0;
        const tickStart = isSignBoundary ? zodiacInner - 2 : isDecan ? zodiacOuter - 18 : zodiacOuter - 11;
        const tickEnd = zodiacOuter;
        const p1 = polarPoint(center, tickStart, angle);
        const p2 = polarPoint(center, tickEnd, angle);
        svg.push(
            `<line x1="${p1.x.toFixed(2)}" y1="${p1.y.toFixed(2)}" x2="${p2.x.toFixed(2)}" y2="${p2.y.toFixed(2)}" class="${isSignBoundary ? "zodiac-boundary" : "degree-tick"}" />`
        );
    }

    svg.push(
        `<circle cx="${center}" cy="${center}" r="${zodiacInner}" class="chart-ring chart-ring-strong" />`,
        `<circle cx="${center}" cy="${center}" r="${houseOuter}" class="chart-ring chart-ring-soft" />`,
        `<circle cx="${center}" cy="${center}" r="${houseInner}" class="chart-ring chart-ring-soft" />`,
        `<circle cx="${center}" cy="${center}" r="${aspectRadius}" class="aspect-field" />`
    );

    // Houses.
    for (let house = 1; house <= 12; house++) {
        const lon = houses[String(house)] ?? houses[house];
        if (lon === undefined || lon === null) continue;

        const angle = wheelAngle(lon, ascendant);
        const p1 = polarPoint(center, houseInner, angle);
        const p2 = polarPoint(center, houseOuter, angle);
        const isAngular = [1, 4, 7, 10].includes(house);
        svg.push(
            `<line x1="${p1.x.toFixed(2)}" y1="${p1.y.toFixed(2)}" x2="${p2.x.toFixed(2)}" y2="${p2.y.toFixed(2)}" class="${isAngular ? "house-cusp house-cusp-angular" : "house-cusp"}" />`
        );

        const nextLon = houses[String(house === 12 ? 1 : house + 1)] ?? houses[house === 12 ? 1 : house + 1];
        const labelLon = nextLon === undefined || nextLon === null
            ? normalizeDeg(Number(lon) + 15)
            : midpointLongitude(Number(lon), Number(nextLon));
        const labelPoint = polarPoint(center, 174, wheelAngle(labelLon, ascendant));
        renderRingLabel(svg, ROMAN_HOUSES[house] || house, labelPoint.x, labelPoint.y, "house-number");
    }

    // Angles.
    const axisLabels = [
        ["ASC", ascendant],
        ["DSC", ascendant + 180],
    ];
    const mc = houses["10"] ?? houses[10];
    if (mc !== undefined && mc !== null) {
        axisLabels.push(["MC", Number(mc)], ["IC", Number(mc) + 180]);
    }
    for (const [label, lon] of axisLabels) {
        const angle = wheelAngle(lon, ascendant);
        const lineStart = polarPoint(center, 44, angle);
        const lineEnd = polarPoint(center, zodiacInner, angle);
        const labelPoint = polarPoint(center, 326, angle);
        svg.push(
            `<line x1="${lineStart.x.toFixed(2)}" y1="${lineStart.y.toFixed(2)}" x2="${lineEnd.x.toFixed(2)}" y2="${lineEnd.y.toFixed(2)}" class="angle-axis" />`
        );
        renderRingLabel(svg, label, labelPoint.x, labelPoint.y, "angle-label");
    }

    // Aspects.
    for (let i = 0; i < planetEntries.length; i++) {
        for (let j = i + 1; j < planetEntries.length; j++) {
            const [, info1] = planetEntries[i];
            const [, info2] = planetEntries[j];
            const diff = Math.abs(normalizeDeg(info1.longitude) - normalizeDeg(info2.longitude));
            const distance = diff > 180 ? 360 - diff : diff;
            const aspect = matchingAspect(distance);
            if (!aspect) continue;

            const a1 = wheelAngle(info1.longitude, ascendant);
            const a2 = wheelAngle(info2.longitude, ascendant);
            const p1 = polarPoint(center, aspectRadius, a1);
            const p2 = polarPoint(center, aspectRadius, a2);
            svg.push(
                `<line x1="${p1.x.toFixed(2)}" y1="${p1.y.toFixed(2)}" x2="${p2.x.toFixed(2)}" y2="${p2.y.toFixed(2)}" class="aspect-line aspect-${aspect.className}" />`
            );
        }
    }

    // Planet markers and labels.
    for (const [name, info] of planetEntries) {
        const trueAngle = wheelAngle(info.longitude, ascendant);
        const labelAngle = labelAngles.get(name) ?? trueAngle;
        const point = polarPoint(center, planetPointRadius, trueAngle);
        const labelPoint = polarPoint(center, planetLabelRadius, labelAngle);
        const glyph = PLANET_GLYPHS[name] || name.charAt(0);
        const label = `${glyph} ${zodiacPosition(info.longitude)}${info.retrograde ? " R" : ""}`;
        const safeName = escapeSvg(name.replace(/_/g, " "));

        svg.push(
            `<g class="planet-marker" data-planet="${escapeSvg(name)}">
                <title>${safeName}: ${escapeSvg(zodiacPosition(info.longitude))}${info.retrograde ? " retrograde" : ""}</title>
                <line x1="${point.x.toFixed(2)}" y1="${point.y.toFixed(2)}" x2="${labelPoint.x.toFixed(2)}" y2="${labelPoint.y.toFixed(2)}" class="planet-leader" />
                <circle cx="${point.x.toFixed(2)}" cy="${point.y.toFixed(2)}" r="4.6" class="planet-dot" />
                <g transform="translate(${labelPoint.x.toFixed(2)} ${labelPoint.y.toFixed(2)})">
                    <rect x="-35" y="-12" width="70" height="24" rx="12" class="planet-label-backdrop" />
                    <text class="planet-label" x="0" y="0" text-anchor="middle" dominant-baseline="middle">${escapeSvg(label)}</text>
                </g>
            </g>`
        );
    }

    svg.push(
        `<circle cx="${center}" cy="${center}" r="40" class="chart-wheel-center" />`,
        `<text x="${center}" y="${center - 4}" text-anchor="middle" dominant-baseline="middle" class="chart-center-title">WHOLE</text>`,
        `<text x="${center}" y="${center + 13}" text-anchor="middle" dominant-baseline="middle" class="chart-center-subtitle">SIGN</text>`,
        "</svg>"
    );

    container.innerHTML = svg.join("");
}
