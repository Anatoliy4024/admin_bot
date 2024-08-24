## helpers/database_helpers.py

import sqlite3
import logging
from telegram import Bot
from modules.constants import ORDER_STATUS
from config.config import DATABASE_PATH, BOT_TOKEN


def get_user_data(user_id):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user_data = cursor.fetchone()
    conn.close()
    return user_data


def get_full_proforma(user_id, session_number):
    """
    Получает полную проформу для пользователя по user_id и session_number.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT user_id, session_number, selected_date, start_time, end_time, people_count, selected_style,
            city, calculated_cost
            FROM orders
            WHERE user_id = ? AND session_number = ?
            """,
            (user_id, session_number)
        )
        order_info = cursor.fetchone()

        if order_info:
            return order_info
        else:
            raise ValueError("Нет подходящей проформы для этого пользователя.")

    finally:
        conn.close()










def get_latest_proforma_for_user(user_id):
    """
    Получает номер последней проформы для пользователя по user_id и статусу 4.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT session_number FROM orders WHERE user_id = ? AND status = ? ORDER BY session_number DESC LIMIT 1",
            (user_id, ORDER_STATUS["админ_бот получил соообщение"])
        )
        result = cursor.fetchone()

        if result:
            session_num = result[0]
            return f"{user_id}_{session_num}_4"
        else:
            raise ValueError("Нет подходящих проформ для этого пользователя.")

    finally:
        conn.close()


async def send_proforma_to_user(proforma_number):
    """Отправляет информацию о заказе пользователю."""

    # Извлечение ключей из номера проформы
    try:
        user_id, session_num, status = map(int, proforma_number.split('_'))
    except ValueError:
        logging.error(f"Invalid proforma number format: {proforma_number}")
        return

    # Создаем подключение к базе данных
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT user_id, session_number, selected_date, start_time, end_time, people_count, selected_style, "
            "city, calculated_cost FROM orders WHERE user_id = ? AND status = ? AND session_number = ?",
            (user_id, ORDER_STATUS["зарезервировано"], session_num)
        )
        order_info = cursor.fetchone()

        if order_info is None:
            logging.error(f"No recent orders with status 3 found for user_id {user_id}.")
            return

        # Формируем сообщение для отправки пользователю
        user_message = (
            f"Ваш заказ подтвержден!\n"
            f"ПРОФОРМА № {order_info[0]}_{order_info[1]}_3\n"
            f"Дата мероприятия: {order_info[2]}\n"
            f"Время: {order_info[3]} - {order_info[4]}\n"
            f"Количество персон: {order_info[5]}\n"
            f"Стиль мероприятия: {order_info[6]}\n"
            f"Город: {order_info[7]}\n"
            f"Сумма к оплате: {float(order_info[8]) - 20} евро\n"
        )

        # Отправляем сообщение пользователю
        bot = Bot(token=BOT_TOKEN)
        await bot.send_message(chat_id=user_id, text=user_message)

        logging.info(f"Message sent to user {user_id}.")

        # Обновляем статус ордера
        cursor.execute("UPDATE orders SET status = ? WHERE user_id = ? AND session_number = ?",
                       (ORDER_STATUS["сообщение отправлено юзеру"], user_id, session_num))
        conn.commit()

    except Exception as e:
        logging.error(f"Failed to send order info to user: {e}")
        print(f"Ошибка при отправке сообщения: {e}")

    finally:
        conn.close()
