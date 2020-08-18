import scraper
import constants

import datetime
import pymongo
import schedule
from telegram.ext import Updater, CommandHandler

service_update_template = open("templates/service_update_template").read()
get_updates_template = open("templates/get_updates_template").read()

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!") 

def get_service_update(update, context):
    if len(context.args) > 1 or len(context.args) < 1:
        context.bot.send_message(chat_id=update.effective_chat.id, 
                text="Please use \get_updates <route_name> to get updates.")

    connection = pymongo.MongoClient(constants.MONGODB_CONNECTION_URL)
    updates_db = connection.translink.service_updates

    service_updates = updates_db.find({"affected_services": {"$elemMatch": {"name": context.args[0]}}})
    str_service_updates = get_updates_template.format(
            route_name=context.args[0],
            date_time=str(datetime.datetime.now().strftime("%H:%M %d/%m/%Y")))
    for service_update in service_updates:
        str_service_updates += "\n"

        if service_update["severity"] == "Major":
            str_service_updates +=  "\U0001F534 "
        elif service_update["severity"] == "Minor":
            str_service_updates +=  "\U0001F7E1 "
        elif service_update["severity"] == "Informative":
            str_service_updates +=  "\U0001F535 "

        str_service_updates += service_update_template.format(
                severity=service_update["severity"], title=service_update["title"], 
                dates=service_update["dates"], url=service_update["url"])

    context.bot.send_message(chat_id=update.effective_chat.id, text=str_service_updates)

updater = Updater(token=constants.TELEGRAM_BOT_TOKEN, use_context=True)
updater.dispatcher.add_handler(CommandHandler("start", start))
updater.dispatcher.add_handler(CommandHandler("get_updates", get_service_update))
updater.start_polling()

schedule.every(5).minutes.do(scraper.main)
while 1:
    schedule.run_pending()


