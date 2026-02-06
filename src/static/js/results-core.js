import { SIGNS } from './config.js';
import { escapeHtml, safeHTML, formatLongitude, formatPlainReading, hashString } from './utils.js';
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
    if (data.forensic_report) {
        const summary = data.forensic_report.summary;
        const events = (summary.universal_events || []).map(e => `[${escapeHtml(e.type)} in ${escapeHtml(e.sign)}]`).join(' ');
        const dominant = summary.dominant_elements && summary.dominant_elements.length ? escapeHtml(summary.dominant_elements[0][0]) : 'Unknown';
        const lunarPhase = escapeHtml(summary.lunar_phase);
        const jonesPattern = escapeHtml(summary.jones_pattern);

        mundaneDiv.innerHTML = `
            <div style="display: flex; gap: 2rem; flex-wrap: wrap;">
                <div><strong>LUNAR PHASE:</strong> ${lunarPhase}</div>
                <div><strong>JONES PATTERN:</strong> ${jonesPattern}</div>
                <div><strong>DOMINANT:</strong> ${dominant}</div>
                ${events ? `<div><strong>ECLIPSE:</strong> ${events}</div>` : ''}
            </div>
        `;
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
            const mansionName = escapeHtml(m.name);
            const mansionId = escapeHtml(m.mansion_id);
            const intentsGood = (m.intents_good || []).slice(0, 3).map(i => escapeHtml(i)).join(', ');
            mansionHTML = `
                <div style="margin-top: 0.5rem; padding-top: 0.5rem; border-top: 1px solid rgba(255,255,255,0.1);">
                    <div style="color: var(--gold); font-weight: bold; font-family: 'Space Mono', monospace;">MANSION ${mansionId}: ${mansionName.toUpperCase()}</div>
                    <div style="font-size: 0.8em; margin-top: 0.3rem;">
                         <span style="color: var(--success);">FOR:</span> ${intentsGood}
                    </div>
                </div>
             `;
        }
        const lunarPhase = escapeHtml(summary.lunar_phase);
        lunarCard.innerHTML = `
            <h4>LUNAR PHASE</h4>
            <div class="summary-list">
                <div><strong>YOU ARE IN:</strong> ${lunarPhase}</div>
                ${mansionHTML}
            </div>
        `;
    }

    if (temperamentCard && summary.temperament) {
        const temperament = escapeHtml(summary.temperament.primary_temperament);
        temperamentCard.innerHTML = `<h4>TEMPERAMENT</h4><div style="color:var(--gold)">YOU ARE: ${temperament}</div>`;
    }
}

export function renderSoulGuardian(data) {
    const card = document.getElementById('soulGuardianCard');
    const teamCard = document.getElementById('soulGuardianTeam');
    if (!card || !data.forensic_report || !data.forensic_report.soul_guardian) return;
    const sg = data.forensic_report.soul_guardian;
    const almuten = escapeHtml(sg.almuten);
    const jobDesc = escapeHtml(sg.job_description);
    card.innerHTML = `
       <h3>PRIMARY RULER (ALMUTEN FIGURIS)</h3>
       <div class="guardian-title">YOU ARE RULED BY: ${almuten}</div>
       <div class="guardian-job">${jobDesc}</div>
    `;

    // Team Logic
    const summary = data.forensic_report.summary || {};
    const constructive = (summary.constructive_team || []).map(t => escapeHtml(t));
    const destructive = (summary.destructive_team || []).map(t => escapeHtml(t));
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
        const receptionStr = receptions.map(r => `${escapeHtml(r.planet_a)}-${escapeHtml(r.planet_b)}`).join(', ');
        card.insertAdjacentHTML('beforeend', `<div class="tool-result-detail" style="margin-top: 1rem;">MUTUAL RECEPTION: ${receptionStr}</div>`);
    }
}

export function renderVitality(data) {
    const card = document.getElementById('vitalityCard');
    if (!card || !data.forensic_report || !data.forensic_report.vitality) return;
    const v = data.forensic_report.vitality;
    const hyleg = escapeHtml(v.hyleg);
    const alcocoden = escapeHtml(v.alcocoden);
    const years = typeof v.total_years === 'number' ? v.total_years.toFixed(1) : '0';
    card.innerHTML = `
        <h3>VITALITY</h3>
        <div>Hyleg: ${hyleg} | Alcocoden: ${alcocoden}</div>
        <div>Years: ${years}</div>
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
    const dirsHtml = dirs.map(d => {
        const promittor = escapeHtml(d.promittor);
        const aspect = escapeHtml(d.aspect);
        const significator = escapeHtml(d.significator);
        const years = typeof d.years === 'number' ? d.years.toFixed(1) : '0';
        return `<div>${promittor} ${aspect} ${significator} (${years} yr)</div>`;
    }).join('');
    card.innerHTML = `<h3>PRIMARY DIRECTIONS</h3>` + dirsHtml;
}

export function renderLots(data) {
    const lotsGrid = document.getElementById('lotsGrid');
    if (!lotsGrid || !data.forensic_report || !data.forensic_report.lots) return;
    const entries = Object.entries(data.forensic_report.lots).filter(([, val]) => typeof val === 'number');
    lotsGrid.innerHTML = entries.map(([name, lon]) => {
        const safeName = escapeHtml(name);
        const safeLon = formatLongitude(lon); // formatLongitude returns safe output
        return `
        <div class="lot-card">
            <div class="lot-name">${safeName}</div>
            <div class="lot-value">${safeLon}</div>
        </div>
    `;
    }).join('');
}

export function renderCelestialWitnesses(data) {
    const starList = document.getElementById('fixedStarList');
    if (starList && data.forensic_report && data.forensic_report.stars) {
        starList.innerHTML = data.forensic_report.stars.map(s => {
            const star = escapeHtml(s.star);
            const contactType = escapeHtml(s.contact_type);
            const planet = escapeHtml(s.planet);
            return `<div>${star} ${contactType} ${planet}</div>`;
        }).join('');
    }
}

export function renderHoraryPhysics(data) {
    const horarySection = document.getElementById('horaryPhysicsSection');
    const horaryList = document.getElementById('horaryPhysicsList');
    if (data.forensic_report && data.forensic_report.horary_physics && horarySection) {
        horarySection.classList.remove('hidden');
        const hp = data.forensic_report.horary_physics;
        const significators = escapeHtml(hp.significators);
        horaryList.innerHTML = `<div class="horary-summary">Significators: ${significators}</div>`;
    }
}

export function renderForensicGrid(data) {
    const forensicGrid = document.getElementById('forensicGrid');
    if (!forensicGrid || !data.forensic_report) return;
    forensicGrid.innerHTML = '';
    data.forensic_report.planets.forEach(p => {
        const card = document.createElement('div');
        card.className = 'planet-card';
        const planetName = escapeHtml(p.planet);
        const powerLabel = escapeHtml(p.power_label);
        const delineation = escapeHtml(p.delineation_text);
        // Serialize data safely for onclick - use data attribute instead
        card.dataset.planetData = JSON.stringify(p);
        card.innerHTML = `
            <div class="card-header"><h3>${planetName}</h3></div>
            <div class="card-body">
                <p>Status: ${powerLabel}</p>
                <div class="delineation-snippet">${delineation}</div>
            </div>
            <div class="card-footer">
                <button class="view-details">VIEW</button>
            </div>
        `;
        // Add click handler safely
        card.querySelector('.view-details').addEventListener('click', () => {
            window.showDetails(p);
        });
        forensicGrid.appendChild(card);
    });
}

export function renderTechnicalData(data) {
    const info = document.getElementById('metaInfo');
    if (info && data.meta) {
        const jd = typeof data.meta.julian_day === 'number' ? data.meta.julian_day.toFixed(2) : '0';
        const lat = escapeHtml(data.meta.lat);
        const lon = escapeHtml(data.meta.lon);
        info.innerHTML = `<p>JD: ${jd}</p><p>Lat/Lon: ${lat}/${lon}</p>`;
    }
    // House Systems Compare
    const container = document.getElementById('houseSystemsCompare');
    if (container && data.houses_by_system) {
        container.innerHTML = Object.entries(data.houses_by_system).map(([sys, houses]) => {
            return `<div>${escapeHtml(sys)}</div>`;
        }).join('');
    }
}

export function renderPrediction(data) {
    const profDiv = document.getElementById('profectionInfo');
    if (!profDiv || !data.forensic_report || !data.forensic_report.prediction) return;
    const pred = data.forensic_report.prediction;
    const annualSign = escapeHtml(pred.annual_profection.sign);
    profDiv.innerHTML = `<div class="prediction-item">Annual: ${annualSign}</div>`;

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
        const returnDate = escapeHtml(data.advanced_prediction.solar_return_info.return_date);
        srDiv.innerHTML = `SR Date: ${returnDate}`;
    }
}

export function renderForecast(data) {
    const grid = document.getElementById('forecastGrid');
    if (grid && data.forensic_forecast) {
        grid.innerHTML = data.forensic_forecast.map(d => {
            const displayDate = escapeHtml(d.display_date);
            const summary = escapeHtml(d.summary);
            return `<div class="forecast-card">${displayDate}: ${summary}</div>`;
        }).join('');
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
