# constants.py

from telegram import InlineKeyboardMarkup, InlineKeyboardButton

# Класс для хранения данных пользователя
class UserData:
    def __init__(self):
        self.language = None
        self.step = None

    def set_language(self, language):
        self.language = language

    def get_language(self):
        return self.language

    def set_step(self, step):
        self.step = step

    def get_step(self):
        return self.step

# Функция для отключения кнопок выбора языка
def disable_language_buttons(reply_markup):
    new_keyboard = []
    for row in reply_markup.inline_keyboard:
        new_row = []
        for button in row:
            # Делаем кнопку неактивной, присваивая ей callback_data='none'
            new_row.append(InlineKeyboardButton(button.text, callback_data='none'))
        new_keyboard.append(new_row)
    return InlineKeyboardMarkup(new_keyboard)

# Другие константы, функции и классы можно добавлять сюда
