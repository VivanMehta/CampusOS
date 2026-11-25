import sys
from pathlib import Path
from datetime import datetime, time
from zoneinfo import ZoneInfo

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.dateparse import parse_datetime, parse_date

from academics.models import CalendarEvent

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from integrations.brightspace import get_events

User = get_user_model()
TIMEZONE = ZoneInfo("America/Edmonton")


class Command(BaseCommand):
    help = "Synchronize Brightspace calendar events"

    def add_arguments(self, parser):
        parser.add_argument("--username", required=True)

    def handle(self, *args, **options):
        username = options["username"]

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError("CampusOS user not found.")

        self.stdout.write("Connecting to Brightspace...")

        try:
            events = get_events()
        except Exception:
            raise CommandError(
                "Calendar synchronization failed. "
                "Check your calendar configuration."
            )

        created_count = 0
        updated_count = 0
        skipped_count = 0

        with transaction.atomic():
            for event in events:
                date_value = event["date"]
                all_day = len(date_value) == 10

                if all_day:
                    parsed_date = parse_date(date_value)

                    if parsed_date is None:
                        skipped_count += 1
                        continue

                    starts_at = datetime.combine(
                        parsed_date,
                        time.min,
                        tzinfo=TIMEZONE
                    )
                else:
                    starts_at = parse_datetime(date_value)

                    if starts_at is None:
                        skipped_count += 1
                        continue

                    if starts_at.tzinfo is None:
                        starts_at = starts_at.replace(
                            tzinfo=TIMEZONE
                        )

                if not event["id"]:
                    skipped_count += 1
                    continue

                obj, created = CalendarEvent.objects.update_or_create(
                    user=user,
                    external_id=event["id"],
                    defaults={
                        "title": event["title"],
                        "description": event["description"],
                        "starts_at": starts_at,
                        "all_day": all_day,
                    }
                )

                if created:
                    created_count += 1
                else:
                    updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                "\nCalendar synchronization complete."
            )
        )

        self.stdout.write(f"New events: {created_count}")
        self.stdout.write(f"Updated events: {updated_count}")
        self.stdout.write(f"Skipped events: {skipped_count}")
