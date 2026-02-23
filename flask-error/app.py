import argparse
from datetime import datetime

import sentry_sdk
from flask import Flask
from sentry_sdk.integrations.flask import FlaskIntegration

LOCAL_SENTRY_DSN = (
    "https://c6b8c6c21bad812e48e2d115968a55e5@alexsohn.ngrok.io/3"  # robots
)
LOCAL_SENTRY_DSN = (
    "https://87bca3472b590976a030e0e6456b72cc@alexsohn.ngrok.io/2"  # humans
)
LOCAL_GETSENTRY_DSN = (
    "https://287a7215db7931a63e5d7a2f62506f9a@alexsohn.ngrok.io/4506974030528528"
)

# devsentry-ecosystem
ECOSYSTEM_DSN = "https://234c699ac7f8b1dfd98765149a65b9fd@o4506792933130240.ingest.us.sentry.io/4509407223152640"
# sentry-alex-eu // legacy-data-forwarding
LEGACY_DATA_FORWARD_DSN = "https://2e0ab03d072b9e54174406624fbf4ecc@o4509708210274304.ingest.de.sentry.io/4510358464954448"

# sentry-alex // all-robots
SENTRY_ALEX_DSN = "https://567e5289194ac1e211357003733f1894@o951660.ingest.us.sentry.io/4510818206810112"
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
        "ecosystem",
        "alex",
        "temp",
        "work-funnel",
    ],
    help="Sentry instance to receive errors",
)


def dsn_selector():
    args = parser.parse_args()
    print(f"Sending errors to '{args.instance}' instance...")
    if args.instance == "getsentry":
        return LOCAL_GETSENTRY_DSN
    elif args.instance == "lxyz2":
        return LXYZ2_DSN
    elif args.instance == "ecosystem":
        return ECOSYSTEM_DSN
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
            "id": 12,
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


@app.route("/txn")
def transaction():
    counter = 1
    with sentry_sdk.start_transaction(op="task", name="Test TXN"):
        with sentry_sdk.start_span(description="Test Span"):
            while counter < 10000:
                counter = counter + 1
        return "<h1>Test</h1>"


if __name__ == "__main__":
    app.run(debug=True)
