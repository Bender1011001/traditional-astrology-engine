import os
import shutil
import re

INDEX_PATH = r'e:\code.projects\astrology\src\static\index.html'
BASIC_JS_PATH = r'e:\code.projects\astrology\src\static\basic.js'
# Correct source path from prev tool output
SOURCE_IMG = r'C:/Users/admin/.gemini/antigravity/brain/4c2669c6-3d33-4a8f-aa8d-5e9d23be9525/pdf_report_mockup_1769713972919.png'
DEST_IMG = r'e:\code.projects\astrology\src\static\pdf_preview.png'

def copy_image():
    try:
        shutil.copy(SOURCE_IMG, DEST_IMG)
        print("Image copied successfully.")
    except Exception as e:
        print(f"Image copy failed: {e}. You might need to move it manually.")

def update_index_html():
    if not os.path.exists(INDEX_PATH):
        print("Index path not found")
        return

    with open(INDEX_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Insert Testimonials (Step 6)
    testimonials_html = '''
        <!-- Testimonials -->
        <section class="testimonials-section">
            <h2 class="section-title">WHAT USERS SAY</h2>
            <div class="testimonial-grid">
                <div class="testimonial-card">
                    <p class="testimonial-quote">"The level of detail is startling. It saw things about my career I'd never verbalized. It felt less like a horoscope and more like a blueprint."</p>
                    <p class="testimonial-author">Sarah J. - London</p>
                </div>
                <div class="testimonial-card">
                    <p class="testimonial-quote">"Finally, astrology that doesn't feel like a fortune cookie. The logic is transparent, and the 'Forensic' approach explains the 'why' behind the predictions."</p>
                    <p class="testimonial-author">Michael R. - Austin</p>
                </div>
                <div class="testimonial-card">
                    <p class="testimonial-quote">"The Annual Profections feature changed how I plan my year. Knowing my Time Lord gives me a concrete focus strategy. Indispensable tool."</p>
                    <p class="testimonial-author">Elena K. - Toronto</p>
                </div>
            </div>
        </section>
    '''
    
    if "testimonials-section" not in content:
        content = content.replace('<section class="comparison-section">', testimonials_html + '\n<section class="comparison-section">')

    # 2. Update Email Modal with Image (Step 16)
    email_modal_pattern = r'<p style="text-align: center; margin-bottom: 1.5rem;">Enter your email to receive a PDF copy of your free\s*reading results.</p>'
    
    new_email_content = '''
            <div style="text-align: center; margin-bottom: 1.5rem;">
                <img src="pdf_preview.png" alt="PDF Report Preview" style="max-width: 100%; border-radius: 8px; border: 1px solid var(--gold); margin-bottom: 1rem; box-shadow: var(--shadow-soft);">
                <p>Enter your email to receive a secure PDF copy of your free reading results.</p>
            </div>
    '''
    
    content = re.sub(email_modal_pattern, new_email_content, content, flags=re.DOTALL)
    
    # Step 20: "What happens next?" guide
    what_next_html = '''
            <div style="text-align: left; margin-top: 1.5rem; border-top: 1px solid var(--glass-border); padding-top: 1rem;">
                <strong style="color: var(--gold); font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px;">What Happens Next:</strong>
                <ol style="margin-top: 0.5rem; padding-left: 1.2rem; color: var(--text-muted); font-size: 0.85rem; line-height: 1.6;">
                    <li>You'll receive an instant confirmation email.</li>
                    <li>Your PDF report (approx. 15 pages) will be attached.</li>
                    <li>Check your specific "Spam" folder if not received in 2 mins.</li>
                </ol>
            </div>
    '''
    
    privacy_p = r'<p style="font-size: 0.8rem; text-align: center; margin-top: 1rem; opacity: 0.7;">We respect your privacy.'
    content = content.replace('<p style="font-size: 0.8rem; text-align: center; margin-top: 1rem; opacity: 0.7;">We respect your privacy.', what_next_html + '\n<p style="font-size: 0.8rem; text-align: center; margin-top: 1rem; opacity: 0.7;">We respect your privacy.')

    with open(INDEX_PATH, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Index HTML updated.")

def update_basic_js():
    if not os.path.exists(BASIC_JS_PATH):
        print("JS path not found")
        return

    with open(BASIC_JS_PATH, 'r', encoding='utf-8') as f:
        js_content = f.read()

    glossary_code = r'''

// --- GLOSSARY TOOLTIPS ---
const GLOSSARY_TERMS = {
    "forensic": "An approach that treats the chart as a crime scene, looking for concrete evidence (dignities, receptions) rather than abstract feelings.",
    "delineation": "The act of interpreting a chart to determine the specific meaning of planets, signs, and houses.",
    "mundane": "Relating to worldly, earthly events rather than spiritual or psychological states. The 'real world' impact.",
    "profections": "A timing technique that advances the Ascendant one sign per year to identify the 'Time Lord' for that age.",
    "firdaria": "A Persian planetary period system where each planet rules a set number of years of life.",
    "zodiacal releasing": "A Hellenistic timing technique using the Lots of Spirit/Fortune to map peak periods of career and health.",
    "lots": "Mathematical points derived from planetary positions (e.g., Lot of Fortune = Asc + Moon - Sun). Also called Arabic Parts.",
    "essential dignities": "The strength of a planet based on its zodiacal position (Rulership, Exaltation, Triplicity, Term, Face).",
    "sect": "The distinction between Day and Night charts, determining which planets are most constructive or difficult.",
    "hyleg": "The Giver of Life; a planet or point signifying vitality and physical constitution.",
    "alcocoden": "The Giver of Years; the planet that determines the potential lifespan based on its relationship to the Hyleg.",
    "almuten": "The logical 'Winner' or 'Ruler' of a specific degree or chart topic based on weighted scoring.",
    "syzygy": "The alignment of the Sun, Earth, and Moon; specifically New Moons and Full Moons.",
    "cazimi": "From the Arabic for 'in the heart of the Sun'. A planet within 17 minutes of the Sun, considered immensely powerful.",
    "combust": "A planet burned by the Sun (within 8 degrees), weakening its ability to act externally.",
    "triplicity": "A group of three signs of the same element (Fire, Earth, Air, Water) and their rulers."
};

function injectGlossaryTooltips() {
    const targets = document.querySelectorAll('.basic-reading-body, .method-body, .sample-content');
    
    targets.forEach(el => {
        const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT, null, false);
        let node;
        const nodesToReplace = [];
        
        while(node = walker.nextNode()) {
            if (node.parentElement.tagName === 'SCRIPT' || node.parentElement.tagName === 'STYLE' || node.parentElement.classList.contains('glossary-term')) continue;
            
            let text = node.nodeValue;
            const terms = Object.keys(GLOSSARY_TERMS).join('|');
            const regex = new RegExp(`\\b(${terms})\\b`, 'gi');
            
            if (regex.test(text)) {
                nodesToReplace.push(node);
            }
        }
        
        nodesToReplace.forEach(node => {
            const wrapper = document.createElement('span');
            const text = node.nodeValue;
            const terms = Object.keys(GLOSSARY_TERMS).join('|');
            const regex = new RegExp(`(\\b(?:${terms})\\b)`, 'gi');
            
            const parts = text.split(regex);
            
            parts.forEach(part => {
                const lower = part.toLowerCase();
                if (GLOSSARY_TERMS[lower]) {
                    const span = document.createElement('span');
                    span.className = 'glossary-term';
                    span.textContent = part;
                    
                    const tip = document.createElement('span');
                    tip.className = 'glossary-tooltip-popup';
                    tip.textContent = GLOSSARY_TERMS[lower];
                    span.appendChild(tip);
                    
                    wrapper.appendChild(span);
                } else {
                    wrapper.appendChild(document.createTextNode(part));
                }
            });
            
            node.parentNode.replaceChild(wrapper, node);
        });
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((m) => {
            if (m.addedNodes.length) {
                injectGlossaryTooltips();
            }
        });
    });
    
    const readingBody = document.getElementById('basicReadingBody');
    if (readingBody) observer.observe(readingBody, { childList: true, subtree: true });
    
    injectGlossaryTooltips();
});
'''
    if "GLOSSARY_TERMS" not in js_content:
        js_content += glossary_code

    search_str = 'if (!email || !lastChartRequest) return;'
    replace_str = 'if (!lastChartRequest) return;\n        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;\n        if (!email || !emailRegex.test(email)) {\n            emailStatus.textContent = "Please enter a valid email address.";\n            emailStatus.style.color = "var(--danger)";\n            return;\n        }\n'
    
    # Simple check to avoid double replace
    if "emailRegex" not in js_content:
        js_content = js_content.replace(search_str, replace_str)

    with open(BASIC_JS_PATH, 'w', encoding='utf-8') as f:
        f.write(js_content)
    print("Basic JS updated.")

def main():
    copy_image()
    update_index_html()
    update_basic_js()

if __name__ == "__main__":
    main()
