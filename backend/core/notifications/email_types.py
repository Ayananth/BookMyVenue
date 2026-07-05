from dataclasses import dataclass


@dataclass(frozen=True)
class EmailTemplate:
    subject: str
    html_template: str
    text_template: str


EMAIL_TEMPLATES: dict[str, EmailTemplate] = {
    "otp_verification": EmailTemplate(
        subject="Your {app_name} verification code",
        html_template="emails/otp_verification.html",
        text_template="emails/otp_verification.txt",
    ),
}
