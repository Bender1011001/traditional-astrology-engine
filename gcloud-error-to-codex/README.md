# Google Cloud Error to Codex Bridge

Cloud Run webhook bridge for production alerts from `traditional-astrology.com`.

Flow:

```text
Google Cloud Logging / Error Reporting
-> Cloud Monitoring alert webhook
-> this Cloud Run service
-> GitHub issue in Bender1011001/astrology
-> codex_prod_error GitHub Actions workflow
-> PR guarded by CI, risk_gate, and automerge_safe
```

The bridge does not repair code directly and does not need repository contents access. It only creates or updates GitHub issues with the `production-error` and `codex` labels.
When Cloud Monitoring sends only incident metadata, the bridge queries Cloud Logging for the newest matching error entry in the incident time window and includes that payload in the GitHub issue.

## Environment

Required:

```text
GITHUB_TOKEN       Fine-grained GitHub token with Issues read/write on Bender1011001/astrology
GITHUB_OWNER       Bender1011001
GITHUB_REPO        astrology
WEBHOOK_TOKEN      Long random token used by the Cloud Monitoring webhook URL
```

Optional:

```text
SITE_NAME          traditional-astrology.com
CODEX_MENTION      @codex
LOG_LOOKUP_DISABLED false
LOG_LOOKUP_WINDOW_SECONDS 300
LOG_LOOKUP_ATTEMPTS 4
LOG_LOOKUP_DELAY_MILLIS 2000
PORT               8080
```

## Local Check

```bash
npm install
npm test
WEBHOOK_TOKEN=local-token GITHUB_TOKEN=local-github-token GITHUB_OWNER=Bender1011001 GITHUB_REPO=astrology npm start
```

Health:

```bash
curl http://127.0.0.1:8080/healthz
```

Manual alert test:

```bash
curl -X POST "http://127.0.0.1:8080/gcloud-error?token=local-token" \
  -H "Content-Type: application/json" \
  -d '{
    "incident": {
      "summary": "Test production error: cannot read property x of undefined",
      "policy_name": "production-errors",
      "condition_name": "severity-error",
      "severity": "ERROR",
      "started_at": "2026-05-11T00:00:00Z",
      "url": "https://console.cloud.google.com/logs/query;query=test",
      "resource": {
        "labels": {
          "service_name": "astrology-engine"
        }
      }
    }
  }'
```

## Deploy

The repository includes `.github/workflows/deploy-error-bridge.yml`, which deploys this service automatically after `ci` succeeds on `main` when files under `gcloud-error-to-codex/` change. The workflow expects:

```text
GitHub repository secret:
GCP_SA_KEY

Google Secret Manager secrets in astrology-engine-prod:
github-token
gcloud-error-webhook-token
```

Use the production Google Cloud project and region already used by the site:

```bash
gcloud config set project astrology-engine-prod
gcloud config set run/region us-central1
gcloud services enable run.googleapis.com secretmanager.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com
gcloud projects add-iam-policy-binding astrology-engine-prod \
  --member serviceAccount:820685644947-compute@developer.gserviceaccount.com \
  --role roles/logging.viewer
```

Store the GitHub token:

```bash
printf "%s" "YOUR_GITHUB_FINE_GRAINED_TOKEN" | gcloud secrets create github-token --data-file=-
```

If it already exists:

```bash
printf "%s" "YOUR_GITHUB_FINE_GRAINED_TOKEN" | gcloud secrets versions add github-token --data-file=-
```

Generate the webhook token:

```bash
openssl rand -hex 32
```

Deploy from this directory:

```bash
gcloud run deploy gcloud-error-to-codex \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --min-instances 0 \
  --max-instances 2 \
  --set-env-vars GITHUB_OWNER="Bender1011001" \
  --set-env-vars GITHUB_REPO="astrology" \
  --set-env-vars SITE_NAME="traditional-astrology.com" \
  --set-env-vars WEBHOOK_TOKEN="YOUR_LONG_RANDOM_WEBHOOK_TOKEN" \
  --set-secrets GITHUB_TOKEN=github-token:latest
```

Cloud Monitoring webhook URL:

```text
https://YOUR_CLOUD_RUN_URL/gcloud-error?token=YOUR_LONG_RANDOM_WEBHOOK_TOKEN
```

Use `/healthz` only for health checks.
