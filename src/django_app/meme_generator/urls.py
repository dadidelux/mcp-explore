from django.urls import path
from . import views

app_name = 'meme_generator'
urlpatterns = [
    path('', views.generate_meme, name='index'),
    path('generate/', views.generate_meme, name='generate_meme'),
    path('templates/', views.get_templates, name='get_templates'),
    path('ai/', views.ai_generate_meme, name='ai_generate_meme'),
]
