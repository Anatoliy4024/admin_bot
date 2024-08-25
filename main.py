import sqlite3
import logging
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from config.config import DATABASE_PATH, BOT_TOKEN, IRA_CHAT_ID, ADMIN_CHAT_ID  # Импортируем ID ДЛЯ СЦЕНАРИЯ ИРИНА И СЕРВИС
from modules.constants import UserData, disable_language_buttons, ORDER_STATUS
from helpers.database_helpers import send_proforma_to_user, get_full_proforma
from keyboards import language_selection_keyboard, user_options_keyboard, irina_service_menu, service_menu_keyboard

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
    user_id = user.id  # Получаем user_id пользователя
    user_data = context.user_data.get('user_data', UserData())
    context.user_data['user_data'] = user_data

    # Проверка ID пользователя
    if user_id == IRA_CHAT_ID:
        # Приветственное сообщение для Ирины
        message = await update.message.reply_text(
            "Привет, Иринушка! Я - твой АдминБот.\n(Это служебное сообщение. На него не надо отвечать)\n"
            "_____________________________________\n"
            "Только что PicnicsAlicanteBot зафиксировал бронирование:\n"
            "ПРОФОРМА №..."
        )
        # Отображаем меню с 5 кнопками для Ирины
        options_message = await update.message.reply_text(
            "Выбери действие:",
            reply_markup=irina_service_menu()
        )
    elif user_id == ADMIN_CHAT_ID:
        # Приветственное сообщение для Службы сервиса
        message = await update.message.reply_text(
            "Привет! Твой id - ........ соответствует Службе сервиса.\n"
            "Предоставляю доступ к технической информации"
        )
        # Отображаем меню с кнопками для Службы сервиса
        options_message = await update.message.reply_text(
            "Выбери действие:",
            reply_markup=service_menu_keyboard()
        )
    elif user_id == ADMIN_CHAT_ID:
        # Приветственное сообщение для Администратора
        message = await update.message.reply_text(
            "Привет, Админ! Твой id - ........ соответствует правам Администратора.\n"
            "Вот что ты можешь сделать:"
        )
        # Отображаем меню с кнопками для Администратора
        options_message = await update.message.reply_text(
            "Выбери действие:",
            reply_markup=irina_service_menu()  # Можно использовать ту же клавиатуру, если действия одинаковые
        )
    else:
        # Обычное приветственное сообщение для других пользователей
        message = await update.message.reply_text(
            f"Welcome {user.first_name}! Choose your language / Выберите язык",
            reply_markup=language_selection_keyboard()
        )

    # Сохраняем ID сообщения с кнопками, чтобы потом их заменить
    context.user_data['language_message_id'] = message.message_id
    context.user_data['options_message_id'] = options_message.message_id

# Функция для получения user_id и username по user_id
def get_user_info_by_user_id(user_id):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, username FROM users WHERE user_id = ?", (user_id,))
    user_info = cursor.fetchone()
    conn.close()
    return user_info

# Функция для получения последнего session_number
def get_latest_session_number(user_id):
    """
    Получает максимальный session_number для пользователя с user_id.
    Сначала проверяет статус 5, если не найдено - ищет с статусом 4.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    try:
        # Сначала пытаемся найти session_number со статусом 5 (сообщение отправлено юзеру)
        cursor.execute("""
            SELECT session_number 
            FROM orders 
            WHERE user_id = ? 
            AND status = ? 
            ORDER BY session_number DESC 
            LIMIT 1
        """, (user_id, ORDER_STATUS["сообщение отправлено юзеру"]))

        result = cursor.fetchone()

        if result:
            return result[0]  # Возвращает session_number для статуса 5
        else:
            # Если ничего не найдено, ищем session_number со статусом 4 (админ_бот получил сообщение)
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
                return result[0]  # Возвращает session_number для статуса 4
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

        # Удаляем предыдущие сообщения с опциями и проформой
        options_message_id = context.user_data.get('options_message_id')
        proforma_message_id = context.user_data.get('proforma_message_id')

        if options_message_id:
            try:
                await context.bot.delete_message(chat_id=query.message.chat_id, message_id=options_message_id)
            except Exception as e:
                logger.error(f"Error deleting options message: {e}")

        if proforma_message_id:
            try:
                await context.bot.delete_message(chat_id=query.message.chat_id, message_id=proforma_message_id)
            except Exception as e:
                logger.error(f"Error deleting proforma message: {e}")

        # Отправляем новые кнопки в соответствии с выбранным языком и заголовок
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

        new_options_message = await query.message.reply_text(
            headers.get(language_code, "Choose"),
            reply_markup=user_options_keyboard(language_code)
        )

        # Обновляем ID сообщения с новыми опциями
        context.user_data['options_message_id'] = new_options_message.message_id

    elif query.data == 'get_proforma':
        try:
            # Получаем user_id пользователя
            user_id = update.effective_user.id

            # Получаем последний session_number для пользователя
            session_number = get_latest_session_number(user_id)

            if session_number:
                # Отправляем проформу пользователю
                proforma_message = await send_proforma_to_user(user_id, session_number, user_data)

                # Сохраняем ID сообщения с проформой
                context.user_data['proforma_message_id'] = proforma_message.message_id

            else:
                await query.message.reply_text(f"Не удалось найти session_number для user_id: {user_id}")
        except Exception as e:
            logger.error(f"Ошибка при получении информации о пользователе: {str(e)}")
            await query.message.reply_text("Произошла ошибка при попытке получить информацию о пользователе.")

# Добавляем обработчик для кнопок Ирины и Службы сервиса
async def irina_service_buttons_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'btn1':
        await query.message.reply_text("Вы выбрали действие 1")
    elif query.data == 'btn2':
        await query.message.reply_text("Вы выбрали действие 2")
    elif query.data == 'btn3':
        await query.message.reply_text("Вы выбрали действие 3")
    elif query.data == 'btn4':
        await query.message.reply_text("Вы выбрали действие 4")
    elif query.data == 'btn5':
        await query.message.reply_text("Вы выбрали действие 5")

# Основной блок
if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(CallbackQueryHandler(irina_service_buttons_callback))  # Обработчик кнопок
    application.run_polling()
