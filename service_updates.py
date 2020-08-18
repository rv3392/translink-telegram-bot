import constants

import datetime
import pymongo
from telegram.ext import Updater, CommandHandler

def get_service_updates_message(route_name, service_updates):
    str_service_updates = get_updates_template.format(
            route_name=route_name,
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
    
    return str_service_updates

def get_service_updates(update, context):
    if len(context.args) < 1:
        context.bot.send_message(chat_id=update.effective_chat.id, 
                text="Please use /get_updates <route_name> to get updates.")
        return

    connection = pymongo.MongoClient(constants.MONGODB_CONNECTION_URL)
    updates_db = connection.translink.service_updates

    route_name = " ".join(context.args)
    service_updates = list(updates_db.find({"affected_services": {"$elemMatch": {"name": route_name}}}))
    if len(service_updates) == 0:
        context.bot.send_message(chat_id=update.effective_chat.id, 
                text="There are no service updates for {}.".format(route_name))
        return

    context.bot.send_message(chat_id=update.effective_chat.id, 
            text=get_service_updates_message(route_name, service_updates))