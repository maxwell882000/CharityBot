from django.views.generic import ListView, DetailView, View
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect
from django.urls import reverse_lazy

from charity.models import HelpRequest, HelpRequestReaction, TelegramUser


class HelpRequestsList(LoginRequiredMixin, ListView):
    model = HelpRequest
    context_object_name = 'help_requests'
    template_name = 'help_requests/index.html'


class HelpRequestDetail(LoginRequiredMixin, DetailView):
    model = HelpRequest
    context_object_name = 'help_request'
    template_name = 'help_requests/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['complains'] = context['help_request'].complains.all()
        return context


class HelpRequestDelete(LoginRequiredMixin, DeleteView):
    model = HelpRequest
    success_url = reverse_lazy('admin-help-index')

    def delete(self, request, *args, **kwargs):
        result = super().delete(request, *args, **kwargs)
        messages.add_message(request, messages.SUCCESS, 'Просьба о помощи удалена')
        return result


class HelpRequestResolveConflict(LoginRequiredMixin, SingleObjectMixin, View):

    model = HelpRequest

    def get(self, request, pk):
        help_request = self.get_object()
        side = request.GET.get('side')
        if side == 'owner':
            help_request.hidden = False
            help_request.reaction.delete()
            messages.add_message(request, messages.SUCCESS, 'Конфликт решён в сторону владельца просьбы. Объявление теперь доступно в списке.')
        elif side == 'helper':
            help_request.hidden = True
            help_request.reaction.owner_reaction = HelpRequestReaction.Reactions.YES
            help_request.reaction.save()
            help_request.helper = TelegramUser.objects.get(pk=help_request.reaction.helper_id)
            messages.add_message(request, messages.SUCCESS, 'Конфликт решён в сторону помошника. Объявление теперь пропадёт из списка.')
        else:
            return HttpResponseBadRequest()
        help_request.has_conflict = False
        help_request.save()
        return redirect('admin-help-detail', help_request.id)
