from django.utils import timezone
from django.db import transaction

DAILY_COIN_LIMIT = 50
MAX_FREEZES = 2


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
    from .models import CoinTransaction, GameProfile
    profile, _ = GameProfile.objects.get_or_create(user=user)

    earned_today = get_coins_earned_today(user)
    remaining = DAILY_COIN_LIMIT - earned_today

    if remaining <= 0:
        return 0

    actual = min(amount, remaining)
    profile.coins += actual
    profile.save(update_fields=['coins'])

    CoinTransaction.objects.create(user=user, amount=actual, reason=reason)
    return actual


def record_activity(user):
    from .models import GameProfile
    today = timezone.now().date()
    profile, _ = GameProfile.objects.get_or_create(user=user)

    if profile.last_activity == today:
        return

    yesterday = today - timezone.timedelta(days=1)

    with transaction.atomic():
        profile.refresh_from_db()

        if profile.last_activity is None:
            # Первый раз
            profile.streak = 1

        elif profile.last_activity == yesterday:
            # Пришёл вовремя — стрик растёт
            profile.streak += 1

        else:
            # Пропустил один или больше дней
            days_missed = (today - profile.last_activity).days - 1
            # days_missed = 0 означает пропустил вчера (today - last = 2 дня)
            # Считаем сколько заморозок нужно потратить
            freezes_needed = (today - profile.last_activity).days - 1

            if profile.freezes >= freezes_needed and freezes_needed > 0:
                # Есть заморозки на все пропущенные дни
                profile.freezes -= freezes_needed
                profile.streak += 1
            elif profile.freezes > 0 and freezes_needed > profile.freezes:
                # Заморозок не хватает — сброс
                profile.freezes = 0
                profile.streak = 1
            else:
                # Нет заморозок вообще — сброс
                profile.streak = 1

        # Бонусы за стрики (только когда достигаем ровно этого числа)
        if profile.streak == 7:
            add_coins(user, 15, 'streak_7')
        elif profile.streak == 30:
            add_coins(user, 50, 'streak_30')

        # +3 монеты за первую активность дня
        add_coins(user, 3, 'daily')

        if profile.streak > profile.longest_streak:
            profile.longest_streak = profile.streak

        profile.last_activity = today
        profile.save()