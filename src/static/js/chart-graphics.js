import { SIGNS } from './config.js';

export function renderChartWheel(data) {
    const container = document.getElementById('chartWheelContainer');
    const size = 600;
    const center = size / 2;
    const radius = 250;
    const innerRadius = 160;
    const houseRadius = 120;

    let svg = `<svg viewBox="0 0 ${size} ${size}" class="chart-wheel-svg">
        <defs>
            <radialGradient id="ringGrad" cx="50%" cy="50%" r="50%">
                <stop offset="60%" stop-color="transparent" />
                <stop offset="100%" stop-color="rgba(192, 112, 47, 0.15)" />
            </radialGradient>
            <filter id="glow">
                <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
                <feMerge>
                    <feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/>
                </feMerge>
            </filter>
        </defs>
        
        <!-- Background Rings -->
        <circle cx="${center}" cy="${center}" r="${radius + 30}" fill="none" stroke="var(--gold)" stroke-width="0.5" opacity="0.2" />
        <circle cx="${center}" cy="${center}" r="${radius}" fill="url(#ringGrad)" stroke="var(--gold)" stroke-width="2" />
        <circle cx="${center}" cy="${center}" r="${innerRadius}" fill="none" stroke="var(--gold)" stroke-width="1" />
        <circle cx="${center}" cy="${center}" r="${houseRadius}" fill="none" stroke="var(--gold)" stroke-width="0.5" opacity="0.5" />
    `;

    const offset = data.angles.Ascendant;

    // Draw Signs (Counter-Clockwise)
    for (let i = 0; i < 12; i++) {
        const startEcl = i * 30;
        // Wheel Angle = 180 - (Ecliptic - Ascendant)
        const wheelStart = (180 - (startEcl - offset)) % 360;

        // Division line
        const rad = (wheelStart * Math.PI) / 180;
        const x1 = center + innerRadius * Math.cos(rad);
        const y1 = center + innerRadius * Math.sin(rad);
        const x2 = center + radius * Math.cos(rad);
        const y2 = center + radius * Math.sin(rad);
        svg += `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="var(--gold)" stroke-width="1" opacity="0.4" />`;

        // Sign Label
        const labelAngle = ((wheelStart - 15) * Math.PI) / 180;
        const lx = center + (radius - 20) * Math.cos(labelAngle);
        const ly = center + (radius - 20) * Math.sin(labelAngle);
        svg += `<text x="${lx}" y="${ly}" fill="var(--gold)" font-size="12" font-weight="bold" text-anchor="middle" alignment-baseline="middle" transform="rotate(${wheelStart - 105}, ${lx}, ${ly})" opacity="0.8">${SIGNS[i].substring(0, 3).toUpperCase()}</text>`;
    }

    // Draw Houses
    for (const [num, lon] of Object.entries(data.houses)) {
        const wheelLon = (180 - (lon - offset)) % 360;
        const rad = (wheelLon * Math.PI) / 180;
        const x1 = center + houseRadius * Math.cos(rad);
        const y1 = center + houseRadius * Math.sin(rad);
        const x2 = center + innerRadius * Math.cos(rad);
        const y2 = center + innerRadius * Math.sin(rad);

        svg += `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="var(--purple)" stroke-width="1" opacity="0.5" />`;

        // House Number
        const hLabelAngle = ((wheelLon - 15) * Math.PI) / 180;
        const hx = center + (houseRadius + 15) * Math.cos(hLabelAngle);
        const hy = center + (houseRadius + 15) * Math.sin(hLabelAngle);
        svg += `<text x="${hx}" y="${hy}" fill="var(--purple-light)" font-size="9" text-anchor="middle" opacity="0.6">${num}</text>`;
    }

    // Draw Aspects (Connecting Planets)
    const planetEntries = Object.entries(data.planets);
    for (let i = 0; i < planetEntries.length; i++) {
        for (let j = i + 1; j < planetEntries.length; j++) {
            const [p1, info1] = planetEntries[i];
            const [p2, info2] = planetEntries[j];
            const diff = Math.abs(info1.longitude - info2.longitude) % 360;
            const dist = diff > 180 ? 360 - diff : diff;

            let color = "";
            let orb = 5;
            if (dist < orb) color = "var(--gold)"; // Conjunction
            else if (Math.abs(dist - 180) < orb) color = "var(--danger)"; // Opposition
            else if (Math.abs(dist - 90) < orb) color = "var(--danger)"; // Square
            else if (Math.abs(dist - 120) < orb) color = "var(--success)"; // Trine
            else if (Math.abs(dist - 60) < orb) color = "var(--success)"; // Sextile

            if (color) {
                const a1 = ((180 - (info1.longitude - offset)) * Math.PI) / 180;
                const a2 = ((180 - (info2.longitude - offset)) * Math.PI) / 180;
                const r = houseRadius - 10;
                svg += `<line x1="${center + r * Math.cos(a1)}" y1="${center + r * Math.sin(a1)}" x2="${center + r * Math.cos(a2)}" y2="${center + r * Math.sin(a2)}" stroke="${color}" stroke-width="0.5" opacity="0.2" />`;
            }
        }
    }

    // Draw Planets
    const PLANET_GLYPHS = {
        "Sun": "☉", "Moon": "☾", "Mercury": "☿", "Venus": "♀", "Mars": "♂",
        "Jupiter": "♃", "Saturn": "♄", "Uranus": "♅", "Neptune": "♆", "Pluto": "♇",
        "North_Node": "☊", "South_Node": "☋"
    };

    planetEntries.forEach(([name, info]) => {
        const wheelDeg = (180 - (info.longitude - offset)) % 360;
        const rad = (wheelDeg * Math.PI) / 180;
        const r = innerRadius - 25;
        const px = center + r * Math.cos(rad);
        const py = center + r * Math.sin(rad);

        svg += `
            <g class="planet-glyph-group" style="cursor: pointer" onclick='window.showDetailsByPlanet("${name}", ${JSON.stringify(data).replace(/'/g, "&apos;")})'>
                <circle cx="${px}" cy="${py}" r="14" fill="var(--bg-card)" stroke="var(--gold)" stroke-width="1.5" filter="url(#glow)" />
                <text x="${px}" y="${py}" fill="var(--gold)" font-size="16" text-anchor="middle" alignment-baseline="middle">${PLANET_GLYPHS[name] || name.charAt(0)}</text>
            </g>
        `;
    });

    // Center Earth
    svg += `<circle cx="${center}" cy="${center}" r="15" fill="var(--bg-card)" stroke="var(--gold)" stroke-width="1" />`;
    svg += `<text x="${center}" y="${center}" fill="var(--gold)" font-size="8" text-anchor="middle" alignment-baseline="middle">TERRA</text>`;

    svg += `</svg>`;
    container.innerHTML = svg;
}
