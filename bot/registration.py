from charity.models import TelegramUser
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters
from .resources import strings, keyboards
from bot.utils import Navigation
import re


LANGUAGE, NAME, PHONE_NUMBER = range(3)


def _to_languages(update, context):
    langauge_message = strings.get_string('start.languages')
    language_keybaord = keyboards.get_keyboard('start.languages')
    update.message.reply_text(text=langauge_message, reply_markup=language_keybaord)
    return LANGUAGE


def _to_name(update, context):
    name_message = strings.get_string('start.name', context.user_data['registration']['language'])
    name_keyboard = keyboards.get_keyboard('remove')
    update.message.reply_text(text=name_message, reply_markup=name_keyboard)
    return NAME


def _to_phone_number(update, context):
    phone_message = strings.get_string('start.phone', context.user_data['registration']['language'])
    phone_keyboard = keyboards.get_keyboard('start.phone')
    update.message.reply_text(text=phone_message, reply_markup=phone_keyboard)
    return PHONE_NUMBER


def start(update, context):
    user = update.message.from_user
    try:
        telegram_user = TelegramUser.objects.get(pk=user.id)
    except TelegramUser.DoesNotExist:
        return _to_languages(update, context)
    else:
        context.user_data['user'] = telegram_user
        Navigation.to_main_menu(update, context)
        return ConversationHandler.END


def language(update, context):
    message = update.message
    if strings.get_string('languages.ru') in message.text:
        language_code = 'ru'
    elif strings.get_string('languages.uz') in message.text:
        language_code = 'uz'
    else:
        return _to_languages(update, context)
    context.user_data['registration'] = {'language': language_code}
    return _to_name(update, context)


def name(update, context):
    context.user_data['registration']['name'] = update.message.text
    return _to_phone_number(update, context)


def phone_number_text(update, context):
    message = update.message
    phone_number = message.text
    match = re.match(r'\+*998\s*\d{2}\s*\d{3}\s*\d{2}\s*\d{2}', phone_number)
    if match is None:
        return _to_phone_number(update, context)
    phone_number = match.group()
    user = TelegramUser.objects.create(id=message.from_user.id, name=context.user_data['registration']['name'], 
                                       phone_number=phone_number,
                                       language=context.user_data['registration']['language'])
    del context.user_data['registration']
    context.user_data['user'] = user
    Navigation.to_main_menu(update, context)
    return ConversationHandler.END


def phone_number_contact(update, context):
    message = update.message
    phone_number = update.message.contact.phone_number
    user = TelegramUser.objects.create(id=message.from_user.id, name=context.user_data['registration']['name'], 
                                       phone_number=phone_number,
                                       username=message.from_user.username,
                                       language=context.user_data['registration']['language'])
    del context.user_data['registration']
    context.user_data['user'] = user
    Navigation.to_main_menu(update, context)
    return ConversationHandler.END


registration_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        LANGUAGE: [MessageHandler(Filters.text, language)],
        NAME: [MessageHandler(Filters.text, name)],
        PHONE_NUMBER: [MessageHandler(Filters.contact, phone_number_contact), 
                       MessageHandler(Filters.text, phone_number_text)]
    },
    fallbacks=[MessageHandler(Filters.text, '')]
)
