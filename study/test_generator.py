import random


def generate_test(cards):
    """
    Принимает queryset карточек, возвращает список вопросов.
    Минимум 10 вопросов, максимум 30.
    """
    cards = list(cards)

    if len(cards) < 2:
        return []

    # Определяем количество вопросов
    count = max(10, min(len(cards), 30))
    # Если карточек меньше 10 — берём все
    if len(cards) < 10:
        count = len(cards)

    # Перемешиваем и берём нужное количество
    pool = random.sample(cards, min(count, len(cards)))
    # Если карточек мало — повторяем пул
    while len(pool) < count:
        pool += random.sample(cards, min(count - len(pool), len(cards)))
    pool = pool[:count]

    questions = []
    types = ['choice', 'write', 'truefalse', 'match']

    # Распределяем типы: 40% choice, 25% write, 20% truefalse, 15% match
    type_weights = [0.40, 0.25, 0.20, 0.15]

    for i, card in enumerate(pool):
        # Выбираем тип вопроса взвешенно
        q_type = random.choices(types, weights=type_weights, k=1)[0]

        # Для match нужно минимум 4 карточки
        if q_type == 'match' and len(cards) < 4:
            q_type = 'choice'

        if q_type == 'choice':
            questions.append(make_choice(card, cards))
        elif q_type == 'write':
            questions.append(make_write(card))
        elif q_type == 'truefalse':
            questions.append(make_truefalse(card, cards))
        elif q_type == 'match':
            # match делаем один раз на группу из 4 карточек
            # чтобы не дублировать, пропускаем если уже есть
            match_q = make_match(cards)
            if match_q:
                questions.append(match_q)
            else:
                questions.append(make_choice(card, cards))

    return questions


def make_choice(card, all_cards):
    """4 варианта ответа, один правильный"""
    others = [c for c in all_cards if c.pk != card.pk]
    wrong_options = random.sample(others, min(3, len(others)))
    options = [c.back_text for c in wrong_options] + [card.back_text]
    random.shuffle(options)

    return {
        'type': 'choice',
        'question': f'Как переводится «{card.front_text}»?',
        'word': card.front_text,
        'options': options,
        'answer': card.back_text,
        'card_id': card.pk,
    }


def make_write(card):
    """Написать перевод самому"""
    return {
        'type': 'write',
        'question': f'Напиши перевод слова «{card.front_text}»',
        'word': card.front_text,
        'answer': card.back_text.lower().strip(),
        'card_id': card.pk,
    }


def make_truefalse(card, all_cards):
    """Верно или неверно — пара слово/перевод"""
    is_correct = random.choice([True, False])

    if is_correct:
        shown_translation = card.back_text
    else:
        others = [c for c in all_cards if c.pk != card.pk]
        if others:
            wrong = random.choice(others)
            shown_translation = wrong.back_text
        else:
            shown_translation = card.back_text
            is_correct = True

    return {
        'type': 'truefalse',
        'question': f'«{card.front_text}» переводится как «{shown_translation}» — верно?',
        'word': card.front_text,
        'shown_translation': shown_translation,
        'answer': str(is_correct).lower(),
        'card_id': card.pk,
    }


def make_match(all_cards):
    """Сопоставить 4 пары слово ↔ перевод"""
    if len(all_cards) < 4:
        return None

    selected = random.sample(all_cards, 4)
    left = [c.front_text for c in selected]
    right = [c.back_text for c in selected]
    right_shuffled = right.copy()
    random.shuffle(right_shuffled)

    pairs = {c.front_text: c.back_text for c in selected}

    return {
        'type': 'match',
        'question': 'Сопоставь слова с переводами',
        'left': left,
        'right': right_shuffled,
        'pairs': pairs,
    }