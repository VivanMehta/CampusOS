from rest_framework.routers import DefaultRouter

from .views import (
    SemesterViewSet,
    CourseViewSet,
    GradeCategoryViewSet,
    GradeItemViewSet,
    AssignmentViewSet,
    CalendarEventViewSet,
)

router = DefaultRouter()

router.register("semesters", SemesterViewSet, basename="semester")
router.register("courses", CourseViewSet, basename="course")
router.register("categories", GradeCategoryViewSet, basename="category")
router.register("grades", GradeItemViewSet, basename="grade")
router.register("assignments", AssignmentViewSet, basename="assignment")
router.register("calendar", CalendarEventViewSet, basename="calendar")

urlpatterns = router.urls
