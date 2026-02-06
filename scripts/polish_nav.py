import os
import re

STATIC_DIR = r'e:\code.projects\astrology\src\static'

def get_nav_html(current_page):
    # standard nav structure
    # Highlight current page if matches
    
    links = [
        ('HOME', 'index.html'),
        ('ABOUT', 'about.html'),
        ('METHODOLOGY', 'methodology.html'),
        ('RESOURCES', 'resources.html'),
        ('FAQ', 'faq.html'),
        ('LOG IN', 'login.html')
    ]
    
    # Special case for "advanced.html" which is usually separate or in a different spot?
    # In index.html it was: HOME | ABOUT | METHODOLOGY | SAMPLE | FAQ | LOGIN | THEME
    # In methodology.html it was: BASIC VERSION | ADVANCED TOOLS
    # In others it varies.
    
    # Let's standardize to a common set for most pages (About, Resources, FAQ, Login, Register)
    # Homepage might keep its special set (Sample, etc.)
    
    # Actually, the user request is "Polish". Inconsistent nav is unpolished.
    # Let's standardize the "Secondary" pages: About, Resources, FAQ, Login.
    # Homepage (index.html) usually has more CTA links.
    
    # Let's just ensure RESOURCES is in:
    # advanced.html
    # faq.html
    # login.html
    # register.html
    # about.html (already done via previous script but let's double check)
    
    return links

def update_nav_in_file(filename):
    path = os.path.join(STATIC_DIR, filename)
    if not os.path.exists(path):
        return

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to find the <nav class="header-actions"...> ... </nav>
    # We want to be careful not to overwrite custom navs like in Methodology if they are very specific.
    # But Resources link should be everywhere useful.
    
    # Strategy: Just check if "resources.html" is present. If not, insert it before FAQ or Login.
    
    if 'href="resources.html"' in content:
        print(f"Skipping {filename}: Resources link already exists.")
        return

    # Insertion point: before FAQ
    target = 'href="faq.html"'
    replacement = 'href="resources.html">RESOURCES</a>\n                    <a class="help-btn" href="faq.html"'
    
    if target in content:
        # Check if we are inside a nav? Assuming yes based on file structure
        # Use simple string replace
        new_content = content.replace(target, replacement)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {filename}: Added Resources link.")
    else:
        # If no FAQ link, try inserting before Login
        target_login = 'href="login.html"'
        replacement_login = 'href="resources.html">RESOURCES</a>\n                    <a class="help-btn" href="login.html"'
        
        if target_login in content:
            new_content = content.replace(target_login, replacement_login)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated {filename}: Added Resources link (before Login).")
        else:
            print(f"Skipped {filename}: Could not find insertion point.")

def main():
    files_to_check = ['faq.html', 'advanced.html', 'login.html', 'register.html', 'about.html']
    for val in files_to_check:
        update_nav_in_file(val)

if __name__ == "__main__":
    main()
