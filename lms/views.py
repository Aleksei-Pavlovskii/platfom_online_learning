from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, generics
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated

from lms.models import Course, Lesson
from lms.permissions import IsModeratorOrOwner
from lms.serializers import CourseSerializer, LessonSerializer, UserSerializer, PaymentSerializer, UserPaymentSerializer
from users.models import Payment


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    permission_classes = [IsAuthenticated, IsModeratorOrOwner]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.groups.filter(name='Moderators').exists():
            return Course.objects.all()
        return Course.objects.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonBaseAPIView(generics.GenericAPIView):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModeratorOrOwner]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.groups.filter(name='Moderators').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)


class LessonCreateAPIView(LessonBaseAPIView, generics.CreateAPIView):
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonListAPIView(LessonBaseAPIView, generics.ListAPIView):
    pass


class LessonRetrieveAPIView(LessonBaseAPIView, generics.RetrieveAPIView):
    pass


class LessonUpdateAPIView(LessonBaseAPIView, generics.UpdateAPIView):
    pass


class LessonDestroyAPIView(LessonBaseAPIView, generics.DestroyAPIView):
    pass


User = get_user_model()


class UserRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class PaymentListAPIView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['course', 'lesson', 'payment_method']
    ordering_fields = ('paid_at',)
    ordering = ['-paid_at']


class UserPaymentRetrieveAPIView(generics.RetrieveAPIView):
    queryset = User.objects.prefetch_related('payments')
    serializer_class = UserPaymentSerializer
