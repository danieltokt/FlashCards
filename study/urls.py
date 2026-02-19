from django.urls import path
from . import views

urlpatterns = [
    path('study/<int:course_pk>/', views.study_view, name='study'),
    path('study/<int:course_pk>/results/', views.study_results, name='study_results'),
    path('test/<int:course_pk>/', views.test_view, name='test'),
    path('test/<int:course_pk>/submit/', views.test_submit, name='test_submit'),
]