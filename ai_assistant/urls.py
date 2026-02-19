from django.urls import path
from . import views

urlpatterns = [
    path('ai/', views.chat_list, name='ai_chat_list'),
    path('ai/new/', views.chat_create, name='ai_chat_create'),
    path('ai/<int:chat_pk>/', views.chat_view, name='ai_chat'),
    path('ai/<int:chat_pk>/send/', views.chat_send, name='ai_send'),
    path('ai/<int:chat_pk>/rename/', views.chat_rename, name='ai_rename'),
    path('ai/<int:chat_pk>/delete/', views.chat_delete, name='ai_chat_delete'),
    path('ai/<int:chat_pk>/clear/', views.chat_clear, name='ai_clear'),
]