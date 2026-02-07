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

export async function initiateCheckout(tier, chartRequest = null) {
    const token = localStorage.getItem('cael_auth_token');
    if (!token) {
        // Redirect to login, preserving intent
        window.location.href = `login.html?redirect=pricing&tier=${tier}`;
        return;
    }

    // Determine annual status
    // If billing toggle exists (Pricing Modal), use it.
    // If not (Paywall Modal), strict logic or passed param? 
    // For now, let's look for billingToggle first, else default to false (monthly) unless explicitly handled
    const billingToggle = document.getElementById("billingToggle");
    const isAnnual = billingToggle ? billingToggle.checked : false;

    // Use passed chartRequest or try fallback logic if needed. 
    let requestPayload = chartRequest;

    // For B2C (onetime), force validation of captured data
    if (tier === 'onetime' && !requestPayload) {
        if (window.dataCapturer) {
            requestPayload = window.dataCapturer.getBirthData();
        }

        if (!requestPayload || !requestPayload.lat) {
            alert("REQUIRED: Please enter your birth data and calculate the 'Preliminary Judgment' first. We need this data to generate your Premium Dossier.");
            if (pricingModal) pricingModal.classList.add("hidden");
            document.getElementById('calculate')?.scrollIntoView({ behavior: 'smooth' });
            return;
        }

        const confirmed = confirm(`VALIDATION: Proceed with this data?\n\nDate: ${requestPayload.date}\nTime: ${requestPayload.time}\nCity: ${requestPayload.city}\n\nFinalizing payment will secure your 100+ page Forensic Audit.`);
        if (!confirmed) return;
    }

    // Default fallback if still null (B2B might not need immediate chart data)
    requestPayload = requestPayload || {
        date: "2000-01-01", time: "12:00", city: "Rome", state: "Italy"
    };

    try {
        const resp = await fetch(apiUrl("/api/v1/billing/create-checkout-session"), {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({
                tier: tier,
                annual: isAnnual,
                chart_request: requestPayload,
                success_url: window.location.origin + "/success.html?session_id={CHECKOUT_SESSION_ID}",
                cancel_url: window.location.href
            })
        });

        if (!resp.ok) {
            const err = await resp.json();
            if (resp.status === 401) {
                // Token invalid
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
