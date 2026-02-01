import { apiUrl } from './api.js';

export function setupPricing() {
    // Pricing Modal Logic
    const pricingBtn = document.getElementById("pricingBtn");
    const pricingModal = document.getElementById("pricingModal");
    const pricingClose = document.getElementById("pricingClose");
    const billingToggle = document.getElementById("billingToggle");

    if (pricingBtn) {
        pricingBtn.onclick = () => {
            if (pricingModal) pricingModal.classList.remove("hidden");
        };
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
            // Scholar (Starter): 9/mo -> 90/yr
            // Magus (Practitioner): 29/mo -> 290/yr
            const priceStarter = document.getElementById("price-starter");
            const pricePractitioner = document.getElementById("price-practitioner");

            if (priceStarter) priceStarter.textContent = isAnnual ? "90" : "9";
            if (pricePractitioner) pricePractitioner.textContent = isAnnual ? "290" : "29";

            const periodStarter = document.getElementById("period-starter");
            const periodPractitioner = document.getElementById("period-practitioner");

            if (periodStarter) periodStarter.textContent = period;
            if (periodPractitioner) periodPractitioner.textContent = period;
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
    // The backend schemas say chart_request is optional but logical for 'onetime'.
    // For subscriptions, chart_request isn't strictly needed for the sub itself but maybe for context?
    // We'll use a dummy if null, or rely on backend handling optional.
    const requestPayload = chartRequest || {
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
