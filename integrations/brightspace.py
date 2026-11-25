import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import requests
from icalendar import Calendar
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

CALENDAR_URL = os.getenv("D2L_CALENDAR_URL")
TIMEZONE = ZoneInfo("America/Edmonton")


def fetch_calendar():
    if not CALENDAR_URL:
        raise ValueError("D2L_CALENDAR_URL is missing from .env")

    url = CALENDAR_URL

    if url.startswith("webcal://"):
        url = "https://" + url[len("webcal://"):]

    try:
        response = requests.get(url, timeout=30)
    except requests.RequestException:
        raise RuntimeError("Could not connect to calendar feed.") from None

    if response.status_code != 200:
        raise RuntimeError(
            f"Calendar returned HTTP {response.status_code}"
        )

    return Calendar.from_ical(response.content)


def get_events():
    calendar = fetch_calendar()
    events = []

    for component in calendar.walk("VEVENT"):
        start = component.decoded("DTSTART")

        if isinstance(start, datetime) and start.tzinfo:
            start = start.astimezone(TIMEZONE)

        events.append({
            "id": str(component.get("UID", "")),
            "title": str(component.get("SUMMARY", "Untitled")),
            "date": start.isoformat(),
            "description": str(component.get("DESCRIPTION", "")),
        })

    events.sort(key=lambda event: event["date"])
    return events


if __name__ == "__main__":
    events = get_events()
    today = datetime.now(TIMEZONE).date().isoformat()

    upcoming = [
        event for event in events
        if event["date"][:10] >= today
    ]

    print("\n=== CampusOS | Brightspace Integration ===\n")
    print(f"Total calendar events: {len(events)}")
    print(f"Upcoming events: {len(upcoming)}\n")

    for event in upcoming:
        print(event["title"])
        print(f"  Date: {event['date']}")
        print()

    print("Calendar synchronization successful.")
