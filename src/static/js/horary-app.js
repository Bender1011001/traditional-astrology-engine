import { API_BASE, trackEvent } from './config.js';

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("horaryForm");
    const submitBtn = document.getElementById("submitBtn");
    const btnText = submitBtn.querySelector(".btn-text");
    const btnLoading = submitBtn.querySelector(".btn-loading");

    const chartFormCard = document.getElementById("chartFormCard");
    const errorSection = document.getElementById("errorSection");
    const errorMessage = document.getElementById("errorMessage");
    const readingSection = document.getElementById("readingSection");
    const readingContent = document.getElementById("readingContent");
    const askAnotherBtn = document.getElementById("askAnotherBtn");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        // UI Reset
        errorMessage.innerText = "";
        errorSection.classList.add("hidden");
        readingSection.classList.add("hidden");

        const payload = {
            question: document.getElementById("question").value.trim(),
            city: document.getElementById("horaryCity").value.trim(),
            state: document.getElementById("horaryState").value.trim()
        };

        if (!payload.question || !payload.city) {
            showError("Question and City are required.");
            return;
        }

        // Loading state
        submitBtn.disabled = true;
        btnText.classList.add("hidden");
        btnLoading.classList.remove("hidden");
        chartFormCard.style.opacity = "0.5";
        chartFormCard.style.pointerEvents = "none";

        try {
            const token = localStorage.getItem('access_token');
            const headers = { "Content-Type": "application/json" };
            if (token) {
                headers["Authorization"] = `Bearer ${token}`;
            }

            const response = await fetch(`${API_BASE}/api/v1/horary`, {
                method: "POST",
                headers: headers,
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || "Failed to consult the oracle.");
            }

            renderHoraryResponse(payload.question, data.oracle);

            // Show Reading
            chartFormCard.classList.add("hidden");
            readingSection.classList.remove("hidden");
            readingSection.scrollIntoView({ behavior: 'smooth', block: 'start' });

            trackEvent("horary_success", { city: payload.city });

        } catch (err) {
            console.error("Horary API error:", err);
            showError(err.message);
            trackEvent("horary_error", { error: err.message });
        } finally {
            // Revert Loading State
            submitBtn.disabled = false;
            btnText.classList.remove("hidden");
            btnLoading.classList.add("hidden");
            chartFormCard.style.opacity = "1";
            chartFormCard.style.pointerEvents = "auto";
        }
    });

    askAnotherBtn.addEventListener("click", () => {
        readingSection.classList.add("hidden");
        chartFormCard.classList.remove("hidden");
        document.getElementById("question").value = "";
        chartFormCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });

    function showError(msg) {
        errorMessage.innerText = msg;
        errorSection.classList.remove("hidden");
        chartFormCard.classList.add("hidden");
    }

    function renderHoraryResponse(question, oracle) {
        let stricturesHtml = '';
        if (oracle.strictures && oracle.strictures.length > 0) {
            stricturesHtml = `<div class="stricture-alert">
                <strong>Stricture Against Judgment:</strong><br>
                ${oracle.strictures.join("<br>")}
            </div>`;
        }

        let conditionsHtml = '';
        if (oracle.conditions && oracle.conditions.length > 0) {
            conditionsHtml = `
            <div style="margin-bottom: 2rem;">
                <h4 style="color:#c9a84c; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 0.5rem; margin-bottom: 1rem;">Mathematical Conditions Found</h4>
                ${oracle.conditions.map(c => `
                    <div class="trace-item">
                        <span class="trace-label">[${c.status}] ${c.condition}</span> 
                        <span style="color:rgba(255,255,255,0.8);">${c.details || ""}</span>
                    </div>
                `).join("")}
            </div>`;
        } else {
            conditionsHtml = `
            <div style="margin-bottom: 2rem;">
                <h4 style="color:#c9a84c; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 0.5rem; margin-bottom: 1rem;">Mathematical Conditions Found</h4>
                <div class="trace-item" style="color:rgba(255,255,255,0.6)">No applying perfections found between significators.</div>
            </div>`;
        }

        readingContent.innerHTML = `
            <div class="verdict-title">The Oracle</div>
            <div class="verdict-text" style="font-size:1.1rem; color:rgba(255,255,255,0.7); font-style:italic;">
                " ${question} "
            </div>
            
            ${stricturesHtml}

            <div class="verdict-box" style="margin-top: 0">
                <div class="verdict-title" style="font-size: 1.5rem">${oracle.verdict}</div>
                <div class="verdict-text" style="font-size: 1rem; margin-bottom: 0; padding-top: 0.5rem;">
                    Score: ${oracle.total_score} | Weight: ${oracle.verdict_weight.toUpperCase()}
                </div>
            </div>

            <div style="margin-top: 2rem; background:rgba(0,0,0,0.2); padding:1.5rem; border-radius:8px;">
                <h4 style="color:#c9a84c; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 0.5rem; margin-bottom: 1rem;">Significators</h4>
                <div class="trace-item"><span class="trace-label">Querent:</span> Ascendant in ${oracle.querent_sign} (Lord: ${oracle.querent_ruler})</div>
                <div class="trace-item"><span class="trace-label">Quesited:</span> ${oracle.quesited_label} (${oracle.quesited_house}H) in ${oracle.quesited_sign} (Lord: ${oracle.quesited_ruler})</div>
                <div class="trace-item"><span class="trace-label">Moon:</span> Co-Significator in ${oracle.moon_sign}</div>
            </div>

            <div style="margin-top: 1.5rem; background:rgba(0,0,0,0.2); padding:1.5rem; border-radius:8px;">
                ${conditionsHtml}
            </div>
        `;
    }
});
