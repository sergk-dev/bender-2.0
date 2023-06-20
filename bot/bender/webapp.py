#!/usr/bin/env python
# pylint: disable=unused-argument,wrong-import-position
# This program is dedicated to the public domain under the CC0 license.

"""
Simple example of a Telegram WebApp which displays a color picker.
The static website for this website is hosted by the PTB team for your convenience.
Currently only showcases starting the WebApp via a KeyboardButton, as all other methods would
require a bot token.
"""
import json
import logging
from telegram import __version__ as TG_VER
import urllib.parse as urllib
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
from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import os
from dotenv import load_dotenv
import psycopg2    
querylist = []
def make_query(query_text, query_params):
    load_dotenv()
    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = os.getenv('DB_PORT')
    DB_NAME = os.getenv('DB_NAME')
    DB_USERNAME = os.getenv('DB_USERNAME')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USERNAME,
        password=DB_PASSWORD
    )
    cursor = conn.cursor()    
    cursor.execute(query_text, query_params)
    if query_text.startswith('SELECT'):
        results = cursor.fetchall()
    else:
        results = None
    cursor.close()
    conn.commit()
    conn.close()
    querylist.append(cursor.query)
    print(querylist) 
    return results   

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# Define a `/start` command handler.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message with a button that opens a the web app."""
    value_to_send = urllib.quote('где кнопка лебовски')
    name = urllib.quote('Где кнопка лебовски')
    web_app_url = f"https://all12steps.ru/botapps/text_input.html?data={value_to_send}&name={name}"
    web_app=WebAppInfo(url=web_app_url)
    await update.message.reply_text(
        "Please press the button below to choose a color via the WebApp.",
        reply_markup=ReplyKeyboardMarkup.from_button(
            KeyboardButton(
                text="Open the color picker!",
                web_app=web_app,
            )
        ),
    )

# Handle incoming WebAppData
async def web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Print the received data and remove the button."""
    # Here we use `json.loads`, since the WebApp sends the data JSON serialized string
    # (see webappbot.html)
    data = json.loads(update.effective_message.web_app_data.data)
    query = "INSERT INTO bender_prey (community_id, text, type, user_id) VALUES (%s, %s, %s, %s)"
    params = (1, data['text'], 'prod', 0)
    make_query(query, params)
    await update.message.reply_html(
        text=data["text"],
        #reply_markup=ReplyKeyboardRemove(),
    )


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    load_dotenv()
    API_KEY = os.getenv('API_KEY')
    application = Application.builder().token(API_KEY).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()