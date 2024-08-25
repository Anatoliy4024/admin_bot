# database_helpers.py
import sqlite3
import logging
from telegram import Bot
from modules.constants import ORDER_STATUS
from config.config import DATABASE_PATH, BOT_TOKEN
from translations import translations


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


async def send_proforma_to_user(user_id, session_number, user_data):
    """Отправляет информацию о заказе пользователю."""

    try:
        # Получаем полную проформу
        order_info = get_full_proforma(user_id, session_number)

        # Получаем язык пользователя из user_data
        language = user_data.get_language() or 'en'
        trans = translations.get(language, translations['en'])  # Используем 'en' по умолчанию

        # Формируем сообщение для отправки пользователю
        user_message = (
            f"{trans['order_confirmed']}\n"
            f"{trans['proforma_number']} {order_info[0]}_{order_info[1]}_3\n"
            f"{trans['event_date']} {order_info[2]}\n"
            f"{trans['time']} {order_info[3]} - {order_info[4]}\n"
            f"{trans['people_count']} {order_info[5]}\n"
            f"{trans['event_style']} {order_info[6]}\n"
            f"{trans['city']} {order_info[7]}\n"
            f"{trans['amount_to_pay']} {float(order_info[8]) - 20} евро\n"
            f"\n{trans['delivery_info']}"
        )

        # Отправляем сообщение пользователю
        bot = Bot(token=BOT_TOKEN)
        message = await bot.send_message(chat_id=user_id, text=user_message)

        logging.info(f"Message sent to user {user_id}.")

        # Обновляем статус ордера
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE orders SET status = ? WHERE user_id = ? AND session_number = ?",
            (ORDER_STATUS["сообщение отправлено юзеру"], user_id, session_number)
        )
        conn.commit()

        return message

    except Exception as e:
        logging.error(f"Failed to send order info to user: {e}")
        print(f"Ошибка при отправке сообщения: {e}")

    finally:
        conn.close()
