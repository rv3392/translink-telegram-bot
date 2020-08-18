from telegram.ext import Updater, CommandHandler

def list_subscriptions(update, context, added_route_name=None):
    str_subscription_list = ""

    if added_route_name != None:
        str_subscription_list += "Your subscription to {} was successfully added!\n\n".format(added_route_name)
    
    str_subscription_list += "Your subscriptions are listed below:\n"
    subscriptions = list(context.user_data.get("subscribed_routes", set()))
    if len(subscriptions) != 0:
        str_subscription_list += ", ".join(subscriptions)
    else:
        str_subscription_list = "You have no subscriptions.\n\nUse /new_subcription <route_name> to get notified about service updates for a route/"

    context.bot.send_message(chat_id=update.effective_chat.id, text=str_subscription_list)

    print(context.bot_data)

def new_subscription(update, context):
    if len(context.args) < 1:
        context.bot.send_message(chat_id=update.effective_chat.id, 
                text="Please use /new_subscription <route_name> to get notified about service updates for a route.")
        return

    route_name = " ".join(context.args)
    if context.bot_data.get("subscribed_routes", None) == None:
        context.bot_data["subscribed_routes"] = dict()

    if context.bot_data["subscribed_routes"].get(route_name, None) == None:
        context.bot_data["subscribed_routes"][route_name] = set()
    context.bot_data["subscribed_routes"][route_name].add(update.effective_chat.id)

    if context.user_data.get("subscribed_routes", None) == None:
        context.user_data["subscribed_routes"] = set()
    context.user_data["subscribed_routes"].add(route_name)

    list_subscriptions(update, context, added_route_name=route_name)

def remove_subscription(update, context):
    if len(context.args) < 1:
        context.bot.send_message(chat_id=update.effective_chat.id, 
                text="Please use /new_subscription <route_name> to get notified about service updates for a route.")
        return

    route_name = " ".join(context.args)
    if route_name in context.bot_data.get("subscribed_routes", None):
        context.user_data["subscribed_routes"].discard(route_name)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, 
                text="{} is not subscribed to.".format(route_name))
        return

    if update.effective_chat.id in list(context.bot_data["subscribed_routes"][route_name]):
        context.bot_data["subscribed_routes"][route_name].discard(update.effective_chat.id)
        context.bot.send_message(chat_id=update.effective_chat.id, 
                text="{} was successfully removed from your subscriptions".format(route_name))
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, 
                text="{} is not subscribed to.".format(route_name))
        return