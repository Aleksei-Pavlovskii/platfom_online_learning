from django.contrib.auth import get_user_model
from rest_framework import serializers

from lms.models import Course, Lesson
from lms.models import Subscription
from lms.validators import YouTubeUrlValidator
from users.models import Payment

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'phone',
            'city',
            'avatar'
        ]
        read_only_fields = ['id', 'email']


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'
        read_only_fields = ['owner']
        validators = [YouTubeUrlValidator(field='video_url')]


class CourseSerializer(serializers.ModelSerializer):
    count_lessons = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = '__all__'
        read_only_fields = ['owner']


    def get_count_lessons(self, obj):
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        user = request.user if request else None
        if not user or not user.is_authenticated:
            return False

        return Subscription.objects.filter(user=user, course=obj).exists()


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'


class UserPaymentSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'phone',
            'city',
            'avatar',
            'payments',
        ]
        read_only_fields = ['id', 'email']
