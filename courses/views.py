from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Folder, Course, Card
from .forms import FolderForm, CourseForm, CardForm
from django.views.decorators.http import require_POST

# ===== ГЛАВНАЯ =====

@login_required
def home(request):
    from django.utils import timezone
    from gamification.models import GameProfile
    from study.models import TestResult

    courses = Course.objects.filter(user=request.user).order_by('-created_at')
    folders = Folder.objects.filter(user=request.user).order_by('-created_at')
    profile, _ = GameProfile.objects.get_or_create(user=request.user)

    # Карточки на повторение сегодня (spaced repetition)
    today = timezone.now().date()
    due_cards = Card.objects.filter(
        course__user=request.user,
        next_review__lte=today
    ).select_related('course')[:20]

    # Последний результат теста
    last_test = TestResult.objects.filter(
        user=request.user
    ).order_by('-created_at').first()

    # Общая статистика
    total_cards = Card.objects.filter(course__user=request.user).count()
    total_tests = TestResult.objects.filter(user=request.user).count()

    # Недавние курсы (последние 4)
    recent_courses = courses[:4]

    return render(request, 'courses/home.html', {
        'courses': courses,
        'folders': folders,
        'profile': profile,
        'due_cards': due_cards,
        'last_test': last_test,
        'total_cards': total_cards,
        'total_tests': total_tests,
        'recent_courses': recent_courses,
    })

# ===== ПАПКИ =====

@login_required
def folder_create(request):
    form = FolderForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        folder = form.save(commit=False)
        folder.user = request.user
        folder.save()
        messages.success(request, 'Папка создана!')
        return redirect('home')
    return render(request, 'courses/folder_form.html', {'form': form})


@login_required
def folder_detail(request, pk):
    folder = get_object_or_404(Folder, pk=pk, user=request.user)
    courses = folder.courses.all()
    return render(request, 'courses/folder_detail.html', {'folder': folder, 'courses': courses})


@login_required
def folder_delete(request, pk):
    folder = get_object_or_404(Folder, pk=pk, user=request.user)
    if request.method == 'POST':
        folder.delete()
        messages.success(request, 'Папка удалена')
        return redirect('home')
    return render(request, 'courses/confirm_delete.html', {'object': folder, 'type': 'папку'})


# ===== КУРСЫ =====

@login_required
def course_create(request):
    form = CourseForm(request.user, request.POST or None)
    if request.method == 'POST' and form.is_valid():
        course = form.save(commit=False)
        course.user = request.user
        course.save()
        messages.success(request, 'Курс создан! Теперь добавь карточки.')
        return redirect('course_edit', pk=course.pk)
    return render(request, 'courses/course_form.html', {'form': form, 'title': 'Новый курс'})


@login_required
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk, user=request.user)
    cards = course.cards.all()
    return render(request, 'courses/course_detail.html', {'course': course, 'cards': cards})


@login_required
def course_edit(request, pk):
    course = get_object_or_404(Course, pk=pk, user=request.user)
    cards = course.cards.all()
    card_form = CardForm()
    course_form = CourseForm(request.user, instance=course)

    if request.method == 'POST':
        # Сохранение данных курса
        if 'save_course' in request.POST:
            course_form = CourseForm(request.user, request.POST, instance=course)
            if course_form.is_valid():
                course_form.save()
                messages.success(request, 'Курс обновлён!')
                return redirect('course_edit', pk=course.pk)

        # Добавление карточки
        elif 'add_card' in request.POST:
            card_form = CardForm(request.POST, request.FILES)
            if card_form.is_valid():
                card = card_form.save(commit=False)
                card.course = course
                card.save()
                return redirect('course_edit', pk=course.pk)

    return render(request, 'courses/course_edit.html', {
        'course': course,
        'cards': cards,
        'card_form': card_form,
        'course_form': course_form,
    })


@login_required
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk, user=request.user)
    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Курс удалён')
        return redirect('home')
    return render(request, 'courses/confirm_delete.html', {'object': course, 'type': 'курс'})


# ===== КАРТОЧКИ =====

@login_required
def card_delete(request, pk):
    card = get_object_or_404(Card, pk=pk, course__user=request.user)
    course_pk = card.course.pk
    card.delete()
    return redirect('course_edit', pk=course_pk)


@login_required
def card_toggle_favorite(request, pk):
    card = get_object_or_404(Card, pk=pk, course__user=request.user)
    card.is_favorite = not card.is_favorite
    card.save()
    return JsonResponse({'is_favorite': card.is_favorite})


@login_required
def get_translations(request):
    """AJAX: авто-перевод при вводе слова"""
    import requests as req
    word = request.GET.get('word', '').strip()
    source = request.GET.get('source', 'ru')
    target = request.GET.get('target', 'en')

    if not word:
        return JsonResponse({'translations': []})

    try:
        response = req.post('https://libretranslate.com/translate', json={
            'q': word,
            'source': source,
            'target': target,
            'api_key': ''
        }, timeout=3)
        translation = response.json().get('translatedText', '')
        return JsonResponse({'translations': [translation] if translation else []})
    except Exception:
        return JsonResponse({'translations': []})
    
@login_required
@require_POST
def course_toggle_share(request, pk):
    course = get_object_or_404(Course, pk=pk, user=request.user)
    course.is_public = not course.is_public
    course.save()
    return JsonResponse({
        'is_public': course.is_public,
        'share_url': request.build_absolute_uri(f'/courses/shared/{course.share_token}/')
    })


def course_shared_view(request, token):
    """Публичная страница курса по ссылке"""
    course = get_object_or_404(Course, share_token=token, is_public=True)
    cards = course.cards.all()
    return render(request, 'courses/course_shared.html', {
        'course': course,
        'cards': cards,
    })