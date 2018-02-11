from django.urls import path
from transcendence.views import IndexView, UserInfoView

urlpatterns = [
    path('', IndexView.as_view()),
    path('users/<int:user_id>/', UserInfoView.as_view()),
]
