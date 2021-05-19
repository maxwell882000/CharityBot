from telegram.ext import ConversationHandler, MessageHandler, Filters
from telegram import ParseMode

from charity.models import TelegramUser, HelpRequest
from .resources import strings, keyboards
from bot.utils import Navigation, CharityFilters

from datetime import datetime


TYPE, DESCRIPTION, LOCATION = range(3)


def _to_type(update, context):
    language = context.user_data['user'].language
    type_message = strings.get_string('need_help.type', language)
    type_keyboard = keyboards.get_keyboard('need_help.type', language)
    update.message.reply_text(text=type_message, reply_markup=type_keyboard, parse_mode=ParseMode.HTML)
    return TYPE


def _to_description(update, context):
    language = context.user_data['user'].language
    description_message = strings.get_string('need_help.description', language)
    description_keyboard = keyboards.get_keyboard('need_help.description', language)
    update.message.reply_text(text=description_message, reply_markup=description_keyboard)
    return DESCRIPTION


def _to_location(update, context):
    language = context.user_data['user'].language
    location_message = strings.get_string('need_help.location', language)
    location_keyboard = keyboards.get_keyboard('need_help.location', language)
    update.message.reply_text(text=location_message, reply_markup=location_keyboard)
    return LOCATION


def need_help(update, context):
    message = update.message
    if 'user' not in context.user_data:
        try:
            user = TelegramUser.objects.get(pk=message.from_user.id)
        except TelegramUser.DoesNotExist:
            return
        context.user_data['user'] = user
    # Check lastest user's help request
    now = datetime.now()
    try:
        latest_user_request = context.user_data['user'].helprequest_set.latest()
    except HelpRequest.DoesNotExist:
        context.user_data['help_request'] = {}
        return _to_type(update, context)
    latest_request_created_at = latest_user_request.created_at.replace(tzinfo=None)
    difference = now - latest_request_created_at
    if difference.days < 14:
        language = context.user_data['user'].language
        not_allowed_message = strings.get_string('need_help.now_allowed', language)
        message.reply_text(text=not_allowed_message)
        return ConversationHandler.END
    context.user_data['help_request'] = {}
    return _to_type(update, context)


def help_type(update, context):
    message = update.message
    context.user_data['help_request']['type'] = message.text
    return _to_description(update, context)


def help_description(update, context):
    message = update.message
    context.user_data['help_request']['description'] = message.text
    return _to_location(update, context)


def help_location(update, context):
    location = update.message.location
    latitude = location.latitude
    longitude = location.longitude
    help_request = HelpRequest.objects.create(help_type=context.user_data['help_request']['type'], 
                                              description=context.user_data['help_request']['description'],
                                              latitude=latitude, longitude=longitude,
                                              user=context.user_data['user'])
    del context.user_data['help_request']
    success_message = strings.get_string('need_help.success', context.user_data['user'].language)
    Navigation.to_main_menu(update, context, message=success_message)
    return ConversationHandler.END


def cancel(update, context):
    if 'help_request' in context.user_data:
        del context.user_data['help_request']
    Navigation.to_main_menu(update, context)
    return ConversationHandler.END


help_request_conversation = ConversationHandler(
    entry_points=[MessageHandler(CharityFilters.NeedHelpFilter(), need_help)],
    states={
        TYPE: [MessageHandler(CharityFilters.CancelFilter(), cancel), MessageHandler(Filters.text, help_type)],
        DESCRIPTION: [MessageHandler(CharityFilters.CancelFilter(), cancel), MessageHandler(Filters.text, help_description)],
        LOCATION: [MessageHandler(Filters.location, help_location), MessageHandler(CharityFilters.CancelFilter(), cancel)]
    },
    fallbacks=[MessageHandler(CharityFilters.CancelFilter(), cancel)]
)
