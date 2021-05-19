import os
import json

from charity.models import TelegramUser, GiveAwayOffer, HelpRequest

_basedir = os.path.abspath(os.path.dirname(__file__))

# Load strings from json
# Russian language
_strings_ru = json.loads(open(os.path.join(_basedir, 'strings_ru.json'), 'r', encoding='utf8').read())

# Uzbek language
_strings_uz = json.loads(open(os.path.join(_basedir, 'strings_uz.json'), 'r', encoding='utf8').read())


def get_string(key, language='ru') -> str:
    if language == 'ru':
        return _strings_ru.get(key, 'no_string')
    elif language == 'uz':
        return _strings_uz.get(key, 'no_string')
    else:
        raise Exception('Invalid language')


def from_help_request_distance(request: dict, language: str) -> str:
    distance = request['distance']
    request = request['request']
    return get_string('help_request.template', language).format(distance=distance, name=request.user.name, 
                                                                type=request.help_type,
                                                                description=request.description)

def from_give_away_offer_distance(offer: dict, language: str) -> str:
    distance = offer['distance']
    offer = offer['offer']
    return get_string('give_away_offer.template', language).format(distance=distance, name=offer.user.name,
                                                                   type=offer.give_away_type,
                                                                   description=offer.description)

def from_user_contact_message(user: TelegramUser, offer: GiveAwayOffer, language):
    return get_string('give_away.contact_template', language).format(
        type=offer.give_away_type,
        description=offer.description,
        name=user.name,
        phone=user.phone_number,
        id=user.id
    )


def from_helper_request_owner_notification(help_request: HelpRequest, helper: TelegramUser, language) -> str:
    return get_string('need_help.owner_notification', language).format(
        type=help_request.help_type,
        description=help_request.description,
        name=helper.name
    )


def notification_sent_message(owner: TelegramUser, language) -> str:
    return get_string('can_help.notification_sent', language).format(
        phone=owner.phone_number,
        id=owner.id
    )


def reaction_owner_message(help_request: HelpRequest, helper: TelegramUser, language) -> str:
    return get_string('reaction.owner', language).format(
        type=help_request.help_type,
        description=help_request.description,
        name=helper.name
    )


def reaction_helper_message(help_request: HelpRequest, owner:TelegramUser, language) -> str:
    return get_string('reaction.helper', language).format(
        type=help_request.help_type,
        description=help_request.description,
        name=owner.name
    )
