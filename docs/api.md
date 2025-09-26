# FileAgent API — /upload (JSON)

This document describes the JSON API used by FileAgent to translate incoming payloads into Snort rules and persist them.

## Overview

- Endpoint: `POST /upload`
- Content-Type: `application/json`
- Purpose: Accept a JSON payload describing a rule action. The payload is translated by `manager_snort.rule_translator`, validated for duplicates, appended to the rules file (`append_rule`) and recorded in history (`save_history`).

## Accepted payload shape

The translator used by FileAgent expects a small set of shapes. The most common fields are:

- `command` (string, required) — the high level action to take. See supported commands below.
- `target` (string, required) — the IP address (IPv4 or IPv6) or domain the command targets.
- `msg` (string, optional) — optional message text used in the generated Snort rule.
- `file` (string, optional) — metadata field used by some workflows; not required for translation.

Examples (minimal):

1. Alert on an IP (JSON sample file: `tests/manual/alert_ip.json`)

```json
{
  "file": "sample",
  "command": "alert_ip",
  "target": "10.1.39.20"
}
```

2. Block an IP (JSON sample file: `tests/manual/block_ip.json`)

```json
{
  "file": "sample",
  "command": "block_ip",
  "target": "10.1.39.20"
}
```

3. Block a domain (JSON sample file: `tests/manual/block_domain.json`)

```json
{
  "file": "Block Domain",
  "command": "block_domain",
  "target": "training.testserver.gr"
}
```

## Supported `command` values

The following commands are implemented (in `manager_snort.rule_translator`):

- `block_ip` — Build a Snort `block` rule for IP traffic (action `block`, protocol `ip`).
- `block_domain` — Build a Snort `block` rule targeting a domain (SNI / SSL-aware rule).
- `alert_ip` — Build a Snort `alert` rule for IP traffic (action `alert`, protocol `ip`).
- `block_icmp` — Build a Snort `block` rule for ICMP traffic.

Notes:

- The translator is permissive for the `target` type — it will accept IPv4, IPv6, and domain names where appropriate.
- If `rule_translator` cannot translate the provided payload (for example, unknown `command` or missing `target`) the request will be rejected with a 400 response.

## Endpoint behavior and responses

- `200 OK` — Rule successfully translated and persisted. The response body includes the translated rule string under the `rule` key.
- `400 Bad Request` — The payload is invalid, empty, or translation failed (missing/invalid fields).
- `409 Conflict` — A duplicate rule was detected (the rule already exists in the rules file); no change is made.
- `500 Internal Server Error` — A failure occurred while persisting the rule or saving history.

Example success response:

```json
{
  "message": "JSON payload received and processed",
  "rule": "alert ip 10.1.39.20 any -> $HOME_NET any (msg:\"IP Alert Incoming From IP 10.1.39.20\"; sid:28154103; rev:1;)"
}
```

## OpenAPI examples (seen in the running app)

The running FastAPI app contains examples that match the `tests/manual` samples:

- `alert_ip_sample` — alerts a single IPv4 host
- `block_ip_sample` — blocks a single IPv4 host
- `block_domain_sample` — blocks a domain via SNI/SSL rule

## How to call the endpoint

Using `curl` (replace host/port as needed):

```bash
curl -X POST "http://127.0.0.1:8000/upload" \
  -H "Content-Type: application/json" \
  -d '{"file":"sample","command":"alert_ip","target":"10.1.39.20"}'
```

Using the manual tester (provided):

```bash
python tests/manual/test_agent.py --host 127.0.0.1 --port 8000
```

Or pass specific files to the tester:

```bash
python tests/manual/test_agent.py --host 127.0.0.1 --port 8000 --files alert_ip.json block_ip.json
```

## Validation recommendations / future improvements

- Add stricter schema validation for `target` depending on the `command` (e.g., require domain vs IP for `block_domain`).
- Return the new `sid` assigned to the rule in the API response to make it easier to cross-reference rules.
- Provide an optional `dry_run` parameter that only runs translation and duplicate checks without persisting.

## Troubleshooting

- If you receive a `400` translation error, check the payload keys: `command` and `target` are mandatory for the translator used today.
- If the app returns `409`, inspect the rules file (configured in the agent) and the generated rule formatting — duplicate detection is currently string-based and may be conservative.

---

Document generated from code in `src/fileagent/managers/manager_snort.py` and manual test samples in `tests/manual`.
