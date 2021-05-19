from django.urls import path

from .views.dashboard import DashboardView
from .views.users import TelegramUserList, TelegramUserDelete, TelegramUserDetail
from .views.helprequests import HelpRequestsList, HelpRequestDetail, HelpRequestDelete, HelpRequestResolveConflict
from .views.giveaway import GiveAwayOffersListView, GiveAwayOfferDetail, GiveAwayOfferDelete
from .views.bot import bot_webhook

from os import getenv

urlpatterns = [
    path('', DashboardView.as_view(), name='admin-home'),
    path('users/', TelegramUserList.as_view(), name='admin-users-index'),
    path('users/<int:pk>/', TelegramUserDetail.as_view(), name='admin-users-detail'),
    path('users/<int:pk>/delete/', TelegramUserDelete.as_view(), name='admin-users-delete'),

    path('help/', HelpRequestsList.as_view(), name='admin-help-index'),
    path('help/<int:pk>/', HelpRequestDetail.as_view(), name='admin-help-detail'),
    path('help/<int:pk>/delete', HelpRequestDelete.as_view(), name='admin-help-delete'),
    path("help/<int:pk>/resolve/", HelpRequestResolveConflict.as_view(), name="admin-help-resolve"),

    path("offers/", GiveAwayOffersListView.as_view(), name="admin-offers-index"),
    path('offers/<int:pk>/', GiveAwayOfferDetail.as_view(), name='admin-offers-detail'),
    path('offers/<int:pk>/delete', GiveAwayOfferDelete.as_view(), name='admin-offers-delete'),

    path(getenv('TELEGRAM_BOT_TOKEN'), bot_webhook, name='bot')
]
