from django.urls import path
from . import views

urlpatterns = [
    path("", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("register/", views.register, name="register"),
    path("chat/", views.chat, name="chat"),
    path("chat/create/", views.create_session, name="create_session"),
    path("chat/<int:session_id>/", views.chat_session, name="chat_session"),
    path("chat/<int:session_id>/send/", views.send_message, name="send_message"),
    path("chat/<int:session_id>/history/", views.chat_history, name="chat_history"),
]
