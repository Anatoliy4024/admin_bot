## keyboards.py

from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from translations import button_texts  # Импортируем тексты кнопок

def language_selection_keyboard():
    """Генерирует клавиатуру для выбора языка."""
    keyboard = [
        [
            InlineKeyboardButton("🇬🇧 EN", callback_data='lang_en'),
            InlineKeyboardButton("🇪🇸 ES", callback_data='lang_es'),
            InlineKeyboardButton("🇮🇹 IT", callback_data='lang_it'),
            InlineKeyboardButton("🇫🇷 FR", callback_data='lang_fr')
        ],
        [
            InlineKeyboardButton("🇺🇦 UA", callback_data='lang_uk'),
            InlineKeyboardButton("🇵🇱 PL", callback_data='lang_pl'),
            InlineKeyboardButton("🇩🇪 DE", callback_data='lang_de'),
            InlineKeyboardButton("🇷🇺 RU", callback_data='lang_ru')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def irina_service_menu():
    keyboard = [
        [InlineKeyboardButton("Найти и смотреть ордер", callback_data='find_and_view_order')],
        # Другие кнопки
        [InlineKeyboardButton("Кнопка 2", callback_data='btn2')],
        [InlineKeyboardButton("Кнопка 3", callback_data='btn3')],
        [InlineKeyboardButton("Кнопка 4", callback_data='btn4')],
        [InlineKeyboardButton("Кнопка 5", callback_data='btn5')],
    ]
    return InlineKeyboardMarkup(keyboard)

def service_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("Кнопка 10", callback_data='btn10')],
        [InlineKeyboardButton("Кнопка 11", callback_data='btn11')],
        [InlineKeyboardButton("Кнопка 12", callback_data='btn12')],
        [InlineKeyboardButton("Кнопка 13", callback_data='btn13')],
        [InlineKeyboardButton("Кнопка 14", callback_data='btn14')],
    ]
    return InlineKeyboardMarkup(keyboard)


def user_options_keyboard(language):
    """Генерирует клавиатуру с кнопками."""
    keyboard = [
        [InlineKeyboardButton(button_texts[language][0], callback_data='get_proforma')],
        [InlineKeyboardButton(button_texts[language][1], callback_data='disabled_button')],  # Неактивная кнопка
        [InlineKeyboardButton(button_texts[language][2], url='https://www.instagram.com/picnicsalicante?utm_source=ig_web_button_share_sheet&igsh=ZDNlZDc0MzIxNw==')]
    ]
    return InlineKeyboardMarkup(keyboard)
