import random
from datetime import timedelta

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
import json
from django.views.decorators.csrf import csrf_exempt

from .models import (
    StudentProfile,
    Question,
    ExamSession,
    OTP,
    StudentAnswer,
    College,
    Branch,
    YearOfPassing
)

# =========================
# CONFIG
# =========================
OTP_EXPIRY_MINUTES = 5
MAX_OTP_ATTEMPTS = 5

# =========================
# HELPERS
# =========================
def normalize_phone(phone):
    if not phone:
        return phone
    return phone.replace("+91", "").replace(" ", "").strip()


def send_sms(phone, message):
    """
    Placeholder SMS sender.
    Company will replace this function with
    their selected SMS gateway integration.
    """
    print(f"[SMS MOCK] {phone} -> {message}")


# =========================
# AJAX CHECK (EMAIL / PHONE)
# =========================
def check_user(request):
    email = request.GET.get("email")
    phone = request.GET.get("phone")

    data = {
        "email_exists": False,
        "phone_exists": False
    }

    if email:
        data["email_exists"] = User.objects.filter(email=email).exists()

    if phone:
        phone = normalize_phone(phone)
        data["phone_exists"] = (
            User.objects.filter(username=phone).exists() or
            StudentProfile.objects.filter(phone=phone).exists()
        )

    return JsonResponse(data)


# =========================
# REGISTER
# =========================
def register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = normalize_phone(request.POST.get('phone'))

        college_id = request.POST.get('college')
        branch_id = request.POST.get('branch')
        qualification = request.POST.get('qualification')
        passing_date = request.POST.get('year_of_passing')

        errors = []

        if User.objects.filter(username=phone).exists() or \
           StudentProfile.objects.filter(phone=phone).exists():
            errors.append("Phone number already exists")

        if User.objects.filter(email=email).exists():
            errors.append("Email ID already exists")

        if not passing_date:
            errors.append("Please select Year of Passing")

        if errors:
            for err in errors:
                messages.error(request, err)
            return redirect('register')

        try:
            year_value = int(passing_date.split('-')[0])
        except (ValueError, IndexError):
            messages.error(request, "Invalid date selected")
            return redirect('register')

        year_obj, _ = YearOfPassing.objects.get_or_create(year=year_value)

        college = College.objects.get(id=college_id)
        branch = Branch.objects.get(id=branch_id)

        user = User.objects.create_user(
            username=phone,
            first_name=name,
            email=email
        )

        StudentProfile.objects.create(
            user=user,
            phone=phone,
            college=college,
            branch=branch,
            year_of_passing=year_obj,
            qualification=qualification
        )

        messages.success(request, "Registration successful. Please login.")
        return redirect('otp_login')

    return render(request, 'register.html', {
        'colleges': College.objects.all(),
        'branches': Branch.objects.all(),
        'years': YearOfPassing.objects.all().order_by('-year')
    })


# =========================
# OTP LOGIN
# =========================
def otp_login(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = normalize_phone(request.POST.get('phone'))

        try:
            profile = StudentProfile.objects.get(
                phone=phone,
                user__first_name=name
            )
        except StudentProfile.DoesNotExist:
            messages.error(request, "Invalid name or phone number")
            return redirect('otp_login')

        user = profile.user

        # Remove old OTPs
        OTP.objects.filter(user=user, is_verified=False).delete()

        otp_value = str(random.randint(100000, 999999))

        OTP.objects.create(
            user=user,
            otp=otp_value,
            expires_at=timezone.now() + timedelta(minutes=OTP_EXPIRY_MINUTES)
        )

        message = f"Your OTP for exam login is {otp_value}. Valid for {OTP_EXPIRY_MINUTES} minutes."
        send_sms(phone, message)

        request.session['otp_user_id'] = user.id
        return redirect('otp_verify')

    return render(request, 'login.html')


# =========================
# OTP VERIFY
# =========================
def otp_verify(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        user_id = request.session.get('otp_user_id')

        if not user_id:
            messages.error(request, "Session expired")
            return redirect('otp_login')

        try:
            otp_obj = OTP.objects.filter(
                user_id=user_id,
                is_verified=False
            ).latest('created_at')
        except OTP.DoesNotExist:
            messages.error(request, "OTP not found")
            return redirect('otp_login')

        if otp_obj.expires_at < timezone.now():
            otp_obj.delete()
            messages.error(request, "OTP expired")
            return redirect('otp_login')

        if otp_obj.attempts >= MAX_OTP_ATTEMPTS:
            otp_obj.delete()
            messages.error(request, "Too many invalid attempts")
            return redirect('otp_login')

        if otp_obj.otp != entered_otp:
            otp_obj.attempts += 1
            otp_obj.save()
            messages.error(request, "Invalid OTP")
            return redirect('otp_verify')

        otp_obj.is_verified = True
        otp_obj.save()

        login(request, otp_obj.user)
        request.session.pop('otp_user_id', None)
        return redirect('start_exam')

    return render(request, 'otp_verify.html')


# =========================
# START EXAM
# =========================
@login_required
def start_exam(request):
    exam = ExamSession.objects.filter(
        student=request.user,
        is_completed=False
    ).first()

    if not exam:
        exam = ExamSession.objects.create(student=request.user)
        questions = list(Question.objects.all())
        exam.questions.set(random.sample(questions, min(25, len(questions))))

    answers = {
        a.question_id: a.selected_answer
        for a in StudentAnswer.objects.filter(exam=exam)
    }

    return render(request, 'exam.html', {
        'questions': exam.questions.all(),
        'answers': answers
    })


# =========================
# SAVE ANSWER (AJAX)
# =========================
#@login_required
def save_answer(request):
    if request.method == "POST":
        data = json.loads(request.body)

        exam = ExamSession.objects.get(
            student=request.user,
            is_completed=False
        )

        question_id = data.get("question_id")
        selected = data.get("answer")

        StudentAnswer.objects.update_or_create(
            exam=exam,
            question_id=question_id,
            defaults={"selected_answer": selected}
        )

        return JsonResponse({"status": "saved"})


# =========================
# SUBMIT EXAM
# =========================
@login_required
def submit_exam(request):
    exam = ExamSession.objects.get(
        student=request.user,
        is_completed=False
    )

    answers = StudentAnswer.objects.filter(exam=exam)

    # DEBUG (optional – remove later)
    #for ans in answers:
        #print(ans.selected_answer, ans.question.correct_answer)

    score = sum(
        1 for ans in answers
        if ans.selected_answer == ans.question.correct_answer
    )

    exam.score = score
    exam.is_completed = True
    exam.save()

    return render(request, "result.html", {"score": score})
