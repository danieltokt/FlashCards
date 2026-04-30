from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import translation
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from .forms import RegisterForm, LoginForm, AvatarForm, ProfileForm


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


def password_reset_view(request):
    from django.contrib.auth import get_user_model
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_url = request.build_absolute_uri(
                f'/users/password-reset/{uid}/{token}/'
            )
            send_mail(
                subject='Сброс пароля — FlashCards',
                message=f'Для сброса пароля перейди по ссылке:\n\n{reset_url}\n\nЕсли ты не запрашивал сброс — просто проигнорируй это письмо.',
                from_email=None,
                recipient_list=[email],
                fail_silently=False,
            )
        except UserModel.DoesNotExist:
            pass
        return redirect('password_reset_done')
    return render(request, 'users/password_reset.html')


@login_required
def profile_view(request):
    from gamification.models import GameProfile, CoinTransaction
    from study.models import TestResult
    from courses.models import Course
    from django.contrib.auth import get_user_model

    UserModel = get_user_model()
    profile, _ = GameProfile.objects.get_or_create(user=request.user)
    test_results = TestResult.objects.filter(user=request.user).order_by('-created_at')[:10]
    courses_count = Course.objects.filter(user=request.user).count()

    all_results = TestResult.objects.filter(user=request.user)
    avg_percent = 0
    if all_results.exists():
        avg_percent = round(sum(r.percent for r in all_results) / all_results.count())

    transactions = CoinTransaction.objects.filter(user=request.user).order_by('-created_at')[:10]

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'language':
            lang = request.POST.get('interface_language', '').strip()
            valid_langs = ['ru', 'en', 'de', 'fr', 'es', 'kk', 'ky']
            if lang in valid_langs:
                UserModel.objects.filter(pk=request.user.pk).update(interface_language=lang)
                translation.activate(lang)
                response = redirect('profile')
                response.set_cookie('django_language', lang, max_age=365*24*60*60)
                messages.success(request, 'Язык сохранён!')
                return response
            else:
                messages.error(request, f'Неверный язык: {lang}')
            return redirect('profile')

        if action == 'avatar':
            form = AvatarForm(request.POST, request.FILES, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, 'Аватар обновлён!')
            else:
                messages.error(request, 'Ошибка загрузки аватара')
            return redirect('profile')

        if action == 'profile':
            form = ProfileForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, 'Профиль обновлён!')
            else:
                messages.error(request, 'Ошибка обновления профиля')
            return redirect('profile')

    fresh_user = UserModel.objects.get(pk=request.user.pk)

    return render(request, 'users/profile.html', {
        'profile': profile,
        'test_results': test_results,
        'courses_count': courses_count,
        'avg_percent': avg_percent,
        'transactions': transactions,
        'fresh_user': fresh_user,
        'avatar_form': AvatarForm(instance=fresh_user),
        'profile_form': ProfileForm(instance=fresh_user),
    })


@login_required
def update_avatar_ajax(request):
    if request.method == 'POST':
        form = AvatarForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            url = request.user.avatar.url if request.user.avatar else ''
            return JsonResponse({'status': 'ok', 'avatar_url': url})
    return JsonResponse({'status': 'error'}, status=400)