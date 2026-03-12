/**
 * seo-bridge.js
 * 
 * Injected into legacy SEO content pages (techniques, houses, natal-charts, etc.)
 * to replace old B2B navigation with a simple nav bar that links back to the
 * main reading form, and adds a CTA banner at the top.
 */

(function () {
    "use strict";

    // 1. Replace the old header-actions nav
    const oldNav = document.querySelector(".header-actions");
    if (oldNav) {
        oldNav.innerHTML = `
            <a class="help-btn" href="/" style="background: linear-gradient(135deg, #c9a84c, #b8922f); color: #0a0a1a; font-weight: 700;">✦ Get Your Reading</a>
            <a class="help-btn" href="/">Home</a>
            <a class="help-btn" href="privacy.html">Privacy</a>
        `;
    }

    // 2. Add a sticky CTA bar at the top of the page
    const ctaBar = document.createElement("div");
    ctaBar.id = "seoCTABar";
    ctaBar.innerHTML = `
        <div style="
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 9999;
            background: linear-gradient(135deg, #c9a84c, #b8922f);
            color: #0a0a1a;
            text-align: center;
            padding: 0.5rem 1rem;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 0.85rem;
            font-weight: 600;
        ">
            ✦ Want to discover YOUR chart? 
            <a href="/#get-reading" style="color: #0a0a1a; text-decoration: underline; margin-left: 0.4rem;">
                Get your free natal chart reading →
            </a>
        </div>
    `;
    document.body.prepend(ctaBar);
    // Push body content down
    document.body.style.paddingTop = "36px";

    // 3. Replace old footer branding
    const footerBottom = document.querySelector(".footer-bottom");
    if (footerBottom) {
        footerBottom.innerHTML = `
            <p>© 2026 Traditional Astrology. All rights reserved.</p>
            <p class="footer-disclaimer">
                For entertainment, historical, and spiritual research purposes only. Not medical, legal, or financial advice.
            </p>
        `;
    }

    // 4. Replace "Try Demo" links → reading form
    document.querySelectorAll('a[href="demo.html"], a[href="signup.html"], a[href="login.html"]').forEach(a => {
        a.href = "/#get-reading";
        if (a.textContent.includes("Trial") || a.textContent.includes("Demo")) {
            a.textContent = "✦ Get Your Reading";
        }
        if (a.textContent.includes("Log")) {
            a.textContent = "Get Reading";
        }
    });

    // 5. Replace "documentation" and "api-guide" links → index
    document.querySelectorAll('a[href="documentation.html"], a[href="api-guide.html"], a[href="blog.html"]').forEach(a => {
        a.href = "/";
    });

    // 6. Clean up B2B-era footer columns
    const footerCols = document.querySelectorAll(".footer-col");
    footerCols.forEach(col => {
        const heading = col.querySelector("h3");
        if (!heading) return;
        const title = heading.textContent.trim();

        // Replace "Contact" column to remove Enterprise Sales
        if (title === "Contact") {
            col.querySelector("ul").innerHTML = `
                <li><a href="mailto:support@traditional-astrology.com">Support</a></li>
                <li><a href="mailto:bugs@traditional-astrology.com">Report a Bug</a></li>
            `;
        }

        // Replace "Product" column to remove developer-facing links
        if (title === "Product") {
            col.querySelector("ul").innerHTML = `
                <li><a href="/#get-reading">Get a Reading</a></li>
                <li><a href="techniques.html">Techniques</a></li>
                <li><a href="index.html#pricing">Pricing</a></li>
            `;
        }
    });
})();
