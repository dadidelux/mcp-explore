from django.urls import path
from . import views

app_name = 'meme_generator'
urlpatterns = [
    path('', views.generate_meme, name='index'),
    path('generate/', views.generate_meme, name='generate_meme'),
]
