from django.contrib import admin
from .models import (
    StudentProfile,
    College,
    Branch,
    YearOfPassing,
    Question,
    ExamSession,
    OTP,
    StudentAnswer
)


# ======================
# MASTER TABLE ADMINS
# ======================

@admin.register(College)
class CollegeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(YearOfPassing)
class YearOfPassingAdmin(admin.ModelAdmin):
    list_display = ('id', 'year')
    ordering = ('-year',)


# ======================
# STUDENT PROFILE ADMIN
# ======================

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'phone',
        'college',
        'branch',
        'year_of_passing',
    )
    search_fields = ('phone', 'user__first_name', 'user__username')
    list_filter = ('college', 'branch', 'year_of_passing')


# ======================
# QUESTION ADMIN
# ======================

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'correct_answer')
    search_fields = ('question',)


# ======================
# EXAM SESSION ADMIN
# ======================

@admin.register(ExamSession)
class ExamSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'score', 'is_completed')
    list_filter = ('is_completed',)


# ======================
# OTP ADMIN
# ======================

@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'otp', 'is_verified')
    list_filter = ('is_verified',)


# ======================
# STUDENT ANSWER ADMIN
# ======================

@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'exam', 'question', 'selected_answer')
