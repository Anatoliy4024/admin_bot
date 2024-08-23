##main.py

from keyboards import language_selection_keyboard, user_options_keyboard
from modules.constants import UserData, disable_language_buttons
from config.config import BOT_TOKEN
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

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

# Обработчик нажатий на кнопки
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_data = context.user_data.get('user_data', UserData())
    context.user_data['user_data'] = user_data

    if query.data.startswith('lang_'):
        language_code = query.data.split('_')[1]
        user_data.set_language(language_code)

        # Блокируем кнопки выбора языка после выбора
        await query.edit_message_reply_markup(reply_markup=disable_language_buttons(query.message.reply_markup))

        # Удаляем предыдущее сообщение с опциями
        options_message_id = context.user_data.get('options_message_id')
        if options_message_id:
            try:
                await context.bot.delete_message(chat_id=query.message.chat_id, message_id=options_message_id)
            except Exception as e:
                logger.error(f"Error deleting message: {e}")

        # Отправляем новые кнопки в соответствии с выбранным языком
        new_options_message = await query.message.reply_text(
            "Options:",
            reply_markup=user_options_keyboard(language_code)
        )

        # Обновляем ID сообщения с новыми опциями
        context.user_data['options_message_id'] = new_options_message.message_id

if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button_callback))

    application.run_polling()
