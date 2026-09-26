"""Google sign-in adapter: the desktop OAuth flow, with the token kept in Credential Manager.

Only the refresh token is stored, through keyring, because Windows Credential Manager caps a
secret at 2,560 bytes. The OAuth client comes from secrets/google_client.json, and a fresh
access token is fetched on every run. No token is ever written to disk.
"""

import json
from pathlib import Path

import keyring
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from ariel.config import REPO_ROOT, load_config

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/calendar.readonly",
]
KEYRING_SERVICE = "ariel-google"
KEYRING_USER = "refresh-token"


class GoogleAuthError(Exception):
    """Ariel cannot get Google credentials; the message says what the owner should do."""


def client_file() -> Path:
    """The OAuth client JSON downloaded from Google Cloud Console."""
    return REPO_ROOT / load_config().paths.secrets / "google_client.json"


def sign_in() -> Credentials:
    """Open the browser for Google sign-in and store the refresh token in Credential Manager."""
    path = client_file()
    if not path.exists():
        raise GoogleAuthError(f"OAuth client file missing: download it to {path}")
    flow = InstalledAppFlow.from_client_secrets_file(str(path), SCOPES)
    credentials = flow.run_local_server(port=0, prompt="consent")
    if not credentials.refresh_token:
        raise GoogleAuthError("Google returned no refresh token; sign in again.")
    keyring.set_password(KEYRING_SERVICE, KEYRING_USER, credentials.refresh_token)
    return credentials


def load_credentials() -> Credentials:
    """Credentials from the stored refresh token, refreshed now so an expired token shows up."""
    refresh_token = keyring.get_password(KEYRING_SERVICE, KEYRING_USER)
    if not refresh_token:
        raise GoogleAuthError(
            "Not signed in to Google: run `uv run python scripts/smoke_google.py`."
        )
    client = json.loads(client_file().read_text(encoding="utf-8"))["installed"]
    credentials = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri=client["token_uri"],
        client_id=client["client_id"],
        client_secret=client["client_secret"],
        scopes=SCOPES,
    )
    try:
        credentials.refresh(Request())
    except RefreshError as exc:
        raise GoogleAuthError(
            "Google sign-in has expired (Testing mode tokens last about seven days): "
            "run `uv run python scripts/smoke_google.py` to sign in again."
        ) from exc
    return credentials
