import argparse
import os
import re
import smtplib
import time
from datetime import UTC, datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Ensure app imports work when executed from repo root.
import sys

sys.path.insert(0, ROOT)

from src.database.core import SessionLocal, engine  # noqa: E402
from src.database.models import Base, OutreachAttempt, OutreachTarget  # noqa: E402


EMAIL_RE = re.compile(r"([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})", re.IGNORECASE)


TEMPLATES = {
    "teacher_v1": {
        "subject": "Tooling for teaching traditional astrology (web-based, deterministic)",
        "html": """\
<p>Hi {name},</p>

<p>I’m building <strong>Codex Caelestis</strong>, a browser-based traditional astrology calculation engine focused on deterministic technique coverage and auditable exports (rule ledger JSON).</p>

<p>Your teaching work is in the category where consistency matters. Quick question:</p>
<p>If you could eliminate the “manual bridge” (calculate in legacy software → export → rebuild slides/PDFs), would you want:</p>
<ol>
  <li>Classroom-ready chart assets (high-res, consistent)</li>
  <li>Structured exports for assignments (JSON + rule ledger)</li>
  <li>A student license flow (cohort provisioning)</li>
</ol>

<p>If relevant, I can share a 2-minute demo and ask 3 questions to prioritize what to ship first.</p>

<p>Thanks,<br/>
{from_name}<br/>
{site}</p>

<hr/>
<p style="font-size: 12px; color: #666;">
If you’d prefer I don’t email you again, reply with <strong>UNSUBSCRIBE</strong>.<br/>
{postal_address}
</p>
""",
    },
    "creator_v1": {
        "subject": "Faster weekly transit assets (deterministic + consistent)",
        "html": """\
<p>Hi {name},</p>

<p>I’m building a traditional astrology engine that outputs deterministic calculations plus consistent, reusable artifacts (not an AI chatbot).</p>

<p>If you publish weekly forecasts: what’s your biggest bottleneck right now?</p>
<ul>
  <li>generating clean chart visuals</li>
  <li>keeping charts/data consistent across posts</li>
  <li>exporting “what matters this week” quickly</li>
</ul>

<p>If you reply with one line, I’ll send back a mock output format aligned to your workflow.</p>

<p>Thanks,<br/>
{from_name}<br/>
{site}</p>

<hr/>
<p style="font-size: 12px; color: #666;">
If you’d prefer I don’t email you again, reply with <strong>UNSUBSCRIBE</strong>.<br/>
{postal_address}
</p>
""",
    },
    "seller_v1": {
        "subject": "Workflow question: delivering astrology PDFs at volume",
        "html": """\
<p>Hi {name},</p>

<p>Quick workflow question: when you deliver a PDF astrology report, what takes the most time?</p>
<ol>
  <li>calculations</li>
  <li>formatting/designing the PDF</li>
  <li>revisions/back-and-forth</li>
</ol>

<p>I’m building tooling to reduce the manual formatting step for practitioners shipping reports at volume. If you’re open to it, I’d love to ask 2 questions so I don’t build the wrong thing.</p>

<p>Thanks,<br/>
{from_name}<br/>
{site}</p>

<hr/>
<p style="font-size: 12px; color: #666;">
If you’d prefer I don’t email you again, reply with <strong>UNSUBSCRIBE</strong>.<br/>
{postal_address}
</p>
""",
    },
}


def extract_first_email(text: str) -> str | None:
    if not text:
        return None
    m = EMAIL_RE.search(text)
    return m.group(1) if m else None


def smtp_send(to_addr: str, subject: str, html: str, *, from_addr: str, from_name: str = "", reply_to: str | None = None) -> None:
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")

    if not (smtp_host and smtp_user and smtp_pass and from_addr):
        raise RuntimeError("SMTP not configured (need SMTP_HOST/SMTP_USER/SMTP_PASS and SENDER_EMAIL).")

    msg = MIMEMultipart("alternative")
    msg["From"] = f"{from_name} <{from_addr}>" if from_name else from_addr
    msg["To"] = to_addr
    msg["Subject"] = subject
    if reply_to:
        msg["Reply-To"] = reply_to

    msg.attach(MIMEText(html, "html", "utf-8"))

    server = smtplib.SMTP(smtp_host, smtp_port, timeout=30)
    server.starttls()
    server.login(smtp_user, smtp_pass)
    server.send_message(msg)
    server.quit()


def choose_template(target: OutreachTarget, override: str | None) -> str:
    if override:
        return override
    seg = (target.segment or "").strip().lower()
    if seg == "teacher":
        return "teacher_v1"
    if seg == "content_creator":
        return "creator_v1"
    if seg == "pdf_seller":
        return "seller_v1"
    return "creator_v1"


def main():
    ap = argparse.ArgumentParser(description="Automated outreach runner (email-only). Defaults to dry-run.")
    ap.add_argument("--send", action="store_true", help="Actually send emails. Without this, it's dry-run.")
    ap.add_argument("--limit", type=int, default=10, help="Max sends this run (default: 10).")
    ap.add_argument("--min-gap-sec", type=int, default=25, help="Minimum sleep between sends (default: 25s).")
    ap.add_argument("--max-per-hour", type=int, default=40, help="Hard throttle per hour (default: 40).")
    ap.add_argument("--template", type=str, default=None, choices=sorted(TEMPLATES.keys()), help="Force a template id.")
    ap.add_argument("--segment", type=str, default=None, help="Filter by segment (teacher/content_creator/pdf_seller).")
    ap.add_argument("--platform", type=str, default=None, help="Filter by platform_primary (website/email/etc).")
    ap.add_argument("--cooldown-hours", type=int, default=168, help="Don't re-email same target within this window (default: 168h).")
    ap.add_argument("--postal-address", type=str, default=os.getenv("OUTREACH_POSTAL_ADDRESS", ""), help="Postal address for compliance footer.")
    ap.add_argument("--from-name", type=str, default=os.getenv("OUTREACH_FROM_NAME", "Traditional-Astrology.com"))
    ap.add_argument("--reply-to", type=str, default=os.getenv("OUTREACH_REPLY_TO", ""))
    args = ap.parse_args()

    # Create tables if needed.
    Base.metadata.create_all(bind=engine)

    from_addr = os.getenv("SENDER_EMAIL", "").strip()
    if args.send:
        if not args.postal_address.strip():
            raise SystemExit("Refusing to send: missing --postal-address (or OUTREACH_POSTAL_ADDRESS).")
        if not from_addr:
            raise SystemExit("Refusing to send: missing SENDER_EMAIL.")

    db = SessionLocal()
    try:
        cooldown_start = datetime.now(UTC) - timedelta(hours=int(args.cooldown_hours))

        # Throttle: if we've sent >= max-per-hour in last hour, abort.
        if args.send:
            hour_start = datetime.now(UTC) - timedelta(hours=1)
            sent_last_hour = (
                db.query(OutreachAttempt)
                .filter(OutreachAttempt.channel == "email")
                .filter(OutreachAttempt.status == "sent")
                .filter(OutreachAttempt.sent_at >= hour_start)
                .count()
            )
            if sent_last_hour >= int(args.max_per_hour):
                raise SystemExit(f"Throttle: already sent {sent_last_hour} emails in the last hour (max {args.max_per_hour}).")

        q = db.query(OutreachTarget)
        if args.segment:
            q = q.filter(OutreachTarget.segment == args.segment.strip().lower())
        if args.platform:
            q = q.filter(OutreachTarget.platform_primary == args.platform.strip().lower())

        targets = q.order_by(OutreachTarget.name.asc()).all()
        eligible = []
        for t in targets:
            # Only email-able targets.
            email = extract_first_email(t.primary_contact or "") or extract_first_email(t.secondary_contact or "")
            if not email:
                continue

            # Skip if recently emailed.
            recent = (
                db.query(OutreachAttempt)
                .filter(OutreachAttempt.target_id == t.id)
                .filter(OutreachAttempt.channel == "email")
                .filter(OutreachAttempt.status == "sent")
                .filter(OutreachAttempt.sent_at >= cooldown_start)
                .first()
            )
            if recent:
                continue

            eligible.append((t, email))

        to_process = eligible[: max(0, int(args.limit))]
        if not to_process:
            print("No eligible email targets found (filters/cooldown may exclude all).")
            return

        site = os.getenv("SITE_BASE_URL", "https://traditional-astrology.com")
        reply_to = args.reply_to.strip() or None

        for idx, (t, email_to) in enumerate(to_process, start=1):
            template_id = choose_template(t, args.template)
            tpl = TEMPLATES[template_id]
            subject = tpl["subject"]
            html = tpl["html"].format(
                name=t.name,
                from_name=args.from_name,
                site=site,
                postal_address=args.postal_address.strip(),
            )

            attempt = OutreachAttempt(
                target_id=t.id,
                channel="email",
                to_addr=email_to,
                subject=subject,
                template_id=template_id,
                status="queued",
            )
            db.add(attempt)
            db.commit()

            if not args.send:
                attempt.status = "skipped"
                attempt.error_message = "dry_run"
                db.commit()
                print(f"[DRY] {idx}/{len(to_process)} {t.name} -> {email_to} ({template_id})")
                continue

            try:
                smtp_send(
                    email_to,
                    subject,
                    html,
                    from_addr=from_addr,
                    from_name=args.from_name,
                    reply_to=reply_to,
                )
                attempt.status = "sent"
                # Store naive UTC for SQLite compatibility.
                attempt.sent_at = datetime.now(UTC).replace(tzinfo=None)
                db.commit()
                print(f"[SENT] {idx}/{len(to_process)} {t.name} -> {email_to}")
            except Exception as e:
                attempt.status = "failed"
                attempt.error_message = str(e)[:800]
                db.commit()
                print(f"[FAIL] {idx}/{len(to_process)} {t.name} -> {email_to}: {e}")

            # Sleep between sends (even on failure).
            if idx < len(to_process):
                time.sleep(max(0, int(args.min_gap_sec)))
    finally:
        db.close()


if __name__ == "__main__":
    main()
