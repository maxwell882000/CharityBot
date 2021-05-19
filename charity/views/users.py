from django.views.generic import ListView, DetailView
from django.views.generic.edit import DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy

from charity.models import TelegramUser


class TelegramUserList(LoginRequiredMixin, ListView):
    model = TelegramUser
    context_object_name = 'telegram_users'
    template_name = 'users/index.html'


class TelegramUserDetail(LoginRequiredMixin, DetailView):
    model = TelegramUser
    template_name = 'users/detail.html'
    context_object_name = 'telegram_user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = context['telegram_user']
        context['complains'] = user.presented_complains.all()
        return context


class TelegramUserDelete(LoginRequiredMixin, DeleteView):
    model = TelegramUser
    success_url = reverse_lazy('admin-users-index')

    def delete(self, request, *args, **kwargs):
        result = super().delete(request, *args, **kwargs)
        messages.add_message(request, messages.SUCCESS, 'Пользователь удалён')
        return result
