from django.urls import path
from . import views

app_name = "tournament"
urlpatterns = [
    path('', views.tournament_detail, name='tournament_index'),
    path('tournament/fixture/', views.fixture_view, name='fixture_list'),
    path('tournament/players/', views.players_list, name='players_list'),
    path('tournament/<int:tournament_id>/fixture/', views.fixture_view_tournament, name='fixture_list_tournament'),
    path('tournament/<int:tournament_id>/players/', views.players_list_tournament, name='players_list_tournament'),
    path('tournament/<int:tournament_id>/', views.tournament_detail_view, name='tournament_detail'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('dashboard/player/add/', views.add_player, name='add_player'),
    path('dashboard/player/<int:player_id>/edit/', views.edit_player, name='edit_player'),
    path('dashboard/player/<int:player_id>/delete/', views.delete_player, name='delete_player'),
    path('team-autocomplete/', views.TeamAutocomplete.as_view(), name='team-autocomplete'),
]