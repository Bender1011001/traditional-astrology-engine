"""Build and deploy the astrology engine to Google Cloud Run.

Usage:
    python scripts/deploy_cloudrun.py [--build-only] [--deploy-only]

Requires:
    - gcloud CLI authenticated
    - Project set to astrology-engine-prod
    - .env file with required environment variables
"""
import subprocess
import sys
import os

PROJECT_ID = "astrology-engine-prod"
REGION = "us-central1"
SERVICE_NAME = "astrology-engine"
IMAGE = f"gcr.io/{PROJECT_ID}/{SERVICE_NAME}"


def run(cmd: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command and print output."""
    print(f"\n{'='*60}")
    print(f"  {cmd}")
    print(f"{'='*60}")
    result = subprocess.run(
        cmd, shell=True, capture_output=False, text=True,
        env={**os.environ, "CLOUDSDK_CORE_DISABLE_PROMPTS": "1"},
    )
    if check and result.returncode != 0:
        print(f"FAILED with exit code {result.returncode}")
        sys.exit(1)
    return result


def load_env_vars() -> dict:
    """Load environment variables from .env file."""
    env_vars = {}
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if not os.path.exists(env_path):
        print(f"ERROR: .env file not found at {env_path}")
        sys.exit(1)

    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            # Remove surrounding quotes if present
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                value = value[1:-1]
            if key:
                env_vars[key] = value
    return env_vars


def build_env_flag(env_vars: dict) -> str:
    """Build the --set-env-vars flag for gcloud run deploy."""
    pairs = []
    for key, value in env_vars.items():
        # Escape commas in values (gcloud uses comma as delimiter)
        safe_value = value.replace(",", "\\,")
        pairs.append(f"{key}={safe_value}")
    return ",".join(pairs)


def main():
    args = sys.argv[1:]
    build_only = "--build-only" in args
    deploy_only = "--deploy-only" in args

    print(f"Project: {PROJECT_ID}")
    print(f"Region:  {REGION}")
    print(f"Service: {SERVICE_NAME}")
    print(f"Image:   {IMAGE}")

    # Step 1: Build and push image via Cloud Build
    if not deploy_only:
        print("\n\n🔨 STEP 1: Building Docker image via Cloud Build...")
        run(f"gcloud builds submit --tag {IMAGE} --timeout=600")
        print("✅ Image built and pushed successfully.")

    # Step 2: Deploy to Cloud Run
    if not build_only:
        print("\n\n🚀 STEP 2: Deploying to Cloud Run...")
        env_vars = load_env_vars()
        print(f"   Loaded {len(env_vars)} environment variables from .env")

        env_flag = build_env_flag(env_vars)

        deploy_cmd = (
            f"gcloud run deploy {SERVICE_NAME} "
            f"--image {IMAGE} "
            f"--region {REGION} "
            f"--platform managed "
            f"--allow-unauthenticated "
            f"--port 8080 "
            f"--memory 512Mi "
            f"--cpu 1 "
            f"--min-instances 0 "
            f"--max-instances 3 "
            f"--timeout 300 "
            f'--set-env-vars "{env_flag}"'
        )
        run(deploy_cmd)
        print("✅ Deployed successfully!")

        # Get the service URL
        print("\n\n📡 Service URL:")
        run(f"gcloud run services describe {SERVICE_NAME} --region {REGION} --format 'value(status.url)'")

    print("\n\n✨ Deployment complete!")


if __name__ == "__main__":
    main()
