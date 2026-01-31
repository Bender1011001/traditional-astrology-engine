import { logEvent } from './telemetry.js';

export function setActiveTab(btn, allButtons, allPanels, datasetKey, panelSuffix) {
    allButtons.forEach((b) => {
        const isActive = b === btn;
        b.classList.toggle('active', isActive);
        b.setAttribute('aria-selected', isActive ? 'true' : 'false');
        b.setAttribute('tabindex', isActive ? '0' : '-1');
    });
    allPanels.forEach((panel) => panel.classList.remove('active'));
    const targetPanel = document.getElementById(btn.dataset[datasetKey] + panelSuffix);
    if (targetPanel) targetPanel.classList.add('active');
}

export function renderToolError(containerId, message) {
    const container = document.getElementById(containerId);
    if (container) {
        container.innerHTML = `<p class="placeholder-text">${message}</p>`;
    }
}

export function setupTabs() {
    // Result Tabs
    const resultTabs = Array.from(document.querySelectorAll('.tab-btn'));
    const resultPanels = Array.from(document.querySelectorAll('.tab-content'));
    const activeResultTab = resultTabs.find((btn) => btn.classList.contains('active'));
    if (activeResultTab) {
        setActiveTab(activeResultTab, resultTabs, resultPanels, 'tab', 'Tab');
    }
    resultTabs.forEach(btn => {
        btn.addEventListener('click', () => {
            setActiveTab(btn, resultTabs, resultPanels, 'tab', 'Tab');
            logEvent("tab_change", { tab: btn.dataset.tab });
        });
    });

    // Tool Tabs
    const toolTabs = Array.from(document.querySelectorAll('.tool-tab-btn'));
    const toolPanels = Array.from(document.querySelectorAll('.tool-content'));
    const activeToolTab = toolTabs.find((btn) => btn.classList.contains('active'));
    if (activeToolTab) {
        setActiveTab(activeToolTab, toolTabs, toolPanels, 'tool', 'Tool');
    }
    toolTabs.forEach(btn => {
        btn.addEventListener('click', () => {
            setActiveTab(btn, toolTabs, toolPanels, 'tool', 'Tool');
            logEvent("tool_tab_change", { tool: btn.dataset.tool });
        });
    });
}
