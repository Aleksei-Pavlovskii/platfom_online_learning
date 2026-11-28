from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from lms.views import PaymentSuccessAPIView, PaymentCancelAPIView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('lms.urls', namespace='lms')),
    path('users/', include('users.urls', namespace='users')),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='docs'),
    path('payment/success/', PaymentSuccessAPIView.as_view(), name='payment-success'),
    path('payment/cancel/', PaymentCancelAPIView.as_view(), name='payment-cancel'),
]
