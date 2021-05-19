from telegram.ext import ConversationHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import ParseMode, Update, CallbackQuery

from bot.utils import Navigation, Geolocation, CharityFilters
from charity.models import TelegramUser, GiveAwayOffer
from .resources import strings, keyboards


TYPE, DESCRIPTION, IMAGE, GIVE_LOCATION, GET_LOCATION = range(5)


def give_away_action(update, context):
    message = update.message
    language = context.user_data['user'].language
    if strings.get_string('menu.give_away', language) in message.text:
        reply_message = strings.get_string('give_away.type', language)
        reply_keyboard = keyboards.get_keyboard('give_away.type', language)
        NEXT_STEP = TYPE
    elif strings.get_string('menu.get_it_for_free', language) in message.text:
        reply_message = strings.get_string('give_away.get_location', language)
        reply_keyboard = keyboards.get_keyboard('give_away.get_location', language)
        NEXT_STEP = GET_LOCATION
    else:
        start_message = strings.get_string('give_away.start', language)
        start_keyboard = keyboards.get_keyboard('give_away.start', language)
        message.reply_text(text=start_message, reply_markup=start_keyboard)
        return ACTION
    message.reply_text(text=reply_message, reply_markup=reply_keyboard)
    return NEXT_STEP


def give_away_type(update, context):
    message = update.message
    language = context.user_data['user'].language
    context.user_data['give_away_offer'] = {}
    context.user_data['give_away_offer']['type'] = message.text
    description_message = strings.get_string('give_away.description', language)
    description_keyboard = keyboards.get_keyboard('give_away.description', language)
    message.reply_text(text=description_message, reply_markup=description_keyboard)
    return DESCRIPTION


def give_away_description(update, context):
    message = update.message
    language = context.user_data['user'].language
    context.user_data['give_away_offer']['description'] = message.text
    image_message = strings.get_string('give_away.image', language)
    image_keyboard = keyboards.get_keyboard('give_away.image', language)
    message.reply_text(text=image_message, reply_markup=image_keyboard)
    return IMAGE


def give_away_image(update, context):
    message = update.message
    language = context.user_data['user'].language
    photo = message.photo[-1]
    context.user_data['give_away_offer']['photo_telegram_id'] = photo.file_id
    telegram_file = context.bot.get_file(photo.file_id)
    telegram_link = 'https://api.telegram.org/file/bot{token}/{file_path}'
    context.user_data['give_away_offer']['photo_telegram_url'] = telegram_link.format(token=context.bot.token, file_path=telegram_file.file_path)
    give_location_message = strings.get_string('give_away.give_location', language)
    give_location_keyboard = keyboards.get_keyboard('give_away.give_location', language)
    message.reply_text(text=give_location_message, reply_markup=give_location_keyboard)
    return GIVE_LOCATION


def give_away_give_location(update, context):
    message = update.message
    latitude = message.location.latitude
    longitude = message.location.longitude
    language = context.user_data['user'].language
    GiveAwayOffer.objects.create(latitude=latitude, longitude=longitude,
                                description=context.user_data['give_away_offer']['description'],
                                user=context.user_data['user'],
                                give_away_type=context.user_data['give_away_offer']['type'],
                                photo_telegram_id=context.user_data['give_away_offer']['photo_telegram_id'],
                                photo_telegram_url=context.user_data['give_away_offer']['photo_telegram_url'])
    del context.user_data['give_away_offer']
    success_message = strings.get_string('give_away.success', language)
    Navigation.to_main_menu(update, context, message=success_message)
    return ConversationHandler.END


def give_away_get_location(update, context):
    message = update.message
    latitude = message.location.latitude
    longitude = message.location.longitude
    give_away_offers = GiveAwayOffer.objects.all()
    results = []
    language = context.user_data['user'].language
    if not give_away_offers:
        empty_message = strings.get_string('give_away.empty', language)
        Navigation.to_main_menu(update, context, message=empty_message)
        return ConversationHandler.END
    far_away = False
    for offer in give_away_offers:
        distance = Geolocation.distance_between_two_points((latitude, longitude), (offer.latitude, offer.longitude))
        if distance <= 1:
            results.append({
                'distance': distance,
                'offer': offer
            })
    if not results or len(results) < 10:
        for offer in give_away_offers:
            distance = Geolocation.distance_between_two_points((latitude, longitude), (offer.latitude, offer.longitude))
            results.append({
                'distance': distance,
                'offer': offer
            })
        far_away = True
    results = sorted(results, key=lambda i: i['distance'])
    if far_away:
        results = results[:10]
    exists_message = strings.get_string('give_away.exists', language)
    Navigation.to_main_menu(update, context, message=exists_message)
    for result in results:
        offer_message = strings.from_give_away_offer_distance(result, language)
        offer_keyboard = keyboards.from_give_away_offer_keybaord(result['offer'], language)
        message.reply_photo(photo=result['offer'].photo_telegram_id, caption=offer_message, 
                            reply_markup=offer_keyboard, parse_mode=ParseMode.HTML)
    return ConversationHandler.END


def cancel(update, context):
    if 'give_away_offer' in context.user_data:
        del context.user_data['give_away_offer']
    Navigation.to_main_menu(update, context)
    return ConversationHandler.END


def get_it_for_free(update, context):
    query = update.callback_query
    id = query.data.split(':')[1]
    try:
        offer = GiveAwayOffer.objects.get(pk=int(id))
    except GiveAwayOffer.DoesNotExist:
        return
    owner = offer.user
    user = TelegramUser.objects.get(pk=query.message.chat_id)
    contact_message = strings.from_user_contact_message(user, offer, owner.language)
    contact_keyboard = keyboards.from_offer_give_away_contact_keyboard(offer, user, owner.language)
    context.bot.send_message(chat_id=owner.id, text=contact_message, reply_markup=contact_keyboard, parse_mode=ParseMode.HTML)
    contact_sended_message = strings.get_string('give_away.contact_sended', user.language)
    message_text = query.message.caption_html
    message_text += contact_sended_message
    query.edit_message_caption(caption=message_text, parse_mode=ParseMode.HTML)
    query.answer()


def give_it_away(update, context):
    query = update.callback_query
    id = query.data.split(':')[1]
    try:
        offer = GiveAwayOffer.objects.get(pk=int(id))
    except GiveAwayOffer.DoesNotExist:
        return
    user = offer.user
    offer.delete()
    deleted_message = strings.get_string('give_away.offer_deleted', user.language)
    query.answer(text=deleted_message, show_alert=True)
    context.bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)


give_away_conversation = ConversationHandler(
    entry_points=[MessageHandler(CharityFilters.GiveAwayFiler(), give_away_action), MessageHandler(CharityFilters.GetItForFreeFilter(), give_away_action)],
    states={
        TYPE: [MessageHandler(CharityFilters.CancelFilter(), cancel), MessageHandler(Filters.text, give_away_type)],
        DESCRIPTION: [MessageHandler(CharityFilters.CancelFilter(), cancel), MessageHandler(Filters.text, give_away_description)],
        IMAGE: [MessageHandler(CharityFilters.CancelFilter(), cancel), MessageHandler(Filters.photo, give_away_image)],
        GIVE_LOCATION: [MessageHandler(CharityFilters.CancelFilter(), cancel), MessageHandler(Filters.location, give_away_give_location)],
        GET_LOCATION: [MessageHandler(CharityFilters.CancelFilter(), cancel), MessageHandler(Filters.location, give_away_get_location)]
    },
    fallbacks=[MessageHandler(CharityFilters.CancelFilter(), cancel)]
)

get_it_for_free_handler = CallbackQueryHandler(get_it_for_free, pattern=r'^get_it_for_free:.*')
give_it_away_handler = CallbackQueryHandler(give_it_away, pattern=r'^give_it_away:.*')
