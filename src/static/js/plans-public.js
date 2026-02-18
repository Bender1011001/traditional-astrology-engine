import { apiUrl } from './api.js';

function setTierDisabled(tier, reason) {
  const anchors = document.querySelectorAll(`a[data-tier-cta="${tier}"]`);
  anchors.forEach((a) => {
    a.textContent = tier === "studio" ? "Request Studio Access" : "Get Started";
    a.href = tier === "studio" ? "mailto:enterprise@traditional-astrology.com?subject=Studio%20Access" : a.href;
    a.classList.add("btn-secondary");
    a.classList.remove("btn-primary");
    if (reason) a.setAttribute("title", reason);
  });

  const notes = document.querySelectorAll(`[data-tier-note="${tier}"]`);
  notes.forEach((n) => {
    n.textContent = reason || "Checkout is not enabled for this tier yet.";
  });
}

function loadPlansAndGate() {
    // Monthly pricing removal: We no longer gate based on specific tiers in this file.
    // The focus is now on the $20 per-reading model.
    console.log("[plans-public] Monthly tier gating disabled. Per-reading model active.");
}

document.addEventListener("DOMContentLoaded", loadPlansAndGate);
