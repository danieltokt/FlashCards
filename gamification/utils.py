from django.utils import timezone
from django.db import transaction

DAILY_COIN_LIMIT = 50


def get_coins_earned_today(user):
    from .models import CoinTransaction
    today = timezone.now().date()
    today_transactions = CoinTransaction.objects.filter(
        user=user,
        created_at__date=today,
        amount__gt=0
    )
    return sum(t.amount for t in today_transactions)


def add_coins(user, amount, reason):
    """Начисляет монеты с учётом дневного лимита"""
    from .models import CoinTransaction, GameProfile
    profile, _ = GameProfile.objects.get_or_create(user=user)

    earned_today = get_coins_earned_today(user)
    remaining = DAILY_COIN_LIMIT - earned_today

    if remaining <= 0:
        return 0

    actual = min(amount, remaining)
    profile.coins += actual
    profile.save()

    CoinTransaction.objects.create(user=user, amount=actual, reason=reason)
    return actual


def record_activity(user):
    """Вызывается после прохождения теста или курса"""
    from .models import GameProfile
    today = timezone.now().date()
    profile, created = GameProfile.objects.get_or_create(user=user)

    if profile.last_activity == today:
        return

    yesterday = today - timezone.timedelta(days=1)

    with transaction.atomic():
        if profile.last_activity == yesterday:
            profile.streak += 1
        elif profile.last_activity is None:
            profile.streak = 1
        else:
            if profile.freezes > 0:
                profile.freezes -= 1
                profile.streak += 1
            else:
                profile.streak = 1

        # Бонусы за стрики
        if profile.streak == 7:
            add_coins(user, 15, 'streak_7')
        elif profile.streak == 30:
            add_coins(user, 50, 'streak_30')

        # +3 монеты за первый курс/тест дня
        add_coins(user, 3, 'daily')

        if profile.streak > profile.longest_streak:
            profile.longest_streak = profile.streak

        profile.last_activity = today
        profile.save()