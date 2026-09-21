from django.urls import path
from . import views

app_name = "tournament"
urlpatterns = [
    path('', views.tournament_detail, name='tournament_index'),
]