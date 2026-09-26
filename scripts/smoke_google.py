"""Google smoke test (task 0.6): read Gmail and Calendar, and create one draft that is not sent.

Run with: uv run python scripts/smoke_google.py
The first run opens the browser for Google sign-in. Later runs reuse the refresh token stored
in Windows Credential Manager. The owner checks the draft in Gmail and deletes it by hand.
"""

from ariel.hands.google import create_draft, latest_inbox, owner_address, todays_events
from ariel.hands.google_auth import GoogleAuthError, load_credentials, sign_in

DRAFT_SUBJECT = "Ariel phase 0 draft"
DRAFT_BODY = "Created by scripts/smoke_google.py to test drafts. It was not sent; delete it."

if __name__ == "__main__":
    try:
        credentials = load_credentials()
    except GoogleAuthError as exc:
        print(f"{exc}\nOpening the browser to sign in...")
        credentials = sign_in()

    print("Five latest inbox mails:")
    for mail in latest_inbox(credentials, 5):
        print(f"  {mail.subject}  (from {mail.sender})")

    events = todays_events(credentials)
    print(f"Today's calendar events: {len(events)}")
    for event in events:
        print(f"  {event.start} to {event.end}: {event.summary}")

    address = owner_address(credentials)
    draft_id = create_draft(credentials, address, DRAFT_SUBJECT, DRAFT_BODY)
    print(f'Draft "{DRAFT_SUBJECT}" to {address} created (id {draft_id}). It was NOT sent.')
    print("Check it in Gmail's Drafts folder, then delete it yourself.")
