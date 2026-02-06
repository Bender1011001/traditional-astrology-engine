import os

RESOURCES_PATH = r'e:\code.projects\astrology\src\static\resources.html'
INDEX_PATH = r'e:\code.projects\astrology\src\static\index.html'
METHODOLOGY_PATH = r'e:\code.projects\astrology\src\static\methodology.html'
ABOUT_PATH = r'e:\code.projects\astrology\src\static\about.html'

def create_resources_page():
    content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Resources & Articles | Codex Caelestis</title>
    <meta name="description" content="Learn about Traditional Astrology, its history, methods, and how it differs from modern approaches.">
    <meta name="theme-color" content="#f4efe6">
    <link rel="canonical" href="https://traditional-astrology.com/resources.html">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600;700&family=Sora:wght@300;400;500;600&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <a class="skip-link" href="#main">Skip to content</a>
    <div class="background-globes">
        <div class="globe globe-1"></div>
        <div class="globe globe-2"></div>
        <div class="stars-overlay"></div>
    </div>

    <main id="main" class="container">
        <header>
            <div class="header-content">
                <h1>RESOURCES</h1>
                <div class="ornament"></div>
                <p class="subtitle">Education, History, and Theory.</p>
                <nav class="header-actions" aria-label="Primary">
                    <a class="help-btn" href="index.html">HOME</a>
                    <a class="help-btn" href="methodology.html">METHODOLOGY</a>
                    <a class="help-btn" href="resources.html" aria-current="page">RESOURCES</a>
                    <a class="help-btn" href="faq.html">FAQ</a>
                    <a class="help-btn" href="login.html">LOG IN</a>
                </nav>
            </div>
        </header>

        <section class="basic-view">
            <div class="basic-card">
                <h2 class="section-title">FEATURED ARTICLES</h2>
                <div class="article-grid" style="display: grid; gap: 2rem; margin-top: 2rem;">
                    
                    <article class="resource-article" style="padding-bottom: 2rem; border-bottom: 1px solid var(--glass-border);">
                        <h3 style="font-family: 'Cormorant Garamond', serif; font-size: 1.5rem; color: var(--gold); margin-bottom: 0.5rem;">What is Traditional Astrology?</h3>
                        <p style="margin-bottom: 1rem;">Traditional astrology refers to the practices and techniques developed between the 2nd century BCE and the 17th century CE. Unlike modern astrology, which often focuses on character analysis and psychological archetypes, traditional astrology is primarily predictive and event-oriented.</p>
                        <p>It relies on a rigorous set of rules for assessing planetary strength ("Essential Dignity") and chart architecture, viewing the chart not just as a map of the psyche, but as a map of destiny.</p>
                    </article>

                    <article class="resource-article" style="padding-bottom: 2rem; border-bottom: 1px solid var(--glass-border);">
                        <h3 style="font-family: 'Cormorant Garamond', serif; font-size: 1.5rem; color: var(--gold); margin-bottom: 0.5rem;">Tradition vs. Modernity</h3>
                        <p style="margin-bottom: 1rem;">The divergence occurred largely in the 20th century with the rise of Theosophy and psychology. Modern astrology adopted the outer planets (Uranus, Neptune, Pluto) as primary rulers and shifted focus to the internal world.</p>
                        <p>Traditional astrology uses the visible planets (Saturn, Jupiter, Mars, Sun, Venus, Mercury, Moon) and emphasizes the "condition" of the planet—is it capable of acting? Is it supported? This allows for more concrete delineations of external circumstances.</p>
                    </article>

                    <article class="resource-article">
                        <h3 style="font-family: 'Cormorant Garamond', serif; font-size: 1.5rem; color: var(--gold); margin-bottom: 0.5rem;">The History of Essential Dignities</h3>
                        <p style="margin-bottom: 1rem;">Essential Dignity is the core scoring system of the traditional astrologer. It categorizes how comfortable a planet is in a specific sign.</p>
                        <p>Developed in the Hellenistic period and refined by medieval Persian and Arabic astrologers, this system assigns points for Rulership (+5), Exaltation (+4), Triplicity (+3), Term (+2), and Face (+1). A planet with high dignity is like an honored guest in its own home—capable and effective. A planet without dignity is like a wanderer, dependent on others.</p>
                    </article>

                </div>
            </div>
        </section>

        <footer style="margin-top: 4rem; text-align: center; font-size: 0.75rem; color: var(--text-muted); padding-bottom: 2rem;">
            <p>&copy; 2026 Codex Caelestis. All rights reserved.</p>
            <div style="margin-top: 0.5rem;">
                <a href="privacy.html" style="color: inherit; text-decoration: none; margin: 0 0.5rem;">Privacy Policy</a>
                <span aria-hidden="true">•</span>
                <a href="terms.html" style="color: inherit; text-decoration: none; margin: 0 0.5rem;">Terms of Service</a>
            </div>
        </footer>
    </main>
    <script src="basic.js"></script>
</body>
</html>
'''
    with open(RESOURCES_PATH, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Resources page created.")

def update_nav(path):
    if not os.path.exists(path):
        return
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'href="resources.html"' in content:
        return
        
    target = '<a class="help-btn" href="faq.html">FAQ</a>'
    link = '<a class="help-btn" href="resources.html">RESOURCES</a>\n                    '
    
    if target in content:
        content = content.replace(target, link + target)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated nav in {path}")
    else:
        # Fallback for methodology page maybe using different nav structure?
        # Checked methodology.html, it uses same structure but "BASIC VERSION" / "ADVANCED TOOLS".
        # Ah, methodology has a different nav.
        # <nav class="header-actions" aria-label="Primary">
        # <a class="help-btn" href="index.html">BASIC VERSION</a>
        # <a class="help-btn" href="advanced.html">ADVANCED TOOLS</a>
        # ...
        # I should just append to that.
        target_nav_end = '</nav>'
        link_inline = '<a class="help-btn" href="resources.html">RESOURCES</a>'
        
        # If it doesn't match default target, check generic nav end
        if target_nav_end in content:
            # Insert before </nav>
             content = content.replace(target_nav_end, link_inline + '\n' + target_nav_end)
             with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
             print(f"Updated nav in {path} (generic append)")

def main():
    create_resources_page()
    update_nav(INDEX_PATH)
    update_nav(METHODOLOGY_PATH)
    update_nav(ABOUT_PATH)

if __name__ == "__main__":
    main()
