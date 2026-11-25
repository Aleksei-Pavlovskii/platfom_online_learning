from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, generics, status
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from lms.models import Course, Lesson, Subscription
from lms.paginators import LmsPaginator
from lms.permissions import IsModeratorOrOwner, IsProfileOwnerOrAdmin
from lms.serializers import CourseSerializer, LessonSerializer, UserSerializer, PaymentSerializer, UserPaymentSerializer
from users.models import Payment


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    permission_classes = [IsAuthenticated, IsModeratorOrOwner]

    pagination_class = LmsPaginator

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
    pagination_class = LmsPaginator


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
    permission_classes = [IsAuthenticated, IsProfileOwnerOrAdmin]


class SubscriptionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get('course_id')
        if not course_id:
            return Response(
                {'error': 'Поле course_id обязательно.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        course_item = get_object_or_404(Course, pk=course_id)

        subs_item = Subscription.objects.filter(user=user, course=course_item)

        if subs_item.exists():
            subs_item.delete()
            message = 'Подписка удалена'
            subscribed = False
        else:
            Subscription.objects.create(user=user, course=course_item)
            message = 'Подписка добавлена'
            subscribed = True

        return Response({'message': message, 'subscribed': subscribed})
