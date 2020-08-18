import constants
import notification
import route_subscription
import scraper
import service_updates

import datetime
import pymongo
import schedule
from telegram.ext import Updater, CommandHandler, MessageHandler, PicklePersistence, Filters

service_update_template = open("templates/service_update_template").read()
get_updates_template = open("templates/get_updates_template").read()

class InvalidRouteNameException(Exception):
    pass

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!") 

def bot_help(update, context):
    help_message = (
        """
        Translink Bot Features:

        General
        /start
        /help - Shows this message

        Current Service Updates
        /service_updates <route_name> - Gets all current service updates for the route name entered

        Notification Subscription
        /new_subscription <route_name> - Adds a new subscription for the route name. You will receive notifications for that route.
        /remove_subscription <route_name> - Removes a subscription for the route name. You will no longer receive notifications for that route.
        /list_subscriptions - Lists all of your current subscriptions
        """)
    context.bot.send_message(chat_id=update.effective_chat.id, text=help_message)

def scrape_service_update(context):
    ids = scraper.main()
    print(ids)

    notification.send_notifications(context, ids["resolved"], "resolved")
    notification.send_notifications(context, ids["new"], "new")
    notification.send_notifications(context, ids["updated"], "updated")

bot_data = PicklePersistence(filename='bot_data')

updater = Updater(token=constants.TELEGRAM_BOT_TOKEN, persistence=bot_data, use_context=True)
updater.dispatcher.add_handler(CommandHandler("start", start))
updater.dispatcher.add_handler(CommandHandler("help", bot_help))
updater.dispatcher.add_handler(CommandHandler("service_updates", service_updates.get_service_updates))
updater.dispatcher.add_handler(CommandHandler("new_subscription", route_subscription.new_subscription))
updater.dispatcher.add_handler(CommandHandler("list_subscriptions", route_subscription.list_subscriptions))
updater.dispatcher.add_handler(CommandHandler("remove_subscription", route_subscription.remove_subscription))
updater.dispatcher.add_handler(MessageHandler(Filters.command, bot_help))

job_minute = updater.job_queue.run_repeating(scrape_service_update, interval=1200, first=0)

updater.start_polling()




