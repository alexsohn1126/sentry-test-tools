---
name: flask-error-to-box
description: Run the flask-error app on this laptop and send its errors to a Sentry devserver on a box (`*.box.getsentry.net`). Use when given a box DSN like `https://<key>@8000--<box>.box.getsentry.net/<project_id>`, or asked to "send errors to my box", "start the error server against crisp-lynx", etc.
---

# Send flask-error events to a box

## Don't use the box DSN as-is

A DSN whose host is `8000--<box>.box.getsentry.net` does not work from the laptop. That host is behind Google IAP, so every envelope gets `401 Invalid IAP credentials: empty token`. The route still returns its 500 and the SDK still returns an event id, so nothing looks wrong unless you turn on `debug=True`.

Keep the key and project id from the DSN, and replace the host with one of the options below.

## Option A: the webhook host (no tunnel needed)

`hooks.box.getsentry.net` is box's public webhook proxy (the one GitHub and Slack webhooks use). It forwards POSTs to the box `box hooks` points at, but only for paths it has signed. Sign the project's ingest path:

```sh
box hooks --port 8000 --path /api/<project_id>/envelope/
```

It prints `https://hooks.box.getsentry.net/8000--<owner>.<token>/api/<project_id>/envelope/`. Build the DSN from everything before `/api/`:

```
https://<key>@hooks.box.getsentry.net/8000--<owner>.<token>/<project_id>
```

Notes:
- `box hooks` with no name keeps the box the hooks already go to. Check it says the right box, and run `box hooks <box>` to change it. Never pass `--new`: it replaces the user's GitHub and Slack webhook URLs.
- A sleeping box answers 503 and wakes, so the first event can be lost.
- The auto-mode classifier may block `box hooks`. If it does, ask the user to run it with `! box hooks ...`.
- This route hasn't been checked end to end yet. If events don't arrive, use option B.

## Option B: port forward (checked, works)

```sh
box forward <box> 8010:8000   # run in the background; it runs until stopped
```

Use local port 8010, because something on this laptop often holds 8000. DSN: `http://<key>@localhost:8010/<project_id>`. Events stop arriving when the forward stops.

## Run the backend

```sh
cd flask-error && SENTRY_DSN="<dsn>" .venv/bin/python app.py   # in the background, serves :5000
```

`SENTRY_DSN` overrides the hardcoded DSNs in `app.py`. The error routes are `/error` (there is no `/error1`) and `/error2` to `/error7`. `@app.route` in `app.py` lists them.

## Check that events reach the box

1. Send one event with SDK debug logging, and look for `Unexpected status code` in the output:
   ```sh
   SENTRY_DSN="<dsn>" .venv/bin/python -c "import sentry_sdk,os; sentry_sdk.init(dsn=os.environ['SENTRY_DSN'], debug=True); sentry_sdk.capture_message('box DSN check'); sentry_sdk.flush(10)"
   ```
2. Look for the event in the project:
   ```sh
   box exec <box> 'curl -s -H "Authorization: Bearer $(cat ~/.box-dev-token)" "localhost:8000/api/0/projects/<org>/<project>/events/?statsPeriod=1h"'
   ```
   On a box, project ids like `4512316397977600` are usually `sentry/devserver`. Use `/api/0/projects/` to look up the slug.
