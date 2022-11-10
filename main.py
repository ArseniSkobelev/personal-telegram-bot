import pytz
from datetime import datetime
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    PrefixHandler,
    Defaults,
    MessageHandler,
    filters,
)
from Modules.database import Database
from Classes.Expense import Expense
from Handlers.env import EnvHandler
from Modules.log import Logger
from Classes.Person import authorize
from Handlers.DialogueHandler import DialogueHandler


# create an instance of the improved logger
logger = Logger()
Logger.log.info("Initialized logger")

# create an instance of EnvHandler
env_handler = EnvHandler('./.env')

dh = DialogueHandler()


# constants
DB_NAME = env_handler.get_env("MONGODB_DB_NAME")


def get_time_of_day(hour):
    if hour >= 0 and hour < 12:
        return "morning"
    elif hour >= 12 and hour < 16:
        return "afternoon"
    elif hour >= 16 and hour < 24:
        return "night"
    else:
        return "day"


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if authorize(update.effective_user.id):
        answer_text = f"Hello, *{update.effective_user.username}* 👋"

        await context.bot.send_message(chat_id=update.effective_chat.id, text=answer_text)
    else:
        answer_text = env_handler.get_env("BOT_MESSAGES_UNATHORIZED_USER")
        Logger.log.warning("An unathorized user has been detected")
        await context.bot.send_message(chat_id=update.effective_chat.id, text=answer_text)


async def default_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.log.debug(
        f"An unhandled command has been executed by {update.effective_user.username}")

    answer_text = env_handler.get_env("BOT_MESSAGES_UNKNOWN_COMMAND")

    await context.bot.send_message(chat_id=update.effective_chat.id, text=answer_text)


async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now()
    current_hour = now.hour

    # TODO fill with information about the current day; fetch APIs for weather data, news and other things that could be relevant
    answer_text = f"Good {get_time_of_day(current_hour)}, *{update.effective_user.username}*!"

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
    today_handler = PrefixHandler("/", "today", today)
    default_handler = MessageHandler(filters.ALL, default_handler)
    app.add_handlers([hello_handler, today_handler])
    app.add_handler(default_handler)
    Logger.log.info(
        f"{BOT_NAME} at {BOT_STAGE} stage version {BOT_VERSION} is ready")
    app.run_polling()
