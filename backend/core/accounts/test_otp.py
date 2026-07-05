from unittest.mock import patch

from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import User, UserRole


@override_settings(
    OTP_LENGTH=6,
    OTP_EXPIRE_MINUTES=10,
    OTP_MAX_ATTEMPTS=3,
    OTP_RESEND_COOLDOWN_SECONDS=60,
)
class SignupOtpApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    @patch("accounts.views.SignupOtpService.send_email_otp")
    def test_send_otp_returns_expiry_metadata(self, mock_send):
        mock_send.return_value = {
            "email": "user@example.com",
            "expires_in_seconds": 600,
            "resend_cooldown_seconds": 60,
        }

        response = self.client.post(
            "/users/register/send-otp",
            {"email": "user@example.com"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "user@example.com")
        self.assertEqual(response.data["expires_in_seconds"], 600)
        mock_send.assert_called_once_with("user@example.com")

    def test_send_otp_rejects_registered_email(self):
        User.objects.create_user(
            email="user@example.com",
            password="SecurePass123!",
            role=UserRole.USER,
        )

        response = self.client.post(
            "/users/register/send-otp",
            {"email": "user@example.com"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    @patch("accounts.views.SignupOtpService.verify_email_otp")
    def test_verify_otp_success(self, mock_verify):
        mock_verify.return_value = True

        response = self.client.post(
            "/users/register/verify-otp",
            {"email": "user@example.com", "otp": "123456"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["verified"])
        self.assertEqual(response.data["email"], "user@example.com")

    @patch("accounts.views.SignupOtpService.verify_email_otp")
    def test_verify_otp_invalid_code(self, mock_verify):
        mock_verify.return_value = False

        response = self.client.post(
            "/users/register/verify-otp",
            {"email": "user@example.com", "otp": "123456"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)

    def test_verify_otp_rejects_non_digit_code(self):
        response = self.client.post(
            "/users/register/verify-otp",
            {"email": "user@example.com", "otp": "abcdef"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("otp", response.data)
