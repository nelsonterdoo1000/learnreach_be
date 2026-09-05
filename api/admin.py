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

from django.contrib import messages
from .email_utils import (
    send_abandoned_cart_email,
    send_ai_weekend_locked_in,
    send_ai_weekend_access_details,
    send_ai_weekend_meeting_link
)

@admin.register(AIWeekendRegistration)
class AIWeekendRegistrationAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'is_paid', 'payment_reference', 'access_email_sent', 'meeting_link_sent', 'created_at')
    list_filter = ('is_paid', 'access_email_sent', 'meeting_link_sent', 'created_at')
    search_fields = ('name', 'email', 'phone', 'payment_reference')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    actions = ['resend_locked_in_email', 'resend_access_details_email', 'send_meeting_link_email', 'mark_as_paid_and_onboard']

    @admin.action(description="📧 Resend 'Locked In' Welcome Email")
    def resend_locked_in_email(self, request, queryset):
        success_count = 0
        for reg in queryset:
            try:
                if send_ai_weekend_locked_in(reg.email):
                    success_count += 1
            except Exception as e:
                self.message_user(request, f"Error sending to {reg.email}: {e}", level=messages.ERROR)
        self.message_user(request, f"Successfully sent 'Locked In' email to {success_count} participant(s).", level=messages.SUCCESS)

    @admin.action(description="📧 Send/Resend 'Access Details' Email")
    def resend_access_details_email(self, request, queryset):
        success_count = 0
        for reg in queryset:
            try:
                if send_ai_weekend_access_details(reg.email):
                    reg.access_email_sent = True
                    reg.save()
                    success_count += 1
            except Exception as e:
                self.message_user(request, f"Error sending to {reg.email}: {e}", level=messages.ERROR)
        self.message_user(request, f"Successfully sent 'Access Details' email to {success_count} participant(s).", level=messages.SUCCESS)

    @admin.action(description="📧 Send 'Meeting Link' Email")
    def send_meeting_link_email(self, request, queryset):
        success_count = 0
        for reg in queryset:
            try:
                if send_ai_weekend_meeting_link(reg.email):
                    reg.meeting_link_sent = True
                    reg.save()
                    success_count += 1
            except Exception as e:
                self.message_user(request, f"Error sending to {reg.email}: {e}", level=messages.ERROR)
        self.message_user(request, f"Successfully sent 'Meeting Link' email to {success_count} participant(s).", level=messages.SUCCESS)

    @admin.action(description="✅ Mark as Paid & Send All Onboarding Emails")
    def mark_as_paid_and_onboard(self, request, queryset):
        count = 0
        for reg in queryset:
            reg.is_paid = True
            try:
                send_ai_weekend_locked_in(reg.email)
                send_ai_weekend_access_details(reg.email)
                reg.access_email_sent = True
                reg.save()
                count += 1
            except Exception as e:
                reg.save()
                self.message_user(request, f"Updated {reg.email} to paid, but email failed: {e}", level=messages.WARNING)
        self.message_user(request, f"Marked {count} registration(s) as Paid and dispatched onboarding emails!", level=messages.SUCCESS)


@admin.register(AIWeekendLead)
class AIWeekendLeadAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'email_1_sent', 'email_2_sent', 'email_3_sent', 'created_at')
    list_filter = ('email_1_sent', 'email_2_sent', 'email_3_sent', 'created_at')
    search_fields = ('name', 'email', 'phone')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    actions = [
        'convert_to_paid_and_send_emails',
        'trigger_level_1_cart_email',
        'trigger_level_2_cart_email',
        'trigger_level_3_cart_email',
        'reset_email_reminders'
    ]

    @admin.action(description="🎉 Convert Lead to Paid Registration & Send Welcome Emails")
    def convert_to_paid_and_send_emails(self, request, queryset):
        converted = 0
        for lead in queryset:
            clean_email = lead.email.strip().lower()
            reg, created = AIWeekendRegistration.objects.get_or_create(
                email=clean_email,
                defaults={
                    'name': lead.name,
                    'phone': lead.phone,
                    'is_paid': True,
                    'access_email_sent': True,
                }
            )
            if not created:
                reg.is_paid = True
                reg.name = lead.name or reg.name
                reg.phone = lead.phone or reg.phone
                reg.access_email_sent = True
                reg.save()

            # Send the onboarding emails
            try:
                send_ai_weekend_locked_in(clean_email)
                send_ai_weekend_access_details(clean_email)
                converted += 1
            except Exception as e:
                self.message_user(request, f"Created registration for {clean_email}, but email error: {e}", level=messages.WARNING)

        self.message_user(request, f"Successfully converted {converted} lead(s) to Paid Registration and sent Locked-in + Access Details emails!", level=messages.SUCCESS)

    @admin.action(description="🛒 Send Abandoned Cart: Level 1 (Initial Reminder)")
    def trigger_level_1_cart_email(self, request, queryset):
        count = 0
        for lead in queryset:
            try:
                if send_abandoned_cart_email(lead.email, lead.name, level=1):
                    lead.email_1_sent = True
                    lead.save()
                    count += 1
            except Exception as e:
                self.message_user(request, f"Error sending to {lead.email}: {e}", level=messages.ERROR)
        self.message_user(request, f"Sent Level 1 Abandoned Cart email to {count} lead(s).", level=messages.SUCCESS)

    @admin.action(description="🛒 Send Abandoned Cart: Level 2 (Urgency)")
    def trigger_level_2_cart_email(self, request, queryset):
        count = 0
        for lead in queryset:
            try:
                if send_abandoned_cart_email(lead.email, lead.name, level=2):
                    lead.email_2_sent = True
                    lead.save()
                    count += 1
            except Exception as e:
                self.message_user(request, f"Error sending to {lead.email}: {e}", level=messages.ERROR)
        self.message_user(request, f"Sent Level 2 Abandoned Cart email to {count} lead(s).", level=messages.SUCCESS)

    @admin.action(description="🛒 Send Abandoned Cart: Level 3 (Final Call)")
    def trigger_level_3_cart_email(self, request, queryset):
        count = 0
        for lead in queryset:
            try:
                if send_abandoned_cart_email(lead.email, lead.name, level=3):
                    lead.email_3_sent = True
                    lead.save()
                    count += 1
            except Exception as e:
                self.message_user(request, f"Error sending to {lead.email}: {e}", level=messages.ERROR)
        self.message_user(request, f"Sent Level 3 Abandoned Cart email to {count} lead(s).", level=messages.SUCCESS)

    @admin.action(description="🔄 Reset Email Flags (Allow resending automated sequence)")
    def reset_email_reminders(self, request, queryset):
        updated = queryset.update(email_1_sent=False, email_2_sent=False, email_3_sent=False)
        self.message_user(request, f"Reset email reminder status for {updated} lead(s).", level=messages.SUCCESS)

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
