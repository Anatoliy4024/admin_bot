## keyboards.py

from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from translations import button_texts, translations  # Импортируем тексты кнопок

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


from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import urllib.parse


def user_options_keyboard(language):
    """Генерирует клавиатуру с тремя кнопками."""

    # Получаем текст сообщения для WhatsApp на нужном языке
    whatsapp_message = translations[language]['whatsapp_message']

    # Кодируем сообщение для использования в URL
    encoded_message = urllib.parse.quote(whatsapp_message)

    # Формируем URL для WhatsApp
    whatsapp_url = f'https://wa.me/34667574895?text={encoded_message}'

    keyboard = [
        [InlineKeyboardButton(button_texts[language][0], callback_data='get_proforma')],
        [InlineKeyboardButton(button_texts[language][1], url=whatsapp_url)],
        [InlineKeyboardButton(button_texts[language][2], url='https://www.instagram.com/picnicsalicante')]
    ]
    return InlineKeyboardMarkup(keyboard)
