from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import GameProfile, CoinTransaction
from .utils import MAX_FREEZES
import json


def get_or_create_profile(user):
    profile, _ = GameProfile.objects.get_or_create(user=user)
    return profile


@login_required
def shop_view(request):
    profile = get_or_create_profile(request.user)

    FREEZE_PRICES = [
        {'amount': 1, 'price': 100, 'label': 'Заморозка × 1'},
        {'amount': 2, 'price': 180, 'label': 'Заморозка × 2'},
    ]

    return render(request, 'gamification/shop.html', {
        'profile': profile,
        'freeze_prices': FREEZE_PRICES,
        'max_freezes': MAX_FREEZES,
    })


@login_required
def buy_freeze(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error'})

    data = json.loads(request.body)
    amount = int(data.get('amount', 1))

    prices = {1: 100, 2: 180}
    price = prices.get(amount)

    if not price:
        return JsonResponse({'status': 'error', 'message': 'Неверное количество'})

    profile = get_or_create_profile(request.user)

    if profile.coins < price:
        return JsonResponse({'status': 'error', 'message': 'Недостаточно монет'})

    if profile.freezes + amount > MAX_FREEZES:
        return JsonResponse({
            'status': 'error',
            'message': f'Максимум {MAX_FREEZES} заморозки. У тебя уже {profile.freezes}.'
        })

    profile.coins -= price
    profile.freezes += amount
    profile.save()

    CoinTransaction.objects.create(
        user=request.user,
        amount=-price,
        reason='purchase'
    )

    return JsonResponse({
        'status': 'ok',
        'coins': profile.coins,
        'freezes': profile.freezes,
    })