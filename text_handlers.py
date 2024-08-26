import re
import logging
from telegram import Update
from telegram.ext import ContextTypes
from helpers.database_helpers import get_full_proforma, send_proforma_to_user
from modules.constants import UserData, ORDER_STATUS

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data.get('user_data', UserData())

    # Получаем текущий шаг пользователя
    step = user_data.get_step()

    if step == 'awaiting_order_number':
        # Извлекаем текст сообщения
        order_number = update.message.text.strip()

        # Проверяем корректность номера ордера (например, формат должен быть userId_sessionNumber_status)
        match = re.match(r'(\d+)_([\d\w]+)_(\d)', order_number)
        if match:
            user_id = match.group(1)
            session_number = match.group(2)
            status = int(match.group(3))

            # Проверяем, допустим ли статус для просмотра
            if status not in [ORDER_STATUS['админ_бот получил соообщение'], ORDER_STATUS['сообщение отправлено юзеру']]:
                await update.message.reply_text("Этот номер проформы недоступен для просмотра.")
                return

            # Проверяем наличие проформы в базе данных
            try:
                proforma_info = get_full_proforma(user_id, session_number)
                if proforma_info:
                    # Отправляем проформу пользователю
                    await send_proforma_to_user(user_id, session_number, user_data)

                    # Обновляем статус, если необходимо (например, если статус 4, обновляем на 5)
                    if status == ORDER_STATUS['админ_бот получил соообщение']:
                        # Обновляем статус в базе данных на "сообщение отправлено юзеру"
                        # Здесь вызов соответствующей функции обновления (надо будет ее реализовать)
                        pass
                else:
                    await update.message.reply_text("Проформа с указанным номером не найдена.")

            except Exception as e:
                logging.error(f"Ошибка при поиске проформы: {str(e)}")
                await update.message.reply_text("Произошла ошибка при поиске проформы.")
        else:
            await update.message.reply_text("Некорректный формат номера ордера. Попробуйте снова.")
    else:
        await update.message.reply_text("Пожалуйста, следуйте инструкциям.")
