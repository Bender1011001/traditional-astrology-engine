import os
import sys

# Add src to path to use api's loader if needed, but let's try raw first
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

def load_dotenv_manual(path=".env"):
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ[k.strip()] = v.strip().strip('"').strip("'")

# Try loading from root .env
root_env = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv_manual(root_env)

key = os.environ.get("OPENROUTER_API_KEY")
if key:
    print(f"OPENROUTER_API_KEY found: {key[:4]}...{key[-4:]} (Length: {len(key)})")
else:
    print("OPENROUTER_API_KEY NOT FOUND")

print(f"Current CWD: {os.getcwd()}")
print(f"Env file path: {root_env}")
print(f"Env file exists: {os.path.exists(root_env)}")
