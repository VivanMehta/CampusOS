from rest_framework import serializers

from .models import (
    Semester,
    Course,
    GradeCategory,
    GradeItem,
    Assignment,
    CalendarEvent,
)


class GradeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GradeCategory
        fields = "__all__"


class GradeItemSerializer(serializers.ModelSerializer):
    percentage = serializers.ReadOnlyField()

    class Meta:
        model = GradeItem
        fields = "__all__"


class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = "__all__"


class CalendarEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalendarEvent
        fields = "__all__"


class CourseSerializer(serializers.ModelSerializer):
    grade_categories = GradeCategorySerializer(many=True, read_only=True)
    grade_items = GradeItemSerializer(many=True, read_only=True)
    assignments = AssignmentSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = "__all__"


class SemesterSerializer(serializers.ModelSerializer):
    courses = CourseSerializer(many=True, read_only=True)

    class Meta:
        model = Semester
        fields = "__all__"
        read_only_fields = ["user"]
