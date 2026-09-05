from django.contrib import admin
from .models import (
    Profile,
    Subject,
    Topic,
    LearningSession,
    Message,
    Quiz,
    Question,
    Answer,
    OTP,
    AIWeekendRegistration,
    AIWeekendLead
)

@admin.register(AIWeekendRegistration)
class AIWeekendRegistrationAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'is_paid', 'payment_reference', 'access_email_sent', 'meeting_link_sent', 'created_at')
    list_filter = ('is_paid', 'access_email_sent', 'meeting_link_sent', 'created_at')
    search_fields = ('name', 'email', 'phone', 'payment_reference')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

@admin.register(AIWeekendLead)
class AIWeekendLeadAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'email_1_sent', 'email_2_sent', 'email_3_sent', 'created_at')
    list_filter = ('email_1_sent', 'email_2_sent', 'email_3_sent', 'created_at')
    search_fields = ('name', 'email', 'phone')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'guardian', 'age', 'learning_level')
    list_filter = ('role', 'learning_level')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'subject')
    list_filter = ('subject',)
    search_fields = ('name',)

@admin.register(LearningSession)
class LearningSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'learner', 'topic', 'custom_topic', 'started_at')
    list_filter = ('started_at', 'topic')
    search_fields = ('learner__username', 'custom_topic')
    readonly_fields = ('started_at',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'sender', 'timestamp')
    list_filter = ('sender', 'timestamp')
    search_fields = ('content', 'session__learner__username')
    readonly_fields = ('timestamp',)

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'score', 'total_questions', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('session__learner__username',)
    readonly_fields = ('created_at',)
    inlines = [QuestionInline]

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'quiz', 'text', 'correct_answer')
    search_fields = ('text', 'correct_answer')

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'learner', 'selected_option', 'is_correct', 'timestamp')
    list_filter = ('is_correct', 'timestamp')
    search_fields = ('learner__username', 'selected_option')
    readonly_fields = ('timestamp',)

@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'code', 'purpose', 'created_at')
    list_filter = ('purpose', 'created_at')
    search_fields = ('user__username', 'user__email', 'code')
    readonly_fields = ('created_at',)
