#TODO Код полностью сгенерирован, нуждается в тестировании и отладке

import random
import time
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

# Функция для блокировки и удаления новых пользователей с RTL-символами или эмодзи в профиле
def block_and_delete_new_users(update, context):
    user = update.effective_user
    if user.is_bot:
        return

    user_info = user.first_name + (user.last_name or '') + (user.username or '') + (user.description or '')
    rtl_percentage = get_rtl_percentage(user_info)
    emoji_percentage = get_emoji_percentage(user_info)

    if rtl_percentage > 20 or emoji_percentage > 20:
        context.bot.restrict_chat_member(update.effective_chat.id, user.id, can_send_messages=False)
        context.bot.kick_chat_member(update.effective_chat.id, user.id)
    else:
        context.bot.restrict_chat_member(update.effective_chat.id, user.id, can_send_messages=True)
        send_greeting_message(update, context)

# Функция для отправки приветственного сообщения и добавления инлайн-кнопки
def send_greeting_message(update, context):
    user = update.effective_user
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Привет, {user.first_name}! Нажми кнопку 'Нажми меня', чтобы получить полный доступ.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Нажми меня", callback_data='access_granted')]])
    )

# Функция обработки нажатия на инлайн-кнопку
def handle_button_click(update, context):
    query = update.callback_query
    user = query.from_user
    context.bot.restrict_chat_member(update.effective_chat.id, user.id, can_send_messages=True)
    query.answer(text="Теперь у вас полный доступ.")

# Функция для расчета процента RTL-символов в тексте
def get_rtl_percentage(text):
    total_chars = len(text)
    rtl_chars = sum((1 for char in text if char >= '\u0590' and char <= '\u05FF'))
    return (rtl_chars / total_chars) * 100 if total_chars > 0 else 0

# Функция для расчета процента эмодзи в тексте
def get_emoji_percentage(text):
    total_chars = len(text)
    emoji_chars = sum((1 for char in text if char in emoji.UNICODE_EMOJI['en']))
    return (emoji_chars / total_chars) * 100 if total_chars > 0 else 0

# Функция для отправки периодического сообщения с определенным интервалом времени
def send_periodic_message(context):
    current_time = time.localtime()
    if current_time.tm_hour >= 9 and current_time.tm_hour <= 20:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="_Ходют тут и ходют..._",
            parse_mode="Markdown"
        )
        context.job_queue.run_once(delete_message, 10 * 60)  # Удаление сообщения через 10 минут

# Функция для удаления сообщения
def delete_message(context):
    context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=context.job.context
    )

# Функция для запуска бота
def start_bot():
    updater = Updater("YOUR_TOKEN")  # Замените "YOUR_TOKEN" на токен вашего бота

    dispatcher = updater.dispatcher

    # Обработчики команд и сообщений
    dispatcher.add_handler(CommandHandler("start", block_and_delete_new_users))
    dispatcher.add_handler(CallbackQueryHandler(handle_button_click))
    dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members, block_and_delete_new_users))

    # Периодическая отправка сообщения
    job_queue = updater.job_queue
    job_queue.run_repeating(send_periodic_message, random.randint(4, 15) * 60 * 60)

    updater.start_polling()

if __name__ == '__main__':
    start_bot()
