import { apiUrl } from './api.js';

function setTierDisabled(tier, reason) {
  const anchors = document.querySelectorAll(`a[data-tier-cta="${tier}"]`);
  anchors.forEach((a) => {
    a.textContent = tier === "studio" ? "Request Studio Access" : "Start Free Trial";
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

async function loadPlansAndGate() {
  try {
    const resp = await fetch(apiUrl("/api/v1/billing/plans"));
    const data = await resp.json();
    if (!resp.ok) return;

    if (data && data.checkout_globally_enabled === false) {
      const mode = String(data.sales_mode || "pilot").toLowerCase();
      const reason = mode === "pilot"
        ? "Pilot build mode: checkout is paused while Etsy workflow features are finalized."
        : "Checkout is currently unavailable.";
      setTierDisabled("practitioner", reason);
      setTierDisabled("studio", reason);
      return;
    }

    const plans = Array.isArray(data.plans) ? data.plans : [];
    const byTier = {};
    plans.forEach((p) => {
      if (p && p.tier) byTier[String(p.tier).toLowerCase()] = p;
    });

    const practitioner = byTier["practitioner"];
    if (practitioner && !practitioner.checkout_enabled_monthly && !practitioner.checkout_enabled_annual) {
      setTierDisabled("practitioner", "Practitioner checkout is not configured yet.");
    }

    const studio = byTier["studio"];
    if (studio && !studio.checkout_enabled_monthly && !studio.checkout_enabled_annual) {
      setTierDisabled("studio", "Studio checkout is not configured yet. Request access.");
    }
  } catch (e) {
    // Non-fatal: leave static CTAs as-is.
  }
}

document.addEventListener("DOMContentLoaded", loadPlansAndGate);

