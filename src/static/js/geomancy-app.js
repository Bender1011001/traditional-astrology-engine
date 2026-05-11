import { API_BASE, trackEvent } from './config.js';

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("geomancyForm");
    const questionInput = document.getElementById("geomancyQuestion");
    const manualToggle = document.getElementById("manualCountsToggle");
    const manualPanel = document.getElementById("manualCountsPanel");
    const manualGrid = document.getElementById("manualCountsGrid");
    const submitBtn = document.getElementById("geomancySubmitBtn");
    const btnText = submitBtn.querySelector(".btn-text");
    const btnLoading = submitBtn.querySelector(".btn-loading");
    const errorSection = document.getElementById("errorSection");
    const errorMessage = document.getElementById("errorMessage");
    const resultSection = document.getElementById("geomancyResultSection");
    const resultContent = document.getElementById("geomancyResultContent");
    const castAgainBtn = document.getElementById("castAgainBtn");

    buildManualCountInputs();

    manualToggle.addEventListener("change", () => {
        manualPanel.classList.toggle("hidden", !manualToggle.checked);
    });

    castAgainBtn.addEventListener("click", () => {
        resultSection.classList.add("hidden");
        form.scrollIntoView({ behavior: "smooth", block: "start" });
    });

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        hideError();
        resultSection.classList.add("hidden");

        const question = questionInput.value.trim();
        if (!question) {
            showError("Question is required.");
            return;
        }

        const payload = { question };
        if (manualToggle.checked) {
            const counts = readManualCounts();
            if (!counts) return;
            payload.mother_counts = counts;
        }

        setLoading(true);
        try {
            trackEvent("geomancy_cast_submit", {
                manual_counts: Boolean(payload.mother_counts),
            });
            const response = await fetch(`${API_BASE}/api/v1/geomancy/cast`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-Requested-With": "XMLHttpRequest",
                },
                body: JSON.stringify(payload),
            });
            const data = await response.json().catch(() => ({}));
            if (!response.ok) {
                throw new Error(data.detail || "Could not cast the geomantic shield.");
            }
            renderGeomancy(data);
            trackEvent("geomancy_cast_success", {
                verdict: data.judgement?.verdict || "unknown",
                generation_method: data.generation_method || "unknown",
            });
        } catch (err) {
            showError(err.message || "Could not cast the geomantic shield.");
            trackEvent("geomancy_cast_error", { error: err.message || "unknown" });
        } finally {
            setLoading(false);
        }
    });

    function buildManualCountInputs() {
        const labels = [];
        for (let mother = 1; mother <= 4; mother += 1) {
            for (let row = 1; row <= 4; row += 1) {
                labels.push(`M${mother}.${row}`);
            }
        }
        manualGrid.innerHTML = labels.map((label, index) => `
            <label class="geomancy-count-field">
                <span>${label}</span>
                <input type="number" min="1" max="99" inputmode="numeric" value="${7 + (index % 9)}" data-count-index="${index}" />
            </label>
        `).join("");
    }

    function readManualCounts() {
        const inputs = Array.from(manualGrid.querySelectorAll("input"));
        const counts = [];
        for (const input of inputs) {
            const value = Number.parseInt(input.value, 10);
            if (!Number.isInteger(value) || value <= 0) {
                showError("Manual line counts must be positive whole numbers.");
                input.focus();
                return null;
            }
            counts.push(value);
        }
        if (counts.length !== 16) {
            showError("Exactly 16 manual line counts are required.");
            return null;
        }
        return counts;
    }

    function renderGeomancy(data) {
        const judge = data.judge || {};
        const outcome = data.outcome || {};
        const witnesses = data.witnesses || {};
        const judgement = data.judgement || {};
        const validity = data.validity || {};
        const topic = data.topic || {};
        const source = data.source_basis || {};

        resultContent.innerHTML = `
            <div class="geomancy-result-header">
                <div>
                    <p class="geomancy-kicker">Geomantic Shield</p>
                    <h2>${escapeHtml(judgement.verdict || "Cast Complete")}</h2>
                    <p>${escapeHtml(judgement.summary || "The shield has been cast.")}</p>
                </div>
                <div class="geomancy-score">
                    <span>Score</span>
                    <strong>${escapeHtml(String(judgement.score ?? 0))}</strong>
                    <small>${escapeHtml(judgement.weight || "balanced")}</small>
                </div>
            </div>

            <div class="geomancy-summary-grid">
                ${summaryCard("Judge", judge)}
                ${summaryCard("Outcome", outcome)}
                ${summaryCard("Questioner", witnesses.questioner)}
                ${summaryCard("Asked About", witnesses.asked_about)}
            </div>

            <div class="geomancy-meta-strip">
                <span><strong>Validity:</strong> ${escapeHtml(validity.message || "")}</span>
                <span><strong>Topic:</strong> ${escapeHtml(topic.label || "general")}</span>
                <span><strong>Method:</strong> ${escapeHtml(data.generation_method || "")}</span>
            </div>

            <div class="geomancy-shield" aria-label="Geomantic shield chart">
                ${(data.shield || []).map(renderShieldCell).join("")}
            </div>

            <div class="geomancy-notes">
                <h3>Judgement Notes</h3>
                <ul>
                    ${(judgement.notes || []).map(note => `<li>${escapeHtml(note)}</li>`).join("")}
                </ul>
            </div>

            <div class="geomancy-source-note">
                <p><strong>Source basis:</strong> ${escapeHtml((source.implemented_rules || []).join("; "))}</p>
                <p>${escapeHtml(source.figure_name_note || "")}</p>
                <p>${escapeHtml(data.safety_notice || "")}</p>
            </div>
        `;
        resultSection.classList.remove("hidden");
        resultSection.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    function summaryCard(title, figure) {
        const safeFigure = figure || {};
        return `
            <article class="geomancy-summary-card">
                <span>${escapeHtml(title)}</span>
                ${renderDots(safeFigure.rows || [])}
                <h3>${escapeHtml(safeFigure.name || "")}</h3>
                <p>${escapeHtml(safeFigure.summary || "")}</p>
            </article>
        `;
    }

    function renderShieldCell(entry) {
        return `
            <article class="geomancy-figure-card">
                <div class="geomancy-role">
                    <strong>${escapeHtml(entry.role || "")}</strong>
                    <span>House ${escapeHtml(String(entry.house || ""))}</span>
                </div>
                ${renderDots(entry.rows || [])}
                <h3>${escapeHtml(entry.name || "")}</h3>
                <p>${escapeHtml(entry.house_english || "")}</p>
            </article>
        `;
    }

    function renderDots(rows) {
        return `
            <div class="geomancy-dots" aria-hidden="true">
                ${rows.map(row => `
                    <div class="geomancy-dot-row">
                        <i></i>${Number(row) === 2 ? "<i></i>" : ""}
                    </div>
                `).join("")}
            </div>
        `;
    }

    function setLoading(isLoading) {
        submitBtn.disabled = isLoading;
        btnText.classList.toggle("hidden", isLoading);
        btnLoading.classList.toggle("hidden", !isLoading);
    }

    function showError(message) {
        errorMessage.textContent = message;
        errorSection.classList.remove("hidden");
        errorSection.scrollIntoView({ behavior: "smooth", block: "center" });
    }

    function hideError() {
        errorMessage.textContent = "";
        errorSection.classList.add("hidden");
    }

    function escapeHtml(value) {
        return String(value ?? "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
});
