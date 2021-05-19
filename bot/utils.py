from telegram import ParseMode
from bot.resources import strings, keyboards
from telegram.ext import BaseFilter
from math import radians, cos, sin, asin, sqrt


class Navigation:
    @staticmethod
    def to_main_menu(update, context, message=None):
        main_menu_message = strings.get_string('main_menu', context.user_data['user'].language)
        if message:
            main_menu_message = message
        main_menu_keyboard = keyboards.get_keyboard('main_menu', context.user_data['user'].language)
        if update.message:
            update.message.reply_text(text=main_menu_message, reply_markup=main_menu_keyboard, parse_mode=ParseMode.HTML)
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, reply_markup=main_menu_keyboard, text=main_menu_message, parse_mode=ParseMode.HTML)


class CharityFilters:

    class NeedHelpFilter(BaseFilter):
        def filter(self, message):
            return message.text and ((strings.get_string('menu.need_help', 'ru') in message.text) or 
                                    (strings.get_string('menu.need_help', 'uz') in message.text))
    
    class CanHelpFilter(BaseFilter):
        def filter(self, message):
            return message.text and ((strings.get_string('menu.can_help', 'ru') in message.text) or 
                                    strings.get_string('menu.can_help', 'uz') in message.text)
    
    class GiveAwayFiler(BaseFilter):
        def filter(self, message):
            return message.text and ((strings.get_string('menu.give_away', 'ru') in message.text) or
                                    strings.get_string('menu.give_away', 'uz') in message.text)

    class GetItForFreeFilter(BaseFilter):
        def filter(self, message):
            return message.text and ((strings.get_string('menu.get_it_for_free', 'ru') in message.text) or
                                    strings.get_string('menu.get_it_for_free', 'uz') in message.text)
    
    class CancelFilter(BaseFilter):
        def filter(self, message):
            return message.text and ((strings.get_string('cancel', 'ru') in message.text) or
                                    (strings.get_string('cancel', 'uz') in message.text))
    
    class LanguagesFilter(BaseFilter):
        def filter(self, message):
            return message.text and ((strings.get_string('menu.chage_language', 'ru') in message.text) or 
                                      strings.get_string('menu.chage_language', 'uz') in message.text)
    
    class ShareFiler(BaseFilter):
        def filter(self, message):
            return message.text and ((strings.get_string('menu.share', 'ru') in message.text) or 
                                      strings.get_string('menu.share', 'uz') in message.text)


class Geolocation:
    @staticmethod
    def distance_between_two_points(first_coordinates: tuple, second_coordinates: tuple) -> float:
        """
        Calculate the great circle distance between two pints
        on the Earth (specified in decimal degrees)
        :param first_coordinates: Coordinates (latitude, longitude) of first point
        :param second_coordinates: Coordinates (latitude, longitude) of second point
        :return: distance
        """
        lat1, lon1 = first_coordinates
        lat2, lon2 = second_coordinates
        # Convert decimal degrees to radians
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        # Haversina formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        # Radius of Earth in kilometers is 6731
        km = 6371 * c
        # If distance in kilometres, round the value
        return round(km, 2)
