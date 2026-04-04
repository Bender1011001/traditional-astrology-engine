import os
import re

def fix_except_blocks(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find except Exception as e:
    # and then logger.debug/error/warning(..., e)
    # Change to logger... (..., repr(e), exc_info=True)
    
    # We will use regex to find logger calls right after except Exception as e:
    # Pattern: capture the logger line
    def replacer(match):
        logger_call = match.group(1)
        # If it already has exc_info, skip
        if "exc_info" in logger_call:
            return match.group(0)
            
        # Replace the last `e)` or `, e)` with `, repr(e), exc_info=True)`
        # This is a bit tricky, but usually it looks like `logger.warning("msg: %s", e)`
        new_call = re.sub(r'([,\s]*e)(\s*\))', r', repr(e), exc_info=True)', logger_call)
        
        # If it was just changing a debug to a warning
        if "logger.debug" in new_call:
            new_call = new_call.replace("logger.debug", "logger.warning")
            
        return "except Exception as e:\n" + new_call

    # match except Exception as e: followed by spaces and a logger line
    pattern = re.compile(r"except Exception as e:\n([ \t]+logger\.(?:debug|warning|error)\([^)]+\))")
    
    new_content = pattern.sub(replacer, content)
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed {filepath}")

def main():
    target_dirs = ["src/engine", "src/api", "src/services", "src/core"]
    for d in target_dirs:
        for root, dirs, files in os.walk(d):
            for f in files:
                if f.endswith(".py"):
                    fix_except_blocks(os.path.join(root, f))
                
if __name__ == "__main__":
    main()
