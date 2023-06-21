import logging
from dotenv import load_dotenv

import os

from telegram import __version__ as TG_VER
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from actions.preys import pr_start, pr_callback

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

MAIN_KEYBOARD = [["Молитвы", "Телефоны", "Группы"],
        ["Файлы", "Спикерские", "Служения"]]

async def web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = json.loads(update.effective_message.web_app_data.data)
    if data["type"] == "pr":
        pr_web_app_data(update, context)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_photo(open('/workspaces/bender-2.0/bot/bender/1.jpg', 'rb'))
        
    await update.effective_message.reply_text(f"Привет, {update.effective_message.from_user.name}, давно не виделись!", reply_markup=ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True, input_field_placeholder="Выбери раздел из меню"))

async def event_in_develop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(f"К сожалению этот раздел еще в разработке. Выбери что-то другое.", reply_markup=ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True, input_field_placeholder="Выбери раздел из меню")) 
    
def main() -> None:

    load_dotenv()
    API_KEY = os.getenv('API_KEY')

    application = Application.builder().token(API_KEY).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(pr_callback, r"^pr_.*$"))
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data))
    application.add_handler(MessageHandler(filters.Text(['Молитвы']), pr_start))
    
    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
