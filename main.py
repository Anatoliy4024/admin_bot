#main.py

from keyboards import language_selection_keyboard, user_options_keyboard
import sqlite3
import logging
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from config.config import DATABASE_PATH, BOT_TOKEN
from modules.constants import UserData, disable_language_buttons
from helpers.database_helpers import send_proforma_to_user
from modules.constants import ORDER_STATUS



# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='helpers/logs/admin_bot.log'
)

logger = logging.getLogger(__name__)

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_data = context.user_data.get('user_data', UserData())
    context.user_data['user_data'] = user_data

    # Отправляем приветственное сообщение с выбором языка и сразу три кнопки
    message = await update.message.reply_text(
        f"Welcome {user.first_name}! Choose your language / Выберите язык",
        reply_markup=language_selection_keyboard()
    )

    # Сохраняем ID сообщения с кнопками, чтобы потом их заменить
    context.user_data['language_message_id'] = message.message_id

    # Отправляем три кнопки, закрепленные под языками
    options_message = await update.message.reply_text(
        "Options:",
        reply_markup=user_options_keyboard(user_data.get_language() or 'en')  # Язык по умолчанию - английский
    )

    # Сохраняем ID сообщения с опциями, чтобы потом их удалить
    context.user_data['options_message_id'] = options_message.message_id


# Функция для получения user_id и username по user_id
def get_user_info_by_user_id(user_id):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT session_number FROM orders WHERE user_id = ? AND status = ? ORDER BY session_number DESC LIMIT 1",
        (user_id, ORDER_STATUS["админ_бот получил соообщение"]))
    cursor.execute("SELECT user_id, username FROM users WHERE user_id = ?", (user_id,))
    user_info = cursor.fetchone()
    conn.close()
    return user_info


# Функция для получения последнего session_number
def get_latest_session_number(user_id):
    """
    Получает максимальный session_number для пользователя с user_id и статусом 4.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT session_number 
            FROM orders 
            WHERE user_id = ? 
            AND status = ? 
            ORDER BY session_number DESC 
            LIMIT 1
        """, (user_id, ORDER_STATUS["админ_бот получил соообщение"]))

        result = cursor.fetchone()

        if result:
            return result[0]  # Возвращает session_number
        else:
            raise ValueError("Нет подходящих записей для этого пользователя.")

    finally:
        conn.close()


# Обработчик нажатий на кнопки
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_data = context.user_data.get('user_data', UserData())
    context.user_data['user_data'] = user_data

    if query.data.startswith('lang_'):
        language_code = query.data.split('_')[1]
        user_data.set_language(language_code)

        # Обновляем текст заголовка в зависимости от выбранного языка
        headers = {
            'en': "Choose",
            'ru': "Выбери",
            'es': "Elige",
            'fr': "Choisissez",
            'uk': "Виберіть",
            'pl': "Wybierz",
            'de': "Wählen",
            'it': "Scegli"
        }

        # Удаляем предыдущее сообщение с опциями
        options_message_id = context.user_data.get('options_message_id')
        if options_message_id:
            try:
                await context.bot.delete_message(chat_id=query.message.chat_id, message_id=options_message_id)
            except Exception as e:
                logger.error(f"Error deleting message: {e}")

        # Отправляем новые кнопки в соответствии с выбранным языком и заголовок
        new_options_message = await query.message.reply_text(
            headers.get(language_code, "Choose"),
            reply_markup=user_options_keyboard(language_code)
        )

        # Обновляем ID сообщения с новыми опциями
        context.user_data['options_message_id'] = new_options_message.message_id
    elif query.data == 'get_proforma':
        try:
            await query.message.reply_text("Привет")

            # Получаем user_id пользователя
            user_id = update.effective_user.id

            # Получаем информацию о пользователе из базы данных
            user_info = get_user_info_by_user_id(user_id)

            if user_info:
                username = user_info[1]
                await query.message.reply_text(f"user_id: {user_id}, username: {username}")

                # Получаем последний session_number для пользователя
                session_number = get_latest_session_number(user_id)

                if session_number:
                    await query.message.reply_text(f"Последний session_number: {session_number}")
                else:
                    await query.message.reply_text(f"Не удалось найти session_number для user_id: {user_id}")
            else:
                await query.message.reply_text(f"user_id: {user_id}, username: не найдено")

        except Exception as e:
            logger.error(f"Ошибка при получении информации о пользователе: {str(e)}")
            await query.message.reply_text(f"Произошла ошибка при попытке получить информацию о пользователе: {str(e)}")


if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button_callback))

    application.run_polling()
