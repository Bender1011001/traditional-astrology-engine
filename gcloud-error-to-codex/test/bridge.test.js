import assert from "node:assert/strict";
import { test } from "node:test";
import {
  buildIssueBody,
  buildIssueTitle,
  clean,
  extractAlert,
  isAuthorizedToken,
  loadConfig,
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
      WEBHOOK_TOKEN: "token"
    }).siteName,
    "traditional-astrology.com"
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
