from django.views import View
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin


class DashboardView(LoginRequiredMixin, View):
    """
    View for dashboard page
    """
    template_name='dashboard.html'

    def get(self, request):
        return render(request, self.template_name)
