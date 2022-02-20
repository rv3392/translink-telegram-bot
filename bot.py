import datetime
import os

import notification
import route_subscription
import scraper
import service_updates

from telegram.ext import Updater, CommandHandler, MessageHandler, PicklePersistence, Filters

class InvalidRouteNameException(Exception):
    pass

help_message = open("messages/help_message").read()

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!") 

def bot_help(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=help_message)

def scrape_service_update(context):
    ids = scraper.main()
    print(ids)

    notification.send_notifications(context, ids["resolved"], "resolved")
    notification.send_notifications(context, ids["new"], "new")
    notification.send_notifications(context, ids["updated"], "updated")

bot_data = PicklePersistence(filename='bot_data')

telegram_bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
updater = Updater(token=telegram_bot_token, persistence=bot_data, use_context=True)
updater.dispatcher.add_handler(CommandHandler("start", start))
updater.dispatcher.add_handler(CommandHandler("help", bot_help))
updater.dispatcher.add_handler(CommandHandler("service_updates", service_updates.get_service_updates))
updater.dispatcher.add_handler(CommandHandler("new_subscription", route_subscription.new_subscription))
updater.dispatcher.add_handler(CommandHandler("list_subscriptions", route_subscription.list_subscriptions))
updater.dispatcher.add_handler(CommandHandler("remove_subscription", route_subscription.remove_subscription))
updater.dispatcher.add_handler(MessageHandler(Filters.command, bot_help))

job_minute = updater.job_queue.run_repeating(scrape_service_update, interval=1200, first=0)

updater.start_polling()




