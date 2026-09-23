from django.urls import path
from . import views

app_name = "tournament"
urlpatterns = [
    path('', views.tournament_detail, name='tournament_index'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('dashboard/player/add/', views.add_player, name='add_player'),
    path('dashboard/player/<int:player_id>/edit/', views.edit_player, name='edit_player'),
    path('dashboard/player/<int:player_id>/delete/', views.delete_player, name='delete_player'),
]