# 0005: Google access (Gmail and Calendar)

- Status: accepted (decided in `docs/phases/phase-0.md`)
- Date: 2026-09-26
- Phase: 0, task 0.6

## Context

Ariel reads and drafts mail and reads the calendar. Following "API, then structure, then pixels", these go through Google's APIs, not the Gmail web page. Something has to hold OAuth credentials, request scopes and call the APIs, and the Phase 1 skills will call it directly.

## Options

1. **Google's official Python client** (`google-api-python-client`, `google-auth-oauthlib`), wrapped by `hands/google_auth.py` and `hands/google.py`.
2. **A third-party Gmail or Calendar MCP server.**

## Decision

Option 1:

- It has fewer moving parts: no extra server process, and no third party holding the owner's tokens.
- Scopes can be least privilege: `gmail.readonly`, `gmail.compose` (drafts, and sending once the gate controls it from Phase 1) and `calendar.readonly`.
- It is what the Phase 1 skills will call, as deterministic code.

The OAuth client is a "Desktop app" in a Google Cloud project named "ariel", with its consent screen in Testing mode and the owner as the only test user. The client file lives in `secrets/google_client.json` (gitignored). The OAuth token is stored in Windows Credential Manager through `keyring`, never as a file.

## Consequences

- In Testing mode, Google refresh tokens expire after about seven days. `ariel doctor` detects an expired token and tells the owner to sign in again. Publishing the app, or moving it to "In production", would remove the expiry but needs Google's verification for Gmail scopes. That can wait.
- `gmail.compose` technically allows sending. The code in Phase 0 only creates drafts, and from Phase 1 every send goes through the safety gate with owner confirmation.
- No MCP server is involved, so Gmail and Calendar calls do not appear in `docs/tools/`. Their functions are documented in `hands/google.py`.
