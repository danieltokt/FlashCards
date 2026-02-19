from django.contrib.auth.models import AbstractUser
from django.db import models

LANGUAGE_CHOICES = [
    ('ru', 'Русский'),
    ('en', 'English'),
    ('kk', 'Қазақша'),
    ('ky', 'Кыргызча'),
    ('de', 'Deutsch'),
    ('fr', 'Français'),
    ('es', 'Español'),
]

class User(AbstractUser):
    email = models.EmailField(unique=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    interface_language = models.CharField(
        max_length=5,
        choices=LANGUAGE_CHOICES,
        default='ru'
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.email