import glob, re

for f in glob.glob(r"e:\code.projects\astrology\src\static\*.html"):
    with open(f, "r", encoding="utf-8") as fh:
        content = fh.read()
    content = re.sub(r'style\.css\?v=[^"\']*', 'style.css?v=mobilenav2', content)
    with open(f, "w", encoding="utf-8") as fh:
        fh.write(content)
    print(f"Updated: {f}")

print("Done.")
