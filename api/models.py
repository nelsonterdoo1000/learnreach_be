from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    ROLE_CHOICES = (
        ('learner', 'Learner'),
        ('guardian', 'Guardian/Teacher'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='learner')
    guardian = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='learners')
    age = models.IntegerField(null=True, blank=True) # for learners
    learning_level = models.CharField(max_length=50, blank=True) # e.g. Grade 5, High School

    def __str__(self):
        return f"{self.user.username} - {self.role}"

class Subject(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Topic(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='topics')
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name

class LearningSession(models.Model):
    learner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True)
    custom_topic = models.CharField(max_length=255, blank=True) # if they just type a topic
    file_context = models.TextField(blank=True, null=True)
    started_at = models.DateTimeField(auto_now_add=True)
    summary = models.TextField(blank=True)
    learning_gaps = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    
    def __str__(self):
        return f"Session {self.id} for {self.learner.username}"

class Message(models.Model):
    SENDER_CHOICES = (
        ('user', 'User'),
        ('ai', 'AI'),
    )
    session = models.ForeignKey(LearningSession, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['timestamp']

class Quiz(models.Model):
    session = models.ForeignKey(LearningSession, on_delete=models.CASCADE, related_name='quizzes')
    created_at = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField(null=True, blank=True)
    total_questions = models.IntegerField(default=0)

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    options = models.JSONField() # JSON list of options
    correct_answer = models.CharField(max_length=255)
    explanation = models.TextField(blank=True)

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    learner = models.ForeignKey(User, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

class OTP(models.Model):
    PURPOSE_CHOICES = (
        ('signup', 'Signup Verification'),
        ('reset', 'Password Reset'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otps')
    code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=10, choices=PURPOSE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.code} ({self.purpose})"

class AIWeekendRegistration(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    payment_reference = models.CharField(max_length=100, unique=True, null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    access_email_sent = models.BooleanField(default=False)
    meeting_link_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.email} - Paid: {self.is_paid}"

class AIWeekendLead(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    email_1_sent = models.BooleanField(default=False)
    email_2_sent = models.BooleanField(default=False)
    email_3_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"Lead: {self.name} - {self.email}"
