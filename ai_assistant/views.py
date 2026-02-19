import json
from groq import Groq
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from .models import Chat, ChatMessage

LANGUAGE_NAMES = {
    'ru': 'русском', 'en': 'английском', 'de': 'немецком',
    'fr': 'французском', 'es': 'испанском', 'kk': 'казахском', 'ky': 'кыргызском',
}

SYSTEM_PROMPT = """Ты — языковой репетитор и помощник по изучению иностранных языков.

Твои задачи:
- Объяснять грамматические правила понятно и с примерами
- Проверять тексты на ошибки и объяснять их
- Составлять примеры предложений с нужными словами
- Отвечать на вопросы о произношении, культуре, идиомах

Правила:
- Всегда отвечай на {lang} языке
- Давай конкретные примеры
- Если проверяешь текст — выдели ошибки и объясни почему это ошибка
- Будь дружелюбным и поддерживающим
- Отвечай структурированно — используй переносы строк для читаемости"""


@login_required
def chat_list(request):
    chats = Chat.objects.filter(user=request.user)
    return render(request, 'ai_assistant/chat_list.html', {'chats': chats})


@login_required
def chat_create(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip() or 'Новый чат'
        chat = Chat.objects.create(user=request.user, title=title)
        return redirect('ai_chat', chat_pk=chat.pk)
    return render(request, 'ai_assistant/chat_create.html')


@login_required
def chat_view(request, chat_pk):
    chat = get_object_or_404(Chat, pk=chat_pk, user=request.user)
    messages = chat.messages.all()
    chats = Chat.objects.filter(user=request.user)
    return render(request, 'ai_assistant/chat.html', {
        'chat': chat,
        'messages': messages,
        'chats': chats,
    })


@login_required
def chat_rename(request, chat_pk):
    chat = get_object_or_404(Chat, pk=chat_pk, user=request.user)
    if request.method == 'POST':
        data = json.loads(request.body)
        chat.title = data.get('title', chat.title).strip() or chat.title
        chat.save()
        return JsonResponse({'status': 'ok', 'title': chat.title})
    return JsonResponse({'status': 'error'})


@login_required
def chat_delete(request, chat_pk):
    chat = get_object_or_404(Chat, pk=chat_pk, user=request.user)
    if request.method == 'POST':
        chat.delete()
        return redirect('ai_chat_list')
    return JsonResponse({'status': 'error'})


@login_required
def chat_send(request, chat_pk):
    if request.method != 'POST':
        return JsonResponse({'status': 'error'})

    chat = get_object_or_404(Chat, pk=chat_pk, user=request.user)
    data = json.loads(request.body)
    user_message = data.get('message', '').strip()

    if not user_message:
        return JsonResponse({'status': 'error', 'message': 'Пустое сообщение'})

    # Сохраняем сообщение пользователя
    ChatMessage.objects.create(
        chat=chat,
        user=request.user,
        role='user',
        content=user_message
    )

    # История последних 20 сообщений
    history = list(chat.messages.order_by('-created_at')[:20])
    history.reverse()

    # Язык пользователя
    lang = LANGUAGE_NAMES.get(
        getattr(request.user, 'interface_language', 'ru'), 'русском'
    )
    system = SYSTEM_PROMPT.replace('{lang}', lang)

    try:
        client = Groq(api_key=settings.GROQ_API_KEY)

        # Формируем историю для Groq
        groq_messages = [{'role': 'system', 'content': system}]
        for msg in history:
            groq_messages.append({
                'role': 'user' if msg.role == 'user' else 'assistant',
                'content': msg.content
            })

        response = client.chat.completions.create(
            model='llama-3.3-70b-versatile',
            messages=groq_messages,
            max_tokens=1024,
            temperature=0.7,
        )

        reply = response.choices[0].message.content

        # Сохраняем ответ
        ChatMessage.objects.create(
            chat=chat,
            user=request.user,
            role='assistant',
            content=reply
        )
        chat.save()

        return JsonResponse({'status': 'ok', 'reply': reply})

    except Exception as e:
        # Удаляем сообщение пользователя при ошибке
        ChatMessage.objects.filter(
            chat=chat,
            role='user',
            content=user_message
        ).last().delete()

        error = str(e)
        if 'rate' in error.lower() or '429' in error:
            error = 'RATE_LIMIT'
        elif 'api_key' in error.lower() or 'invalid' in error.lower():
            error = 'Неверный API ключ. Проверь GROQ_API_KEY в .env'

        return JsonResponse({'status': 'error', 'message': error})


@login_required
def chat_clear(request, chat_pk):
    if request.method == 'POST':
        chat = get_object_or_404(Chat, pk=chat_pk, user=request.user)
        chat.messages.all().delete()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'})