from django.db import models
from accounts.models import User


# Create your models here.
class Conversation(models.Model):
    STATUS_CHOICES = [
        ('active','Active'),
        ('pending','Pending'),
        ('resolved','Resolved')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name="conversation")
    title = models.CharField(max_length=64)
    status = models.CharField(choices=STATUS_CHOICES, default='active', max_length=10)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"Conversation {self.id} - {self.user.email}"



class Message(models.Model):
    SENDER_CHOICES = [
        ("user", "User"),
        ("assistant", "Assistant"),
    ]

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE,related_name="messages")
    sender = models.CharField(max_length=20,choices=SENDER_CHOICES)
    message = models.TextField()

    confidence_score = models.FloatField(blank=True, null=True)
    source = models.JSONField(
        blank=True,
        null=True,
        default=list
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["conversation", "created_at"]),
        ]

    def __str__(self):
        return f"{self.sender} message in Conversation {self.conversation.id}"

