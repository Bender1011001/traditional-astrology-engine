import re
import os

HTML_PATH = r'e:\code.projects\astrology\src\static\methodology.html'
BACKUP_PATH = r'e:\code.projects\astrology\src\static\methodology.html.bak'

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def categorize_source(text):
    text_lower = text.lower()
    
    # Core Canon Detection (for distinct highlighting within sections if needed, though we have a separate section)
    # Categorization buckets
    if any(k in text_lower for k in ['ptolemy', 'valens', 'dorotheus', 'firmicus', 'manilius', 'rhetorius', 'paulus', 'hephaistion', 'antiochus', 'thrasyllus']):
        return 'Primary Classical Sources'
    
    if any(k in text_lower for k in ['lilly', 'bonatti', 'biruni', 'ma\'shar', 'mashar', 'qabisi', 'sahl', 'masha\'allah', 'culpeper', 'morin', 'regiomontanus', 'cardan', 'ficino', 'agrippa', 'alkindi', 'abenragel']):
        return 'Medieval & Renaissance Texts'
        
    if any(k in text_lower for k in ['medical', 'disease', 'illness', 'health', 'decumbiture', 'temperament', 'humors', 'galen', 'hippocrates', 'iatromathematical']):
        return 'Medical Astrology Sources'
        
    if any(k in text_lower for k in ['profection', 'firdaria', 'zodiacal releasing', 'solar return', 'direction', 'progression', 'dasha', 'period', 'time lord', 'chronocrator', 'timing']):
        return 'Timing Techniques References'
        
    if any(k in text_lower for k in ['project hindsight', 'brill', 'dykes', 'hand', 'houlding', 'schmidt', 'brennan', 'watson', 'george', 'holden', 'history', 'transmission', 'academic', 'research']):
        return 'Modern Scholarship & Transmission History'
        
    if any(k in text_lower for k in ['reddit', 'blog', 'youtube', 'podcast', 'wikipedia', 'scribd', 'cafeastrology', 'astro.com', 'astro-seek', 'twitter', 'medium', 'substack', 'vlog', 'transcript']):
        return 'Contemporary Discussions & Verification'

    return 'Modern Scholarship & Transmission History' # Default fallback for academic looking titles, or Verification if looks generic

def bold_primary_names(text):
    primaries = [
        "Ptolemy", "Claudius Ptolemy", "Vettius Valens", "Valens", "Dorotheus", "Firmicus Maternus", "Firmicus",
        "William Lilly", "Lilly", "Guido Bonatti", "Bonatti", "Al-Biruni", "Abu Ma'shar", "Sahl", "Masha'allah",
        "Culpeper", "Morinus", "Morin", "Paulus Alexandrinus", "Rhetorius", "Hephaistion", "Manilius", "Antiochus"
    ]
    for p in primaries:
        # Simple replace avoiding double bolding if run multiple times (though we run once on raw text)
        # Use regex to match whole words/phrases to avoid partial matches inside links?
        # For simplicity, string replace is risky if inside attributes. 
        # But this is just text content of LI usually.
        # We will apply this only to the content of the LI, not the whole HTML.
        pattern = re.compile(re.escape(p), re.IGNORECASE)
        text = pattern.sub(f"<strong>{p}</strong>", text)
    return text

def main():
    if not os.path.exists(HTML_PATH):
        print(f"File not found: {HTML_PATH}")
        return

    content = read_file(HTML_PATH)
    
    # Backup
    write_file(BACKUP_PATH, content)

    # 1. Extract List Items
    list_match = re.search(r'<ol class="sources-list">(.*?)</ol>', content, re.DOTALL)
    if not list_match:
        print("Could not find sources-list")
        return
    
    raw_list_content = list_match.group(1)
    # Split by </li> to get items. 
    # Valid HTML splitting by <li> might be messy with newlines.
    # regex findall might be better.
    items = re.findall(r'<li>(.*?)</li>', raw_list_content, re.DOTALL)
    
    categories = {
        'Primary Classical Sources': [],
        'Medieval & Renaissance Texts': [],
        'Medical Astrology Sources': [],
        'Timing Techniques References': [],
        'Modern Scholarship & Transmission History': [],
        'Contemporary Discussions & Verification': []
    }
    
    for item in items:
        # Clean item
        item_text = item.strip()
        cat = categorize_source(item_text)
        
        # Apply Bolding (Step 3)
        # We only bold if it's NOT a link title maybe? Or just bold it generally.
        # User said "Bold all primary source names... Make them stand out from URLs"
        item_final = bold_primary_names(item_text)
        
        categories[cat].append(item_final)

    # 2. Build New Accordion HTML
    accordion_html = '<div class="sources-accordion">\n'
    
    # Ensure "Primary Classical Sources" is open by default
    for cat_name in ['Primary Classical Sources', 'Medieval & Renaissance Texts', 'Medical Astrology Sources', 'Timing Techniques References', 'Modern Scholarship & Transmission History', 'Contemporary Discussions & Verification']:
        items_list = categories[cat_name]
        is_open = ' open' if cat_name == 'Primary Classical Sources' else ''
        
        # Sort items? Maybe keep original order to preserve some logic? 
        # Original order was messy. Alphabetical might be better, or just as is. 
        # Let's keep existing order.
        
        accordion_html += f'''
        <details class="source-category"{is_open}>
            <summary>{cat_name} ({len(items_list)})</summary>
            <ol class="sources-list category-list">
        '''
        for it in items_list:
            accordion_html += f'        <li>{it}</li>\n'
        accordion_html += '''    </ol>
        </details>
        '''
    accordion_html += '</div>'

    # 3. Core Canon Section (Step 2 & 11)
    core_canon_html = '''
    <div class="core-canon-section">
        <h2 class="section-title">CORE CANON & ESSENTIAL TEXTS</h2>
        <div class="method-body">
            <p>While hundreds of fragments inform the engine, the following texts constitute the "spine" of the logic. These sources provide the primary algorithms for dignity, rulership, and predictive timing.</p>
            <div class="core-canon-grid">
                <div class="canon-card">
                    <h3>Ptolemy's Tetrabiblos</h3>
                    <span class="canon-date">2nd Century CE</span>
                    <p>Foundational text for Western astrology, particularly essential dignities, planetary meanings, and mundane predictions.</p>
                </div>
                <div class="canon-card">
                    <h3>Vettius Valens' Anthology</h3>
                    <span class="canon-date">2nd Century CE</span>
                    <p>The practitioner's manual. Essential for timing techniques (Profections, Zodiacal Releasing) and concrete interpretive rules.</p>
                </div>
                <div class="canon-card">
                    <h3>William Lilly's Christian Astrology</h3>
                    <span class="canon-date">1647</span>
                    <p>The definitive guide to Horary and Renaissance delineation. Provides the core scoring logic for planetary strength (The Weighted Scores).</p>
                </div>
                <div class="canon-card">
                    <h3>Dorotheus of Sidon's Carmen Astrologicum</h3>
                    <span class="canon-date">1st Century CE</span>
                    <p>The primary source for Triplicity Lords and electional logic. Defines the structure of the "Tripod of Life".</p>
                </div>
                <div class="canon-card">
                    <h3>Guido Bonatti's Liber Astronomiae</h3>
                    <span class="canon-date">13th Century</span>
                    <p>Synthesized Arabic and Latin traditions. His 146 Considerations form the basis of the engine's "Forensic Warnings".</p>
                </div>
                <div class="canon-card">
                    <h3>Firmicus Maternus' Mathesis</h3>
                    <span class="canon-date">4th Century CE</span>
                    <p>Provides extensive delineations for planets in houses and specific configurations, used for the "Destiny" engine.</p>
                </div>
                <div class="canon-card">
                    <h3>Abu Ma'shar's Great Introduction</h3>
                    <span class="canon-date">9th Century</span>
                    <p>Crucial for understanding the Solar Revolution and the intersection of Aristotelian physics with astrology.</p>
                </div>
                <div class="canon-card">
                    <h3>Al-Biruni's Instruction in the Elements</h3>
                    <span class="canon-date">11th Century</span>
                    <p>The master technical reference for definitions, creating the standard taxonomies used for calculations.</p>
                </div>
                <div class="canon-card">
                    <h3>Rhetorius the Egyptian</h3>
                    <span class="canon-date">6th/7th Century</span>
                    <p>Preserves earlier definitions of Lots and house meanings that were otherwise lost; key for the "Lots" module.</p>
                </div>
                <div class="canon-card">
                    <h3>Nicholas Culpeper's English Physician</h3>
                    <span class="canon-date">1652</span>
                    <p>Integrates astrological judgment with herbal medicine. The basis for the medical/humoral output layer.</p>
                </div>
            </div>
        </div>
    </div>
    '''

    # 4. About Developer Section (Step 4)
    about_dev_html = '''
    <section class="about-developer-section">
        <h2 class="section-title">ABOUT THE DEVELOPER</h2>
        <div class="method-body about-body">
            <div class="about-text">
                <p>Hello, I built this engine to answer a single question: <em>"Can we compute destiny?"</em></p>
                <p>My background bridges <strong>Computer Science</strong> and <strong>Traditional Astrology</strong>. After years of studying the classical texts—struggling to manually calculate profections, primary directions, and dignities for every chart—I realized that the "Art" of astrology is built upon a rigid, almost algorithmic "Science" of rules.</p>
                <p>I have studied under the lineages of Project Hindsight and the modern traditional revival. My goal with <strong>Codex Caelestis</strong> is not to replace the astrologer, but to provide a flaw-free calculation substrate that respects the immense complexity of the tradition.</p>
                <p>Verify the code yourself. The rule engine is transparent.</p>
                <div class="about-links">
                    <a href="https://github.com/Bender1011001/astrology" target="_blank" class="help-btn">VIEW ON GITHUB</a>
                </div>
            </div>
        </div>
    </section>
    '''

    # 5. Add Anchor Links Check (Step 13)
    anchor_nav = '''
    <nav class="toc-nav">
        <a href="#why-this">Why This Approach</a>
        <a href="#core-principles">Core Principles</a>
        <a href="#core-canon">Core Canon</a>
        <a href="#full-bibliography">Full Method</a>
        <a href="#about-dev">About Developer</a>
    </nav>
    '''

    # --- Applying Changes ---

    # 1. Add Anchor Nav after finding the Header Title or Subtitle
    content = content.replace('<nav class="header-actions" aria-label="Primary">', anchor_nav + '\n<nav class="header-actions" aria-label="Primary">')

    # 2. Change Steps 8 Heading
    content = content.replace('>WHY THIS APPROACH<', 'id="why-this">WHY THIS APPROACH<') # add ID
    content = content.replace('>WHAT MAKES IT "BEST"<', '>WHAT MAKES IT DIFFERENT<')
    content = content.replace('>WHAT MAKES IT DIFFERENT<', 'id="core-principles">WHAT MAKES IT DIFFERENT<') # Add ID

    # 3. Add Core Canon + Accordion List
    # We replace the entire text block of "SOURCES & BIBLIOGRAPHY" section
    # Find start of section
    
    # Move Disclaimers to Footer (Step 10)
    # First, find the disclaimers section and extract/remove it
    disclaimer_pattern = r'<h2 class="section-title">SCOPE & DISCLAIMERS</h2>\s*<div class="method-body">.*?</div>'
    disclaimer_match = re.search(disclaimer_pattern, content, re.DOTALL)
    disclaimer_text = ""
    if disclaimer_match:
        # We replace it with nothing or a small note? Step 10 says "Move... to footer... Keep just one sentence"
        short_disclaimer = '''
        <h2 class="section-title">SCOPE</h2>
        <div class="method-body">
            <p>The engine is designed for traditional delineation and timing. This is an educational tool for studying traditional astrological techniques, not medical or psychological advice.</p>
        </div>
        '''
        content = content.replace(disclaimer_match.group(0), short_disclaimer)

    # Now Replace Bibliography
    # Find existing header and OL
    # We replace from <h2 class="section-title">SOURCES & BIBLIOGRAPHY</h2> down to the end of the </ol>
    # Note: the </ol> is inside a div.
    
    start_marker = '<h2 class="section-title">SOURCES & BIBLIOGRAPHY</h2>'
    # Find the closing </ol> and the closing </div> of that section
    # The OL is inside <div class="method-body">.
    
    if start_marker in content:
        # Construct new section content
        new_bib_section = f'''
        <h2 class="section-title" id="core-canon">CORE CANON</h2>
        {core_canon_html}

        <h2 class="section-title" id="full-bibliography">FULL BIBLIOGRAPHY</h2>
        <div class="method-body">
            <p>The complete index of 492 sources ingested into the engine, categorized by tradition and usage.</p>
            {accordion_html}
        </div>
        '''
        
        # Replace the old section. 
        # CAUTION: Regex replace for the large block.
        # The block starts with the H2, then <div class="method-body">, then <p>, then <ol>, then </div>
        # We can find the end of the </section> containing it?
        # The file has <section class="basic-view"> wrapping ALL of this.
        # The specific block is just one part.
        # Let's target the exact string creation we parsed earlier.
        
        # We parsed `list_match` earlier which was just the `<ol>`.
        # We need to replace the H2, the P, and the OL.
        
        # Let's find the span from H2 to </ol> </div>
        # It's: <h2...>...</h2>\n<div class="method-body">\n<p>...</p>\n<ol>...</ol>\n</div>
        
        # We can try to replace `list_match.group(0)` (the OL) with the Accordion HTML, 
        # AND insert the Core Canon Before the H2.
        
        # Let's do it safe:
        # 1. Replace the OL with the Accordion HTML.
        content = content.replace(list_match.group(0), accordion_html)
        
        # 2. Add Core Canon BEFORE the SOURCES header.
        content = content.replace(start_marker, core_canon_html + '\n' + start_marker)
        
    # 4. Insert About Developer at the end of the 'basic-card' but inside it? Or after?
    # Step 4 says "Add... to methodology page".
    # Putting it after Full Bibliography seems right.
    # Included ID "about-dev" in anchor, so adding id here.
    about_dev_html = about_dev_html.replace('class="about-developer-section"', 'class="about-developer-section" id="about-dev"')
    
    # Find the closing </div> of the basic-card
    # It ends before </section>
    content = content.replace('</div>\n        </section>', about_dev_html + '\n</div>\n        </section>')

    # 5. Comparison Table (Step 15)
    # "Implement a comparison table somewhere visible". 
    # Let's put it in "Why This Approach" or "What Makes It Different".
    # "What Makes It Different" (formerly Best) seems appropriate.
    
    comp_table = '''
    <div class="comparison-container">
        <h3 class="comparison-title">TRADITION VS. MODERNITY</h3>
        <div class="comparison-table-wrapper">
            <table class="comparison-table">
                <thead>
                    <tr>
                        <th>Feature</th>
                        <th class="col-trad">Codex Caelestis (Traditional)</th>
                        <th class="col-mod">Modern Psychological</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>Core Philosophy</strong></td>
                        <td>Deterministic, External, Fate-oriented</td>
                        <td>Archetypal, Internal, Choice-oriented</td>
                    </tr>
                    <tr>
                        <td><strong>Primary Technique</strong></td>
                        <td>Essential Dignity, Sect, House Ruling & Strength</td>
                        <td>Aspects, Signs, Outer Planets</td>
                    </tr>
                    <tr>
                        <td><strong>Planets Used</strong></td>
                        <td>7 Visible Planets (Septener)</td>
                        <td>10+ Planets (Uranus, Neptune, Pluto)</td>
                    </tr>
                    <tr>
                        <td><strong>House System</strong></td>
                        <td>Whole Sign (Principal)</td>
                        <td>Placidus / Quadrant</td>
                    </tr>
                    <tr>
                        <td><strong>Outcome Focus</strong></td>
                        <td>Concrete Events & Objective Circumstances</td>
                        <td>Psychological Drives & Personality</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
    '''
    
    # Insert this after the UL in "WHAT MAKES IT DIFFERENT"
    # The UL is <ul class="method-list">...</ul>
    # We find that UL and append.
    ul_pattern = r'<ul class="method-list">.*?</ul>'
    ul_match = re.search(ul_pattern, content, re.DOTALL)
    if ul_match:
         content = content.replace(ul_match.group(0), ul_match.group(0) + '\n' + comp_table)

    # 6. Sample Rule Chain (Step 9)
    # "Create a Sample Rule Chain... diagram... on methodology page"
    # Insert in "Traceable outputs" bullet or near it?
    # Or maybe just after the list, before Scope.
    
    rule_chain_html = '''
    <div class="rule-chain-visual">
        <h3 class="comparison-title">LOGIC VISUALIZED</h3>
        <div class="chain-flow">
            <div class="chain-step">
                <span class="chain-icon">♂</span>
                <span class="chain-label">Mars in Aries</span>
                <span class="chain-score">+5 (Rulership)</span>
            </div>
            <div class="chain-arrow">→</div>
            <div class="chain-step">
                <span class="chain-icon">X</span>
                <span class="chain-label">10th House</span>
                <span class="chain-action">Angular (Active)</span>
            </div>
            <div class="chain-arrow">→</div>
            <div class="chain-step final">
                <span class="chain-result">"Strong drive toward competitive leadership"</span>
            </div>
        </div>
    </div>
    '''
    
    # Append this to the "WHAT MAKES IT DIFFERENT" section as well, maybe before the table? 
    # Or after the table. Let's put it after the UL, before the table.
    
    # Re-doing the replace logic for UL to include both
    # Actually, let's keep it simple. Insert 'rule_chain_html' before 'comp_table'.
    # I already replaced UL with UL + Table.
    # Now I can replace "comparison-container" with "rule-chain... \n comparison-container"
    content = content.replace('<div class="comparison-container">', rule_chain_html + '\n<div class="comparison-container">')

    write_file(HTML_PATH, content)
    print("Methodology page refactored successfully.")

if __name__ == "__main__":
    main()
