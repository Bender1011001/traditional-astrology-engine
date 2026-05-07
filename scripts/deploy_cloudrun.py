"""Build and deploy the astrology engine to Google Cloud Run.

Usage:
    python scripts/deploy_cloudrun.py [--build-only] [--deploy-only] [--run-tests]

Requires:
    - gcloud CLI authenticated
    - Project set to astrology-engine-prod
    - env.yaml with environment variables (generate via scripts/gen_env_yaml.py)
"""
import subprocess
import sys
import os
import time

PROJECT_ID = "astrology-engine-prod"
REGION = "us-central1"
SERVICE_NAME = "astrology-engine"
IMAGE = f"gcr.io/{PROJECT_ID}/{SERVICE_NAME}"
CLOUD_SQL_INSTANCE = "astrology-487423:us-central1:astrology-db"
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run(cmd: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command and print output."""
    print(f"\n{'='*60}")
    print(f"  {cmd}")
    print(f"{'='*60}")
    result = subprocess.run(
        cmd, shell=True, capture_output=False, text=True,
        cwd=ROOT_DIR,
        env={
            **os.environ,
            "CLOUDSDK_CORE_DISABLE_PROMPTS": "1",
            "CLOUDSDK_CORE_DISABLE_FILE_LOGGING": "1",
        },
    )
    if check and result.returncode != 0:
        print(f"FAILED with exit code {result.returncode}")
        sys.exit(1)
    return result


def ensure_env_yaml():
    """Ensure env.yaml exists, generating it from .env if needed."""
    env_yaml_path = os.path.join(ROOT_DIR, "env.yaml")
    env_path = os.path.join(ROOT_DIR, ".env")

    if os.path.exists(env_yaml_path):
        # Check if .env is newer than env.yaml
        if os.path.exists(env_path):
            env_mtime = os.path.getmtime(env_path)
            yaml_mtime = os.path.getmtime(env_yaml_path)
            if env_mtime > yaml_mtime:
                print("   .env is newer than env.yaml; regenerating...")
                run(f'python "{os.path.join(ROOT_DIR, "scripts", "gen_env_yaml.py")}"')
        return

    if not os.path.exists(env_path):
        print("ERROR: Neither env.yaml nor .env found. Cannot deploy.")
        sys.exit(1)

    print("   Generating env.yaml from .env...")
    run(f'python "{os.path.join(ROOT_DIR, "scripts", "gen_env_yaml.py")}"')


def main():
    args = sys.argv[1:]
    build_only = "--build-only" in args
    deploy_only = "--deploy-only" in args
    run_tests = "--run-tests" in args

    print("\nAstrology Engine Deployment")
    print(f"   Project: {PROJECT_ID}")
    print(f"   Region:  {REGION}")
    print(f"   Service: {SERVICE_NAME}")
    print(f"   Image:   {IMAGE}")

    # Step 0: Run tests (optional)
    if run_tests:
        print("\n\nSTEP 0: Running tests...")
        result = run("pytest src/tests/ -q --tb=short", check=False)
        if result.returncode != 0:
            print("Tests failed. Aborting deployment.")
            sys.exit(1)
        print("All tests passed.")

    # Step 1: Build and push image via Cloud Build
    if not deploy_only:
        print("\n\nSTEP 1: Building Docker image via Cloud Build...")
        start = time.time()
        run(f"gcloud builds submit --tag {IMAGE} --timeout=600 --project {PROJECT_ID}")
        elapsed = time.time() - start
        print(f"Image built and pushed in {elapsed:.0f}s.")

    # Step 2: Deploy to Cloud Run
    if not build_only:
        print("\n\nSTEP 2: Deploying to Cloud Run...")
        ensure_env_yaml()

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
            f"--add-cloudsql-instances {CLOUD_SQL_INSTANCE} "
            f"--env-vars-file env.yaml "
            f"--project {PROJECT_ID} "
            f"--quiet"
        )
        run(deploy_cmd)
        print("Deployed successfully!")

        # Get the service URL
        print("\n\nService URL:")
        run(f'gcloud run services describe {SERVICE_NAME} --region {REGION} --project {PROJECT_ID} --format="value(status.url)"', check=False)

    print("\n\nDeployment complete.")


if __name__ == "__main__":
    main()
