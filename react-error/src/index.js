import React from "react";
import ReactDOM from "react-dom";
import * as Sentry from "@sentry/react";
// import * as FullStory from "@fullstory/browser";
// import SentryFullStory from "@sentry/fullstory";
import { Integrations as TracingIntegrations } from "@sentry/tracing";
import "./index.css";
import App from "./App";

// FullStory.init({ orgId: "164KVD" });

Sentry.init({
  dsn: "https://4bb8adf9789742c590395533a427a0e1@alexsohn.ngrok.io/8",
  integrations: [
    // new SentryFullStory("alex-test"),
    new TracingIntegrations.BrowserTracing({
      tracingOrigins: ["localhost", "catfact.ninja", /^\//],
      shouldCreateSpanForRequest: (_url) => true,
    }),
  ],
  tracesSampleRate: 1.0,
});

Sentry.setContext("session_id", "12123");

ReactDOM.render(<App />, document.getElementById("root"));
