import os
import re

directory = r'e:\code.projects\astrology\src\static'
new_version = '20260129polish'

files_updated = []

for filename in os.listdir(directory):
    if filename.endswith('.html'):
        filepath = os.path.join(directory, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Regex to replace version strings
        # Matches style.css?v=ANYTHING
        new_content = re.sub(r'style\.css\?v=[a-zA-Z0-9]+', f'style.css?v={new_version}', content)
        # Matches basic.js?v=ANYTHING
        new_content = re.sub(r'basic\.js\?v=[a-zA-Z0-9]+', f'basic.js?v={new_version}', new_content)
        # Matches script.js?v=ANYTHING
        new_content = re.sub(r'script\.js\?v=[a-zA-Z0-9]+', f'script.js?v={new_version}', new_content)
        
        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            files_updated.append(filename)

print(f"Updated {len(files_updated)} files: {', '.join(files_updated)}")
