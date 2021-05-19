from telegram.ext import CallbackQueryHandler, MessageHandler, ConversationHandler, CallbackContext, Filters
from telegram import Update

from charity.models import TelegramUser

from .resources import strings, keyboards
from bot.utils import Navigation, CharityFilters


LANGUAGE = range(1)


def languages(update: Update, context: CallbackContext):
    message = update.message
    user =  TelegramUser.objects.get(pk=message.from_user.id)
    context.user_data['user'] = user
    languages_message = strings.get_string('languages.select', user.language)
    languages_keyboard = keyboards.get_keyboard('languages.select', user.language)
    message.reply_text(text=languages_message, reply_markup=languages_keyboard)
    return LANGUAGE


def select_language(update: Update, context: CallbackContext):
    query = update.callback_query
    user =  TelegramUser.objects.get(pk=query.from_user.id)
    language = query.data.split(':')[1]
    user.language = language
    user.save()
    context.user_data['user'] = user
    context.bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
    Navigation.to_main_menu(update, context)
    return ConversationHandler.END


def skip_message(update: Update, context: CallbackContext):
    return LANGUAGE


languages_handler = ConversationHandler(
    entry_points=[MessageHandler(CharityFilters.LanguagesFilter(), languages)],
    states={
        LANGUAGE: [CallbackQueryHandler(select_language, pattern=r'^language:.*'), MessageHandler(Filters.text, skip_message)]
    },
    fallbacks=[None]
)
