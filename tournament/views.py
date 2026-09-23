from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .models import Tournament, Player, Team
from .services import calculate_team_points, get_top_scorers, get_best_goalkeepers
from .forms import CustomUserCreationForm, EmailAuthenticationForm, TeamLogoForm, PlayerForm

def tournament_detail(request):
    tournament = Tournament.objects.first() 
    groups = tournament.groups.all()  

    group_tables = []
    for group in groups:
        table = calculate_team_points(group)
        group_tables.append({
            'group': group,
            'posiciones': table
        })

    top_scorers = get_top_scorers(tournament, limit=5)
    best_goalkeepers = get_best_goalkeepers(tournament)

    context = {
        'tournament': tournament,
        'group_tables': group_tables,
        'top_scorers': top_scorers,
        'best_goalkeepers': best_goalkeepers,
    }

    return render(request, 'tournament/index.html', context)


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  
            return redirect('tournament:tournament_index')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'tournament/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = EmailAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('tournament:tournament_index')
    else:
        form = EmailAuthenticationForm()

    return render(request, 'tournament/login.html', {'form': form})

def team_manager_required(view_func):
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not getattr(request.user, 'is_team_manager', False) or not request.user.team:
            messages.error(request, "No tienes permisos de delegado o no tienes un equipo asignado.")
            return redirect('tournament:tournament_index')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@team_manager_required
def manager_dashboard(request):
    team = request.user.team
    players = team.players.all() 

    if request.method == 'POST' and 'update_logo' in request.POST:
        logo_form = TeamLogoForm(request.POST, request.FILES, instance=team)
        if logo_form.is_valid():
            logo_form.save()
            messages.success(request, "Logo del equipo actualizado con éxito.")
            return redirect('tournament:manager_dashboard')
    else:
        logo_form = TeamLogoForm(instance=team)

    context = {
        'team': team,
        'players': players,
        'logo_form': logo_form,
    }
    return render(request, 'tournament/manager_dashboard.html', context)


@team_manager_required
def add_player(request):
    team = request.user.team
    if request.method == 'POST':
        form = PlayerForm(request.POST)
        if form.is_valid():
            player = form.save(commit=False)
            player.team = team
            player.save()
            messages.success(request, f"Jugador {player.name} {player.last_name} agregado exitosamente.")
            return redirect('tournament:manager_dashboard')
    else:
        form = PlayerForm()

    return render(request, 'tournament/player_form.html', {'form': form, 'action': 'Agregar'})


@team_manager_required
def edit_player(request, player_id):
    team = request.user.team
    player = get_object_or_404(Player, id=player_id, team=team)  # Garantiza que el jugador pertenezca a su equipo

    if request.method == 'POST':
        form = PlayerForm(request.POST, instance=player)
        if form.is_valid():
            form.save()
            messages.success(request, f"Datos de {player.name} actualizados.")
            return redirect('tournament:manager_dashboard')
    else:
        form = PlayerForm(instance=player)

    return render(request, 'tournament/player_form.html', {'form': form, 'action': 'Editar', 'player': player})


@team_manager_required
def delete_player(request, player_id):
    team = request.user.team
    player = get_object_or_404(Player, id=player_id, team=team)

    if request.method == 'POST':
        player_name = f"{player.name} {player.last_name}"
        player.delete()
        messages.success(request, f"El jugador {player_name} ha sido eliminado.")

    return redirect('tournament:manager_dashboard')