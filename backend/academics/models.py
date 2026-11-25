from django.db import models
from django.conf import settings


class Semester(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    name = models.CharField(max_length=100)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name


class Course(models.Model):
    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE,
        related_name="courses"
    )

    brightspace_id = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    code = models.CharField(max_length=30)
    name = models.CharField(max_length=200)
    instructor = models.CharField(max_length=150, blank=True)
    color = models.CharField(max_length=7, default="#3B82F6")

    is_active = models.BooleanField(default=True)
    can_access = models.BooleanField(default=True)

    home_url = models.URLField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["semester", "brightspace_id"],
                name="unique_semester_brightspace_course"
            )
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"


class GradeCategory(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="grade_categories"
    )

    brightspace_id = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    name = models.CharField(max_length=200)

    weight = models.DecimalField(
        max_digits=7,
        decimal_places=3,
        default=0
    )

    excluded = models.BooleanField(default=False)

    highest_to_drop = models.PositiveIntegerField(default=0)
    lowest_to_drop = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class GradeItem(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="grade_items"
    )

    category = models.ForeignKey(
        GradeCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="grade_items"
    )

    brightspace_id = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    name = models.CharField(max_length=250)

    max_points = models.DecimalField(
        max_digits=12,
        decimal_places=4
    )

    earned_points = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True
    )

    weight = models.DecimalField(
        max_digits=7,
        decimal_places=3,
        default=0
    )

    displayed_grade = models.CharField(
        max_length=50,
        blank=True
    )

    is_bonus = models.BooleanField(default=False)
    excluded = models.BooleanField(default=False)

    feedback = models.TextField(blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    @property
    def percentage(self):
        if self.earned_points is None or self.max_points == 0:
            return None

        return round(
            self.earned_points / self.max_points * 100,
            2
        )

    def __str__(self):
        return self.name


class Assignment(models.Model):
    class Status(models.TextChoices):
        UNKNOWN = "unknown", "Unknown"
        PENDING = "pending", "Pending"
        SUBMITTED = "submitted", "Submitted"
        GRADED = "graded", "Graded"
        MISSING = "missing", "Missing"

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="assignments"
    )

    grade_item = models.ForeignKey(
        GradeItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    brightspace_id = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)

    available_from = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    available_until = models.DateTimeField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.UNKNOWN
    )

    submission_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title


class CalendarEvent(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    external_id = models.CharField(max_length=500)

    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)

    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField(null=True, blank=True)

    all_day = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "external_id"],
                name="unique_user_calendar_event"
            )
        ]

    def __str__(self):
        return self.title
