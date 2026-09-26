"""Gmail and Calendar adapter over Google's official API client (read calls and drafts only).

Nothing here sends mail. Sending arrives in Phase 1, behind the safety gate.
"""

import base64
from datetime import datetime, time, timedelta
from email.message import EmailMessage

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from pydantic import BaseModel


class MailSummary(BaseModel):
    sender: str
    subject: str


class CalendarEvent(BaseModel):
    summary: str
    start: str
    end: str


def owner_address(credentials: Credentials) -> str:
    """The signed-in owner's Gmail address."""
    gmail = build("gmail", "v1", credentials=credentials, cache_discovery=False)
    return gmail.users().getProfile(userId="me").execute()["emailAddress"]


def latest_inbox(credentials: Credentials, count: int = 5) -> list[MailSummary]:
    """Sender and subject of the newest mails in the inbox."""
    gmail = build("gmail", "v1", credentials=credentials, cache_discovery=False)
    listing = gmail.users().messages().list(userId="me", labelIds=["INBOX"], maxResults=count)
    summaries = []
    for item in listing.execute().get("messages", []):
        message = (
            gmail.users()
            .messages()
            .get(userId="me", id=item["id"], format="metadata", metadataHeaders=["From", "Subject"])
            .execute()
        )
        headers = {h["name"]: h["value"] for h in message["payload"].get("headers", [])}
        summaries.append(
            MailSummary(sender=headers.get("From", ""), subject=headers.get("Subject", ""))
        )
    return summaries


def todays_events(credentials: Credentials) -> list[CalendarEvent]:
    """Events on the owner's primary calendar today, in local time."""
    calendar = build("calendar", "v3", credentials=credentials, cache_discovery=False)
    start = datetime.combine(datetime.now().date(), time.min).astimezone()
    events = (
        calendar.events()
        .list(
            calendarId="primary",
            timeMin=start.isoformat(),
            timeMax=(start + timedelta(days=1)).isoformat(),
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    return [
        CalendarEvent(
            summary=event.get("summary", "(no title)"),
            start=event["start"].get("dateTime", event["start"].get("date", "")),
            end=event["end"].get("dateTime", event["end"].get("date", "")),
        )
        for event in events.get("items", [])
    ]


def create_draft(credentials: Credentials, to: str, subject: str, body: str) -> str:
    """Save a draft in Gmail and return its id. The draft is not sent."""
    message = EmailMessage()
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    gmail = build("gmail", "v1", credentials=credentials, cache_discovery=False)
    draft = gmail.users().drafts().create(userId="me", body={"message": {"raw": raw}}).execute()
    return draft["id"]
