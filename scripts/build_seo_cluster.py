import os
import shutil

STATIC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src", "static"))
BASE_TEMPLATE = os.path.join(STATIC_DIR, "natal-charts.html")

PAGES = [
    {
        "filename": "traditional-natal-chart-calculator.html",
        "title": "Traditional Natal Chart Calculator | Free Classical Reading",
        "desc": "Calculate your traditional natal chart using the exact methods of Hellenistic and Medieval astrologers. 100% free deterministic planetary calculations.",
        "h1": "Traditional Natal Chart Calculator",
        "subtitle": "Uncover your life's blueprint with the precision of classical astrology.",
        "body": "<p>A traditional natal chart calculator relies on concrete astronomical positions interpreted through classical rules like essential dignities, sect, and house rulerships. Modern calculators often blend psychological language and outer planets, but here we calculate your natal chart exactly as a 17th-century practitioner would.</p>"
    },
    {
        "filename": "traditional-birth-chart-calculator.html",
        "title": "Traditional Birth Chart Calculator | Classical Astrology",
        "desc": "The most accurate traditional birth chart calculator online. Retrieve your exact planetary dignities, sect, and classical placements.",
        "h1": "Traditional Birth Chart Calculator",
        "subtitle": "Real calculations from ancient texts, not arbitrary AI guesswork.",
        "body": "<p>Your birth chart is the fundamental map of the sky at your moment of birth. By using a traditional birth chart calculator, you ensure that factors like day/night sect, traditional planetary rulerships (like Mars ruling Scorpio), and whole-sign houses are respected.</p>"
    },
    {
        "filename": "traditional-vs-modern-astrology.html",
        "title": "Traditional vs. Modern Astrology | What's the Difference?",
        "desc": "Learn the key differences between traditional and modern astrology, from planetary rulerships to predictive techniques.",
        "h1": "Traditional vs. Modern Astrology",
        "subtitle": "Why precision and historical methods yield clearer results than psychological frameworks.",
        "body": "<p>Modern astrology focuses heavily on psychological profiles, Jungian archetypes, and the outer planets (Uranus, Neptune, Pluto). Traditional astrology is a concrete, predictive system using the 7 visible planets to deliver tangible judgments on life circumstances, fortune, and timing.</p>"
    },
    {
        "filename": "traditional-astrology-chart-interpretation.html",
        "title": "Traditional Astrology Chart Interpretation Techniques",
        "desc": "A guide to interpreting a birth chart using traditional astrology methods like dignities, receptions, and profections.",
        "h1": "Traditional Astrology Chart Interpretation",
        "subtitle": "How to judge a natal chart like a classical astrologer.",
        "body": "<p>Traditional interpretation requires layering evidence. We look at the Ascendant for life path, evaluate the Sect to determine the most helpful and challenging planets, and score Essential Dignities to understand which planetary promises can actually manifest.</p>"
    },
    {
        "filename": "traditional-astrology-methodology.html",
        "title": "Our Traditional Astrology Methodology | The Math & Sources",
        "desc": "An inside look at the methodology behind our traditional astrology engine. We cite our algorithms and classical sources.",
        "h1": "Traditional Astrology Methodology",
        "subtitle": "Rooted in Vettius Valens, Guido Bonatti, and rigorous astronomical data.",
        "body": "<p>Our calculator does not hallucinate. Every line of our traditional astrology methodology is tied to classical literature. We utilize the Swiss Ephemeris for exact planetary coordinate calculations and apply the deterministic interpretation rules of medieval horary and natal texts.</p>"
    }
]

def build_pages():
    with open(BASE_TEMPLATE, "r", encoding="utf-8") as f:
        template_html = f.read()

    for page in PAGES:
        # Replace SEO Meta
        html = template_html.replace(
            '<title>Traditional Birth Chart Calculator &amp; Natal Chart Reading</title>',
            f"<title>{page['title']}</title>"
        )
        html = html.replace(
            '<meta content="The definitive traditional astrology calculator. Calculate your classical natal chart, identify essential dignities, and generate a traditional birth chart reading using verifiable, pre-1700s techniques." name="description"/>',
            f'<meta content="{page["desc"]}" name="description"/>'
        )
        # Replace H1
        html = html.replace(
            '<h1>Traditional Birth Chart Calculator &amp; Reading</h1>',
            f"<h1>{page['h1']}</h1>"
        )
        # Replace Subtitle
        html = html.replace(
            '<p class="subtitle">Enter your birth details in the calculator above or discover the mechanics behind a classical traditional natal chart reading below.</p>',
            f'<p class="subtitle">{page["subtitle"]}</p>'
        )
        
        # Replace body copy (the first paragraph in the basic-card)
        body_target = '<p>In traditional practice, every planet, sign, and house contributes concrete testimony. The Sun, Moon, and\n          planets describe areas of life and the quality of events, while the Ascendant anchors the chart as the\n          native’s life path. This makes natal chart astrology a foundational technique for anyone seeking a serious\n          traditional reading.</p>'
        
        # Depending on how exact the string is in memory vs file, a safer replace might be needed. 
        # But we'll try direct replace or segment replace.
        # Actually inject after the first section-subtitle
        
        target_marker = '<p class="section-subtitle">A natal chart (also called a traditional birth chart) is a map of the sky for the exact moment\n          and location of birth. Traditional astrology treats it as a structured record of life circumstances, talents,\n          and challenges—not a vague personality test.</p>'
        
        if target_marker in html:
            html = html.replace(target_marker, page['body'])
            
        # Update Canonical
        html = html.replace(
            '<link href="https://traditional-astrology.com/natal-charts.html" rel="canonical"/>',
            f'<link href="https://traditional-astrology.com/{page["filename"]}" rel="canonical"/>'
        )
        
        # Write file
        out_path = os.path.join(STATIC_DIR, page['filename'])
        with open(out_path, "w", encoding="utf-8") as out:
            out.write(html)
        print(f"Generated: {page['filename']}")

if __name__ == "__main__":
    build_pages()
