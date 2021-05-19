from telegram.ext import CallbackQueryHandler, CallbackContext, ConversationHandler, MessageHandler, Filters
from telegram import Update

from charity.models import TelegramUser, TelegramUserComplain, HelpRequest, HelpRequestComplain
from .resources import strings, keyboards
from bot.utils import Navigation, CharityFilters


TEXT = range(1)

def give_away_offer_user_comlain(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.data.split(':')[1]
    try:
        user_to = TelegramUser.objects.get(pk=user_id)
    except TelegramUser.DoesNotExist:
        query.answer()
        return
    user = TelegramUser.objects.get(pk=query.from_user.id)
    context.user_data['user'] = user
    context.user_data['complain'] = TelegramUserComplain(user_from=user, user_to=user_to)
    complain_message = strings.get_string('give_away.complain.text', user.language)
    complain_keyboard = keyboards.get_keyboard('complain', user.language)
    query.message.reply_text(text=complain_message, reply_markup=complain_keyboard)
    query.answer()
    return TEXT


def help_request_complain(update: Update, context: CallbackContext):
    query = update.callback_query
    help_request_id = query.data.split(':')[1]
    try:
        help_request = HelpRequest.objects.get(pk=help_request_id)
    except HelpRequest.DoesNotExist:
        query.answer()
        return
    user = TelegramUser.objects.get(pk=query.from_user.id)
    context.user_data['user'] = user
    context.user_data['complain'] = HelpRequestComplain(user_from=user, help_request=help_request)
    complain_message = strings.get_string('need_help.complain.text', user.language)
    complain_keyboard = keyboards.get_keyboard('complain', user.language)
    query.message.reply_text(text=complain_message, reply_markup=complain_keyboard)
    query.answer()
    return TEXT


def complain_text(update: Update, context: CallbackContext):
    message = update.message
    complain = context.user_data['complain']
    complain.text = message.text
    complain.save()
    complain_success = strings.get_string('complain.success', context.user_data['user'].language)
    Navigation.to_main_menu(update, context, message=complain_success)
    del context.user_data['complain']
    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext):
    if 'complain' in context.user_data:
        del context.user_data['complain']
    Navigation.to_main_menu(update, context)
    return ConversationHandler.END


telegram_user_complain_conversation = ConversationHandler(
    entry_points=[CallbackQueryHandler(give_away_offer_user_comlain, pattern=r'^give_it_away_complain:.*')],
    states={
        TEXT: [MessageHandler(CharityFilters.CancelFilter(), cancel), MessageHandler(Filters.text, complain_text)]
    },
    fallbacks=[MessageHandler(CharityFilters.CancelFilter(), cancel)]
)

help_request_complain_conversation = ConversationHandler(
    entry_points=[CallbackQueryHandler(help_request_complain, pattern=r'^complain:.*')],
    states={
        TEXT: [MessageHandler(CharityFilters.CancelFilter(), cancel), MessageHandler(Filters.text, complain_text)]
    },
    fallbacks=[MessageHandler(CharityFilters.CancelFilter(), cancel)]
)
