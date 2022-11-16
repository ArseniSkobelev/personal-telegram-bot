from datetime import datetime
import numpy as np
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
from Handlers.config import ConfigHandler
from Handlers.weather_code import WeatherCodeHandler
from Handlers.dialogue_handler import DialogueHandler
from Handlers.keywords import KeywordHandler
from Handlers.budget import BudgetHandler
from Classes.Person import (
    Person
)
from Classes.Person import authorize
from Classes.News import Article
from Modules.database import Database
from Modules.log import Logger


logger = Logger()
Logger.log.info("Initialized logger")

_ch = ConfigHandler()
_wch = WeatherCodeHandler()
_dh = DialogueHandler()
_db = Database()
_ph = Person()
_bh = BudgetHandler()
_kh = KeywordHandler([["User management", "Budget"],
                     ["Automation", "Miscellaneous"]])


def get_time_of_day(hour):
    if hour >= 0 and hour < 12:
        return "morning"
    elif hour >= 12 and hour < 16:
        return "afternoon"
    elif hour >= 16 and hour < 24:
        return "night"
    else:
        return "day"


async def budget(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    new_budget = _bh.create_budget(update.effective_chat.id)
    new_transaction = _bh.create_transaction(update.effective_chat.id)
    print(new_budget, new_transaction)

    await context.bot.send_message(update.effective_chat.id, "Test")


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
        if _dh.get_dialogues_by_userid(update.effective_user.id) or _kh.is_keyword(_kh.keywords, update.effective_message.text):
            if _dh.get_dialogue_by_title(_ch.get_key(
                    "DIALOGUE", "CREATE_BUDGET"), update.effective_user.id):
                await dialogue_create_budget(update, context, update.effective_user.id)
            if update.effective_message.text == "Budget" or _dh.get_dialogue_by_title(_ch.get_key(
                    "DIALOGUE", "BUDGET"), update.effective_user.id):

                await dialogue_budget(update, context, update.effective_user.id)
                # TODO: handle keyword in default handler

            else:
                user = _db.find_one(
                    'user', {"userid": update.effective_user.id})
                if user:
                    logger.log.debug(
                        f"An unhandled command has been executed by {update.effective_user.username}")
                    answer_text = _ch.get_key(
                        "BOT_MESSAGES", "UNKNOWN_COMMAND")

                    await context.bot.send_message(chat_id=update.effective_chat.id, text=answer_text)
                else:
                    await dialogue_create_user(update, context, update.effective_chat.id)
    else:
        answer_text = _ch.get_key("BOT_MESSAGES", "UNATHORIZED_USER")
        Logger.log.warning(_ch.get_key(
            "LOG", "USER_AUTHORIZATION_UNAUTHORIZED"))
        await context.bot.send_message(chat_id=update.effective_chat.id, text=answer_text)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if authorize(update.effective_user.id):
        keyboard = _kh.keywords

        reply_markup = ReplyKeyboardMarkup(keyboard)

        await update.message.reply_text("Please choose:", reply_markup=reply_markup)
    else:
        answer_text = _ch.get_key("BOT_MESSAGES", "UNATHORIZED_USER")
        Logger.log.warning(_ch.get_key(
            "LOG", "USER_AUTHORIZATION_UNAUTHORIZED"))
        await context.bot.send_message(chat_id=update.effective_chat.id, text=answer_text)


async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if authorize(update.effective_user.id):
        date_today = datetime.today()
        str_format = date_today.strftime(f"%Y-%m-%d")
        hour = datetime.now(pytz.timezone("Europe/Berlin")).strftime("%H")

        # TODO
        # TODO
        # TODO location configuration
        # TODO
        # TODO

        api_url = f"https://api.open-meteo.com/v1/forecast?latitude=60.79&longitude=11.03&hourly=temperature_2m,rain,weathercode&current_weather=true&timezone=Europe%2FBerlin&start_date={str(str_format)}&end_date={str(str_format)}"

        response = requests.get(api_url, timeout=5)
        response_json = response.json()
        weather_status = ""
        for time, temp, code, rain in zip(response_json['hourly']['time'], response_json['hourly']['temperature_2m'], response_json['hourly']['weathercode'], response_json['hourly']['rain']):
            if (str(time[11:]).__contains__(hour)):
                weather_status = _wch.get_weather_status(str(code))
                data = dict()
                data['time'] = time
                data['temp'] = temp
                data['code'] = weather_status
                data['rain'] = rain
                return data
    else:
        answer_text = _ch.get_key("BOT_MESSAGES", "UNATHORIZED_USER")
        Logger.log.warning(_ch.get_key(
            "LOG", "USER_AUTHORIZATION_UNAUTHORIZED"))
        await context.bot.send_message(chat_id=update.effective_chat.id, text=answer_text)


async def news(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if authorize(update.effective_user.id):
        url = _ch.get_key("CONFIG", "ARTICLE_WEBSITE")
        number_of_articles = int(_ch.get_key(
            "CONFIG", "NUMBER_OF_NEWS_ARTICLES"))
        message = ""

        articles = []

        r1 = requests.get(url, timeout=5)
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

        await update.message.reply_text(message, disable_web_page_preview=True)
    else:
        answer_text = _ch.get_key("BOT_MESSAGES", "UNATHORIZED_USER")
        Logger.log.warning(_ch.get_key(
            "LOG", "USER_AUTHORIZATION_UNAUTHORIZED"))
        await context.bot.send_message(chat_id=update.effective_chat.id, text=answer_text)


async def dialogue_create_budget(update: Update, context: ContextTypes.DEFAULT_TYPE, userid) -> None:
    dialogue = _dh.get_dialogue_by_title(
        title=_ch.get_key(
            "DIALOGUE", "CREATE_BUDGET"), userid=userid)

    if dialogue:
        current_step = dialogue.current_step
        if current_step == 1:
            budget = _bh.create_budget(userid)
            budget.balance = update.effective_message.text
            budget.last_update = datetime.now()
            budget.is_updated = True
            budget.save()

            _dh.delete_dialogue(_ch.get_key(
                "DIALOGUE", "CREATE_BUDGET"))

            await context.bot.send_message(chat_id=update.effective_chat.id, text="Nice! Your budget is now created!")
    else:
        dialogue_title = _ch.get_key(
            "DIALOGUE", "CREATE_BUDGET")
        Logger.log.info(
            f"A new dialogue has been started with the following title: {dialogue_title} by {update.effective_user.username}")
        _dh.create_dialogue(dialogue_title, userid)
        text = "What is your budget for this month?"

        await update.message.reply_text(text)


async def dialogue_budget(update: Update, context: ContextTypes.DEFAULT_TYPE, userid) -> None:
    dialogue = _dh.get_dialogue_by_title(
        title=_ch.get_key(
            "DIALOGUE", "BUDGET"), userid=userid)

    if dialogue:
        current_step = dialogue.current_step
        if current_step == 1:
            if (update.effective_message.text == "Yes"):
                if (len(list(_db.find("budget", {"owner_id": userid}))) == 0):
                    keyboard = [["Yes", "No"]]

                    reply_markup = ReplyKeyboardMarkup(keyboard)

                    await context.bot.send_message(userid, f"You don't seem to have a budget setup yet, {update.effective_user.username}. Do you wan't to do it now?", reply_markup=reply_markup)
            elif update.effective_message.text == "No":
                _dh.delete_dialogue(_ch.get_key(
                    "DIALOGUE", "BUDGET"))
                return await update.message.reply_text("That's ok. I am always here to help if you need me!")
            dialogue.next_step()
        if current_step == 2:
            if (update.effective_message.text == "Yes"):
                return await dialogue_create_budget(update, context, userid)
            elif update.effective_message.text == "No":
                _dh.delete_dialogue(_ch.get_key(
                    "DIALOGUE", "BUDGET"))
                return await update.message.reply_text("That's ok. I am always here to help if you need me!")
    else:
        dialogue_title = _ch.get_key(
            "DIALOGUE", "BUDGET")
        Logger.log.info(
            f"A new dialogue has been started with the following title: {dialogue_title} by {update.effective_user.username}")
        _dh.create_dialogue(dialogue_title, userid)
        text = f"Hey, *{update.effective_user.username}*! Do you want to do something related to budgetting?"
        keyboard = [["Yes", "No"]]

        reply_markup = ReplyKeyboardMarkup(keyboard)

        await update.message.reply_text(text, reply_markup=reply_markup)


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

    weather_data = await weather(update, context)

    answer_text = f"Good {get_time_of_day(current_hour)}, *{update.effective_user.username}*!\nThe weather status for today is: {weather_data['code']}. The current temperature is {weather_data['temp']}°C and the rain expectancy is at {weather_data['rain']}mm for the current hour.\n\nHere are the news from today's newspaper:"

    await context.bot.send_message(chat_id=update.effective_chat.id, text=answer_text)

    await news(update, context)


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

    budget_handler = PrefixHandler("!", "budget", budget)

    default_handler = MessageHandler(filters.ALL, default_handler)
    app.add_handlers([hello_handler, today_handler,
                     start_handler, budget_handler])
    app.add_handler(default_handler)
    Logger.log.info(
        f"{BOT_NAME} at {BOT_STAGE} stage version {BOT_VERSION} is ready")
    app.run_polling()
