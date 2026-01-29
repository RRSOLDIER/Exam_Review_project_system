from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


# =========================
# MASTER TABLES (ADMIN MANAGEABLE)
# =========================

class College(models.Model):
    name = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.name


class Branch(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class YearOfPassing(models.Model):
    year = models.IntegerField(unique=True)

    def __str__(self):
        return str(self.year)


# =========================
# STUDENT PROFILE
# =========================
class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    college = models.ForeignKey(College, on_delete=models.SET_NULL, null=True)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True)
    year_of_passing = models.ForeignKey(YearOfPassing, on_delete=models.SET_NULL, null=True)

    qualification = models.CharField(
        max_length=50,
        default="Not Specified"
    )

    def __str__(self):
        return self.user.first_name


# =========================
# QUESTION BANK
# =========================

class Question(models.Model):
    question = models.TextField()
    option1 = models.CharField(max_length=200)
    option2 = models.CharField(max_length=200)
    option3 = models.CharField(max_length=200)
    option4 = models.CharField(max_length=200)
    correct_answer = models.CharField(max_length=200)

    def __str__(self):
        return self.question[:50]


# =========================
# EXAM SESSION
# =========================

class ExamSession(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    questions = models.ManyToManyField(Question)

    score = models.IntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['student'],
                condition=models.Q(is_completed=False),
                name='unique_active_exam_per_student'
            )
        ]

    def __str__(self):
        return f"{self.student.username} - Exam"



# =========================
# OTP MODEL
# =========================


class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)

    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    is_verified = models.BooleanField(default=False)
    attempts = models.PositiveIntegerField(default=0)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"{self.user.username} - OTP"


# =========================
# STUDENT ANSWERS (EXAM RESUME)
# =========================

class StudentAnswer(models.Model):
    exam = models.ForeignKey(ExamSession, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.CharField(max_length=200)

    class Meta:
        unique_together = ('exam', 'question')

    def __str__(self):
        return f"{self.exam} - Q{self.question.id}"
