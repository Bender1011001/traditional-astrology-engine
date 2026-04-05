import os, glob, re

folder = r"e:\code.projects\astrology\src\static"
html_files = glob.glob(os.path.join(folder, "*.html"))

button_html = """
    <button class="mobile-menu-toggle" aria-label="Toggle menu" aria-expanded="false">
      <span class="hamburger-icon"></span>
    </button>
    <div class="nav-links">"""

script_html = """
  <script>
    document.addEventListener('DOMContentLoaded', function() {
      var toggles = document.querySelectorAll('.mobile-menu-toggle');
      toggles.forEach(function(toggle) {
        // Only attach if not already attached to prevent duplicates if script runs twice
        if (toggle.dataset.navAttached) return;
        toggle.dataset.navAttached = 'true';
        toggle.addEventListener('click', function() {
          var expanded = this.getAttribute('aria-expanded') === 'true';
          this.setAttribute('aria-expanded', !expanded);
          this.classList.toggle('active');
          var navLinks = this.nextElementSibling;
          if (navLinks && navLinks.classList.contains('nav-links')) {
            navLinks.classList.toggle('active');
          }
        });
      });
    });
  </script>
</body>"""

for f in html_files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Check if button already injected avoiding duplication
    if 'class="mobile-menu-toggle"' not in content:
        # replace the generic nav-links
        content = re.sub(r'(\s*)<div class="nav-links">', r'\1' + button_html.strip(), content)
        
    # Check if script already injected avoiding duplication
    if 'mobile-menu-toggle' in script_html and 'var toggles = document' not in content:
        content = content.replace('</body>', script_html)
        
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)
