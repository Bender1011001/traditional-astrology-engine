import os, glob

folder = r"e:\code.projects\astrology\src\static"
html_files = glob.glob(os.path.join(folder, "*.html"))

for f in html_files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    content = content.replace("v=astro-v4", "v=astro-v5")
    content = content.replace("v=20260319progress", "v=flexnav1")
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)
