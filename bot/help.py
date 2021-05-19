from telegram.ext import CallbackQueryHandler, ConversationHandler, CallbackContext
from telegram import Update, ParseMode, Message

from charity.models import TelegramUser, HelpRequestReaction, HelpRequest
from .resources import strings, keyboards

from threading import Timer


def offer_help(update: Update, context: CallbackContext):
    query = update.callback_query
    help_request_id = query.data.split(':')[1]
    try:
        help_request = HelpRequest.objects.get(pk=help_request_id)
    except HelpRequest.DoesNotExist:
        query.answer()
        return
    user = TelegramUser.objects.get(pk=query.from_user.id)
    help_request.hidden = True
    help_request.save()
    owner = help_request.user
    context.user_data['user'] = user
    reaction = HelpRequestReaction.objects.create(help_request=help_request, helper_id=user.id)
    owner_timer = Timer(60, send_reaction_to_owner, (context, reaction, owner, user))
    helper_timer = Timer(60, send_reaction_to_helper, (context, reaction, owner, user))
    owner_notification = strings.from_helper_request_owner_notification(help_request, user, owner.language)
    try:
        context.bot.send_message(chat_id=owner.id, text=owner_notification, parse_mode=ParseMode.HTML)
    except e:
        print(e)
    notification_sent = strings.notification_sent_message(owner, user.language)
    notification_sent = query.message.text_html + notification_sent
    query.edit_message_text(text=notification_sent, parse_mode=ParseMode.HTML)
    owner_timer.start()
    helper_timer.start()
    query.answer()


def owner_reaction(update: Update, context: CallbackContext):
    query = update.callback_query
    reaction_id = query.data.split(':')[1]
    reaction_text = query.data.split(':')[3]
    try:
        reaction = HelpRequestReaction.objects.get(pk=reaction_id)
    except HelpRequestReaction.DoesNotExist:
        query.answer()
        return
    user = TelegramUser.objects.get(pk=query.from_user.id)
    reaction.owner_reaction = reaction_text
    reaction.save()
    help_request = reaction.help_request
    if reaction_text == HelpRequestReaction.Reactions.YES:
        # If owner said "Yes" - it's over
        help_request_deleted_message = strings.get_string('reaction.owner.request_deleted', user.language)
        query.edit_message_text(text=help_request_deleted_message)
        help_request.helper = TelegramUser.objects.get(pk=reaction.helper_id)
        message = strings.get_string('reaction.helper.thanks', user.language)
        context.bot.send_message(chat_id=reaction.helper_id, text=message)
    elif not reaction.helper_reaction:
        # If owner said "No" but helper haven't responded yet
        clear_request_timer = Timer(3600, clear_request_reactions, (context, help_request, user))
        clear_request_timer.start()
        message = strings.get_string('reaction.owner.no_helper_reaction', user.language)
        query.edit_message_text(text=message)
    elif reaction.helper_reaction == HelpRequestReaction.Reactions.YES:
        # If owner said "No" but helper said "Yes"
        message = strings.get_string('reaction.owner.helper_say_yes', user.language)
        query.edit_message_text(text=message)
        help_request.has_conflict = True
        help_request.save()
        message = strings.get_string('reaction.helper.owner_say_no', user.language)
        context.bot.send_message(chat_id=reaction.helper_id, text=message)
    else:
        # If owner and helper both said "No"
        message = strings.get_string('reaction.owner.both_no', user.language)
        help_request.hidden = False
        help_request.save()
        reaction.delete()
        query.edit_message_text(text=message)
        message = strings.get_string('reaction.helper.both_no', user.language)
        context.bot.send_message(chat_id=reaction.helper_id, text=message)
    query.answer()


def helper_reaction(update: Update, context: CallbackContext):
    query = update.callback_query
    reaction_id = query.data.split(':')[1]
    reaction_text = query.data.split(':')[3]
    user = TelegramUser.objects.get(pk=query.from_user.id)
    try:
        reaction = HelpRequestReaction.objects.get(pk=reaction_id)
    except HelpRequestReaction.DoesNotExist:
        late_message = strings.get_string('reaction.helper.too_late', user.language)
        query.answer(text=late_message, show_alert=True)
        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.effective_message.message_id)
        return
    user = TelegramUser.objects.get(pk=query.from_user.id)
    reaction.helper_reaction = reaction_text
    help_request = reaction.help_request
    reaction.save()
    if not reaction.owner_reaction:
        # If helper responded but owner haven't responded yet
        message = strings.get_string('reaction.helper.no_owner_reaction', user.language)
        query.edit_message_text(text=message)
    elif reaction_text == HelpRequestReaction.Reactions.NO and reaction.owner_reaction == reaction_text:
        # If helper and owner both said "No"
        message = strings.get_string('reaction.helper.both_no', user.language)
        query.edit_message_text(text=message)
        message = strings.get_string('reaction.owner.both_no', reaction.help_request.user.language)
        context.bot.send_message(chat_id=reaction.help_request.user.id, text=message)
        help_request.hidden = False
        help_request.save()
        reaction.delete()
    elif reaction_text == HelpRequestReaction.Reactions.YES and reaction.owner_reaction != reaction_text:
        # If helper said "Yes" but owner said "No"
        message = strings.get_string('reaction.helper.owner_say_no', user.language)
        query.edit_message_text(text=message)
        message = strings.get_string('reaction.owner.helper_say_yes', user.language)
        help_request.has_conflict = True
        help_request.save()
        context.bot.send_message(chat_id=reaction.help_request.user.id, text=message)
    else:
        # If owner said "Yes"
        message = strings.get_string('reaction.helper.thanks', user.language)
        query.edit_message_text(text=message)


def send_reaction_to_owner(context: CallbackContext, reaction: HelpRequestReaction, owner: TelegramUser, helper: TelegramUser):
    owner_reaction_message = strings.reaction_owner_message(reaction.help_request, helper, owner.language)
    owner_reaction_keyboard = keyboards.from_reaction_owner_keyboard(reaction, owner.language)
    context.bot.send_message(chat_id=owner.id, text=owner_reaction_message, reply_markup=owner_reaction_keyboard, parse_mode=ParseMode.HTML)


def send_reaction_to_helper(context: CallbackContext, reaction: HelpRequestReaction, owner: TelegramUser, helper: TelegramUser):
    helper_reaction_message = strings.reaction_helper_message(reaction.help_request, owner, helper.language)
    helper_reaction_keyboard = keyboards.from_reaction_helper_keyboard(reaction, helper.language)
    context.bot.send_message(chat_id=helper.id, text=helper_reaction_message, reply_markup=helper_reaction_keyboard, parse_mode=ParseMode.HTML)


def clear_request_reactions(context: CallbackContext, request: HelpRequest, owner: TelegramUser):
    if request.is_completted():
        return
    request.reaction.delete()
    request.hidden = False
    request.has_conflict = False
    request.save()
    no_helper_reaction_message = strings.get_string('reaction.owner.no_helper_reaction_yet', owner.language)
    context.bot.send_message(chat_id=owner.id, text=no_helper_reaction_message)


help_handler = CallbackQueryHandler(offer_help, pattern=r'^help:.*')
owner_reaction_handler = CallbackQueryHandler(owner_reaction, pattern=r'^reaction:.*:owner:.*')
helper_reaction_handler = CallbackQueryHandler(helper_reaction, pattern=r'reaction:.*:helper:.*')
