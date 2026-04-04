import os

def fix_double_replacement(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # The bad output is: repr(, repr(e), exc_info=True), exc_info=True)
    # The correct target is: repr(e), exc_info=True)
    bad_string = "repr(, repr(e), exc_info=True), exc_info=True)"
    good_string = "repr(e), exc_info=True)"
    
    if bad_string in content:
        new_content = content.replace(bad_string, good_string)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed double-replacement in {filepath}")

def main():
    target_dirs = ["src/engine", "src/api", "src/services", "src/core"]
    for d in target_dirs:
        for root, dirs, files in os.walk(d):
            for f in files:
                if f.endswith(".py"):
                    fix_double_replacement(os.path.join(root, f))
                
if __name__ == "__main__":
    main()
