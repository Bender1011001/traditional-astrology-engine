"""Dump this engine's own vitality + forward-looking output for the owner's chart."""
import os
import sys
import json

sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "src"))

from src.scripts.generate_premium_report import generate_chart_data_object

d = generate_chart_data_object(
    "Andrew", "1996-08-13", "07:18", "Fairfield", "CA",
    latitude=38.2494, longitude=-122.0397,
)


def walk(obj, prefix="", depth=0, maxdepth=3):
    """Print the key tree so we can see what the engine actually produced."""
    if depth > maxdepth:
        return
    if isinstance(obj, dict):
        for k, v in obj.items():
            path = f"{prefix}.{k}" if prefix else k
            if isinstance(v, (dict, list)):
                n = len(v)
                print(f"{'  ' * depth}{path}  <{type(v).__name__} n={n}>")
                walk(v, path, depth + 1, maxdepth)
            else:
                s = str(v)
                if len(s) > 110:
                    s = s[:110] + "..."
                print(f"{'  ' * depth}{path} = {s}")
    elif isinstance(obj, list) and obj and depth <= maxdepth:
        walk(obj[0], prefix + "[0]", depth + 1, maxdepth)


print("=" * 100)
print("TOP-LEVEL KEYS")
print("=" * 100)
for k, v in d.items():
    print(f"  {k}  <{type(v).__name__}>", end="")
    if isinstance(v, (dict, list)):
        print(f" n={len(v)}")
    else:
        print()

an = d.get("analysis", {})
print()
print("=" * 100)
print("ANALYSIS KEYS")
print("=" * 100)
for k, v in an.items():
    print(f"  {k}  <{type(v).__name__}>", end="")
    if isinstance(v, (dict, list)):
        print(f" n={len(v)}")
    else:
        print()

# Vitality / hyleg / alcocoden — hunt for it wherever it lives
print()
print("=" * 100)
print("VITALITY / HYLEG / ALCOCODEN")
print("=" * 100)
found = False
for scope_name, scope in [("root", d), ("analysis", an)] + [
    (f"analysis.{k}", v) for k, v in an.items() if isinstance(v, dict)
]:
    for key in ("vitality", "hyleg", "alcocoden", "lifespan", "longevity"):
        if isinstance(scope, dict) and key in scope:
            found = True
            print(f"--- {scope_name}.{key} ---")
            print(json.dumps(scope[key], indent=2, default=str)[:4000])
            print()
if not found:
    print("(not present in report payload -- will call the engine directly)")
