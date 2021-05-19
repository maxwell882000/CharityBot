from telegram.ext import ConversationHandler, MessageHandler, Filters
from telegram import ParseMode

from charity.models import TelegramUser, HelpRequest
from .resources import strings, keyboards
from bot.utils import Navigation, CharityFilters, Geolocation

LOCATION = range(1)


def can_help(update, context):
    message = update.message
    if 'user' not in context.user_data:
        try:
            user = TelegramUser.objects.get(pk=message.from_user.id)
        except TelegramUser.DoesNotExist:
            return
        context.user_data['user'] = user
    language = context.user_data['user'].language
    location_message = strings.get_string('can_help.location', language)
    location_keyboard = keyboards.get_keyboard('can_help.location', language)
    message.reply_text(text=location_message, reply_markup=location_keyboard)
    return LOCATION


def can_help_location(update, context):
    location = update.message.location
    latitude = location.latitude
    longitude = location.longitude
    all_help_requests = HelpRequest.objects.filter(hidden=False)
    results = []
    language = context.user_data['user'].language
    far_away = False
    if not all_help_requests:
        empty_message = strings.get_string('can_help.empty', language)
        Navigation.to_main_menu(update, context, message=empty_message)
        return ConversationHandler.END
    for request in all_help_requests:
        # Find all requests within 1 kilometer
        distance = Geolocation.distance_between_two_points((latitude, longitude), (request.latitude, request.longitude))
        if distance <= 1:
            results.append({
                'distance': distance,
                'request': request
            })
    if not results or len(results) < 10:
        # If there aren't requests within 1 kilometer, find all requests 
        for request in all_help_requests:
            distance = Geolocation.distance_between_two_points((latitude, longitude), (request.latitude, request.longitude))
            results.append({
                'distance': distance,
                'request': request
            })
        far_away = True
    exists_message = strings.get_string('can_help.exists', language)
    Navigation.to_main_menu(update, context, message=exists_message)
    results = sorted(results, key=lambda i: i['distance'])
    if far_away:
        # If found requests are far away, show first 10 elements
        results = results[:10]
    for result in results:
        request_message = strings.from_help_request_distance(result, language)
        request_keyboard = keyboards.from_help_request_keyboard(result['request'], language)
        update.message.reply_text(text=request_message, reply_markup=request_keyboard, parse_mode=ParseMode.HTML)
    return ConversationHandler.END


def cancel(update, context):
    Navigation.to_main_menu(update, context)
    return ConversationHandler.END


can_help_conversation = ConversationHandler(
    entry_points=[MessageHandler(CharityFilters.CanHelpFilter(), can_help)],
    states={
        LOCATION: [MessageHandler(Filters.location, can_help_location), MessageHandler(CharityFilters.CancelFilter(), cancel)]
    },
    fallbacks=[MessageHandler(CharityFilters.CancelFilter(), cancel)]
)
