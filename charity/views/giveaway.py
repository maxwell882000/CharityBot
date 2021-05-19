from django.views.generic import ListView, DetailView
from django.views.generic.edit import DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy

from charity.models import GiveAwayOffer


class GiveAwayOffersListView(LoginRequiredMixin, ListView):
    model = GiveAwayOffer
    context_object_name = 'offers'
    template_name = 'offers/index.html'


class GiveAwayOfferDetail(LoginRequiredMixin, DetailView):
    model = GiveAwayOffer
    context_object_name = 'offer'
    template_name = 'offers/detail.html'


class GiveAwayOfferDelete(LoginRequiredMixin, DeleteView):
    model = GiveAwayOffer
    success_url = reverse_lazy('admin-offers-index')

    def delete(self, request, *args, **kwargs):
        result = super().delete(request, *args, **kwargs)
        messages.add_message(request, messages.SUCCESS, 'Предложение отдать даром удалено')
        return result
