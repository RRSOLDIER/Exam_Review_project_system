Scholarship Examination System

Description:
This is a Django-based online examination system developed as part of a training project.
The system supports student registration, OTP-based authentication, and online exams.

Features:
- Student registration with academic details
- OTP-based login (no password)
- OTP expiry and attempt limit for security
- Online examination with resume support
- Automatic score calculation and result display

OTP Handling:
- OTP is generated and validated securely
- OTP expires after 5 minutes
- Maximum 5 verification attempts allowed
- SMS sending is mocked for demo purposes

SMS Note:
Actual SMS gateway integration is intentionally not included.
The SMS provider can be selected and integrated as per organization or client preference.

Technology Stack:
- Python
- Django
- SQLite
- HTML, CSS, JavaScript

Note:
No third-party credentials or API keys are included in this project.
