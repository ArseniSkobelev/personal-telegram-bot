import pytz
import json
import bson
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    PrefixHandler,
    Defaults,
    MessageHandler,
    filters
)
from Modules.database import Database
from Classes.ExpenseHandler import Expense
from Modules.env import EnvHandler
from Modules.log import Logger

# create an instance of the improved logger
logger = Logger()
Logger.log.info("Initialized logger")

# create an instance of EnvHandler
env_handler = EnvHandler('./.env')

# constants
DB_NAME = env_handler.get_env("MONGODB_DB_NAME")


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer_text = f"Hello, *{update.effective_user.username}* 👋"

    expense = Expense()
    Database.insert('Expenses', expense.save())

    await context.bot.send_message(chat_id=update.effective_chat.id, text=answer_text)


async def default_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.log.debug(
        f"An unhandled command has been executed by {update.effective_user.username}")

    answer_text = env_handler.get_env("BOT_MESSAGES_UNKNOWN_COMMAND")

    await context.bot.send_message(chat_id=update.effective_chat.id, text=answer_text)

# main loop
if __name__ == '__main__':
    BOT_NAME = env_handler.get_env("BOT_NAME")
    BOT_STAGE = env_handler.get_env("BOT_STAGE")
    BOT_VERSION = env_handler.get_env("BOT_VERSION")
    Database.initialize()
    defaults = Defaults(parse_mode=ParseMode.MARKDOWN,
                        tzinfo=pytz.timezone('Europe/Berlin'))

    app = (
        ApplicationBuilder()
        .token(env_handler.get_env("TELEGRAM_API_KEY"))
        .defaults(defaults)
        .build()
    )

    hello_handler = PrefixHandler("", "hello", hello)
    rest_handler = MessageHandler(filters.ALL, default_handler)
    app.add_handlers([hello_handler])
    app.add_handler(rest_handler)
    Logger.log.info(
        f"{BOT_NAME} at {BOT_STAGE} stage version {BOT_VERSION} is ready")
    app.run_polling()
