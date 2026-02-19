from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import GameProfile, CoinTransaction


def get_or_create_profile(user):
    profile, _ = GameProfile.objects.get_or_create(user=user)
    return profile


@login_required
def shop_view(request):
    profile = get_or_create_profile(request.user)

    FREEZE_PRICES = [
        {'amount': 1, 'price': 100, 'label': 'Заморозка × 1'},
        {'amount': 3, 'price': 250, 'label': 'Заморозка × 3'},
        {'amount': 7, 'price': 500, 'label': 'Заморозка × 7'},
    ]

    return render(request, 'gamification/shop.html', {
        'profile': profile,
        'freeze_prices': FREEZE_PRICES,
    })


@login_required
def buy_freeze(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        amount = int(data.get('amount', 1))

        prices = {1: 100, 3: 250, 7: 500}
        price = prices.get(amount)

        if not price:
            return JsonResponse({'status': 'error', 'message': 'Неверное количество'})

        profile = get_or_create_profile(request.user)

        if profile.coins < price:
            return JsonResponse({'status': 'error', 'message': 'Недостаточно монет'})

        if profile.freezes + amount > 30:
            return JsonResponse({'status': 'error', 'message': 'Максимум 30 заморозок'})

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

    return JsonResponse({'status': 'error'})