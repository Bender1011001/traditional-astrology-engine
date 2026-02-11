import { apiUrl } from './api.js';

export function setupPricing() {
    // Pricing Modal Logic
    const pricingBtn = document.getElementById("pricingBtn");
    const pricingTriggers = document.querySelectorAll("[data-pricing-trigger]");
    const pricingModal = document.getElementById("pricingModal");
    const pricingClose = document.getElementById("pricingClose");
    const billingToggle = document.getElementById("billingToggle");

    const openPricing = () => {
        if (pricingModal) pricingModal.classList.remove("hidden");
    };

    if (pricingBtn) {
        pricingBtn.onclick = openPricing;
    }
    if (pricingTriggers.length) {
        pricingTriggers.forEach((trigger) => {
            trigger.addEventListener("click", openPricing);
        });
    }
    if (pricingClose) {
        pricingClose.onclick = () => {
            if (pricingModal) pricingModal.classList.add("hidden");
        };
    }
    if (pricingModal) {
        pricingModal.onclick = (e) => {
            if (e.target === pricingModal) pricingModal.classList.add("hidden");
        };
    }

    if (billingToggle) {
        billingToggle.onchange = function () {
            const isAnnual = this.checked;
            const period = isAnnual ? "/yr" : "/mo";

            // Update DOM classes for styling
            const mLabel = document.getElementById("monthlyLabel");
            const aLabel = document.getElementById("annualLabel");
            if (mLabel) mLabel.classList.toggle("active", !isAnnual);
            if (aLabel) aLabel.classList.toggle("active", isAnnual);

            // Update Prices
            // Practitioner Access: 79/mo -> 790/yr
            const priceStarter = document.getElementById("price-starter");

            if (priceStarter) priceStarter.textContent = isAnnual ? "790" : "79";

            const periodStarter = document.getElementById("period-starter");
            if (periodStarter) periodStarter.textContent = period;
        };
    }
}


let pendingTier = null;

export function setupDirectIntake() {
    const intakeModal = document.getElementById("intakeModal");
    const intakeClose = document.getElementById("intakeClose");
    const intakeForm = document.getElementById("intakeForm");
    const intakeTimeUnknown = document.getElementById("intakeTimeUnknown");
    const intakeTime = document.getElementById("intakeTime");

    if (intakeClose) {
        intakeClose.onclick = () => {
            if (intakeModal) intakeModal.classList.add("hidden");
            pendingTier = null;
        };
    }

    if (intakeTimeUnknown && intakeTime) {
        intakeTimeUnknown.addEventListener('change', (e) => {
            if (e.target.checked) {
                intakeTime.value = "12:00";
                intakeTime.disabled = true;
            } else {
                intakeTime.disabled = false;
            }
        });
    }

    if (intakeForm) {
        intakeForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const date = document.getElementById("intakeDate").value;
            const time = document.getElementById("intakeTime").value;
            const city = document.getElementById("intakeCity").value;
            const unknown = document.getElementById("intakeTimeUnknown")?.checked;

            if (!date || !city) {
                alert("Please enter birth date and city.");
                return;
            }

            const payload = {
                date: date,
                time: (unknown || !time) ? "12:00" : time,
                city: city,
                state: "" // Optional for rough intake
            };

            // Save for persistence
            localStorage.setItem("cael_last_request", JSON.stringify(payload));

            // Hide modal
            if (intakeModal) intakeModal.classList.add("hidden");

            // Resume checkout
            if (pendingTier) {
                initiateCheckout(pendingTier, payload);
                pendingTier = null;
            } else {
                // If somehow triggered without a tier, default to something or just stop
                // But realistically pendingTier should be set.
            }
        });
    }
}

export async function initiateCheckout(tier, chartRequest = null) {
    const token = localStorage.getItem('cael_auth_token');
    
    // Auth Check first
    if (!token) {
        window.location.href = `login.html?redirect=pricing&tier=${tier}`;
        return;
    }

    const billingToggle = document.getElementById("billingToggle");
    const isAnnual = billingToggle ? billingToggle.checked : false;

    // Chart request is optional for subscription checkout.
    // If present, it will be attached to metadata for downstream workflows.
    let requestPayload = chartRequest;
    if (!requestPayload) {
        try {
            const saved = localStorage.getItem("cael_last_request");
            if (saved) requestPayload = JSON.parse(saved);
        } catch (e) { }
    }

    // Proceed with checkout
    try {
        const resp = await fetch(apiUrl("/api/v1/billing/create-checkout-session"), {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-Requested-With": "XMLHttpRequest",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({
                tier: tier,
                annual: isAnnual,
                chart_request: requestPayload,
                success_url: window.location.origin + "/success.html",
                cancel_url: window.location.href
            })
        });

        if (!resp.ok) {
            const err = await resp.json();
            if (resp.status === 401) {
                window.location.href = "login.html";
                return;
            }
            throw new Error(err.detail || "Checkout Failed");
        }

        const data = await resp.json();
        if (data.url) {
            window.location.href = data.url;
        }

    } catch (e) {
        alert("Billing Error: " + e.message);
    }
}
