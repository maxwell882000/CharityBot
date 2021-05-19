from telegram.ext import MessageHandler, CallbackContext
from telegram import Update, Bot

from charity.models import TelegramUser

from .resources import strings
from bot.utils import CharityFilters


def share(update: Update, context: CallbackContext):
    message = update.message
    user = TelegramUser.objects.get(pk=message.from_user.id)
    share_text = strings.get_string('share.text', user.language)
    share_content = strings.get_string('share.content', user.language).format(link=context.bot.link)
    message.reply_text(text=share_text)
    message.reply_text(text=share_content, disable_web_page_preview=False)


share_handler = MessageHandler(CharityFilters.ShareFiler(), share)
