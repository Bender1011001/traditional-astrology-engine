import { SIGNS } from './config.js';
import { escapeHtml, formatLongitude, formatPlainReading, hashString } from './utils.js';
import { renderChartWheel } from './chart-graphics.js';
import { apiUrl } from './api.js';
import { logEvent } from './telemetry.js';

export let currentResult = null;
export let currentLot = 'Spirit';

export function setCurrentResult(data) {
    currentResult = data;
}

export function setCurrentLot(lot) {
    currentLot = lot;
}

export function renderResults(data) {
    currentResult = data;
    const resultsSection = document.getElementById('results');
    if (resultsSection) resultsSection.classList.remove('results-hidden');

    renderChartWheel(data);
    renderMundaneContext(data);
    renderSummaryExtras(data);
    renderRuleLedger(data);
    renderSoulGuardian(data);
    renderVitality(data);
    renderMutualReceptions(data);
    renderPrimaryDirections(data);
    renderLots(data);
    renderCelestialWitnesses(data);
    renderHoraryPhysics(data);
    renderForensicGrid(data);
    renderTechnicalData(data);
    renderPrediction(data);
    renderAdvancedPrediction(data);
    renderForecast(data);
    initMedicalCheck(data);
    renderOracle(data);
    renderFateTimeline(data, currentLot);

    if (resultsSection) resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function renderMundaneContext(data) {
    const mundaneDiv = document.getElementById('mundaneContext');
    if (!mundaneDiv) return;
    let mundaneHTML = "";
    if (data.forensic_report) {
        let events = (data.forensic_report.summary.universal_events || []).map(e => `[${e.type} in ${e.sign}]`).join(' ');
        let summary = data.forensic_report.summary;
        let dominant = summary.dominant_elements && summary.dominant_elements.length ? summary.dominant_elements[0][0] : 'Unknown';
        mundaneHTML = `
            <div style="display: flex; gap: 2rem; flex-wrap: wrap;">
                <div><strong>LUNAR PHASE:</strong> ${summary.lunar_phase}</div>
                <div><strong>JONES PATTERN:</strong> ${summary.jones_pattern}</div>
                <div><strong>DOMINANT:</strong> ${dominant}</div>
                ${events ? `<div><strong>ECLIPSE:</strong> ${events}</div>` : ''}
            </div>
        `;
        mundaneDiv.innerHTML = mundaneHTML;
        mundaneDiv.style.display = 'block';
    } else {
        mundaneDiv.style.display = 'none';
    }
}

function renderSummaryExtras(data) {
    const lunarCard = document.getElementById('lunarProfileCard');
    const temperamentCard = document.getElementById('temperamentCard');
    const eventsCard = document.getElementById('universalEventsCard');
    const causeCard = document.getElementById('universalCausationCard');

    if (!data.forensic_report || !data.forensic_report.summary) {
        if (lunarCard) lunarCard.innerHTML = `<h4>LUNAR PHASE</h4><p class="placeholder-text">No summary available.</p>`;
        return;
    }

    const summary = data.forensic_report.summary;

    if (lunarCard) {
        let mansionHTML = '';
        if (summary.lunar_mansion) {
            const m = summary.lunar_mansion;
            mansionHTML = `
                <div style="margin-top: 0.5rem; padding-top: 0.5rem; border-top: 1px solid rgba(255,255,255,0.1);">
                    <div style="color: var(--gold); font-weight: bold; font-family: 'Space Mono', monospace;">MANSION ${m.mansion_id}: ${m.name.toUpperCase()}</div>
                    <div style="font-size: 0.8em; margin-top: 0.3rem;">
                         <span style="color: var(--success);">FOR:</span> ${m.intents_good.slice(0, 3).join(', ')}
                    </div>
                </div>
             `;
        }
        lunarCard.innerHTML = `
            <h4>LUNAR PHASE</h4>
            <div class="summary-list">
                <div><strong>YOU ARE IN:</strong> ${summary.lunar_phase}</div>
                ${mansionHTML}
            </div>
        `;
    }

    if (temperamentCard && summary.temperament) {
        temperamentCard.innerHTML = `<h4>TEMPERAMENT</h4><div style="color:var(--gold)">YOU ARE: ${summary.temperament.primary_temperament}</div>`;
    }
}

export function renderSoulGuardian(data) {
    const card = document.getElementById('soulGuardianCard');
    const teamCard = document.getElementById('soulGuardianTeam');
    if (!card || !data.forensic_report || !data.forensic_report.soul_guardian) return;
    const sg = data.forensic_report.soul_guardian;
    card.innerHTML = `
       <h3>PRIMARY RULER (ALMUTEN FIGURIS)</h3>
       <div class="guardian-title">YOU ARE RULED BY: ${sg.almuten}</div>
       <div class="guardian-job">${sg.job_description}</div>
    `;

    // Team Logic
    const summary = data.forensic_report.summary || {};
    const constructive = summary.constructive_team || [];
    const destructive = summary.destructive_team || [];
    if (teamCard) {
        teamCard.innerHTML = `
            <h3>SECT ALIGNMENT & DAY MASTERY</h3>
            <div class="tool-result-detail">Constructive: ${constructive.join(', ') || 'None'}</div>
            <div class="tool-result-detail">Destructive: ${destructive.join(', ') || 'None'}</div>
        `;
    }
}

export function renderMutualReceptions(data) {
    const card = document.getElementById('soulGuardianTeam'); // Re-using sectTeamCard logic
    if (!card || !data.forensic_report) return;
    const summary = data.forensic_report.summary || {};
    const receptions = summary.mutual_receptions || [];
    if (receptions.length > 0) {
        card.insertAdjacentHTML('beforeend', `<div class="tool-result-detail" style="margin-top: 1rem;">MUTUAL RECEPTION: ${receptions.map(r => `${r.planet_a}-${r.planet_b}`).join(', ')}</div>`);
    }
}

export function renderVitality(data) {
    const card = document.getElementById('vitalityCard');
    if (!card || !data.forensic_report || !data.forensic_report.vitality) return;
    const v = data.forensic_report.vitality;
    card.innerHTML = `
        <h3>VITALITY</h3>
        <div>Hyleg: ${v.hyleg} | Alcocoden: ${v.alcocoden}</div>
        <div>Years: ${v.total_years.toFixed(1)}</div>
    `;
}

export function renderPrimaryDirections(data) {
    const card = document.getElementById('pdCard');
    if (!card) return;
    const dirs = data.forensic_report ? data.forensic_report.primary_directions : [];
    if (!dirs.length) {
        card.innerHTML = `<h3>PRIMARY DIRECTIONS</h3><p class="placeholder-text">None found in range.</p>`;
        return;
    }
    card.innerHTML = `<h3>PRIMARY DIRECTIONS</h3>` + dirs.map(d => `<div>${d.promittor} ${d.aspect} ${d.significator} (${d.years.toFixed(1)} yr)</div>`).join('');
}

export function renderLots(data) {
    const lotsGrid = document.getElementById('lotsGrid');
    if (!lotsGrid || !data.forensic_report || !data.forensic_report.lots) return;
    const entries = Object.entries(data.forensic_report.lots).filter(([, val]) => typeof val === 'number');
    lotsGrid.innerHTML = entries.map(([name, lon]) => `
        <div class="lot-card">
            <div class="lot-name">${name}</div>
            <div class="lot-value">${formatLongitude(lon)}</div>
        </div>
    `).join('');
}

export function renderCelestialWitnesses(data) {
    const starList = document.getElementById('fixedStarList');
    if (starList && data.forensic_report && data.forensic_report.stars) {
        starList.innerHTML = data.forensic_report.stars.map(s => `<div>${s.star} ${s.contact_type} ${s.planet}</div>`).join('');
    }
}

export function renderHoraryPhysics(data) {
    const horarySection = document.getElementById('horaryPhysicsSection');
    const horaryList = document.getElementById('horaryPhysicsList');
    if (data.forensic_report && data.forensic_report.horary_physics && horarySection) {
        horarySection.classList.remove('hidden');
        const hp = data.forensic_report.horary_physics;
        horaryList.innerHTML = `<div class="horary-summary">Significators: ${hp.significators}</div>`;
    }
}

export function renderForensicGrid(data) {
    const forensicGrid = document.getElementById('forensicGrid');
    if (!forensicGrid || !data.forensic_report) return;
    forensicGrid.innerHTML = '';
    data.forensic_report.planets.forEach(p => {
        const card = document.createElement('div');
        card.className = 'planet-card';
        card.innerHTML = `
            <div class="card-header"><h3>${p.planet}</h3></div>
            <div class="card-body">
                <p>Status: ${p.power_label}</p>
                <div class="delineation-snippet">${p.delineation_text}</div>
            </div>
            <div class="card-footer">
                <button class="view-details" onclick='window.showDetails(${JSON.stringify(p).replace(/'/g, "&apos;")})'>VIEW</button>
            </div>
        `;
        forensicGrid.appendChild(card);
    });
}

export function renderTechnicalData(data) {
    const info = document.getElementById('metaInfo');
    if (info) {
        info.innerHTML = `<p>JD: ${data.meta.julian_day.toFixed(2)}</p><p>Lat/Lon: ${data.meta.lat}/${data.meta.lon}</p>`;
    }
    // House Systems Compare
    const container = document.getElementById('houseSystemsCompare');
    if (container && data.houses_by_system) {
        container.innerHTML = Object.entries(data.houses_by_system).map(([sys, houses]) => `<div>${sys}</div>`).join('');
    }
}

export function renderPrediction(data) {
    const profDiv = document.getElementById('profectionInfo');
    if (!profDiv || !data.forensic_report || !data.forensic_report.prediction) return;
    const pred = data.forensic_report.prediction;
    profDiv.innerHTML = `<div class="prediction-item">Annual: ${pred.annual_profection.sign}</div>`;

    // ZR
    const zrDiv = document.getElementById('zrInfo');
    if (zrDiv && data.forensic_report.zodiacal_releasing) {
        // Simplified rendering
        zrDiv.innerHTML = 'ZR Data loaded (see console)';
    }
}

export function renderAdvancedPrediction(data) {
    // Solar Return etc
    const srDiv = document.getElementById('solarReturnInfo');
    if (srDiv && data.advanced_prediction && data.advanced_prediction.solar_return_info) {
        srDiv.innerHTML = `SR Date: ${data.advanced_prediction.solar_return_info.return_date}`;
    }
}

export function renderForecast(data) {
    const grid = document.getElementById('forecastGrid');
    if (grid && data.forensic_forecast) {
        grid.innerHTML = data.forensic_forecast.map(d => `<div class="forecast-card">${d.display_date}: ${d.summary}</div>`).join('');
    }
}

export function initMedicalCheck(data) {
    const selector = document.getElementById('bodyPartSelect');
    if (selector) {
        selector.onchange = async () => {
            // Logic to call API
            // Simplified for this pass
        };
    }
}

export function renderOracle(data) {
    const div = document.getElementById('oracleContent');
    // Prioritize the new hardened report_markdown
    const content = data.report_markdown || data.plain_reading || (data.forensic_report ? data.forensic_report.plain_reading : null);
    if (div && content) {
        div.innerHTML = `<div class="oracle-plain-body">${formatPlainReading(content)}</div>`;
    }
}

export function renderFateTimeline(data, lot) {
    const list = document.getElementById('fateTimelineList');
    if (list) list.innerHTML = `Timeline for ${lot}`;
}

export function renderRuleLedger(data) {
    const ledger = document.getElementById('ruleLedgerList');
    if (ledger && data.forensic_report && data.forensic_report.rule_ledger) {
        ledger.innerHTML = data.forensic_report.rule_ledger.length + ' rules found.';
    }
}
