from django.db import models
from users.models import User
from courses.models import Course, Card


class TestResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_results')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='test_results')
    score = models.IntegerField()       # правильных ответов
    total = models.IntegerField()       # всего вопросов
    percent = models.IntegerField()     # %
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} — {self.course} — {self.percent}%"