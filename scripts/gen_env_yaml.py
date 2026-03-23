"""Generate a YAML env vars file from .env for Cloud Run deployment."""
import os
import yaml

def main():
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    out_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "env.yaml")

    env_vars = {}
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                value = value[1:-1]
            if key:
                env_vars[key] = value

    with open(out_path, "w", encoding="utf-8") as f:
        yaml.dump(env_vars, f, default_flow_style=False)

    print(f"Wrote {len(env_vars)} env vars to {out_path}")


if __name__ == "__main__":
    main()
