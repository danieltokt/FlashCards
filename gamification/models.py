from django.db import models
from users.models import User


class GameProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='gameprofile')
    coins = models.IntegerField(default=0)
    streak = models.IntegerField(default=0)
    freezes = models.IntegerField(default=0)
    last_activity = models.DateField(null=True, blank=True)
    longest_streak = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} — 🔥{self.streak} 🪙{self.coins}"


class CoinTransaction(models.Model):
    REASON_CHOICES = [
        ('test', 'Тест'),
        ('streak_7', 'Стрик 7 дней'),
        ('streak_30', 'Стрик 30 дней'),
        ('daily', 'Первый курс за день'),
        ('purchase', 'Покупка'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='coin_transactions')
    amount = models.IntegerField()
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)