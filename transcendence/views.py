from django.views.generic import TemplateView, DetailView
from django.contrib.auth.models import User


class IndexView(TemplateView):
    template_name = "transcendence/index.html"


class UserInfoView(DetailView):
    template_name = "transcendence/user_info.html"
    model = User
    pk_url_kwarg = 'user_id'
