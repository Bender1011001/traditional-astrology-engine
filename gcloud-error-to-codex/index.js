import crypto from "crypto";
import express from "express";
import { Logging } from "@google-cloud/logging";
import { Octokit } from "@octokit/rest";
import { pathToFileURL } from "url";

const LABELS = [
  ["production-error", "B60205", "Created from a production error alert"],
  ["codex", "7057ff", "Task intended for Codex"],
  ["needs-owner-review", "D93F0B", "Requires human review before merge/deploy"],
  ["autofix-safe", "0E8A16", "Low-risk autofix candidate"],
  ["autofix-failed", "5319E7", "Autofix attempt failed or CI failed"]
];

const REQUIRED_ENV = [
  "GITHUB_TOKEN",
  "GITHUB_OWNER",
  "GITHUB_REPO",
  "WEBHOOK_TOKEN"
];

export function loadConfig(env = process.env) {
  const missing = REQUIRED_ENV.filter((key) => !String(env[key] || "").trim());
  if (missing.length > 0) {
    throw new Error(`Missing required env vars: ${missing.join(", ")}`);
  }

  return {
    githubToken: String(env.GITHUB_TOKEN).trim(),
    githubOwner: String(env.GITHUB_OWNER).trim(),
    githubRepo: String(env.GITHUB_REPO).trim(),
    webhookToken: String(env.WEBHOOK_TOKEN).trim(),
    siteName: String(env.SITE_NAME || "traditional-astrology.com").trim(),
    codexMention: String(env.CODEX_MENTION || "@codex").trim(),
    logLookupDisabled: /^(1|true|yes)$/i.test(String(env.LOG_LOOKUP_DISABLED || "").trim()),
    logLookupWindowSeconds: parsePositiveInteger(env.LOG_LOOKUP_WINDOW_SECONDS, 900),
    logLookupAttempts: parsePositiveInteger(env.LOG_LOOKUP_ATTEMPTS, 4),
    logLookupDelayMillis: parsePositiveInteger(env.LOG_LOOKUP_DELAY_MILLIS, 2000)
  };
}

function parsePositiveInteger(value, fallback) {
  const parsed = Number(value);
  return Number.isFinite(parsed) && parsed > 0 ? Math.floor(parsed) : fallback;
}

export function sha1(value) {
  return crypto.createHash("sha1").update(String(value)).digest("hex");
}

export function truncate(value, max = 12000) {
  const text = typeof value === "string" ? value : JSON.stringify(value, null, 2);
  return text.length > max ? `${text.slice(0, max)}\n...[truncated]` : text;
}

export function clean(value, fallback = "unknown") {
  if (value === undefined || value === null || value === "") {
    return fallback;
  }
  const text = typeof value === "string" ? value : JSON.stringify(value);
  return text.replace(/\s+/g, " ").trim() || fallback;
}

function firstScalar(value) {
  if (Array.isArray(value)) {
    return firstScalar(value[0]);
  }
  if (value === undefined || value === null) {
    return "";
  }
  return String(value);
}

export function isAuthorizedToken(providedToken, expectedToken) {
  const provided = Buffer.from(firstScalar(providedToken), "utf8");
  const expected = Buffer.from(firstScalar(expectedToken), "utf8");
  if (provided.length === 0 || expected.length === 0 || provided.length !== expected.length) {
    return false;
  }
  return crypto.timingSafeEqual(provided, expected);
}

function deepString(...values) {
  for (const value of values) {
    if (value === undefined || value === null || value === "") {
      continue;
    }
    if (typeof value === "string") {
      return value;
    }
    return JSON.stringify(value, null, 2);
  }
  return "";
}

function escapeLoggingString(value) {
  return String(value).replace(/\\/g, "\\\\").replace(/"/g, '\\"');
}

export function parseAlertTimestamp(value, fallback = new Date()) {
  if (typeof value === "number" && Number.isFinite(value)) {
    return new Date(value > 1_000_000_000_000 ? value : value * 1000);
  }

  if (typeof value === "string" && value.trim()) {
    const trimmed = value.trim();
    if (/^\d+(\.\d+)?$/.test(trimmed)) {
      const numeric = Number(trimmed);
      return new Date(numeric > 1_000_000_000_000 ? numeric : numeric * 1000);
    }

    const parsed = new Date(trimmed);
    if (!Number.isNaN(parsed.getTime())) {
      return parsed;
    }
  }

  return fallback;
}

export function buildMatchedLogFilter(payload, windowSeconds = 900, now = new Date()) {
  const source = payload && typeof payload === "object" ? payload : {};
  const incident = source.incident || {};
  const resource = incident.resource || source.resource || {};
  const labels = resource.labels || {};
  const projectId = labels.project_id || incident.scoping_project_id || source.project_id || "";
  const end = new Date(now.getTime() + 60 * 1000);
  const start = new Date(now.getTime() - windowSeconds * 1000);
  const terms = [];

  if (resource.type) {
    terms.push(`resource.type="${escapeLoggingString(resource.type)}"`);
  }

  for (const [key, value] of Object.entries(labels)) {
    if (value !== undefined && value !== null && value !== "") {
      terms.push(`resource.labels.${key}="${escapeLoggingString(value)}"`);
    }
  }

  terms.push("severity>=ERROR");
  terms.push(`timestamp>="${start.toISOString()}"`);
  terms.push(`timestamp<="${end.toISOString()}"`);

  return {
    projectId: String(projectId || "").trim(),
    filter: terms.join(" AND ")
  };
}

export function normalizeLogEntry(entry) {
  const metadata = entry?.metadata || {};
  const payload = entry?.data ?? entry?.jsonPayload ?? entry?.textPayload ?? "";
  const jsonPayload =
    payload && typeof payload === "object" && !Array.isArray(payload) ? payload : undefined;
  const textPayload = typeof payload === "string" ? payload : undefined;

  return {
    timestamp: cleanLogScalar(metadata.timestamp || entry?.timestamp),
    severity: cleanLogScalar(metadata.severity || entry?.severity),
    logName: cleanLogScalar(metadata.logName || entry?.logName),
    insertId: cleanLogScalar(metadata.insertId || entry?.insertId),
    resource: metadata.resource || entry?.resource || {},
    jsonPayload,
    textPayload,
    raw: {
      metadata,
      payload
    }
  };
}

function cleanLogScalar(value) {
  if (value === undefined || value === null || value === "") {
    return "";
  }
  if (value instanceof Date) {
    return value.toISOString();
  }
  if (typeof value === "object") {
    if (typeof value.toISOString === "function") {
      return String(value.toISOString());
    }
    if (typeof value.toJSON === "function") {
      const json = value.toJSON();
      return typeof json === "string" ? json : clean(json, "");
    }
  }
  return clean(value, "");
}

export async function lookupMatchedLogEntry(payload, config, loggingClient, now = new Date()) {
  if (config.logLookupDisabled) {
    return null;
  }

  const { projectId, filter } = buildMatchedLogFilter(
    payload,
    config.logLookupWindowSeconds,
    now
  );
  if (!projectId || !filter) {
    return null;
  }

  const client = loggingClient || new Logging({ projectId });
  const attempts = parsePositiveInteger(config.logLookupAttempts, 1);
  const delayMillis = parsePositiveInteger(config.logLookupDelayMillis, 0);

  for (let attempt = 1; attempt <= attempts; attempt += 1) {
    const [entries] = await client.getEntries({
      filter,
      orderBy: "timestamp desc",
      pageSize: 1
    });

    if (entries && entries.length > 0) {
      return normalizeLogEntry(entries[0]);
    }

    if (attempt < attempts && delayMillis > 0) {
      await new Promise((resolve) => setTimeout(resolve, delayMillis));
    }
  }

  return null;
}

export async function enrichAlertPayload(payload, config, loggingClient) {
  try {
    const matchedLogEntry = await lookupMatchedLogEntry(payload, config, loggingClient);
    if (!matchedLogEntry) {
      return payload;
    }
    return {
      ...payload,
      matchedLogEntry
    };
  } catch (err) {
    console.warn("Cloud Logging lookup failed; creating issue from alert payload only", {
      message: err.message
    });
    return payload;
  }
}

function topStackLine(value) {
  return String(value || "")
    .split(/\r?\n/)
    .map((line) => line.trim())
    .find((line) => line && !line.startsWith("Traceback")) || "";
}

export function extractAlert(payload, siteName = "traditional-astrology.com") {
  const source = payload && typeof payload === "object" ? payload : {};
  const incident = source.incident || {};
  const matchedLog = source.matchedLogEntry || {};
  const resource = incident.resource || source.resource || matchedLog.resource || {};
  const labels = resource.labels || {};
  const metadata = incident.metadata || source.metadata || {};
  const systemLabels = metadata.system_labels || source.system_labels || {};
  const matchedJsonPayload = matchedLog.jsonPayload || {};
  const jsonPayload = source.jsonPayload || source.json_payload || matchedJsonPayload || {};
  const errorPayload = source.error || source.exception || {};

  const summary = deepString(
    jsonPayload.message,
    jsonPayload.error?.message,
    matchedLog.textPayload,
    source.message,
    source.textPayload,
    source.summary,
    source.subject,
    incident.summary,
    incident.documentation?.content,
    source.textPayload,
    "Google Cloud production error"
  );

  const policyName = deepString(
    incident.policy_name,
    incident.policy_display_name,
    source.policy_name,
    source.policyDisplayName,
    "unknown-policy"
  );

  const conditionName = deepString(
    incident.condition_name,
    incident.condition_display_name,
    source.condition_name,
    source.conditionDisplayName,
    "unknown-condition"
  );

  const service = deepString(
    labels.service_name,
    labels.service,
    labels.container_name,
    labels.module_id,
    labels.instance_id,
    incident.resource_display_name,
    source.service,
    "unknown-service"
  );

  const severity = deepString(
    matchedLog.severity,
    source.severity,
    jsonPayload.severity,
    incident.severity,
    systemLabels.severity,
    "ERROR"
  );

  const startedAt = deepString(
    matchedLog.timestamp,
    source.timestamp,
    source.receiveTimestamp,
    incident.started_at,
    incident.start_time,
    new Date().toISOString()
  );

  const url = deepString(
    incident.url,
    source.url,
    source.log_url,
    source.error_url,
    source.logUrl,
    "no-link-provided"
  );

  const possibleStack = deepString(
    jsonPayload.stack_trace,
    jsonPayload.stackTrace,
    jsonPayload.stack,
    jsonPayload.exception,
    jsonPayload.error,
    matchedLog.textPayload,
    source.stack,
    source.stack_trace,
    source.stackTrace,
    errorPayload.stack,
    errorPayload.stack_trace,
    source.textPayload,
    incident.documentation?.content,
    summary
  );

  const rawText = JSON.stringify(source, null, 2);
  const fingerprintSource = [
    siteName,
    clean(service),
    clean(policyName),
    clean(conditionName),
    clean(summary),
    topStackLine(possibleStack)
  ].join("|");

  return {
    fingerprint: sha1(fingerprintSource).slice(0, 12),
    summary: clean(summary, "Google Cloud production error"),
    service: clean(service),
    severity: clean(severity, "ERROR"),
    policyName: clean(policyName),
    conditionName: clean(conditionName),
    startedAt: clean(startedAt),
    url: clean(url, "no-link-provided"),
    possibleStack: clean(possibleStack, "No stack trace supplied"),
    matchedLogFound: Boolean(source.matchedLogEntry),
    matchedLogEntry: source.matchedLogEntry || null,
    rawText
  };
}

export async function ensureLabel(octokit, config, name, color, description) {
  try {
    await octokit.issues.getLabel({
      owner: config.githubOwner,
      repo: config.githubRepo,
      name
    });
  } catch (err) {
    if (err.status !== 404) {
      throw err;
    }
    try {
      await octokit.issues.createLabel({
        owner: config.githubOwner,
        repo: config.githubRepo,
        name,
        color,
        description
      });
    } catch (createErr) {
      const alreadyExists =
        createErr.status === 422 && String(createErr.message || "").includes("already_exists");
      if (!alreadyExists) {
        throw createErr;
      }
    }
  }
}

export async function ensureLabels(octokit, config) {
  for (const [name, color, description] of LABELS) {
    await ensureLabel(octokit, config, name, color, description);
  }
}

export async function findExistingIssue(octokit, config, fingerprint) {
  const q = `repo:${config.githubOwner}/${config.githubRepo} is:issue is:open prod-error ${fingerprint} in:title`;
  const result = await octokit.search.issuesAndPullRequests({ q, per_page: 5 });
  return result.data.items?.[0] || null;
}

export function buildIssueTitle(alert) {
  const shortSummary = alert.summary.replace(/\s+/g, " ").slice(0, 140);
  return `[prod-error ${alert.fingerprint}] ${alert.service}: ${shortSummary}`.slice(0, 240);
}

export function buildIssueBody(alert, config) {
  return `${config.codexMention} investigate this production error and propose the smallest safe fix.

Autofix policy:
- You may fix and open a PR automatically only if this is low-risk.
- Low-risk means no auth, payment, database schema, IAM, secret, DNS, infrastructure, deployment, or broad refactor changes.
- If low-risk, make the smallest fix, add/update a regression test if practical, run checks, open a PR, and label it \`autofix-safe\`.
- If risky or uncertain, do not make broad changes. Explain the cause and label the issue or PR \`needs-owner-review\`.

Production error report:

| Field | Value |
|---|---|
| Site | ${config.siteName} |
| Fingerprint | ${alert.fingerprint} |
| Service | ${alert.service} |
| Severity | ${alert.severity} |
| Policy | ${alert.policyName} |
| Condition | ${alert.conditionName} |
| Started at | ${alert.startedAt} |
| Google Cloud link | ${alert.url} |
| Matched log entry | ${alert.matchedLogFound ? "yes" : "no"} |

Likely error / stack / alert text:

\`\`\`
${truncate(alert.possibleStack, 6000)}
\`\`\`

Matched Cloud Logging entry:

\`\`\`json
${truncate(alert.matchedLogEntry || { status: "not_found" }, 8000)}
\`\`\`

Raw Google Cloud alert payload:

\`\`\`json
${truncate(alert.rawText, 12000)}
\`\`\`
`;
}

export function buildOccurrenceComment(alert) {
  return `Repeated production error occurrence.

| Field | Value |
|---|---|
| Fingerprint | ${alert.fingerprint} |
| Service | ${alert.service} |
| Severity | ${alert.severity} |
| Started at | ${alert.startedAt} |
| Google Cloud link | ${alert.url} |

Latest alert text:

\`\`\`
${truncate(alert.possibleStack, 4000)}
\`\`\``;
}

export function createApp({ config, octokit, logging }) {
  const app = express();
  app.disable("x-powered-by");
  app.use(express.json({ limit: "3mb" }));

  app.get(["/healthz", "/healthz/"], (_req, res) => {
    res.status(200).json({
      ok: true,
      service: "gcloud-error-to-codex",
      site: config.siteName,
      repo: `${config.githubOwner}/${config.githubRepo}`
    });
  });

  app.post("/gcloud-error", async (req, res) => {
    try {
      const token = firstScalar(req.query.token) || req.get("x-webhook-token");
      if (!isAuthorizedToken(token, config.webhookToken)) {
        return res.status(401).json({ ok: false, error: "unauthorized" });
      }

      await ensureLabels(octokit, config);

      const alertPayload = await enrichAlertPayload(req.body, config, logging);
      const alert = extractAlert(alertPayload, config.siteName);
      const existing = await findExistingIssue(octokit, config, alert.fingerprint);

      if (existing) {
        await octokit.issues.createComment({
          owner: config.githubOwner,
          repo: config.githubRepo,
          issue_number: existing.number,
          body: buildOccurrenceComment(alert)
        });

        return res.status(200).json({
          ok: true,
          mode: "commented_existing_issue",
          issue: existing.html_url,
          fingerprint: alert.fingerprint
        });
      }

      const issue = await octokit.issues.create({
        owner: config.githubOwner,
        repo: config.githubRepo,
        title: buildIssueTitle(alert),
        body: buildIssueBody(alert, config),
        labels: ["production-error", "codex"]
      });

      return res.status(200).json({
        ok: true,
        mode: "created_issue",
        issue: issue.data.html_url,
        fingerprint: alert.fingerprint
      });
    } catch (err) {
      console.error("gcloud-error-to-codex request failed", {
        message: err.message,
        status: err.status
      });
      return res.status(500).json({ ok: false, error: "bridge_failure" });
    }
  });

  app.use((err, _req, res, _next) => {
    if (err instanceof SyntaxError && "body" in err) {
      return res.status(400).json({ ok: false, error: "invalid_json" });
    }
    console.error("gcloud-error-to-codex express failure", { message: err.message });
    return res.status(500).json({ ok: false, error: "bridge_failure" });
  });

  return app;
}

function main() {
  const config = loadConfig();
  const octokit = new Octokit({ auth: config.githubToken });
  const app = createApp({ config, octokit });
  const port = Number(process.env.PORT || 8080);

  app.listen(port, () => {
    console.log(`gcloud-error-to-codex listening on ${port}`);
  });
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  main();
}
