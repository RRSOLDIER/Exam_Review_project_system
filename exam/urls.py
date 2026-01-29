from django.urls import path
from .views import register, otp_login, otp_verify, start_exam, submit_exam, save_answer,check_user

urlpatterns = [
    path('', register, name='register'),   # 👈 THIS FIXES IT
    path('check-user/', check_user, name='check_user'),
    path('login/', otp_login, name='otp_login'),
    path('otp/', otp_verify, name='otp_verify'),
    path('exam/', start_exam, name='start_exam'),
    path('submit/', submit_exam, name='submit_exam'),
    path('save-answer/', save_answer, name='save_answer'),
]

