from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from lms.models import Course, Lesson, Subscription
from lms.paginators import LmsPaginator
from lms.permissions import IsModeratorOrOwner, IsProfileOwnerOrAdmin
from lms.serializers import CourseSerializer, LessonSerializer, UserSerializer, PaymentSerializer, UserPaymentSerializer
from users.models import Payment
from lms.tasks import send_course_update_email


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


    def perform_update(self, serializer):
        course = serializer.save()
        send_course_update_email.delay(course.id)


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
        course = serializer.validated_data['course']
        if course.owner_id != self.request.user.id:
            raise PermissionDenied('Добавлять урок можно только в свой курс.')
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
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsProfileOwnerOrAdmin]

    def get_queryset(self):
        if self.request.user.is_staff:
            return User.objects.all()
        return User.objects.filter(pk=self.request.user.pk)

class PaymentListAPIView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()


    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['course', 'lesson', 'payment_method']
    ordering_fields = ('paid_at',)
    ordering = ['-paid_at']
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(user=user)


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


from lms.services.stripe_service import (
    create_stripe_product,
    create_stripe_price,
    create_stripe_checkout_session,
    retrieve_stripe_session,
)
from users.models import Payment


class PaymentCreateAPIView(APIView):
    """
    Создаёт продукт, цену, сессию в Stripe и сохраняет Payment.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        course_id = request.data.get('course_id')
        lesson_id = request.data.get('lesson_id')

        if not course_id and not lesson_id:
            return Response(
                {'error': 'Укажите course_id или lesson_id.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if course_id:
            from lms.models import Course
            item = Course.objects.filter(pk=course_id).first()
            if not item:
                return Response({'error': 'Курс не найден.'}, status=404)
            amount = item.price
            item_name = f'Курс: {item.title}'
            item_description = item.description or ''
            payment = Payment(user=request.user, course=item, amount=amount)
        else:
            from lms.models import Lesson
            item = Lesson.objects.filter(pk=lesson_id).first()
            if not item:
                return Response({'error': 'Урок не найден.'}, status=404)
            amount = item.price
            item_name = f'Урок: {item.title}'
            item_description = item.description or ''
            payment = Payment(user=request.user, lesson=item, amount=amount)

        # 1. Продукт
        product = create_stripe_product(name=item_name, description=item_description)

        # 2. Цена (в центах!)
        price = create_stripe_price(
            product_id=product['id'],
            amount=int(amount * 100),
            currency=settings.STRIPE_CURRENCY,
        )

        # 3. Сессия
        session = create_stripe_checkout_session(
            price_id=price['id'],
            success_url=settings.STRIPE_SUCCESS_URL,
            cancel_url=settings.STRIPE_CANCEL_URL,
            metadata={'payment_user_id': request.user.id},
        )

        # 4. Сохраняем Payment
        payment.stripe_product_id = product['id']
        payment.stripe_price_id = price['id']
        payment.stripe_session_id = session['id']
        payment.payment_url = session['url']
        payment.payment_method = Payment.STRIPE
        payment.save()

        return Response({
            'payment_id': payment.id,
            'amount': str(payment.amount),
            'payment_url': payment.payment_url,
            'session_id': payment.stripe_session_id,
        }, status=status.HTTP_201_CREATED)


class PaymentStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Статус платежа',
        description='Получает статус Stripe-сессии и синхронизирует paid_at в локальной модели.',
        parameters=[
            OpenApiParameter('pk', OpenApiTypes.INT, OpenApiParameter.PATH, description='ID платежа'),
        ],
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'payment_id': {'type': 'integer'},
                    'stripe_status': {'type': 'string', 'example': 'complete'},
                    'stripe_payment_status': {'type': 'string', 'example': 'paid'},
                    'paid_at': {'type': 'string', 'format': 'date-time', 'nullable': True},
                },
            },
            404: {'description': 'Платёж не найден'},
        },
    )

    def get(self, request, pk):
        payment = Payment.objects.filter(pk=pk, user=request.user).first()
        if not payment:
            return Response({'error': 'Платёж не найден.'}, status=404)
        if not payment.stripe_session_id:
            return Response({'error': 'У платежа нет Stripe-сессии.'}, status=400)

        session_data = retrieve_stripe_session(payment.stripe_session_id)

        if session_data['payment_status'] == 'paid' and not payment.paid_at:
            payment.paid_at = timezone.now()
            payment.save(update_fields=['paid_at'])

        return Response({
            'payment_id': payment.id,
            'stripe_status': session_data['status'],
            'stripe_payment_status': session_data['payment_status'],
            'paid_at': payment.paid_at,
        })

class PaymentSuccessAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Успешная оплата',
        description='Callback после успешной оплаты Stripe. Синхронизирует paid_at.',
        parameters=[
            OpenApiParameter('session_id', OpenApiTypes.STR, OpenApiParameter.QUERY,
                             description='ID Stripe-сессии', required=False),
        ],
        responses={200: {'description': 'Оплата успешна'}},
    )

    def get(self, request):
        session_id = request.query_params.get('session_id')
        if not session_id:
            return Response({'message': 'Оплата прошла успешно!'})

        payment = Payment.objects.filter(stripe_session_id=session_id).first()
        if not payment:
            return Response({
                'message': 'Оплата прошла успешно, но платёж не найден в системе.',
                'session_id': session_id,
            })

        from lms.services.stripe_service import retrieve_stripe_session
        session_data = retrieve_stripe_session(session_id)
        if session_data['payment_status'] == 'paid' and not payment.paid_at:
            payment.paid_at = timezone.now()
            payment.save(update_fields=['paid_at'])

        return Response({
            'message': 'Оплата прошла успешно!',
            'session_id': session_id,
            'stripe_payment_status': session_data['payment_status'],
            'paid_at': payment.paid_at,
        })


class PaymentCancelAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({'message': 'Оплата отменена.'})