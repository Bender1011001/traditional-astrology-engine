import { apiUrl, apiFetch } from './api.js';
import { logEvent } from './telemetry.js';
import { renderResults } from './results-core.js';
import { renderSynastry, renderKairos, renderHorary, renderWorld, renderRectification } from './results-tools.js';
import { renderToolError } from './ui.js';

export function setupForms() {
    // Chart Form
    const chartForm = document.getElementById('chartForm');
    if (chartForm) {
        chartForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = document.getElementById('calculateBtn');
            const originalText = btn.querySelector('.btn-text').textContent;
            btn.querySelector('.btn-text').textContent = "RUNNING ANALYSIS...";
            btn.disabled = true;

            const timeInput = document.getElementById("time");
            const timeUnknownToggle = document.getElementById("timeUnknown");
            const isTimeUnknown = timeUnknownToggle ? timeUnknownToggle.checked : false;
            const timeValue = timeInput ? timeInput.value : "";

            // Collect Form Data
            const formData = {
                date: document.getElementById('date').value,
                time: isTimeUnknown && !timeValue ? "12:00" : timeValue,
                city: document.getElementById('city').value,
                state: document.getElementById('state').value,
                age: document.getElementById('currentAge').value ? parseInt(document.getElementById('currentAge').value) : null,
                analysis_date: document.getElementById('analysisDate').value || null,
                house_system: document.getElementById('houseSystem').value || null,
                compare_house_systems: document.getElementById('compareHouseSystems').checked,
                zodiac_system: document.getElementById('zodiacSystem').value || null,
                ayanamsa: document.getElementById('ayanamsa').value || null
            };

            logEvent("chart_request", { form: formData });

            try {
                const response = await apiFetch('/api/calculate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                });

                if (!response.ok) {
                    const err = await response.json();
                    throw new Error(err.detail || 'No response from engine.');
                }

                const result = await response.json();
                logEvent("chart_result", { result });
                renderResults(result);

            } catch (error) {
                logEvent("chart_error", { message: error.message || String(error) });
                alert(error.message);
            } finally {
                btn.querySelector('.btn-text').textContent = originalText;
                btn.disabled = false;
            }
        });
    }

    // Synastry Form
    const synastryForm = document.getElementById('synastryForm');
    if (synastryForm) {
        synastryForm.addEventListener('submit', async (e) => {
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
            logEvent("tool_request", { tool: "synastry", payload });
            try {
                const resp = await apiFetch('/api/synastry', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                if (!resp.ok) throw new Error('Synastry calculation failed.');
                const result = await resp.json();
                renderSynastry(result);
            } catch (err) {
                renderToolError('synastryResults', err.message);
            }
        });
    }

    // Kairos
    const kairosForm = document.getElementById('kairosForm');
    if (kairosForm) {
        kairosForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            // ... Similar logic ...
            const payload = {
                activity: document.getElementById('kairosActivity').value,
                city: document.getElementById('kairosCity').value,
                state: document.getElementById('kairosState').value,
                start_date: document.getElementById('kairosStartDate').value || null,
                hours: parseInt(document.getElementById('kairosHours').value, 10) || 168
            };
            try {
                const resp = await apiFetch('/api/kairos', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                if (!resp.ok) throw new Error('Kairos failed');
                renderKairos(await resp.json());
            } catch (err) {
                renderToolError('kairosResults', err.message);
            }
        });
    }

    // Horary
    const horaryForm = document.getElementById('horaryForm');
    if (horaryForm) {
        horaryForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const payload = {
                question: document.getElementById('horaryQuestion').value,
                city: document.getElementById('horaryCity').value,
                state: document.getElementById('horaryState').value,
                date: document.getElementById('horaryDate').value || null,
                time: document.getElementById('horaryTime').value || null
            };
            try {
                const resp = await apiFetch('/api/horary', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                if (!resp.ok) throw new Error('Horary failed');
                renderHorary(await resp.json());
            } catch (err) {
                renderToolError('horaryResults', err.message);
            }
        });
    }

    // World
    const worldForm = document.getElementById('worldForm');
    if (worldForm) {
        worldForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const payload = {
                date: document.getElementById('worldDate').value || null,
                time: document.getElementById('worldTime').value || null
            };
            try {
                const resp = await apiFetch('/api/world', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
                if (!resp.ok) throw new Error('World failed');
                renderWorld(await resp.json());
            } catch (err) {
                renderToolError('worldResults', err.message);
            }
        });
    }

    // Rectification
    const rectForm = document.getElementById('rectificationForm');
    if (rectForm) {
        rectForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            // ... Logic ...
            const payload = {
                date: document.getElementById('rectDate').value,
                time: document.getElementById('rectTime').value,
                city: document.getElementById('rectCity').value,
                state: document.getElementById('rectState').value,
                rectification_methods: ['animodar', 'trutina_hermetis'] // Simplify for now
            };
            try {
                const resp = await apiFetch('/api/rectification', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
                if (!resp.ok) throw new Error('Rect failed');
                renderRectification(await resp.json());
            } catch (err) {
                renderToolError('rectificationResults', err.message);
            }
        });
    }
}
