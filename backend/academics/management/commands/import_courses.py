import json
import re
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.dateparse import parse_datetime

from academics.models import Semester, Course, CalendarEvent


ROOT = Path(__file__).resolve().parents[4]

COLORS = [
    "#818CF8",
    "#22C55E",
    "#38BDF8",
    "#F59E0B",
    "#F472B6",
    "#A78BFA",
    "#14B8A6",
    "#EF4444",
]


class Command(BaseCommand):
    help = "Import Brightspace courses from a local JSON export"

    def add_arguments(self, parser):
        parser.add_argument("--username", required=True)

    def handle(self, *args, **options):
        User = get_user_model()

        try:
            user = User.objects.get(
                username=options["username"]
            )
        except User.DoesNotExist:
            raise CommandError("CampusOS user not found.")

        file_path = ROOT / "private" / "brightspace" / "courses.json"

        if not file_path.exists():
            raise CommandError("courses.json was not found.")

        try:
            data = json.loads(
                file_path.read_text(encoding="utf-8-sig")
            )
        except (ValueError, OSError):
            raise CommandError("Unable to read courses.json.")

        items = data.get("Items", [])

        created_count = 0
        updated_count = 0
        skipped_count = 0
        linked_count = 0

        with transaction.atomic():
            for item in items:
                org = item.get("OrgUnit", {})
                access = item.get("Access", {})

                if org.get("Type", {}).get("Id") != 3:
                    skipped_count += 1
                    continue

                full_name = org.get("Name", "")

                semester_match = re.match(
                    r"^(Fall|Winter|Spring|Summer)\s+\d{4}",
                    full_name,
                    re.IGNORECASE
                )

                semester_name = (
                    semester_match.group(0)
                    if semester_match
                    else "Other Courses"
                )

                semester, _ = Semester.objects.get_or_create(
                    user=user,
                    name=semester_name
                )

                code_match = re.search(
                    r"\(([A-Z]+-\d+)[^)]*\)$",
                    full_name
                )

                course_code = (
                    code_match.group(1).replace("-", " ")
                    if code_match
                    else org.get("Code", "")
                )

                course_name = re.sub(
                    r"^(Fall|Winter|Spring|Summer)\s+\d{4}\s+",
                    "",
                    full_name,
                    flags=re.IGNORECASE
                )

                course_name = re.sub(
                    r"\s*\([^)]*\)$",
                    "",
                    course_name
                ).strip()

                start = parse_datetime(
                    access["StartDate"]
                ) if access.get("StartDate") else None

                end = parse_datetime(
                    access["EndDate"]
                ) if access.get("EndDate") else None

                if start:
                    if (
                        semester.start_date is None
                        or start.date() < semester.start_date
                    ):
                        semester.start_date = start.date()

                if end:
                    if (
                        semester.end_date is None
                        or end.date() > semester.end_date
                    ):
                        semester.end_date = end.date()

                semester.save()

                course, created = Course.objects.update_or_create(
                    semester=semester,
                    brightspace_id=org["Id"],
                    defaults={
                        "code": course_code,
                        "name": course_name,
                        "is_active": access.get("IsActive", False),
                        "can_access": access.get("CanAccess", False),
                        "home_url": org.get("HomeUrl") or "",
                    }
                )

                if created:
                    course.color = COLORS[
                        created_count % len(COLORS)
                    ]
                    course.save(update_fields=["color"])
                    created_count += 1
                else:
                    updated_count += 1

                self.stdout.write(
                    f"{semester_name} | {course.code} | {course.name}"
                )

            courses = {
                course.brightspace_id: course
                for course in Course.objects.filter(
                    semester__user=user
                )
            }

            events = CalendarEvent.objects.filter(user=user)

            for event in events:
                match = re.search(
                    r"[?&]ou=(\d+)",
                    event.description
                )

                if not match:
                    continue

                course_id = int(match.group(1))
                course = courses.get(course_id)

                if course and event.course_id != course.id:
                    event.course = course
                    event.save(update_fields=["course"])
                    linked_count += 1

        self.stdout.write(
            self.style.SUCCESS("\nCourse import complete.")
        )

        self.stdout.write(f"New courses: {created_count}")
        self.stdout.write(f"Updated courses: {updated_count}")
        self.stdout.write(f"Skipped non-course entries: {skipped_count}")
        self.stdout.write(f"Calendar events linked: {linked_count}")
