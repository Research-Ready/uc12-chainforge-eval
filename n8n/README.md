# UC12 — n8n Automation

## What this does

Runs the full benchmark pipeline on a weekly schedule (or on-demand via webhook):

```
Schedule / Webhook → run_benchmark.py → make_academic_report.py
                                       → generate_report.py (LinkedIn)
                                       → git commit → notify
```

## Import

1. Open n8n at http://localhost:5678
2. New workflow → Import from file → select `uc12-benchmark-workflow.json`
3. Activate the workflow

## Environment variables (set in n8n Settings → Variables)

| Variable | Value | Purpose |
|----------|-------|---------|
| `WEBHOOK_NOTIFY_URL` | your Slack/Teams/email webhook URL | Post-run notification |

If `WEBHOOK_NOTIFY_URL` is not set the Notify node fails silently (`continueOnFail: true`) and the rest still runs.

## Manual trigger

POST to `http://localhost:5678/webhook/uc12-benchmark-trigger` to trigger a run immediately without waiting for the schedule.

```bash
curl -X POST http://localhost:5678/webhook/uc12-benchmark-trigger
```

## Schedule

Runs every Sunday at 02:00 local time. Change in the "Weekly Schedule" node.

## LinkedIn auto-post

`generate_report.py` writes a draft to `output/social-media/`. Auto-posting to LinkedIn requires an OAuth token in `.env`:

```
LINKEDIN_ACCESS_TOKEN=your_token
```

Add an n8n LinkedIn node after "Generate LinkedIn Post" once the token is available.
