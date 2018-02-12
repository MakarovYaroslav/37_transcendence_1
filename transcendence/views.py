from django.views.generic import TemplateView
from datetime import datetime
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404


class IndexView(TemplateView):
    template_name = "transcendence/index.html"


class UserInfoView(TemplateView):
    template_name = "transcendence/user_info.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = context['user_id']
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            user = None
        context['user'] = user
        return context
