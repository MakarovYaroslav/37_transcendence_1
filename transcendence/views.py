from django.views.generic import TemplateView
from datetime import datetime


class IndexView(TemplateView):
    template_name = "transcendence/index.html"


class UserInfoView(TemplateView):
    template_name = "transcendence/user_info.html"
    registration_date = datetime.now()
