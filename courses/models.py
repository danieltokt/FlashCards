from django.db import models
from users.models import User
import uuid

class Folder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='folders')
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Course(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses')
    folder = models.ForeignKey(Folder, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    front_language = models.CharField(max_length=10, default='ru')
    back_language = models.CharField(max_length=10, default='en')
    created_at = models.DateTimeField(auto_now_add=True)
    share_token = models.UUIDField(default=uuid.uuid4, unique=True)
    is_public = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def cards_count(self):
        return self.cards.count()


class Card(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='cards')
    front_text = models.TextField()
    back_text = models.TextField()
    image = models.ImageField(upload_to='cards/', null=True, blank=True)
    is_favorite = models.BooleanField(default=False)
    # Для spaced repetition (пригодится позже)
    ease_factor = models.FloatField(default=2.5)
    next_review = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.front_text} → {self.back_text}"
