import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.dateparse import parse_datetime

from academics.models import (
    Course,
    GradeCategory,
    GradeItem,
    Assignment,
)


ROOT = Path(__file__).resolve().parents[4]


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        raise CommandError(f"Unable to read {path.name}")


def read_date(value):
    return parse_datetime(value) if value else None


class Command(BaseCommand):
    help = "Import Brightspace grades and assignments"

    def add_arguments(self, parser):
        parser.add_argument("--username", required=True)
        parser.add_argument("--course", required=True, type=int)

    @transaction.atomic
    def handle(self, *args, **options):
        User = get_user_model()

        try:
            user = User.objects.get(
                username=options["username"]
            )

            course = Course.objects.get(
                semester__user=user,
                brightspace_id=options["course"]
            )

        except (User.DoesNotExist, Course.DoesNotExist):
            raise CommandError("User or course not found.")

        folder = (
            ROOT / "private" / "brightspace"
            / str(course.brightspace_id)
        )

        grades = read_json(folder / "grades.json")
        categories = read_json(folder / "categories.json")
        assignments = read_json(folder / "assignments.json")

        grade_values = {
            str(item["GradeObjectIdentifier"]): item
            for item in grades
        }

        grade_objects = {}
        imported_categories = 0
        imported_grades = 0
        imported_assignments = 0

        self.stdout.write(f"Importing {course.code}...")

        for category_data in categories:

            category, _ = GradeCategory.objects.update_or_create(
                course=course,
                brightspace_id=category_data["Id"],
                defaults={
                    "name": category_data["Name"],
                    "weight": category_data.get("Weight") or 0,
                    "excluded": category_data.get(
                        "ExcludeFromFinalGrade", False
                    ),
                    "highest_to_drop": category_data.get(
                        "NumberOfHighestToDrop"
                    ) or 0,
                    "lowest_to_drop": category_data.get(
                        "NumberOfLowestToDrop"
                    ) or 0,
                }
            )

            imported_categories += 1

            for item in category_data.get("Grades", []):

                if item.get("IsHidden"):
                    continue

                value = grade_values.get(str(item["Id"]), {})

                grade, _ = GradeItem.objects.update_or_create(
                    course=course,
                    brightspace_id=item["Id"],
                    defaults={
                        "category": category,
                        "name": item["Name"],
                        "max_points": item.get("MaxPoints") or 0,
                        "earned_points": value.get(
                            "PointsNumerator"
                        ),
                        "weight": item.get("Weight") or 0,
                        "displayed_grade": str(
                            value.get("DisplayedGrade") or ""
                        ),
                        "is_bonus": item.get("IsBonus", False),
                        "excluded": item.get(
                            "ExcludeFromFinalGradeCalculation",
                            False
                        ),
                        "feedback": (
                            value.get("Comments") or {}
                        ).get("Text") or (
                            value.get("Comments") or {}
                        ).get("Html") or "",
                    }
                )

                grade_objects[item["Id"]] = grade
                imported_grades += 1

        for item in assignments:

            if item.get("IsHidden"):
                continue

            grade_item = grade_objects.get(
                item.get("GradeItemId")
            )

            status = Assignment.Status.UNKNOWN

            if (
                grade_item
                and grade_item.earned_points is not None
            ):
                status = Assignment.Status.GRADED

            availability = item.get("Availability") or {}
            instructions = item.get("CustomInstructions") or {}

            Assignment.objects.update_or_create(
                course=course,
                brightspace_id=item["Id"],
                defaults={
                    "grade_item": grade_item,
                    "title": item["Name"],
                    "description": (
                        instructions.get("Text")
                        or instructions.get("Html")
                        or ""
                    ),
                    "available_from": read_date(
                        availability.get("StartDate")
                    ),
                    "due_date": read_date(
                        item.get("DueDate")
                    ),
                    "available_until": read_date(
                        availability.get("EndDate")
                    ),
                    "status": status,
                }
            )

            imported_assignments += 1

        self.stdout.write(
            self.style.SUCCESS("\nAcademic import complete.")
        )

        self.stdout.write(
            f"Grade categories: {imported_categories}"
        )
        self.stdout.write(
            f"Grade items: {imported_grades}"
        )
        self.stdout.write(
            f"Assignments: {imported_assignments}"
        )
