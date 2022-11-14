import numpy as np
from datetime import datetime
import pytz
import requests
from bs4 import BeautifulSoup
from telegram import (Update,
                      ReplyKeyboardMarkup)
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    PrefixHandler,
    Defaults,
    MessageHandler,
    filters,
)
from Classes.Person import (
    Person
)
from Classes.Person import authorize
from Classes.News import Article
from Modules.database import Database
from Modules.log import Logger
from Handlers.config import ConfigHandler
from Handlers.dialogue_handler import DialogueHandler
from Handlers.keywords import KeywordHandler


# create an instance of the improved logger
logger = Logger()
Logger.log.info("Initialized logger")

_ch = ConfigHandler()
_dh = DialogueHandler()
_db = Database()
_ph = Person()
_kh = KeywordHandler([["User management", "Finances"],
                     ["Automation", "Miscellaneous"]])

# constants
DB_NAME = _ch.get_key("DATABASE", "NAME")


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
        answer_text = _ch.get_key("BOT_MESSAGES", "UNATHORIZED_USER")
        Logger.log.warning(_ch.get_key(
            "LOG", "USER_AUTHORIZATION_UNAUTHORIZED"))
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
                answer_text = _ch.get_key("BOT_MESSAGES", "UNKNOWN_COMMAND")

                await context.bot.send_message(chat_id=update.effective_chat.id, text=answer_text)
            else:
                await dialogue_create_user(update, context, update.effective_chat.id)
    else:
        answer_text = _ch.get_key("BOT_MESSAGES", "UNATHORIZED_USER")
        Logger.log.warning(_ch.get_key(
            "LOG", "USER_AUTHORIZATION_UNAUTHORIZED"))
        await context.bot.send_message(chat_id=update.effective_chat.id, text=answer_text)


async def start(update: Update) -> None:
    keyboard = _kh.keywords

    reply_markup = ReplyKeyboardMarkup(keyboard)

    await update.message.reply_text("Please choose:", reply_markup=reply_markup)


async def get_news(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = "https://www.vg.no/"
    number_of_articles = int(_ch.get_key("CONFIG", "NUMBER_OF_NEWS_ARTICLES"))
    message = ""

    articles = []

    r1 = requests.get(url)
    coverpage = r1.content
    soup1 = BeautifulSoup(coverpage, 'html5lib')
    coverpage_news = soup1.find_all('article', class_='article')

    for i in np.arange(0, number_of_articles):
        link = coverpage_news[i].find(
            'div', class_='article-container').find('a')['href']

        title = coverpage_news[i].find(
            'div', class_='article-container').find('a').find('div', class_="titles").find('h3')['aria-label']

        article = Article(title, link)
        articles.append(article)

    for i, article in enumerate(articles):
        message += f"[{article.title}]({article.url})\n\n"

    await update.message.reply_text(message)


async def dialogue_create_user(update: Update, context: ContextTypes.DEFAULT_TYPE, userid):
    dialogue = _dh.get_dialogue_by_title(
        title=_ch.get_key(
            "DIALOGUE", "CREATE_USER"), userid=userid)

    if dialogue:
        current_step = dialogue.current_step
        if current_step == 1:
            if update.effective_message.text.lower() == "no":
                _dh.delete_dialogue(
                    _ch.get_key(
                        "DIALOGUE", "CREATE_USER"))
            else:
                text = "Let's do it! 🎉🎉\nSo, what is your full name?"
                _ph.create_person()
                _ph.set_userid(userid=update.effective_chat.id)
                await context.bot.send_message(update.effective_chat.id, text)
                dialogue.next_step()
        elif current_step == 2:
            _ph.name = update.effective_message.text
            text = f"Nice to meet you, {_ph.name}! What is your age?"
            await context.bot.send_message(update.effective_chat.id, text)
            dialogue.next_step()
        elif current_step == 3:
            _ph.age = update.effective_message.text
            text = "Cool, how tall are you tho?"
            await context.bot.send_message(update.effective_chat.id, text)
            dialogue.next_step()
        elif current_step == 4:
            _ph.height = update.effective_message.text
            text = "What about the weight?"
            await context.bot.send_message(update.effective_chat.id, text)
            dialogue.next_step()
        elif current_step == 5:
            _ph.weight = update.effective_message.text
            text = "And when were you born?"
            await context.bot.send_message(update.effective_chat.id, text)
            dialogue.next_step()
        elif current_step == 6:
            _ph.birthday = update.effective_message.text
            _ph.username = update.effective_user.username
            f_name = _ph.name.split(" ")
            text = f"I think that is about it, {f_name[0]}. Would you like to do something interesting right away?"

            keyboard = [["Yes", "No"]]
            reply_markup = ReplyKeyboardMarkup(keyboard)

            _db.initialize()
            _db.insert('user', _ph.save())

            _ph.destroy_person()
            await update.message.reply_text(text, reply_markup=reply_markup)
            dialogue.next_step()
        elif current_step == 7:
            if update.effective_message.text.lower() == "no":
                print("does not want to do anything")
            else:
                text = "What are you interested in right now?"
                await context.bot.send_message(update.effective_chat.id, text)
                dialogue.next_step()
    else:
        dialogue_title = _ch.get_key(
            "DIALOGUE", "CREATE_USER")
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
    BOT_NAME = _ch.get_key(
        "BOT", "NAME")
    BOT_STAGE = _ch.get_key(
        "BOT", "STAGE")
    BOT_VERSION = _ch.get_key(
        "BOT", "VERSION")

    Database.initialize()

    defaults = Defaults(parse_mode=ParseMode.MARKDOWN,
                        tzinfo=pytz.timezone('Europe/Berlin'))

    app = (
        ApplicationBuilder()
        .token(_ch.get_key(
            "TELEGRAM", "API_KEY"))
        .defaults(defaults)
        .build()
    )

    hello_handler = PrefixHandler("", "hello", hello)
    today_handler = PrefixHandler("!", "today", today)
    start_handler = PrefixHandler("!", "start", start)
    get_news_handler = PrefixHandler("", "news", get_news)
    default_handler = MessageHandler(filters.ALL, default_handler)
    app.add_handlers([hello_handler, today_handler,
                     start_handler, get_news_handler])
    app.add_handler(default_handler)
    Logger.log.info(
        f"{BOT_NAME} at {BOT_STAGE} stage version {BOT_VERSION} is ready")
    app.run_polling()
