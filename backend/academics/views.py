from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import (
    Semester,
    Course,
    GradeCategory,
    GradeItem,
    Assignment,
    CalendarEvent,
)

from .serializers import (
    SemesterSerializer,
    CourseSerializer,
    GradeCategorySerializer,
    GradeItemSerializer,
    AssignmentSerializer,
    CalendarEventSerializer,
)


class SemesterViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SemesterSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Semester.objects.filter(
            user=self.request.user
        ).prefetch_related(
            "courses__grade_items",
            "courses__grade_categories",
            "courses__assignments",
        )


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Course.objects.filter(
            semester__user=self.request.user
        ).prefetch_related(
            "grade_categories",
            "grade_items",
            "assignments",
        )


class GradeCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = GradeCategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return GradeCategory.objects.filter(
            course__semester__user=self.request.user
        )


class GradeItemViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = GradeItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return GradeItem.objects.filter(
            course__semester__user=self.request.user
        )


class AssignmentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AssignmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Assignment.objects.filter(
            course__semester__user=self.request.user
        ).order_by("due_date")


class CalendarEventViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CalendarEventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CalendarEvent.objects.filter(
            user=self.request.user
        ).order_by("starts_at")
