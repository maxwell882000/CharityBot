from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from telegram import Update
from bot import dp
from os import getenv
import json

@csrf_exempt
def bot_webhook(request):
    try:
        update = Update.de_json(json.loads(request.body.decode('utf-8')), dp.bot)
        dp.process_update(update)
        return JsonResponse({})
    except Exception as e:
        print(e)
        return JsonResponse({})
