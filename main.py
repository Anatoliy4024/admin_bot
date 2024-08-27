import sqlite3
import logging
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from config.config import DATABASE_PATH, BOT_TOKEN, IRA_CHAT_ID, ADMIN_CHAT_ID  # Импортируем ID ДЛЯ СЦЕНАРИЯ ИРИНА И СЕРВИС
from modules.constants import UserData, disable_language_buttons, ORDER_STATUS
from helpers.database_helpers import send_proforma_to_user, get_full_proforma
from keyboards import language_selection_keyboard, user_options_keyboard, irina_service_menu, service_menu_keyboard
from text_handlers import handle_message
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters

ORDER_STATUS_REVERSE = {v: k for k, v in ORDER_STATUS.items()}


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

    options_message = None  # Инициализация переменной

    # Проверка ID пользователя
    if user_id == IRA_CHAT_ID:
        # Приветственное сообщение для Ирины
        message = await update.message.reply_text(
            "Привет, Иринушка! Я - твой АдминБот."
        )
        # Отображаем меню с 5 кнопками для Ирины
        options_message = await update.message.reply_text(
            "ВЫБЕРИ ДЕЙСТВИЕ:",
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
            "ВЫБЕРИ ДЕЙСТВИЕ:",
            reply_markup=service_menu_keyboard()
        )
    else:
        # Обычное приветственное сообщение для других пользователей
        message = await update.message.reply_text(
            f"Welcome {user.first_name}! Choose your language / Выберите язык",
            reply_markup=language_selection_keyboard()
        )

    # Сохраняем ID сообщения с кнопками, чтобы потом их заменить
    context.user_data['language_message_id'] = message.message_id

    # Проверка и сохранение ID сообщения с опциями, если оно существует
    if options_message:
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
    Если найден статус 4, обновляет его на 5 после просмотра проформы.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    try:
        # Сначала пытаемся найти session_number со статусом 4 (Ирина и Сервисная служба получили сообщение)
        cursor.execute("""
            SELECT session_number 
            FROM orders 
            WHERE user_id = ? 
            AND status = ? 
            ORDER BY session_number DESC 
            LIMIT 1
        """, (user_id, ORDER_STATUS["4-Ирина и Сервисная служба получили сообщение о новой ПРОФОРМЕ"]))

        result = cursor.fetchone()

        if result:
            session_number = result[0]

            return session_number  # Возвращает session_number после обновления статуса

        else:
            # Если ничего не найдено, ищем session_number со статусом 5 (Заказчик просмотрел ПРОФОРМУ)
            cursor.execute("""
                SELECT session_number 
                FROM orders 
                WHERE user_id = ? 
                AND status = ? 
                ORDER BY session_number DESC 
                LIMIT 1
            """, (user_id, ORDER_STATUS["5-Заказчик зашел в АдминБот и просмотрел свою ПРОФОРМУ"]))

            result = cursor.fetchone()

            if result:
                return result[0]  # Возвращает session_number для статуса 5
            else:
                raise ValueError("Нет подходящих записей для этого пользователя.")

    finally:
        conn.close()


# Обработчик нажатий на кнопки
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'inactive_button':
        # Эта кнопка неактивна, ничего не делаем
        return

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

        # Добавляем новый блок для обработки кнопки "Найти и смотреть ордер"
    elif query.data == 'find_and_view_order':
        try:
            # Отправляем сообщение с запросом номера ордера
            await query.message.reply_text("Пожалуйста, введите номер ордера:")

            # Устанавливаем шаг для ожидания ввода номера ордера
            user_data.set_step('awaiting_order_number')
        except Exception as e:
            logger.error(f"Ошибка при обработке запроса на поиск ордера: {str(e)}")
            await query.message.reply_text("Произошла ошибка при попытке обработать запрос на поиск ордера.")


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


def format_proforma_message(order_info):
    """Форматирует сообщение с информацией о проформе для Ирины."""
    return (
        f"Информация по заказу:\n"
        f"Номер проформы: {order_info[0]}_{order_info[1]}\n"
        f"Дата мероприятия: {order_info[2]}\n"
        f"Время: {order_info[3]} - {order_info[4]}\n"
        f"Количество людей: {order_info[5]}\n"
        f"Стиль мероприятия: {order_info[6]}\n"
        f"Город: {order_info[7]}\n"
        f"Стоимость: {order_info[8]} евро\n"
        f"Предпочтения: {order_info[9]}\n"  # Добавляем предпочтения
        f"Текущий статус: {order_info[10]}"  # Добавляем текущий статус
    )


async def handle_irina_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    if user.id == IRA_CHAT_ID:
        proforma_number = update.message.text

        # Удаляем предыдущее сообщение с проформой, если оно существует
        previous_message_id = context.user_data.get('proforma_message_id')
        if previous_message_id:
            try:
                await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=previous_message_id)
            except Exception as e:
                logging.error(f"Ошибка при удалении предыдущего сообщения: {e}")

        # Парсим номер проформы и получаем данные из БД
        user_id, session_number, status = parse_proforma_number(proforma_number)
        order_info = get_full_proforma(user_id, session_number)
        if order_info:
            # Преобразуем числовой статус в текстовое описание
            status_description = ORDER_STATUS_REVERSE.get(order_info[10], "Неизвестный статус")

            # Формируем сообщение с информацией о проформе
            message_text = (
                f"Информация по заказу:\n"
                f"Номер проформы: {order_info[0]}_{order_info[1]}\n"
                f"Дата мероприятия: {order_info[2]}\n"
                f"Время: {order_info[3]} - {order_info[4]}\n"
                f"Количество людей: {order_info[5]}\n"
                f"Стиль мероприятия: {order_info[6]}\n"
                f"Город: {order_info[7]}\n"
                f"Стоимость: {order_info[8]} евро\n"
                f"Предпочтения: {order_info[9]}\n"
                f"Текущий статус: {status_description}"
            )

            # Отправляем информацию о проформе Ирине и сохраняем ID сообщения
            sent_message = await update.message.reply_text(message_text)
            context.user_data['proforma_message_id'] = sent_message.message_id
        else:
            await update.message.reply_text("Проформа не найдена.")


def parse_proforma_number(proforma_number):
    """
    Парсинг номера проформы для извлечения user_id, session_number и status.
    Пример формата: '123456_1_3' => user_id=123456, session_number=1, status=3
    """
    try:
        user_id, session_number, status = proforma_number.split('_')

        logging.info(f"Результат парсинга: user_id={user_id}, session_number={session_number}, status={status}")

        return int(user_id), int(session_number), int(status)
    except ValueError:
        logging.error(f"Ошибка парсинга номера проформы: {proforma_number}")
        return None, None, None


# Основной блок

if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(CallbackQueryHandler(irina_service_buttons_callback))
    application.add_handler(MessageHandler(filters.TEXT & filters.User(IRA_CHAT_ID), handle_irina_input))  # Обработчик для Ирины

    application.run_polling()