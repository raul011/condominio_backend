# urls.py
from django.urls import path
from . import views
from .views import SendNotificationView


urlpatterns = [
    path('fcm/tokens/register/', views.register_token, name='register-token'),
    path('fcm/tokens/desactivate/', views.deactivate_token, name='desactivate-token'),
    path('fcm/tokens/mine/', views.my_tokens, name='my-tokens'),
    path("fcm/send/", SendNotificationView.as_view(), name="send-notification"),
]