from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton
from .strings import get_string
from typing import Union, Optional

from charity.models import HelpRequest, GiveAwayOffer, TelegramUser, HelpRequestReaction


def _create_keyboard(keyboard: list, one_time: bool = False) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=one_time)


def get_keyboard(key, language='ru') -> Union[ReplyKeyboardRemove, ReplyKeyboardMarkup, InlineKeyboardMarkup]:
    if key == 'start.languages':
        return _create_keyboard([[get_string('languages.ru', language), get_string('languages.uz', language)]])
    elif key == 'start.phone':
        keyboard = [[KeyboardButton(get_string('phone', language), request_contact=True)]]
        return _create_keyboard(keyboard)
    elif key == 'main_menu':
        keyboard = [
            [get_string('menu.need_help', language), get_string('menu.can_help', language)],
            [get_string('menu.give_away', language)],
            [get_string('menu.get_it_for_free', language)],
            [get_string('menu.share', language)],
            [get_string('menu.chage_language', language)]
        ]
        return _create_keyboard(keyboard)
    elif key == 'remove':
        return ReplyKeyboardRemove()
    elif key == 'need_help.type':
        keyboard = [
            [get_string('products', language), get_string('medicines', language)],
            [get_string('cancel', language)]
        ]
        return _create_keyboard(keyboard)
    elif key == 'need_help.description':
        keyboard = [[get_string('cancel', language)]]
        return _create_keyboard(keyboard)
    elif key == 'need_help.location':
        keyboard = [
            [KeyboardButton(get_string('location', language), request_location=True)],
            [get_string('cancel', language)]
        ]
        return _create_keyboard(keyboard)
    elif key == 'can_help.location':
        keyboard = [
            [KeyboardButton(get_string('location', language), request_location=True)],
            [get_string('cancel', language)]
        ]
        return _create_keyboard(keyboard)
    elif key == 'give_away.start':
        keyboard = [
            [get_string('give_away.give', language)],
            [get_string('give_away.get', language)]
        ]
        return _create_keyboard(keyboard)
    elif key == 'give_away.type':
        keyboard = [
            [get_string('products', language), get_string('medicines', language)],
            [get_string('cancel', language)]
        ]
        return _create_keyboard(keyboard)
    elif key == 'give_away.description':
        keyboard = [
            [get_string('cancel', language)]
        ]
        return _create_keyboard(keyboard)
    elif key == 'give_away.image':
        keyboard = [
            [get_string('cancel', language)]
        ]
        return _create_keyboard(keyboard)
    elif key == 'give_away.give_location':
        keyboard = [
            [KeyboardButton(get_string('location', language), request_location=True)],
            [get_string('cancel', language)]
        ]
        return _create_keyboard(keyboard)
    elif key == 'give_away.get_location':
        keyboard = [
            [KeyboardButton(get_string('location', language), request_location=True)],
            [get_string('cancel', language)]
        ]
        return _create_keyboard(keyboard)
    elif key == 'complain':
        keyboard = [
            [get_string('cancel', language)]
        ]
        return _create_keyboard(keyboard)
    elif key == 'languages.select':
        keyboard = []
        if language == 'ru':
            keyboard.append([InlineKeyboardButton(get_string('languages.uz'), callback_data='language:uz')])
        elif language == 'uz':
            keyboard.append([InlineKeyboardButton(get_string('languages.ru'), callback_data='language:ru')])
        return InlineKeyboardMarkup(keyboard)
    else:
        return _create_keyboard([['no_keyboard']])


def from_help_request_keyboard(request: HelpRequest, language) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(get_string('help', language), callback_data='help:' + str(request.id))],
        [InlineKeyboardButton(get_string('complain', language), callback_data='complain:' + str(request.id))]
    ]
    return InlineKeyboardMarkup(keyboard)


def from_give_away_offer_keybaord(offer: GiveAwayOffer, language) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(get_string('get_it_for_free', language), callback_data='get_it_for_free:' + str(offer.id))]
    ]
    return InlineKeyboardMarkup(keyboard)


def from_offer_give_away_contact_keyboard(offer: GiveAwayOffer, user: TelegramUser, language: str) -> InlineKeyboardMarkup:
    keybaord = [
        [InlineKeyboardButton(get_string('give_it_away', language), callback_data='give_it_away:' + str(offer.id))],
        [InlineKeyboardButton(get_string('complain', language), callback_data='give_it_away_complain:' + str(user.id))]
    ]
    return InlineKeyboardMarkup(keybaord)


def from_reaction_owner_keyboard(reaction: HelpRequestReaction, language) -> InlineKeyboardMarkup:
    id = str(reaction.id)
    keyboard = [
        [InlineKeyboardButton(get_string('yes', language), callback_data='reaction:' + id + ':owner:yes'), 
         InlineKeyboardButton(get_string('no', language), callback_data='reaction:' + id + ':owner:no')]
    ]
    return InlineKeyboardMarkup(keyboard)

def from_reaction_helper_keyboard(reaction: HelpRequestReaction, language) -> InlineKeyboardMarkup:
    id = str(reaction.id)
    keyboard = [
        [InlineKeyboardButton(get_string('yes', language), callback_data='reaction:' + id + ':helper:yes'),
         InlineKeyboardButton(get_string('no', language), callback_data='reaction:' + id + ':helper:no')]
    ]
    return InlineKeyboardMarkup(keyboard)
