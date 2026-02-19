import json
import random
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from courses.models import Course, Card
from .models import TestResult
from .test_generator import generate_test

@login_required
def study_view(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk, user=request.user)
    cards = list(course.cards.all())

    if not cards:
        return render(request, 'study/no_cards.html', {'course': course})

    # Перемешать если нужно
    shuffle = request.GET.get('shuffle', 'false') == 'true'
    favorites_only = request.GET.get('favorites', 'false') == 'true'

    if favorites_only:
        cards = [c for c in cards if c.is_favorite]
        if not cards:
            cards = list(course.cards.all())

    if shuffle:
        random.shuffle(cards)

    cards_data = [
        {
            'id': c.pk,
            'front': c.front_text,
            'back': c.back_text,
            'image': c.image.url if c.image else None,
            'is_favorite': c.is_favorite,
        }
        for c in cards
    ]

    return render(request, 'study/study.html', {
        'course': course,
        'cards_json': json.dumps(cards_data, ensure_ascii=False),
        'total': len(cards_data),
        'shuffle': shuffle,
        'favorites_only': favorites_only,
    })


@login_required
def study_results(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk, user=request.user)

    if request.method == 'POST':
        data = json.loads(request.body)
        wrong_ids = data.get('wrong_ids', [])
        correct_count = data.get('correct', 0)
        total = data.get('total', 0)

        wrong_cards = Card.objects.filter(pk__in=wrong_ids)

        return JsonResponse({
            'status': 'ok',
            'correct': correct_count,
            'total': total,
            'wrong_count': len(wrong_ids),
        })

    return JsonResponse({'status': 'error'})

@login_required
def test_view(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk, user=request.user)
    cards = course.cards.all()

    if cards.count() < 2:
        return render(request, 'study/no_cards.html', {'course': course})

    questions = generate_test(cards)

    import json as _json
    questions_json = _json.dumps(questions, ensure_ascii=False)

    return render(request, 'study/test.html', {
        'course': course,
        'questions_json': questions_json,
        'total': len(questions),
    })


@login_required
def test_submit(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk, user=request.user)

    if request.method == 'POST':
        data = json.loads(request.body)
        correct = data.get('correct', 0)
        total = data.get('total', 0)
        percent = round((correct / total) * 100) if total > 0 else 0

        # Сохраняем результат
        TestResult.objects.create(
            user=request.user,
            course=course,
            score=correct,
            total=total,
            percent=percent,
        )

        # Начисляем монеты
        coins = 0
        if percent >= 90:
            coins = 20
        elif percent >= 70:
            coins = 10
        elif percent >= 50:
            coins = 5

        
        if coins > 0:
            from gamification.utils import add_coins
            coins = add_coins(request.user, coins, 'test')

        # Засчитываем активность для огонька
        from gamification.utils import record_activity
        record_activity(request.user)

        return JsonResponse({
            'status': 'ok',
            'percent': percent,
            'coins_earned': coins,
        })

    return JsonResponse({'status': 'error'})