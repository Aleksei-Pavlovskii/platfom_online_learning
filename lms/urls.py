from lms.apps import LmsConfig
from rest_framework.routers import DefaultRouter
from django.urls import path

from lms.views import (
    CourseViewSet,
    LessonListAPIView,
    LessonCreateAPIView,
    LessonUpdateAPIView,
    LessonDestroyAPIView,
    LessonRetrieveAPIView,
    UserRetrieveUpdateAPIView, PaymentListAPIView, UserPaymentRetrieveAPIView
)

app_name = LmsConfig.name

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='courses')

urlpatterns = [
                  path('lessons/', LessonListAPIView.as_view(), name='lessons-list'),
                  path('lessons/create/', LessonCreateAPIView.as_view(), name='lesson-create'),
                  path('lessons/<int:pk>/', LessonRetrieveAPIView.as_view(), name='lesson-retrieve'),
                  path('lessons/<int:pk>/update/', LessonUpdateAPIView.as_view(), name='lesson-update'),
                  path('lessons/<int:pk>/delete/', LessonDestroyAPIView.as_view(), name='lesson-delete'),
                  path('users/<int:pk>/', UserRetrieveUpdateAPIView.as_view(), name='user-retrieve-update'),
                  path('payments/', PaymentListAPIView.as_view(), name='payment-list'),
                  path('user/<int:pk>/payments/', UserPaymentRetrieveAPIView.as_view(), name='user-payment-retrieve'),
              ] + router.urls
