# keyboards.py

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

def user_options_keyboard(language):
    """Генерирует три основные кнопки для пользователя на основе выбранного языка."""
    keyboard = [
        [InlineKeyboardButton(button_texts[language][0], callback_data='view_proforma')],
        [InlineKeyboardButton(button_texts[language][1], callback_data='event_gallery')],
        [InlineKeyboardButton(button_texts[language][2], callback_data='contact_organizer')]
    ]
    return InlineKeyboardMarkup(keyboard)
