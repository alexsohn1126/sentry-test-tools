import argparse
import os
import random
from datetime import datetime

import sentry_sdk
from flask import Flask
from sentry_sdk.integrations.flask import FlaskIntegration

LOCAL_SENTRY_DSN = "https://6c38fd78856456eea748437c435e3423@o4511065992724480.ingest.us.sentry.io/4511263749832704"
LOCAL_GETSENTRY_DSN = "https://b288aadaab57a0b3cfd2178c5a6130ec@us.alexsohn.ngrok.io/4511276748701712"

# prod sentry
PROD_SENTRY_DSN = "https://d59d6ec001bd69291b7de6efd8b697d1@o4509921934573568.ingest.us.sentry.io/4511185813766144"
# sentry-alex-eu // legacy-data-forwarding
LEGACY_DATA_FORWARD_DSN = "https://2e0ab03d072b9e54174406624fbf4ecc@o4509708210274304.ingest.de.sentry.io/4510358464954448"

# sentry-alex // all-robots
SENTRY_ALEX_DSN = "https://a1eb5b30cb6e687c10cd1cbfdcbf249e@o1.ingest.us.sentry.io/4511021725646848"
#  lxyz2 // django
LXYZ2_DSN = "https://2d557e71645717ee2b69cb7caf4c4d1c@o1115830.ingest.us.sentry.io/4508609084981249"
# alexsohn // work-funnel
WORK_FUNNEL_DSN = "https://1de16b5fb20c0dfe0379ec83d78194a5@o209069.ingest.us.sentry.io/4509707355947008"

SILO_DSN = "https://e9a3d278c7729cdf4e9d2162ba377d83@test-region.test.my.sentry.io/4505992947957808"

parser = argparse.ArgumentParser(description="Create some sentry errors")
parser.add_argument(
    "instance",
    default="sentry",
    const="sentry",
    nargs="?",
    choices=[
        "sentry",
        "getsentry",
        "lxyz2",
        "prod",
        "alex",
        "temp",
        "work-funnel",
    ],
    help="Sentry instance to receive errors",
)


def dsn_selector():
    env_dsn = os.environ.get("SENTRY_DSN")
    if env_dsn:
        print(f"Sending errors to DSN from SENTRY_DSN env var: {env_dsn}")
        return env_dsn
    args = parser.parse_args()
    print(f"Sending errors to '{args.instance}' instance...")
    if args.instance == "getsentry":
        return LOCAL_GETSENTRY_DSN
    elif args.instance == "lxyz2":
        return LXYZ2_DSN
    elif args.instance == "prod":
        return PROD_SENTRY_DSN
    elif args.instance == "alex":
        return SENTRY_ALEX_DSN
    elif args.instance == "work-funnel":
        return WORK_FUNNEL_DSN
    elif args.instance == "temp":
        return LEGACY_DATA_FORWARD_DSN
    else:
        return LOCAL_SENTRY_DSN


sentry_sdk.init(
    dsn=dsn_selector(),
    integrations=[FlaskIntegration()],
    send_default_pii=True,
    traces_sample_rate=1.0,
)

app = Flask(__name__)


@app.route("/")
def home():
    return """
    <div>
    <h1>Hello World!</h1>
    <h1></h2>
    <a href="/regular">Link to regular page</a>
    <a href="/error">Link to error page</a>
    </div>"""


@app.route("/regular")
def regular():
    return """
    <div>
    <h1>Hello World!</h1>
    <a href="/">Link to home page</a>
    <a href="/error">Link to error page</a>
    </div>"""


@app.route("/error")
@app.route("/error/")
def error():
    sentry_sdk.set_user(
        {
            "id": random.randint(1, 100),
            "email": "alex.sohn@sentry.io",
            "username": "alexsohn",
            "ip_address": "12.34.56.78",
            "other": "property",
            "location": "canada",
        }
    )
    with sentry_sdk.configure_scope() as scope:
        scope.set_context(
            "large_numbers",
            {
                "decimal_number": 123456.789,
                "number": 123456789,
                "negative_number": -123456789,
                "big_decimal_number": 123456789.123456789,
                "big_number": 123456789123456789,
                "big_negative_number": -123456789123456789,
                "bug_report_number": 608548899684111178,
            },
        )
        from src.runner import error

        application = {}

        error()


@app.route("/error2")
def error2():
    sentry_sdk.set_user(
        {
            "id": random.randint(1, 100),
            "email": "alex.sohn@sentry.io",
            "username": "alexsohn",
        }
    )
    users = [
        {"name": "Alex", "age": 30},
        {"name": "Jordan", "age": None},
        {"name": "Sam", "age": 25},
    ]
    # TypeError: '>' not supported between instances of 'NoneType' and 'int'
    eligible = [u for u in users if u["age"] is not None and u["age"] > 18]
    return f"Eligible users: {eligible}"


@app.route("/error3")
def error3():
    sentry_sdk.set_user(
        {
            "id": random.randint(1, 100),
            "email": "alex.sohn@sentry.io",
            "username": "alexsohn",
        }
    )
    config = {"database": {"host": "localhost", "port": 5432}}
    # KeyError: 'credentials'
    db_password = config["database"]["credentials"]["password"]
    return f"Connected with password: {db_password}"


@app.route("/error4")
def error4():
    sentry_sdk.set_user(
        {
            "id": random.randint(1, 100),
            "email": "alex.sohn@sentry.io",
            "username": "alexsohn",
        }
    )
    import re

    pattern = re.compile(r"(\w+)\s(\w+)")
    log_line = "2026-03-27T14:32:01Z [ERROR] PaymentService.process_refund: refund_id=RF-9182 amount=49.99"
    match = pattern.search(log_line)
    # RecursionError from a deeply nested refund retry loop
    def retry_refund(attempt, max_retries=3):
        if attempt > max_retries:
            raise RecursionError(
                f"Maximum refund retry depth exceeded after {attempt} attempts for refund RF-9182"
            )
        # simulate a failing refund that accidentally recurses without incrementing
        retry_refund(attempt)

    retry_refund(1)
    return "Refund processed"


@app.route("/error5")
def error5():
    sentry_sdk.set_user(
        {
            "id": random.randint(1, 100),
            "email": "alex.sohn@sentry.io",
            "username": "alexsohn",
        }
    )
    import json

    # Simulate receiving a webhook payload with malformed UTF-8 bytes
    raw_payload = b'{"event": "invoice.paid", "customer": "\xc3\x28", "amount": 250}'
    decoded = raw_payload.decode("utf-8")
    event = json.loads(decoded)
    return f"Webhook processed: {event['customer']}"


@app.route("/error6")
def error6():
    sentry_sdk.set_user(
        {
            "id": random.randint(1, 100),
            "email": "alex.sohn@sentry.io",
            "username": "alexsohn",
        }
    )
    # Simulate a race condition where inventory goes negative
    inventory = {"SKU-8812": 0}
    requested_qty = 3
    remaining = inventory["SKU-8812"] - requested_qty
    if remaining < 0:
        raise ValueError(
            f"Inventory underflow for SKU-8812: attempted to reserve {requested_qty} units but only 0 available (balance would be {remaining})"
        )
    return f"Reserved {requested_qty} units"


@app.route("/error7")
def error7():
    sentry_sdk.set_user(
        {
            "id": random.randint(1, 100),
            "email": "alex.sohn@sentry.io",
            "username": "alexsohn",
        }
    )
    # Simulate parsing a CSV export where a column was silently dropped
    rows = [
        ["order_id", "total", "currency", "region"],
        ["ORD-001", "149.99", "USD"],
        ["ORD-002", "89.50", "EUR", "eu-west"],
    ]
    headers = rows[0]
    for row in rows[1:]:
        record = dict(zip(headers, row))
        # raises KeyError on the row missing 'region'
        shipping_zone = record["region"].upper()

    return "Export parsed"


@app.route("/login", methods=["GET", "POST"])
def login():
    sentry_sdk.set_user(
        {
            "id": random.randint(1, 100),
            "email": "alex.sohn@sentry.io",
            "username": "alexsohn",
        }
    )
    # Simulate fetching user profile from OAuth provider callback
    oauth_response = {
        "sub": "google-oauth2|108234751629",
        "name": "Alex Sohn",
        "locale": "en",
        "updated_at": "2026-04-07T09:14:33Z",
        # 'email' field missing — org revoked email scope on the OAuth app
    }

    email = oauth_response["email"]
    return f"Welcome back, {email}"


@app.route("/txn")
def transaction():
    counter = 1
    with sentry_sdk.start_transaction(op="task", name="Test TXN"):
        with sentry_sdk.start_span(description="Test Span"):
            while counter < 10000:
                counter = counter + 1
        return "<h1>Test</h1>"


if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("PORT", 5000)))
