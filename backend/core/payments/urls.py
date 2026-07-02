from django.urls import path

from payments.views import PaymentVerifyView

urlpatterns = [
    path("verify/", PaymentVerifyView.as_view(), name="payment-verify"),
]
