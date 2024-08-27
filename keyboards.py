## keyboards.py

from translations import button_texts
import urllib.parse

import urllib.parse


def irina_service_menu():
    keyboard = [
        [InlineKeyboardButton("Найти и смотреть ПРОФОРМУ", callback_data='find_and_view_order')],
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
from helpers.database_helpers import get_latest_session_number, get_full_proforma
import urllib.parse
import logging

from translations import translations  # Убедитесь, что словарь translations подключен

def user_options_keyboard(language, user_id):
    # Стандартное сообщение на языке пользователя
    trans = translations.get(language, translations['en'])  # Используем 'en' как язык по умолчанию
    contact_message = trans['whatsapp_message']

    try:
        # Получаем последний session_number для пользователя
        session_number = get_latest_session_number(user_id)

        if session_number:
            # Получаем полную информацию о проформе
            order_info = get_full_proforma(user_id, session_number)

            if order_info and len(order_info) >= 3:  # Убедитесь, что данные извлечены корректно
                # Формируем номер проформы и добавляем статус
                proforma_number = f"{order_info[0]}_{order_info[1]}_{order_info[10]}"
                contact_message = f"{trans['whatsapp_message']} {proforma_number}. {trans['whatsapp_footer']}"
    except Exception as e:
        logging.error(f"Ошибка при получении номера проформы: {e}")
        # Оставляем contact_message по умолчанию

    # Кодируем сообщение для использования в URL
    encoded_message = urllib.parse.quote(contact_message)

    # Создаем клавиатуру с тремя кнопками
    keyboard = [
        [InlineKeyboardButton(button_texts[language][0], callback_data='get_proforma')],
        [InlineKeyboardButton(button_texts[language][1], url=f'https://wa.me/34667574895?text={encoded_message}')],
        [InlineKeyboardButton(button_texts[language][2], url='https://www.instagram.com/picnicsalicante')]
    ]

    return InlineKeyboardMarkup(keyboard)
