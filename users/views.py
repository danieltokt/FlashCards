from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, LoginForm

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    form = RegisterForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Добро пожаловать!')
            return redirect('home')
        else:
            messages.error(request, 'Проверьте правильность заполнения формы')
    
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Неверный email или пароль')
    
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def profile_view(request):
    from gamification.models import GameProfile, CoinTransaction
    from study.models import TestResult
    from courses.models import Course
    from django.contrib.auth import get_user_model

    profile, _ = GameProfile.objects.get_or_create(user=request.user)
    test_results = TestResult.objects.filter(user=request.user).order_by('-created_at')[:10]
    courses_count = Course.objects.filter(user=request.user).count()

    all_results = TestResult.objects.filter(user=request.user)
    avg_percent = 0
    if all_results.exists():
        avg_percent = round(sum(r.percent for r in all_results) / all_results.count())

    transactions = CoinTransaction.objects.filter(user=request.user).order_by('-created_at')[:10]

    if request.method == 'POST':
        lang = request.POST.get('interface_language', '').strip()
        valid_langs = ['ru', 'en', 'de', 'fr', 'es', 'kk', 'ky']

        if lang in valid_langs:
            # Обновляем напрямую через queryset — надёжнее
            get_user_model().objects.filter(pk=request.user.pk).update(
                interface_language=lang
            )
            messages.success(request, 'Язык сохранён!')
        else:
            messages.error(request, f'Неверный язык: {lang}')

        return redirect('profile')

    # Перечитываем пользователя из базы чтобы показать актуальный язык
    from django.contrib.auth import get_user_model
    fresh_user = get_user_model().objects.get(pk=request.user.pk)

    return render(request, 'users/profile.html', {
        'profile': profile,
        'test_results': test_results,
        'courses_count': courses_count,
        'avg_percent': avg_percent,
        'transactions': transactions,
        'fresh_user': fresh_user,
    })