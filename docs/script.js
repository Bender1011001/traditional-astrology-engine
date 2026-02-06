
const SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
];

const API_BASE = window.CAEL_API_BASE || "";
const IS_GH_PAGES = window.location.hostname.endsWith("github.io");
const backendNotice = document.getElementById("backendNotice");
if (backendNotice && IS_GH_PAGES && !API_BASE) {
    backendNotice.classList.remove("hidden");
}

function apiUrl(path) {
    return `${API_BASE}${path}`;
}

function formatLongitude(lon) {
    let signIdx = Math.floor(lon / 30) % 12;
    let degree = lon % 30;
    let d = Math.floor(degree);
    let m = Math.floor((degree - d) * 60);
    return `${d}° ${SIGNS[signIdx]} ${m}'`;
}

// Set default analysis date to today
document.getElementById('analysisDate').value = new Date().toISOString().split('T')[0];

function setLocalDateTime(dateId, timeId) {
    const now = new Date();
    const pad = (v) => String(v).padStart(2, '0');
    const dateVal = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`;
    const timeVal = `${pad(now.getHours())}:${pad(now.getMinutes())}`;
    const dateEl = document.getElementById(dateId);
    const timeEl = document.getElementById(timeId);
    if (dateEl) dateEl.value = dateVal;
    if (timeEl) timeEl.value = timeVal;
}

function setUtcDateTime(dateId, timeId) {
    const iso = new Date().toISOString();
    const dateVal = iso.slice(0, 10);
    const timeVal = iso.slice(11, 16);
    const dateEl = document.getElementById(dateId);
    const timeEl = document.getElementById(timeId);
    if (dateEl) dateEl.value = dateVal;
    if (timeEl) timeEl.value = timeVal;
}

setLocalDateTime('horaryDate', 'horaryTime');
setUtcDateTime('worldDate', 'worldTime');
setUtcDateTime('kairosStartDate');

const timeInput = document.getElementById("time");
const timeUnknownToggle = document.getElementById("timeUnknown");
const timeWarning = document.getElementById("timeWarning");

function setTimeUnknownState(isUnknown) {
    if (timeWarning) timeWarning.classList.toggle("hidden", !isUnknown);
    if (timeInput) {
        timeInput.required = !isUnknown;
        if (isUnknown && !timeInput.value) {
            timeInput.value = "12:00";
        }
    }
}

if (timeUnknownToggle) {
    timeUnknownToggle.addEventListener("change", (e) => {
        setTimeUnknownState(e.target.checked);
    });
    setTimeUnknownState(timeUnknownToggle.checked);
}

// Tab Logic
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        btn.classList.add('active');
        document.getElementById(btn.dataset.tab + 'Tab').classList.add('active');
    });
});

document.getElementById('chartForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const btn = document.getElementById('calculateBtn');
    const originalText = btn.querySelector('.btn-text').textContent;
    btn.querySelector('.btn-text').textContent = "CONSULTING THE STARS...";
    btn.disabled = true;

    const isTimeUnknown = timeUnknownToggle ? timeUnknownToggle.checked : false;
    const timeValue = timeInput ? timeInput.value : "";
    const formData = {
        date: document.getElementById('date').value,
        time: isTimeUnknown && !timeValue ? "12:00" : timeValue,
        city: document.getElementById('city').value,
        state: document.getElementById('state').value,
        age: document.getElementById('currentAge').value ? parseInt(document.getElementById('currentAge').value) : null,
        analysis_date: document.getElementById('analysisDate').value || null
    };

    try {
        const response = await fetch(apiUrl('/api/calculate'), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'The heavens remain silent.');
        }

        const result = await response.json();
        renderResults(result);

    } catch (error) {
        alert(error.message);
    } finally {
        btn.querySelector('.btn-text').textContent = originalText;
        btn.disabled = false;
    }
});

// City Autocomplete
const cityInput = document.getElementById('city');
const suggestionsBox = document.getElementById('citySuggestions');
let debounceTimer;

cityInput.addEventListener('input', () => {
    clearTimeout(debounceTimer);
    const query = cityInput.value;
    if (query.length < 3) {
        suggestionsBox.style.display = 'none';
        return;
    }

    debounceTimer = setTimeout(async () => {
        try {
            const resp = await fetch(`https://photon.komoot.io/api/?q=${encodeURIComponent(query)}&limit=5&type=city`);
            if (!resp.ok) return;
            const data = await resp.json();
            renderSuggestions(data.features || []);
        } catch (err) {
            console.error("Autocomplete error", err);
        }
    }, 300);
});

function renderSuggestions(features) {
    suggestionsBox.innerHTML = '';
    if (!features || features.length === 0) {
        suggestionsBox.style.display = 'none';
        return;
    }

    features.forEach(f => {
        const item = document.createElement('div');
        item.className = 'suggestion-item';
        const city = f.properties.name;
        const state = f.properties.state || f.properties.country;
        item.textContent = `${city}, ${state}`;
        item.onclick = () => {
            cityInput.value = city;
            document.getElementById('state').value = state;
            suggestionsBox.style.display = 'none';
        };
        suggestionsBox.appendChild(item);
    });
    suggestionsBox.style.display = 'block';
}

document.addEventListener('click', (e) => {
    if (e.target !== cityInput) suggestionsBox.style.display = 'none';
});

function renderResults(data) {
    const resultsSection = document.getElementById('results');
    resultsSection.classList.remove('results-hidden');

    // 0. Chart Wheel
    renderChartWheel(data);

    // 1. Mundane Context
    const mundaneDiv = document.getElementById('mundaneContext');
    let mundaneHTML = "";
    if (data.forensic_report) {
        let events = data.forensic_report.summary.universal_events.map(e => `[${e.type} in ${e.sign}]`).join(' ');
        let summary = data.forensic_report.summary;
        let dominant = summary.dominant_elements && summary.dominant_elements.length ? summary.dominant_elements[0][0] : 'Unknown';
        mundaneHTML = `
            <div style="display: flex; gap: 2rem; flex-wrap: wrap;">
                <div><strong>LUNAR PHASE:</strong> ${summary.lunar_phase}</div>
                <div><strong>JONES PATTERN:</strong> ${summary.jones_pattern}</div>
                <div><strong>DOMINANT:</strong> ${dominant}</div>
                ${events ? `<div><strong>UNIVERSAL:</strong> ${events}</div>` : ''}
            </div>
        `;
        mundaneDiv.innerHTML = mundaneHTML;
        mundaneDiv.style.display = 'block';
    } else {
        mundaneDiv.style.display = 'none';
    }

    renderSummaryExtras(data);

    // 1a. Soul Guardian
    renderSoulGuardian(data);

    // 1c. Hermetic Lots / Celestial Curia
    renderLots(data);
    renderCelestialWitnesses(data);

    // 1b. Horary Physics / Interactions
    const horarySection = document.getElementById('horaryPhysicsSection');
    const horaryList = document.getElementById('horaryPhysicsList');
    if (data.forensic_report && data.forensic_report.horary_physics) {
        const hp = data.forensic_report.horary_physics;
        horarySection.classList.remove('hidden');
        horaryList.innerHTML = `
            <div class="horary-summary">
                <strong>Significators:</strong> ${hp.significators}
            </div>
            ${hp.interactions.map(i => `
                <div class="horary-item">
                    <span class="horary-condition">${i.condition}</span>
                    <span class="horary-details">${i.details || i.aspect || ''}</span>
                    <span class="horary-status ${i.status.toLowerCase()}">${i.status}</span>
                </div>
            `).join('')}
        `;
        if (hp.interactions.length === 0) {
            horaryList.innerHTML += '<p class="text-muted">No shadow interactions detected between primary significators.</p>';
        }
    } else {
        horarySection.classList.add('hidden');
    }


    // 2. Forensic Grid
    const forensicGrid = document.getElementById('forensicGrid');
    forensicGrid.innerHTML = '';

    if (data.forensic_report) {
        data.forensic_report.planets.forEach(p => {
            const card = document.createElement('div');
            card.className = 'planet-card';

            const badgeClass = p.power_label.toLowerCase().includes('sovereign') ? 'badge-sovereign' :
                p.power_label.toLowerCase().includes('corrupt') ? 'badge-corrupt' : 'badge-common';

            let impactsHTML = p.impacts.map(i => `<div class="impact-alert"><strong>${i.cause}:</strong> ${i.effect}</div>`).join('');

            card.innerHTML = `
                <div class="card-header">
                    <h3>${p.planet}</h3>
                    <span class="badge ${badgeClass}">${p.power_label}</span>
                </div>
                <div class="card-body">
                    <p><strong>Status:</strong> ${p.sect_status}</p>
                    <p><strong>Position:</strong> ${formatLongitude(p.longitude)}</p>
                    <p class="planet-meta"><strong>Solar:</strong> ${p.solar_status || 'UNKNOWN'} | <strong>Medical:</strong> ${p.medical_region || 'Unknown'}</p>
                    ${p.medical_pathology ? `<p class="planet-meta">${p.medical_pathology}</p>` : ''}
                    ${impactsHTML}
                    <div class="delineation-snippet">
                        "${p.delineation_text}"
                    </div>
                </div>
                <div class="card-footer">
                    <button class="view-details" onclick='showDetails(${JSON.stringify(p).replace(/'/g, "&apos;")})'>EXAMINE CODEX</button>
                </div>
            `;
            forensicGrid.appendChild(card);
        });
    }

    // 3. Technical Data
    const analysisJd = data.meta.analysis_jd || data.meta.julian_day;
    document.getElementById('metaInfo').innerHTML = `
        <p><strong>JULIAN DAY:</strong> ${data.meta.julian_day.toFixed(2)}</p>
        <p><strong>ANALYSIS JD:</strong> ${analysisJd.toFixed(2)}</p>
        <p><strong>UTC:</strong> ${data.meta.utc_time || 'Unknown'}</p>
        <p><strong>LATITUDE:</strong> ${data.meta.lat.toFixed(4)} | <strong>LONGITUDE:</strong> ${data.meta.lon.toFixed(4)}</p>
        <p><strong>TIMEZONE:</strong> ${data.meta.timezone}</p>
    `;

    if (data.angles) {
        const nn = data.planets && data.planets.North_Node ? formatLongitude(data.planets.North_Node.longitude) : 'Unknown';
        const sn = data.planets && data.planets.South_Node ? formatLongitude(data.planets.South_Node.longitude) : 'Unknown';
        document.getElementById('anglesInfo').innerHTML = `
            <p><strong>ASCENDANT:</strong> ${formatLongitude(data.angles.Ascendant)}</p>
            <p><strong>MIDHEAVEN:</strong> ${formatLongitude(data.angles.MC)}</p>
            <p><strong>NORTH NODE:</strong> ${nn}</p>
            <p><strong>SOUTH NODE:</strong> ${sn}</p>
        `;
    } else {
        document.getElementById('anglesInfo').innerHTML = '<p class="placeholder-text">Angles unavailable.</p>';
    }

    // Planets
    let planetHTML = '';
    for (const [name, info] of Object.entries(data.planets)) {
        planetHTML += `
            <div class="item-row">
                <span class="chart-item-name">${name.toUpperCase()}</span>
                <span class="chart-item-val">${formatLongitude(info.longitude)} ${info.is_retrograde ? '(R)' : ''}</span>
            </div>
        `;
    }
    document.getElementById('planetList').innerHTML = planetHTML;

    // Houses
    let houseHTML = '';
    const sortedHouses = Object.entries(data.houses).sort((a, b) => parseInt(a[0]) - parseInt(b[0]));
    for (const [num, lon] of sortedHouses) {
        houseHTML += `
            <div class="item-row">
                <span class="chart-item-name">HOUSE ${num}</span>
                <span class="chart-item-val">${formatLongitude(lon)}</span>
            </div>
        `;
    }
    document.getElementById('houseList').innerHTML = houseHTML;

    // 4. Prediction
    renderPrediction(data);
    renderAdvancedPrediction(data);

    // 5. Forecast
    renderForecast(data);

    // 6. Medical Check
    initMedicalCheck(data);

    // 7. Daily Oracle
    renderOracle(data);

    // 8. Fate Timeline
    currentResult = data;
    renderFateTimeline(data, currentLot);

    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function renderSummaryExtras(data) {
    const lunarCard = document.getElementById('lunarProfileCard');
    const elementCard = document.getElementById('elementBalanceCard');
    const eventsCard = document.getElementById('universalEventsCard');
    const causeCard = document.getElementById('universalCausationCard');

    if (!data.forensic_report || !data.forensic_report.summary) {
        if (lunarCard) lunarCard.innerHTML = `<h4>LUNAR PROFILE</h4><p class="placeholder-text">No summary available.</p>`;
        if (elementCard) elementCard.innerHTML = `<h4>ELEMENTAL BALANCE</h4><p class="placeholder-text">No summary available.</p>`;
        if (eventsCard) eventsCard.innerHTML = `<h4>UNIVERSAL EVENTS</h4><p class="placeholder-text">No summary available.</p>`;
        if (causeCard) causeCard.innerHTML = `<h4>UNIVERSAL CAUSATION</h4><p class="placeholder-text">No summary available.</p>`;
        return;
    }

    const summary = data.forensic_report.summary;

    if (lunarCard) {
        lunarCard.innerHTML = `
            <h4>LUNAR PROFILE</h4>
            <div class="summary-list">
                <div><strong>Phase:</strong> ${summary.lunar_phase}</div>
                <div>${summary.lunar_phase_profile || 'Profile unavailable.'}</div>
            </div>
        `;
    }

    if (elementCard) {
        const elements = summary.dominant_elements || [];
        elementCard.innerHTML = `
            <h4>ELEMENTAL BALANCE</h4>
            <div class="summary-list">
                ${elements.length ? elements.map(([el, count]) => `<div><strong>${el}:</strong> ${count}</div>`).join('') : '<div>No elemental data.</div>'}
            </div>
        `;
    }

    if (eventsCard) {
        const events = summary.universal_events || [];
        eventsCard.innerHTML = `
            <h4>UNIVERSAL EVENTS</h4>
            <div class="summary-list">
                ${events.length ? events.map(e => {
                    const degree = typeof e.degree === 'number' ? `${e.degree.toFixed(2)}°` : '';
                    const duration = typeof e.duration_hours === 'number' ? `${e.duration_hours.toFixed(1)}h` : '';
                    return `<div><strong>${e.type}</strong> ${degree} ${e.sign} ${duration ? `(${duration})` : ''}</div>`;
                }).join('') : '<div>No eclipse activity detected.</div>'}
            </div>
        `;
    }

    if (causeCard) {
        const causes = summary.universal_causation_audit || [];
        causeCard.innerHTML = `
            <h4>UNIVERSAL CAUSATION</h4>
            <div class="summary-list">
                ${causes.length ? causes.map(c => `
                    <div class="summary-item">
                        <div><strong>${c.cause}</strong></div>
                        <div>${c.status}</div>
                        ${c.rule ? `<div>${c.rule}</div>` : ''}
                    </div>
                `).join('') : '<div>No active suspensions in the audit window.</div>'}
            </div>
        `;
    }
}

function renderLots(data) {
    const lotsGrid = document.getElementById('lotsGrid');
    if (!lotsGrid) return;

    if (!data.forensic_report || !data.forensic_report.lots) {
        lotsGrid.innerHTML = '<p class="placeholder-text">Lots will appear after calculation.</p>';
        return;
    }

    const lots = data.forensic_report.lots;
    const entries = Object.entries(lots).filter(([, val]) => typeof val === 'number');
    if (!entries.length) {
        lotsGrid.innerHTML = '<p class="placeholder-text">No lot data available.</p>';
        return;
    }

    lotsGrid.innerHTML = entries.map(([name, lon]) => {
        const signIdx = Math.floor(lon / 30) % 12;
        const sign = SIGNS[signIdx];
        return `
            <div class="lot-card">
                <div class="lot-name">${name}</div>
                <div class="lot-value">${formatLongitude(lon)}</div>
                <div class="lot-sign">${sign.toUpperCase()}</div>
            </div>
        `;
    }).join('');
}

function renderCelestialWitnesses(data) {
    const starList = document.getElementById('fixedStarList');
    const nodeList = document.getElementById('nodeList');

    if (starList) {
        const stars = data.forensic_report && data.forensic_report.stars ? data.forensic_report.stars : [];
        if (!stars.length) {
            starList.innerHTML = '<p class="placeholder-text">No stellar contacts logged.</p>';
        } else {
            starList.innerHTML = stars.map(s => {
                const starName = s.star_name || s.star || 'Unknown Star';
                const planetName = s.planet_name || s.planet || 'Unknown';
                const contact = s.contact_type || 'Contact';
                const angle = s.angle ? ` (${s.angle})` : '';
                const message = s.message ? `<div>${s.message}</div>` : '';
                return `
                    <div class="witness-item">
                        <strong>${starName}</strong> ${contact} ${planetName}${angle}
                        ${message}
                    </div>
                `;
            }).join('');
        }
    }

    if (nodeList) {
        const nodes = data.forensic_report && data.forensic_report.nodes ? data.forensic_report.nodes : [];
        if (!nodes.length) {
            nodeList.innerHTML = '<p class="placeholder-text">No nodal activations detected.</p>';
        } else {
            nodeList.innerHTML = nodes.map(n => `
                <div class="witness-item">
                    <strong>${n.planet_name}</strong> ${n.node_type} - ${n.metabolic_phase}
                    <div>${n.description}</div>
                </div>
            `).join('');
        }
    }
}

function renderAdvancedPrediction(data) {
    const firdariaDiv = document.getElementById('firdariaInfo');
    const munthaDiv = document.getElementById('munthaInfo');
    const solarReturnDiv = document.getElementById('solarReturnInfo');
    const solarArcDiv = document.getElementById('solarArcInfo');
    const lunarPhaseDiv = document.getElementById('lunarPhaseInfo');

    const adv = data.advanced_prediction;
    if (!adv) {
        const msg = data.advanced_prediction_error || 'Advanced prediction unavailable.';
        const placeholder = `<p class="placeholder-text">${msg}</p>`;
        if (firdariaDiv) firdariaDiv.innerHTML = placeholder;
        if (munthaDiv) munthaDiv.innerHTML = '';
        if (solarReturnDiv) solarReturnDiv.innerHTML = placeholder;
        if (solarArcDiv) solarArcDiv.innerHTML = placeholder;
        if (lunarPhaseDiv) lunarPhaseDiv.innerHTML = placeholder;
        return;
    }

    if (firdariaDiv) {
        const f = adv.firdaria || {};
        if (f.error) {
            firdariaDiv.innerHTML = `<p class="placeholder-text">${f.error}</p>`;
        } else {
            firdariaDiv.innerHTML = `
                <div class="tool-result-detail"><strong>Major:</strong> ${f['Major Period']}</div>
                <div class="tool-result-detail"><strong>Sub:</strong> ${f['Sub Period']}</div>
                <div class="tool-result-detail"><strong>Major Range:</strong> ${f['Major Start']} to ${f['Major End']}</div>
                <div class="tool-result-detail"><strong>Sub Range:</strong> ${f['Sub Start']} to ${f['Sub End']}</div>
                <div class="tool-result-detail"><strong>Current Age:</strong> ${f['Current Age']}</div>
            `;
        }
    }

    if (munthaDiv) {
        const m = adv.muntha || {};
        munthaDiv.innerHTML = m.sign ? `
            <div class="tool-result-detail"><strong>Muntha:</strong> ${m.sign} (Age ${m.age})</div>
        ` : '<p class="placeholder-text">Muntha unavailable.</p>';
    }

    if (solarReturnDiv) {
        const sr = adv.solar_return_info || {};
        const natalSun = typeof sr.natal_sun_longitude === 'number' ? formatLongitude(sr.natal_sun_longitude) : 'Unknown';
        solarReturnDiv.innerHTML = sr.return_date ? `
            <div class="tool-result-detail"><strong>Return Date:</strong> ${new Date(sr.return_date).toLocaleString()}</div>
            <div class="tool-result-detail"><strong>Return JD:</strong> ${sr.return_jd.toFixed ? sr.return_jd.toFixed(4) : sr.return_jd}</div>
            <div class="tool-result-detail"><strong>Natal Sun:</strong> ${natalSun}</div>
        ` : '<p class="placeholder-text">Solar return unavailable.</p>';
    }

    if (solarArcDiv) {
        const arcs = adv.solar_arcs || [];
        solarArcDiv.innerHTML = arcs.length ? `
            ${arcs.map(a => `<div class="tool-result-detail"><strong>${a.planet}:</strong> ${formatLongitude(a.longitude)}</div>`).join('')}
        ` : '<p class="placeholder-text">Solar arcs unavailable.</p>';
    }

    if (lunarPhaseDiv) {
        const lp = adv.lunar_phase || {};
        lunarPhaseDiv.innerHTML = lp.name ? `
            <div class="tool-result-detail"><strong>${lp.name}</strong> (${lp.type || 'Phase'})</div>
            <div class="tool-result-detail">${lp.profile || ''}</div>
        ` : '<p class="placeholder-text">Lunar phase profile unavailable.</p>';
    }
}

let currentResult = null;
let currentLot = 'Spirit';

// Lot Selector Logic
document.querySelectorAll('.lot-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.lot-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentLot = btn.dataset.lot;
        if (currentResult) renderFateTimeline(currentResult, currentLot);
    });
});

function renderFateTimeline(data, lot) {
    const list = document.getElementById('fateTimelineList');
    const alert = document.getElementById('fateTimelineAlert');
    if (!data.forensic_report) {
        if (alert) {
            alert.innerHTML = `<p class="placeholder-text">Cast a nativity to calculate your pivots.</p>`;
        }
        return;
    }

    const timelineData = lot === 'Spirit' ? data.forensic_report.fate_timeline_spirit : data.forensic_report.fate_timeline_fortune;

    if (!timelineData) {
        list.innerHTML = '<p class="placeholder-text">Fate Timeline unavailable for this Lot.</p>';
        if (alert) {
            alert.innerHTML = `<p class="placeholder-text">No pivots detected for this Lot.</p>`;
        }
        return;
    }

    if (alert) {
        const pivots = [];
        timelineData.forEach(chapter => {
            chapter.paragraphs.forEach(p => {
                if (p.is_pivot) {
                    pivots.push({
                        status: p.status,
                        sign: p.sign,
                        date: p.start_date
                    });
                }
            });
        });

        pivots.sort((a, b) => new Date(`${a.date}T00:00:00`) - new Date(`${b.date}T00:00:00`));
        const today = new Date();
        const nextPivot = pivots.find(p => new Date(`${p.date}T00:00:00`) >= today);
        const pivot = nextPivot || pivots[pivots.length - 1];

        if (pivot) {
            const label = pivot.status === 'Loosing of the Bond' ? 'LOOSING OF THE BOND' : 'FORESHADOWING';
            const tense = nextPivot ? 'On' : 'Most recent';
            alert.innerHTML = `
                <strong>${label}</strong>
                <div>${tense} ${pivot.date}: ${pivot.sign} pivot begins. Expect a structural shift.</div>
            `;
        } else {
            alert.innerHTML = `<p class="placeholder-text">No pivots detected for this Lot.</p>`;
        }
    }

    const now = new Date();
    const nowStr = now.toISOString().split('T')[0];

    list.innerHTML = timelineData.map(chapter => `
        <div class="chapter-block">
            <div class="chapter-header">
                <div class="chapter-title">
                    CHAPTER IN ${chapter.sign.toUpperCase()}
                    <span class="chapter-years">${chapter.duration_years} YEARS</span>
                </div>
                <div class="p-dates">${chapter.start_date} to ${chapter.end_date}</div>
            </div>
            <div class="paragraphs-grid">
                ${chapter.paragraphs.map(p => {
        const isActive = nowStr >= p.start_date && nowStr < p.end_date;
        const isLB = p.status === 'Loosing of the Bond';
        const isFore = p.status === 'Foreshadowing';

        return `
                        <div class="paragraph-card ${p.is_pivot ? (isLB ? 'pivot-lb' : 'pivot') : ''}">
                            ${isActive ? '<div class="active-p">PRESENT</div>' : ''}
                            <span class="p-sign">${p.sign}</span>
                            <span class="p-dates">${p.start_date} - ${p.end_date}</span>
                            ${p.status !== 'Normal' ? `<div class="p-status ${isLB ? 'lb' : 'foreshadowing'}">${p.status.toUpperCase()}</div>` : ''}
                        </div>
                    `;
    }).join('')}
            </div>
        </div>
    `).join('');
}

function renderOracle(data) {
    const div = document.getElementById('oracleContent');
    if (!data.forensic_report || !data.forensic_report.daily_oracle) {
        div.innerHTML = `<p class="placeholder-text">Oracle requires a full Nativity calculation.</p>`;
        return;
    }

    const o = data.forensic_report.daily_oracle;
    div.innerHTML = `
        <div class="oracle-mood-badge">${o.mood}</div>
        <h3 class="oracle-title">${o.title}</h3>
        ${o.day_lord ? `<div class="oracle-day-lord">DAY LORD: ${o.day_lord}</div>` : ''}
        <p class="oracle-summary">${o.summary}</p>
        <div class="oracle-details">
            ${(o.details || []).map(d => `<div class="oracle-detail-item">${d}</div>`).join('')}
        </div>
        ${o.secret_key ? `<div class="secret-key-alert">THE SECRET KEY IS ACTIVE - HIGH MAGNITUDE EVENTS LIKELY</div>` : ''}
    `;
}

function renderSoulGuardian(data) {
    const card = document.getElementById('soulGuardianCard');
    const teamCard = document.getElementById('soulGuardianTeam');
    if (!card || !teamCard) return;

    if (!data.forensic_report || !data.forensic_report.soul_guardian || !data.forensic_report.soul_guardian.almuten) {
        card.innerHTML = `
            <h3>ALMUTEN FIGURIS</h3>
            <p class="placeholder-text">Cast a nativity to reveal the Soul's Guardian.</p>
        `;
        teamCard.innerHTML = `
            <h3>SECT TEAMS</h3>
            <p class="placeholder-text">Constructive vs. Destructive forces appear here.</p>
        `;
        return;
    }

    const sg = data.forensic_report.soul_guardian;
    const scores = sg.scores || {};
    const sortedScores = Object.entries(scores).sort((a, b) => (b[1].total || 0) - (a[1].total || 0));
    const topScores = sortedScores.slice(0, 5);

    card.innerHTML = `
        <h3>ALMUTEN FIGURIS</h3>
        <div class="guardian-title">${sg.almuten} in the Terms of ${sg.term_ruler}</div>
        <div class="guardian-job">${sg.job_description}</div>
        <div class="guardian-meta">Total Score: ${sg.total_score}</div>
        ${sg.prenatal_syzygy_lon ? `<div class="guardian-meta">Prenatal Syzygy: ${formatLongitude(sg.prenatal_syzygy_lon)}</div>` : ''}
        <div class="guardian-scores">
            ${topScores.map(([name, info]) => `
                <div class="guardian-score-item">
                    <span>${name.toUpperCase()}</span>
                    <span>${info.total}</span>
                </div>
            `).join('')}
        </div>
    `;

    const summary = data.forensic_report.summary || {};
    const constructive = summary.constructive_team || [];
    const destructive = summary.destructive_team || [];

    teamCard.innerHTML = `
        <h3>SECT TEAMS</h3>
        <p class="tool-result-detail">${summary.team_note || ''}</p>
        <div class="tool-result-detail">Constructive Team</div>
        <div class="team-list">
            ${constructive.length ? constructive.map(p => `<span class="team-pill constructive">${p}</span>`).join('') : '<span class="placeholder-text">None</span>'}
        </div>
        <div class="tool-result-detail" style="margin-top: 1rem;">Destructive Team</div>
        <div class="team-list">
            ${destructive.length ? destructive.map(p => `<span class="team-pill destructive">${p}</span>`).join('') : '<span class="placeholder-text">None</span>'}
        </div>
    `;
}

function renderForecast(data) {
    const grid = document.getElementById('forecastGrid');
    if (!data.forensic_forecast) {
        grid.innerHTML = `<p class="placeholder-text">Forecast data unavailable.</p>`;
        return;
    }

    grid.innerHTML = data.forensic_forecast.map(day => `
        <div class="forecast-card ${day.epitasis ? 'epitasis' : ''}">
            <div class="forecast-date">${day.display_date}</div>
            <div class="forecast-lord">
                <div class="lord-icon">${day.chronocrator.charAt(0)}</div>
                <div class="lord-info">
                    <span class="lord-name">${day.chronocrator}</span>
                    <span class="lord-sign">Lord of ${day.profection_sign}</span>
                </div>
            </div>
            <div class="forecast-mood">${day.mood}</div>
            <p class="forecast-summary">${day.summary}</p>
            ${day.medical && day.medical.length > 0 ? `
                <div class="medical-alerts">
                    ${day.medical.map(m => `<div class="medical-alert-item">${m}</div>`).join('')}
                </div>
            ` : ''}
        </div>
    `).join('');
}

function initMedicalCheck(data) {
    const selector = document.getElementById('bodyPartSelect');
    const panel = document.getElementById('surgeryResult');

    const runCheck = async () => {
        const part = selector.value;
        const jd = data.meta.analysis_jd || data.meta.julian_day;

        try {
            const resp = await fetch(apiUrl(`/api/surgery_check?body_part=${part}&jd=${jd}`));
            const res = await resp.json();

            panel.innerHTML = `
                <div class="surgery-status-card ${res.safe ? 'status-safe' : 'status-danger'}">
                    <div class="status-icon">${res.safe ? '✓' : '⚠'}</div>
                    <div class="status-msg">
                        <h4>${res.safe ? 'FAVORABLE' : 'DANGEROUS'}</h4>
                        <p>${res.safe ? 'No major celestial impediments for this operation.' : 'HEAVENLY PROHIBITION DETECTED'}</p>
                    </div>
                </div>
                ${res.reasons.length > 0 ? `
                    <div class="surgery-reasons">
                        ${res.reasons.map(r => `<div class="reason-item">✦ ${r}</div>`).join('')}
                    </div>
                ` : ''}
                <div class="medical-meta">
                    <small>Moon: ${res.moon_sign} | Target: ${res.target_body_part}</small>
                </div>
                <div class="medical-footer">
                    <small>${res.historical_context}</small>
                </div>
            `;
        } catch (err) {
            panel.innerHTML = `<p class="error">Failed to consult the medical codex.</p>`;
        }
    };

    selector.onchange = runCheck;
    runCheck();
}

function renderChartWheel(data) {
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
                <stop offset="100%" stop-color="rgba(197, 160, 89, 0.15)" />
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
    // Simple: draw lines for major aspects
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
            <g class="planet-glyph-group" style="cursor: pointer" onclick='showDetailsByPlanet("${name}", ${JSON.stringify(data)})'>
                <circle cx="${px}" cy="${py}" r="14" fill="var(--bg-card)" stroke="var(--gold)" stroke-width="1.5" filter="url(#glow)" />
                <text x="${px}" y="${py}" fill="var(--gold)" font-size="16" text-anchor="middle" alignment-baseline="middle">${PLANET_GLYPHS[name] || name.charAt(0)}</text>
            </g>
        `;
    });

    // Center Earth
    svg += `<circle cx="${center}" cy="${center}" r="15" fill="var(--bg-deep)" stroke="var(--gold)" stroke-width="1" />`;
    svg += `<text x="${center}" y="${center}" fill="var(--gold)" font-size="8" text-anchor="middle" alignment-baseline="middle">TERRA</text>`;

    svg += `</svg>`;
    container.innerHTML = svg;
}

window.showDetailsByPlanet = (name, data) => {
    const p = data.forensic_report.planets.find(pl => pl.planet === name);
    if (p) showDetails(p);
};

function renderPrediction(data) {
    const profDiv = document.getElementById('profectionInfo');
    const zrDiv = document.getElementById('zrInfo');

    if (!data.forensic_report || !data.forensic_report.prediction) {
        profDiv.innerHTML = '<p class="placeholder-text">Provide Age/Analysis Date in the form to unlock Temporal Audits.</p>';
        zrDiv.innerHTML = '<p class="placeholder-text">Zodiacal Releasing requires full birth data.</p>';
        return;
    }

    const pred = data.forensic_report.prediction;
    profDiv.innerHTML = `
        <div class="prediction-item">
            <p><strong>ANNUAL:</strong> ${pred.annual_profection.sign} (Lord: ${pred.annual_profection.lord_of_year})</p>
            <p><strong>MONTHLY:</strong> ${pred.monthly_profection.continuous}</p>
            <p><strong>MONTHLY (SALT):</strong> ${pred.monthly_profection.saltatory || 'Unavailable'}</p>
            <p><strong>DAILY:</strong> ${pred.daily_profection.sign}</p>
            <p><strong>SECRET KEY:</strong> ${pred.epitasis_days && pred.epitasis_days.length ? `Days ${pred.epitasis_days.join(', ')}` : 'None detected'}</p>
        </div>
    `;

    const zrData = data.forensic_report.zodiacal_releasing;
    if (Array.isArray(zrData)) {
        let zrHTML = '';
        zrData.forEach(p => {
            zrHTML += `
                <div class="zr-period">
                    <div class="zr-period-header">
                        <span>${p.sign}</span>
                        <span style="color:var(--gold)">Level ${p.level}</span>
                    </div>
                    <div class="zr-period-dates">${new Date(p.start).toLocaleDateString()} - ${new Date(p.end).toLocaleDateString()}</div>
                </div>
             `;
        });
        zrDiv.innerHTML = zrHTML;
    } else if (zrData && typeof zrData === 'object') {
        zrDiv.innerHTML = Object.entries(zrData).map(([key, value]) => `
            <div class="zr-period">
                <div class="zr-period-header">
                    <span>${key}</span>
                    <span style="color:var(--gold)">${value}</span>
                </div>
            </div>
        `).join('');
    } else {
        zrDiv.innerHTML = '<p class="placeholder-text">No Zodiacal Releasing data returned.</p>';
    }
}

window.showDetails = (p) => {
    const modal = document.getElementById('modalOverlay');
    const body = document.getElementById('modalBody');

    body.innerHTML = `
        <h2 style="font-family: Cinzel, serif; color: var(--gold); margin-bottom: 2rem;">${p.planet} IN THE TWELVE DOMAINS</h2>
        <div class="modal-detail-section">
            <h4 style="color: var(--gold); letter-spacing: 2px;">JUDGMENT OF DIGNITY</h4>
            <p style="margin: 1rem 0;">The planet holds a score of <strong>${p.dignity_score}</strong> in the celestial hierarchy.</p>
            <ul style="list-style: '✦ '; padding-left: 1.5rem; color: var(--text-muted);">
                ${p.dignity_details.map(d => `<li>${d}</li>`).join('')}
            </ul>
        </div>
        <div class="modal-detail-section">
            <h4 style="color: var(--gold); letter-spacing: 2px;">SOLAR CONDITION & MEDICAL</h4>
            <p style="margin: 0.75rem 0;"><strong>Solar Status:</strong> ${p.solar_status || 'Unknown'}</p>
            <p style="margin: 0.75rem 0;"><strong>Medical Region:</strong> ${p.medical_region || 'Unknown'}</p>
            ${p.medical_pathology ? `<p style="margin: 0.75rem 0;"><strong>Pathology:</strong> ${p.medical_pathology}</p>` : ''}
        </div>
        <hr style="border: 0; border-top: 1px solid var(--glass-border); margin: 2rem 0;">
        <div class="modal-detail-section">
            <h4 style="color: var(--gold); letter-spacing: 2px;">CODEX DELINEATION</h4>
            <p style="font-family: Playfair Display, serif; font-size: 1.1rem; line-height: 1.8; margin-top: 1rem;">
                ${p.delineation_text}
            </p>
        </div>
        <div class="modal-detail-section" style="margin-top: 2rem;">
            <h4 style="color: var(--gold); letter-spacing: 2px;">HOUSE PLACEMENT: ${p.house_number}</h4>
            <p style="font-family: Playfair Display, serif; font-size: 1.1rem; line-height: 1.8; margin-top: 1rem;">
                ${p.house_delineation_text}
            </p>
        </div>
    `;

    modal.classList.remove('hidden');
};

document.querySelector('.modal-close').addEventListener('click', () => {
    document.getElementById('modalOverlay').classList.add('hidden');
});

document.getElementById('modalOverlay').addEventListener('click', (e) => {
    if (e.target.id === 'modalOverlay') {
        document.getElementById('modalOverlay').classList.add('hidden');
    }
});

// Tool Tabs
document.querySelectorAll('.tool-tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.tool-tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tool-content').forEach(c => c.classList.remove('active'));
        btn.classList.add('active');
        document.getElementById(btn.dataset.tool + 'Tool').classList.add('active');
    });
});

function renderToolError(containerId, message) {
    const container = document.getElementById(containerId);
    if (container) {
        container.innerHTML = `<p class="placeholder-text">${message}</p>`;
    }
}

// Synastry
document.getElementById('synastryForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
        person_a: {
            date: document.getElementById('synDateA').value,
            time: document.getElementById('synTimeA').value,
            city: document.getElementById('synCityA').value,
            state: document.getElementById('synStateA').value
        },
        person_b: {
            date: document.getElementById('synDateB').value,
            time: document.getElementById('synTimeB').value,
            city: document.getElementById('synCityB').value,
            state: document.getElementById('synStateB').value
        }
    };

    try {
        const resp = await fetch(apiUrl('/api/synastry'), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (!resp.ok) {
            const err = await resp.json();
            throw new Error(err.detail || 'Synastry calculation failed.');
        }
        const result = await resp.json();
        renderSynastry(result);
    } catch (err) {
        renderToolError('synastryResults', err.message);
    }
});

function renderSynastry(data) {
    const container = document.getElementById('synastryResults');
    const syn = data.synastry;
    if (!syn) {
        renderToolError('synastryResults', 'No synastry data returned.');
        return;
    }

    const dependencies = syn.dependency_audits || [];
    const shared = syn.shared_fate || [];

    container.innerHTML = `
        <div class="tool-result-card">
            <div class="tool-result-title">Overall Assessment</div>
            <div>${syn.overall_assessment}</div>
        </div>
        <div class="tool-result-card">
            <div class="tool-result-title">Dependency Audits</div>
            ${dependencies.length ? dependencies.map(d => `
                <div class="tool-result-detail"><strong>${d.subject} ${d.planet}</strong> on ${d.target} (${d.type})</div>
                <div class="tool-result-detail">${d.delineation}</div>
            `).join('') : '<div class="tool-result-detail">No direct planet-to-fortune locks detected.</div>'}
        </div>
        <div class="tool-result-card">
            <div class="tool-result-title">Shared Fate</div>
            ${shared.length ? shared.map(s => `
                <div class="tool-result-detail"><strong>${s.type}:</strong> ${s.description}</div>
                <div class="tool-result-detail">${s.delineation}</div>
            `).join('') : '<div class="tool-result-detail">No Spirit handshakes or will-to-matter links detected.</div>'}
        </div>
    `;
}

// Kairos
document.getElementById('kairosForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
        activity: document.getElementById('kairosActivity').value,
        city: document.getElementById('kairosCity').value,
        state: document.getElementById('kairosState').value,
        start_date: document.getElementById('kairosStartDate').value || null,
        hours: parseInt(document.getElementById('kairosHours').value, 10) || 168
    };

    try {
        const resp = await fetch(apiUrl('/api/kairos'), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (!resp.ok) {
            const err = await resp.json();
            throw new Error(err.detail || 'Kairos scan failed.');
        }
        const result = await resp.json();
        renderKairos(result);
    } catch (err) {
        renderToolError('kairosResults', err.message);
    }
});

function renderKairos(data) {
    const container = document.getElementById('kairosResults');
    const windows = data.best_windows || [];
    if (!windows.length) {
        container.innerHTML = '<p class="placeholder-text">No viable windows found in the scan range.</p>';
        return;
    }

    const query = data.query || {};
    const topSlots = data.raw_top_slots || [];

    const queryHTML = `
        <div class="tool-result-card">
            <div class="tool-result-title">Query</div>
            <div class="tool-result-detail"><strong>Activity:</strong> ${query.activity || 'Unknown'}</div>
            <div class="tool-result-detail"><strong>Location:</strong> ${query.location || 'Unknown'}</div>
            <div class="tool-result-detail"><strong>Start:</strong> ${query.start_time ? new Date(query.start_time).toLocaleString() : 'Unknown'}</div>
            <div class="tool-result-detail"><strong>Range:</strong> ${query.scan_range || 'Unknown'}</div>
        </div>
    `;

    const windowsHTML = windows.map(w => `
        <div class="tool-result-card">
            <div class="tool-result-title">${w.mood} Window</div>
            <div class="tool-result-detail">Start: ${new Date(w.start).toLocaleString()}</div>
            <div class="tool-result-detail">End: ${new Date(w.end).toLocaleString()}</div>
            <div class="tool-result-detail">Duration: ${w.duration_hours} hours</div>
            <div class="tool-result-detail">Peak: ${new Date(w.peak_time).toLocaleString()} (Score ${w.peak_score})</div>
            ${(w.details || []).length ? `<div class="tool-result-detail">${w.details.slice(0, 4).join(' | ')}</div>` : ''}
        </div>
    `).join('');

    const slotsHTML = topSlots.length ? `
        <div class="tool-result-card">
            <div class="tool-result-title">Top Slots</div>
            ${topSlots.slice(0, 6).map(s => `
                <div class="tool-result-detail"><strong>${new Date(s.time).toLocaleString()}</strong> | Score ${s.score} | ${s.mood}</div>
            `).join('')}
        </div>
    ` : '';

    container.innerHTML = `${queryHTML}${windowsHTML}${slotsHTML}`;
}

// Horary Oracle
document.getElementById('horaryForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
        question: document.getElementById('horaryQuestion').value,
        city: document.getElementById('horaryCity').value,
        state: document.getElementById('horaryState').value,
        date: document.getElementById('horaryDate').value || null,
        time: document.getElementById('horaryTime').value || null
    };

    try {
        const resp = await fetch(apiUrl('/api/horary'), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (!resp.ok) {
            const err = await resp.json();
            throw new Error(err.detail || 'Horary oracle failed.');
        }
        const result = await resp.json();
        renderHorary(result);
    } catch (err) {
        renderToolError('horaryResults', err.message);
    }
});

function renderHorary(data) {
    const container = document.getElementById('horaryResults');
    const oracle = data.oracle;
    if (!oracle) {
        renderToolError('horaryResults', 'No horary response returned.');
        return;
    }

    const conditions = oracle.conditions || [];
    container.innerHTML = `
        <div class="tool-result-card">
            <div class="tool-result-title">Verdict: ${oracle.verdict}</div>
            <div class="tool-result-detail"><strong>Question:</strong> ${oracle.question}</div>
            <div class="tool-result-detail">Querent: ${oracle.querent_ruler} (Asc ${oracle.querent_sign})</div>
            <div class="tool-result-detail">Quesited: ${oracle.quesited_ruler} (House ${oracle.quesited_house} ${oracle.quesited_label}, ${oracle.quesited_sign})</div>
            <div class="tool-result-detail">Weight: ${oracle.verdict_weight}</div>
            <div class="tool-result-detail">Conditions: ${oracle.positive_count} favorable | ${oracle.negative_count} adverse</div>
        </div>
        <div class="tool-result-card">
            <div class="tool-result-title">Horary Physics</div>
            ${conditions.length ? conditions.map(c => `
                <div class="tool-result-detail"><strong>${c.condition}</strong>${c.status ? ` (${c.status})` : ''}${formatHoraryCondition(c) ? `: ${formatHoraryCondition(c)}` : ''}</div>
            `).join('') : '<div class="tool-result-detail">No applying physics detected between significators.</div>'}
        </div>
    `;
}

function formatHoraryCondition(c) {
    const parts = [];
    if (c.details) parts.push(c.details);
    if (c.aspect) parts.push(`Aspect ${c.aspect}`);
    if (c.via) parts.push(`Via ${c.via}`);
    if (c.from && c.to) parts.push(`${c.from} -> ${c.to}`);
    if (c.collector) parts.push(`Collector ${c.collector}`);
    if (c.p1 && c.p2) parts.push(`${c.p1} + ${c.p2}`);
    if (c.p1_aspect || c.p2_aspect) {
        const aspects = [c.p1_aspect, c.p2_aspect].filter(Boolean).join('/');
        if (aspects) parts.push(aspects);
    }
    if (c.intervener) parts.push(`Intervener ${c.intervener}`);
    if (c.target) parts.push(`Target ${c.target}`);
    if (c.giver && c.receiver) parts.push(`${c.giver} -> ${c.receiver}`);
    if (c.by) parts.push(`By ${Array.isArray(c.by) ? c.by.join(', ') : c.by}`);
    return parts.join(' | ');
}

// World Dashboard
document.getElementById('worldForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
        date: document.getElementById('worldDate').value || null,
        time: document.getElementById('worldTime').value || null
    };

    try {
        const resp = await fetch(apiUrl('/api/world'), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (!resp.ok) {
            const err = await resp.json();
            throw new Error(err.detail || 'World dashboard failed.');
        }
        const result = await resp.json();
        renderWorld(result);
    } catch (err) {
        renderToolError('worldResults', err.message);
    }
});

// Rectification
document.getElementById('rectificationForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
        date: document.getElementById('rectDate').value,
        time: document.getElementById('rectTime').value,
        city: document.getElementById('rectCity').value,
        state: document.getElementById('rectState').value
    };

    try {
        const resp = await fetch(apiUrl('/api/rectification'), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (!resp.ok) {
            const err = await resp.json();
            throw new Error(err.detail || 'Rectification failed.');
        }
        const result = await resp.json();
        renderRectification(result);
    } catch (err) {
        renderToolError('rectificationResults', err.message);
    }
});

function renderWorld(data) {
    const container = document.getElementById('worldResults');
    const stars = data.fixed_star_alerts || [];
    const eclipses = data.eclipses || [];
    const epoch = data.universal_overdrive || [];
    const transits = data.transiting_planets || [];

    let personalHits = [];
    if (currentResult && eclipses.length) {
        const points = [];
        Object.entries(currentResult.planets || {}).forEach(([name, info]) => {
            points.push({ label: name, longitude: info.longitude });
        });
        if (currentResult.angles) {
            points.push({ label: 'Ascendant', longitude: currentResult.angles.Ascendant });
            points.push({ label: 'Midheaven', longitude: currentResult.angles.MC });
        }

        eclipses.forEach(e => {
            points.forEach(p => {
                let diff = Math.abs(e.longitude - p.longitude) % 360;
                if (diff > 180) diff = 360 - diff;
                if (diff <= 3) {
                    personalHits.push(`${p.label} within ${diff.toFixed(1)}° of ${e.type} in ${e.sign}`);
                }
            });
        });
    }

    container.innerHTML = `
        <div class="tool-result-card">
            <div class="tool-result-title">Transiting Planets</div>
            ${transits.length ? transits.map(t => `
                <div class="tool-result-detail"><strong>${t.planet}:</strong> ${formatLongitude(t.longitude)} (${t.sign})${typeof t.speed === 'number' ? ` | Speed ${t.speed}` : ''}</div>
            `).join('') : '<div class="tool-result-detail">Transit list unavailable.</div>'}
        </div>
        <div class="tool-result-card">
            <div class="tool-result-title">Fixed Stars Active</div>
            ${stars.length ? stars.map(s => `
                <div class="tool-result-detail"><strong>${s.star}</strong> conjunct ${s.planet} (orb ${s.orb}°) | ${s.nature}</div>
                ${s.glory ? `<div class="tool-result-detail">Glory: ${s.glory}</div>` : ''}
                ${s.nemesis ? `<div class="tool-result-detail">Nemesis: ${s.nemesis}</div>` : ''}
            `).join('') : '<div class="tool-result-detail">No major fixed star activations at this moment.</div>'}
        </div>
        <div class="tool-result-card">
            <div class="tool-result-title">Eclipse Pressure</div>
            ${eclipses.length ? eclipses.map(e => `
                <div class="tool-result-detail"><strong>${e.type}</strong> at ${e.degree}° ${e.sign} (${e.triplicity})</div>
                ${e.duration_hours ? `<div class="tool-result-detail">Duration: ${e.duration_hours} hours</div>` : ''}
                ${e.affected_regions && e.affected_regions.length ? `<div class="tool-result-detail">Regions: ${e.affected_regions.join(', ')}</div>` : ''}
                ${e.stress_note ? `<div class="tool-result-detail">${e.stress_note}</div>` : ''}
            `).join('') : '<div class="tool-result-detail">No recent eclipses returned for this date.</div>'}
        </div>
        <div class="tool-result-card">
            <div class="tool-result-title">Personal Suspension Checks</div>
            ${personalHits.length ? personalHits.map(h => `<div class="tool-result-detail">${h}</div>`).join('') : '<div class="tool-result-detail">No personal suspensions detected from current eclipses.</div>'}
        </div>
        <div class="tool-result-card">
            <div class="tool-result-title">December 2025 Epoch</div>
            ${epoch.length ? epoch.map(e => `
                <div class="tool-result-detail"><strong>${e.cause}:</strong> ${e.status}</div>
                ${e.rule ? `<div class="tool-result-detail">${e.rule}</div>` : ''}
                ${e.description ? `<div class="tool-result-detail">${e.description}</div>` : ''}
            `).join('') : '<div class="tool-result-detail">No universal overdrive flags for this timestamp.</div>'}
        </div>
        <div class="tool-result-card">
            <div class="tool-result-title">World Note</div>
            <div class="tool-result-detail">${data.note || 'No global note provided.'}</div>
            ${data.timestamp ? `<div class="tool-result-detail">Timestamp: ${data.timestamp}</div>` : ''}
        </div>
    `;
}

function renderRectification(data) {
    const container = document.getElementById('rectificationResults');
    const animodar = data.animodar || [];
    const trutina = data.trutina_hermetis || [];
    const syzygy = data.syzygy || {};
    const meta = data.meta || {};

    const metaHTML = meta && meta.city ? `
        <div class="tool-result-card">
            <div class="tool-result-title">Chart Context</div>
            <div class="tool-result-detail"><strong>Birth:</strong> ${meta.date} ${meta.time}</div>
            <div class="tool-result-detail"><strong>Location:</strong> ${meta.city}${meta.state ? `, ${meta.state}` : ''}</div>
            <div class="tool-result-detail"><strong>Coordinates:</strong> ${typeof meta.lat === 'number' ? meta.lat.toFixed(4) : meta.lat}, ${typeof meta.lon === 'number' ? meta.lon.toFixed(4) : meta.lon}</div>
        </div>
    ` : '';

    const syzygyHTML = syzygy && syzygy.jd ? `
        <div class="tool-result-card">
            <div class="tool-result-title">Prenatal Syzygy</div>
            <div class="tool-result-detail"><strong>Type:</strong> ${syzygy.type}</div>
            <div class="tool-result-detail"><strong>JD:</strong> ${syzygy.jd.toFixed ? syzygy.jd.toFixed(4) : syzygy.jd}</div>
            <div class="tool-result-detail"><strong>Longitude:</strong> ${typeof syzygy.longitude === 'number' ? formatLongitude(syzygy.longitude) : 'Unknown'}</div>
        </div>
    ` : '';

    const animodarHTML = animodar.length ? `
        <div class="tool-result-card">
            <div class="tool-result-title">Animodar (Ptolemaic)</div>
            ${animodar.map(a => `
                <div class="tool-result-detail"><strong>${a.rectifying_planet}</strong> | ${a.suggestion}</div>
                <div class="tool-result-detail">Target Degree: ${a.target_degree.toFixed ? a.target_degree.toFixed(2) : a.target_degree}°</div>
                <div class="tool-result-detail">Difference: ${a.difference.toFixed ? a.difference.toFixed(2) : a.difference}° | Confidence ${a.confidence}%</div>
            `).join('')}
        </div>
    ` : '';

    const trutinaHTML = trutina.length ? `
        <div class="tool-result-card">
            <div class="tool-result-title">Trutina Hermetis</div>
            ${trutina.map(t => `
                <div class="tool-result-detail"><strong>Suggested Asc:</strong> ${formatLongitude(t.suggested_ascendant)}</div>
                <div class="tool-result-detail">Gestation: ${t.gestation_days} days | Confidence ${t.confidence}%</div>
                ${t.conception_date ? `<div class="tool-result-detail">Conception: ${t.conception_date}</div>` : ''}
            `).join('')}
        </div>
    ` : '';

    container.innerHTML = `
        ${metaHTML}
        ${syzygyHTML || '<div class="tool-result-card"><div class="tool-result-title">Prenatal Syzygy</div><div class="tool-result-detail">No syzygy found.</div></div>'}
        ${animodarHTML || '<div class="tool-result-card"><div class="tool-result-title">Animodar (Ptolemaic)</div><div class="tool-result-detail">No Animodar results returned.</div></div>'}
        ${trutinaHTML || '<div class="tool-result-card"><div class="tool-result-title">Trutina Hermetis</div><div class="tool-result-detail">No Trutina results returned.</div></div>'}
    `;
}
