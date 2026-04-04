import os
import re

def fix_stragglers(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern: logger.(error|warning|debug)("some string... %s", e)
    # Target: logger.($1)("some string... %s", repr(e), exc_info=True)
    def replacer(match):
        logger_call = match.group(0)
        if "exc_info" in logger_call:
             return logger_call
             
        # Find the `, e)` and replace it
        new_call = re.sub(r'([,\s]+)e\s*\)', r'\1repr(e), exc_info=True)', logger_call)
        return new_call

    pattern = re.compile(r"logger\.(?:error|warning|debug)\(\s*\"[^\"]*%s[^\"]*\"\s*,\s*e\s*\)")
    new_content = pattern.sub(replacer, content)
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed stragglers in {filepath}")

def main():
    target_dirs = ["src/middleware", "src/scripts", "src/engine", "src/database", "src/api"]
    for d in target_dirs:
        for root, dirs, files in os.walk(d):
            for f in files:
                if f.endswith(".py"):
                    fix_stragglers(os.path.join(root, f))
                
if __name__ == "__main__":
    main()
