import constants
import service_updates

import pymongo
from telegram.ext import Updater, CommandHandler

def send_notification(context, route_name, chat_id, notification_type, service_update):
    str_service_updates = "You have a {} service update for {}!\n".format(notification_type, route_name)
    str_service_updates += service_updates.get_service_updates_message(route_name, [service_update])
    context.bot.send_message(chat_id=chat_id, text=str_service_updates)
    context.bot.send_message(chat_id=chat_id, text="Use /service_updates {} to view all current notifications for that route".format(route_name))

def send_notifications(context, affected_route_ids, notification_type):
    connection = pymongo.MongoClient(constants.MONGODB_CONNECTION_URL)
    updates_db = connection.translink.service_updates

    for route_id in affected_route_ids:
        service_update = updates_db.find_one({"id": route_id})
        for affected_service in service_update["affected_services"]:
            route_name = affected_service["name"]
            chat_ids = context.bot_data["subscribed_routes"].get(route_name, set())
            for chat_id in chat_ids:
                send_notification(context, route_name, chat_id, notification_type, service_update)
