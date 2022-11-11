import pytz
from datetime import datetime
from telegram import (Update,
                      InlineKeyboardButton,
                      InlineKeyboardMarkup,
                      ReplyKeyboardMarkup,
                      KeyboardButton)
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
from Handlers.dialogue_handler import DialogueHandler
from Handlers.keywords import KeywordHandler


# create an instance of the improved logger
logger = Logger()
Logger.log.info("Initialized logger")

# create an instance of EnvHandler
env_handler = EnvHandler(dotenv_path='./.env')

_dh = DialogueHandler()
_db = Database()
_kh = KeywordHandler([["User management", "Finances"],
                     ["Automation", "Miscellaneous"]])

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
    if authorize(update.effective_user.id):
        if (_kh.is_keyword(_kh.keywords, update.effective_message.text)):
            logger.log.debug(
                f"Handling a keyword entered by {update.effective_user.username}")
            # TODO: handle keyword in default handler
            print("keyword")
        else:
            user = _db.find_one('user', {"userid": update.effective_user.id})
            if user:
                logger.log.debug(
                    f"An unhandled command has been executed by {update.effective_user.username}")
                answer_text = env_handler.get_env(
                    "BOT_MESSAGES_UNKNOWN_COMMAND")

                await context.bot.send_message(chat_id=update.effective_chat.id, text=answer_text)
            else:
                await dialogue_create_user(update, context, update.effective_chat.id)
    else:
        answer_text = env_handler.get_env("BOT_MESSAGES_UNATHORIZED_USER")
        Logger.log.warning("An unathorized user has been detected")
        await context.bot.send_message(chat_id=update.effective_chat.id, text=answer_text)


async def start(update: Update) -> None:
    keyboard = _kh.keywords

    reply_markup = ReplyKeyboardMarkup(keyboard)

    await update.message.reply_text("Please choose:", reply_markup=reply_markup)


async def dialogue_create_user(update: Update, context: ContextTypes.DEFAULT_TYPE, userid):
    dialogue = _dh.get_dialogue_by_title(
        title=env_handler.get_env("DIALOGUE_CREATE_USER"), userid=userid)

    if dialogue:
        current_step = dialogue.current_step
        # TODO: continue dialogue
        if current_step == 1:
            if update.effective_message.text.lower() == "no":
                _dh.delete_dialogue(
                    env_handler.get_env("DIALOGUE_CREATE_USER"))
            else:
                text = "Let's do it! 🎉🎉\nSo, what is your full name?"
                await context.bot.send_message(update.effective_chat.id, text)
                dialogue.next_step()
        elif current_step == 2:
            dialogue.next_step()
            print("yes")
    else:
        dialogue_title = env_handler.get_env("DIALOGUE_CREATE_USER")
        Logger.log.info(
            f"A new dialogue has been started with the following title: {dialogue_title} by {update.effective_user.username}")
        _dh.create_dialogue(dialogue_title, userid)
        text = f"I've noticed that you are new here, *{update.effective_user.username}* 🤓\nDo you want to create a new user account?"
        keyboard = [["Yes", "No"]]

        reply_markup = ReplyKeyboardMarkup(keyboard)

        await update.message.reply_text(text, reply_markup=reply_markup)


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
    today_handler = PrefixHandler("!", "today", today)
    start_handler = PrefixHandler("!", "start", start)
    default_handler = MessageHandler(filters.ALL, default_handler)
    app.add_handlers([hello_handler, today_handler, start_handler])
    app.add_handler(default_handler)
    Logger.log.info(
        f"{BOT_NAME} at {BOT_STAGE} stage version {BOT_VERSION} is ready")
    app.run_polling()
