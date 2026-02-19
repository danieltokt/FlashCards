from django.urls import path
from . import views

urlpatterns = [
    # Главная
    path('', views.home, name='home'),

    # Папки
    path('folders/create/', views.folder_create, name='folder_create'),
    path('folders/<int:pk>/', views.folder_detail, name='folder_detail'),
    path('folders/<int:pk>/delete/', views.folder_delete, name='folder_delete'),

    # Курсы
    path('courses/create/', views.course_create, name='course_create'),
    path('courses/<int:pk>/', views.course_detail, name='course_detail'),
    path('courses/<int:pk>/edit/', views.course_edit, name='course_edit'),
    path('courses/<int:pk>/delete/', views.course_delete, name='course_delete'),

    # Карточки
    path('cards/<int:pk>/delete/', views.card_delete, name='card_delete'),
    path('cards/<int:pk>/favorite/', views.card_toggle_favorite, name='card_toggle_favorite'),

    # AJAX
    path('api/translate/', views.get_translations, name='get_translations'),
    path('courses/<int:pk>/share/', views.course_toggle_share, name='course_toggle_share'),
    path('courses/shared/<uuid:token>/', views.course_shared_view, name='course_shared'),
]