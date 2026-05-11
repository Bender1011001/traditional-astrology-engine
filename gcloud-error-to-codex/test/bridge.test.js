import assert from "node:assert/strict";
import { test } from "node:test";
import {
  buildMatchedLogFilter,
  buildIssueBody,
  buildIssueTitle,
  clean,
  extractAlert,
  isAuthorizedToken,
  lookupMatchedLogEntry,
  loadConfig,
  normalizeLogEntry,
  truncate
} from "../index.js";

const config = {
  githubOwner: "Bender1011001",
  githubRepo: "astrology",
  webhookToken: "0123456789abcdef",
  siteName: "traditional-astrology.com",
  codexMention: "@codex"
};

test("loadConfig requires the deployment secrets", () => {
  assert.throws(() => loadConfig({}), /Missing required env vars/);
  assert.equal(
    loadConfig({
      GITHUB_TOKEN: "unit-github-token",
      GITHUB_OWNER: "owner",
      GITHUB_REPO: "repo",
      WEBHOOK_TOKEN: "token",
      LOG_LOOKUP_WINDOW_SECONDS: "120"
    }).siteName,
    "traditional-astrology.com"
  );
  assert.equal(
    loadConfig({
      GITHUB_TOKEN: "unit-github-token",
      GITHUB_OWNER: "owner",
      GITHUB_REPO: "repo",
      WEBHOOK_TOKEN: "token",
      LOG_LOOKUP_DISABLED: "true"
    }).logLookupDisabled,
    true
  );
});

test("isAuthorizedToken accepts only exact token matches", () => {
  assert.equal(isAuthorizedToken("0123456789abcdef", config.webhookToken), true);
  assert.equal(isAuthorizedToken("bad", config.webhookToken), false);
  assert.equal(isAuthorizedToken("", config.webhookToken), false);
  assert.equal(isAuthorizedToken("0123456789abcdeg", config.webhookToken), false);
});

test("extractAlert normalizes a Cloud Monitoring incident payload", () => {
  const alert = extractAlert(
    {
      incident: {
        summary: "TypeError: Cannot read properties of undefined",
        policy_name: "production-errors",
        condition_name: "severity-error",
        severity: "ERROR",
        started_at: "2026-05-11T00:00:00Z",
        url: "https://console.cloud.google.com/logs/query;query=test",
        resource: {
          labels: {
            service_name: "astrology-engine"
          }
        }
      },
      stack_trace: "TypeError: Cannot read properties of undefined\n    at handler"
    },
    config.siteName
  );

  assert.match(alert.fingerprint, /^[0-9a-f]{12}$/);
  assert.equal(alert.service, "astrology-engine");
  assert.equal(alert.policyName, "production-errors");
  assert.equal(alert.conditionName, "severity-error");
  assert.match(alert.possibleStack, /TypeError/);
});

test("extractAlert can use structured log payload fields", () => {
  const alert = extractAlert(
    {
      resource: { labels: { service_name: "astrology-engine" } },
      severity: "ERROR",
      jsonPayload: {
        message: "stripe_webhook failed",
        stack_trace: "AttributeError: get\n  at stripe_webhook"
      }
    },
    config.siteName
  );

  assert.equal(alert.summary, "stripe_webhook failed");
  assert.match(alert.possibleStack, /AttributeError/);
});

test("extractAlert prefers an enriched matched Cloud Logging entry", () => {
  const alert = extractAlert(
    {
      incident: {
        summary: "Log match condition fired for Cloud Run Revision",
        documentation: {
          content: "Generic alert documentation"
        },
        resource: {
          labels: {
            service_name: "astrology-engine",
            project_id: "astrology-engine-prod"
          }
        },
        severity: "No severity",
        started_at: 1778515562
      },
      matchedLogEntry: {
        timestamp: "2026-05-11T16:05:48.496Z",
        severity: "ERROR",
        resource: {
          labels: {
            service_name: "astrology-engine"
          }
        },
        jsonPayload: {
          message: "Codex drill synthetic production error",
          stack_trace: "CodexDrillError: synthetic monitored error\n    at drill"
        }
      }
    },
    config.siteName
  );

  assert.equal(alert.summary, "Codex drill synthetic production error");
  assert.equal(alert.severity, "ERROR");
  assert.equal(alert.startedAt, "2026-05-11T16:05:48.496Z");
  assert.equal(alert.matchedLogFound, true);
  assert.match(alert.possibleStack, /CodexDrillError/);
  assert.match(buildIssueBody(alert, config), /Matched log entry \| yes/);
});

test("buildMatchedLogFilter targets the incident resource and time window", () => {
  const { projectId, filter } = buildMatchedLogFilter(
    {
      incident: {
        started_at: 1778515562,
        resource: {
          type: "cloud_run_revision",
          labels: {
            project_id: "astrology-engine-prod",
            service_name: "astrology-engine",
            revision_name: "astrology-engine-00099-hvs"
          }
        }
      }
    },
    60,
    new Date("2026-05-11T16:07:00Z")
  );

  assert.equal(projectId, "astrology-engine-prod");
  assert.match(filter, /resource\.type="cloud_run_revision"/);
  assert.match(filter, /resource\.labels\.service_name="astrology-engine"/);
  assert.match(filter, /resource\.labels\.revision_name="astrology-engine-00099-hvs"/);
  assert.match(filter, /severity>=ERROR/);
  assert.match(filter, /timestamp>="2026-05-11T16:05:02\.000Z"/);
  assert.match(filter, /timestamp<="2026-05-11T16:07:02\.000Z"/);
});

test("lookupMatchedLogEntry returns the newest entry from Cloud Logging", async () => {
  const fakeClient = {
    lastRequest: null,
    async getEntries(request) {
      this.lastRequest = request;
      return [
        [
          {
            metadata: {
              timestamp: "2026-05-11T16:05:48.496Z",
              severity: "ERROR",
              logName: "projects/astrology-engine-prod/logs/codex-prod-error-drill",
              resource: {
                type: "cloud_run_revision",
                labels: {
                  service_name: "astrology-engine"
                }
              }
            },
            data: {
              message: "drill failure",
              stack_trace: "CodexDrillError"
            }
          }
        ]
      ];
    }
  };

  const entry = await lookupMatchedLogEntry(
    {
      incident: {
        started_at: 1778515562,
        resource: {
          type: "cloud_run_revision",
          labels: {
            project_id: "astrology-engine-prod",
            service_name: "astrology-engine"
          }
        }
      }
    },
    { logLookupDisabled: false, logLookupWindowSeconds: 900 },
    fakeClient,
    new Date("2026-05-11T16:07:00Z")
  );

  assert.equal(fakeClient.lastRequest.orderBy, "timestamp desc");
  assert.equal(fakeClient.lastRequest.pageSize, 1);
  assert.equal(entry.severity, "ERROR");
  assert.equal(entry.jsonPayload.message, "drill failure");
});

test("normalizeLogEntry handles text payloads", () => {
  const entry = normalizeLogEntry({
    metadata: {
      timestamp: {
        toJSON() {
          return "2026-05-11T16:05:48Z";
        }
      },
      severity: "ERROR"
    },
    data: "RuntimeError: plain text log"
  });

  assert.equal(entry.timestamp, "2026-05-11T16:05:48Z");
  assert.equal(entry.textPayload, "RuntimeError: plain text log");
  assert.equal(entry.jsonPayload, undefined);
});

test("issue title and body include Codex task and review policy", () => {
  const alert = extractAlert(
    {
      incident: {
        summary: "Validation crashed on missing optional field",
        policy_name: "production-errors",
        condition_name: "severity-error",
        severity: "ERROR",
        resource: { labels: { service_name: "astrology-engine" } }
      }
    },
    config.siteName
  );

  assert.match(buildIssueTitle(alert), /^\[prod-error [0-9a-f]{12}\] astrology-engine:/);
  const body = buildIssueBody(alert, config);
  assert.match(body, /@codex investigate this production error/);
  assert.match(body, /needs-owner-review/);
  assert.match(body, /Raw Google Cloud alert payload/);
});

test("clean and truncate keep issue content bounded", () => {
  assert.equal(clean(" a\n b\t c "), "a b c");
  assert.equal(truncate("abcdef", 3), "abc\n...[truncated]");
});
