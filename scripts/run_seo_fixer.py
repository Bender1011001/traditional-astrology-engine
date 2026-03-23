import os
from bs4 import BeautifulSoup

target_files = [
    "techniques.html",
    "predictive-techniques.html",
    "planetary-periods.html",
    "natal-charts.html",
    "methodology.html",
    "lot-of-fortune.html",
    "hyleg-calculator.html",
    "houses.html",
    "faq.html",
    "aspects.html",
    "almuten-figuris.html",
    "about.html",
]

base_dir = r"E:\code.projects\astrology\src\static"

for file_name in target_files:
    file_path = os.path.join(base_dir, file_name)
    if not os.path.exists(file_path):
        continue
    
    with open(file_path, "r", encoding="utf-8") as f:
        html = f.read()
    
    soup = BeautifulSoup(html, "html.parser")
    
    # 1. Replace header-actions
    nav = soup.find("nav", class_="header-actions")
    if nav:
        nav.clear()
        
        a1 = soup.new_tag("a", href="/", style="background: linear-gradient(135deg, #c9a84c, #b8922f); color: #0a0a1a; font-weight: 700;", **{"class": "help-btn"})
        a1.string = "✦ Get Your Reading"
        
        a2 = soup.new_tag("a", href="/", **{"class": "help-btn"})
        a2.string = "Home"
        
        a3 = soup.new_tag("a", href="privacy.html", **{"class": "help-btn"})
        a3.string = "Privacy"
        
        nav.append("\n  ")
        nav.append(a1)
        nav.append("\n  ")
        nav.append(a2)
        nav.append("\n  ")
        nav.append(a3)
        nav.append("\n")

    # 2. Add sticky CTA bar
    if not soup.find(id="seoCTABar"):
        import textwrap
        cta_html = textwrap.dedent("""
            <div id="seoCTABar">
                <div style="position: fixed; top: 0; left: 0; right: 0; z-index: 9999; background: linear-gradient(135deg, #c9a84c, #b8922f); color: #0a0a1a; text-align: center; padding: 0.5rem 1rem; font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; font-size: 0.85rem; font-weight: 600;">
                    ✦ Want to discover YOUR chart? 
                    <a href="/#get-reading" style="color: #0a0a1a; text-decoration: underline; margin-left: 0.4rem;">
                        Get your full natal chart reading →
                    </a>
                </div>
            </div>
        """).strip()
        cta_soup = BeautifulSoup(cta_html, "html.parser")
        
        body = soup.find("body")
        if body:
            body.insert(0, cta_soup)
            
            current_style = body.get("style", "")
            if "padding-top" not in current_style:
                new_style = (current_style + "; padding-top: 36px").strip('; ')
                body["style"] = new_style

    # 3. Replace old footer branding
    footer_bottom = soup.find(class_="footer-bottom")
    if footer_bottom:
        footer_bottom.clear()
        p1 = soup.new_tag("p")
        p1.string = "© 2026 Traditional Astrology. All rights reserved."
        
        p2 = soup.new_tag("p", **{"class": "footer-disclaimer"})
        p2.string = "For entertainment, historical, and spiritual research purposes only. Not medical, legal, or financial advice."
        
        footer_bottom.append("\n  ")
        footer_bottom.append(p1)
        footer_bottom.append("\n  ")
        footer_bottom.append(p2)
        footer_bottom.append("\n")

    # 4 & 5. Replace links
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href in ["demo.html", "signup.html", "login.html"]:
            a["href"] = "/#get-reading"
            if "Trial" in a.text or "Demo" in a.text:
                a.string = "✦ Get Your Reading"
            if "Log" in a.text:
                a.string = "Get Reading"
        elif href in ["documentation.html", "api-guide.html", "blog.html"]:
            a["href"] = "/"

    # 6. Clean up B2B-era footer columns
    footer_cols = soup.find_all(class_="footer-col")
    for col in footer_cols:
        h3 = col.find("h3")
        if not h3:
            continue
        title = h3.text.strip()
        ul = col.find("ul")
        
        if title == "Contact":
            ul.clear()
            li1 = soup.new_tag("li")
            a1 = soup.new_tag("a", href="mailto:support@traditional-astrology.com")
            a1.string = "Support"
            li1.append(a1)
            
            li2 = soup.new_tag("li")
            a2 = soup.new_tag("a", href="mailto:bugs@traditional-astrology.com")
            a2.string = "Report a Bug"
            li2.append(a2)
            
            ul.append("\n    ")
            ul.append(li1)
            ul.append("\n    ")
            ul.append(li2)
            ul.append("\n  ")
            
        elif title == "Product":
            ul.clear()
            li1 = soup.new_tag("li")
            a1 = soup.new_tag("a", href="/#get-reading")
            a1.string = "Get a Reading"
            li1.append(a1)
            
            li2 = soup.new_tag("li")
            a2 = soup.new_tag("a", href="techniques.html")
            a2.string = "Techniques"
            li2.append(a2)
            
            li3 = soup.new_tag("li")
            a3 = soup.new_tag("a", href="index.html#pricing")
            a3.string = "Pricing"
            li3.append(a3)
            
            ul.append("\n    ")
            ul.append(li1)
            ul.append("\n    ")
            ul.append(li2)
            ul.append("\n    ")
            ul.append(li3)
            ul.append("\n  ")

    # Remove the seo-bridge script tag
    for script in soup.find_all("script", src=True):
        if "seo-bridge.js" in script["src"]:
            script.decompose()

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(str(soup))
    print(f"Processed {file_name}")

print("Done processing SEO static markup.")
