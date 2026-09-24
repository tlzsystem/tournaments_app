from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .models import Tournament, Player, Team, Match
from .services import calculate_team_points, get_top_scorers, get_best_goalkeepers
from .forms import CustomUserCreationForm, EmailAuthenticationForm, TeamLogoForm, PlayerForm, TeamColorForm
from dal_select2.views import Select2QuerySetView

def tournament_detail(request):
    tournament = Tournament.objects.filter(is_default=True).first()
    groups = tournament.groups.all()

    matches = Match.objects.filter(group__tournament=tournament).select_related('team_a', 'team_b', 'group', 'venue').order_by('date')

    group_matches = matches.filter(fase='group')
    semifinal_matches = matches.filter(fase='semifinal')
    final_matches = matches.filter(fase='final')

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
        'group_matches': group_matches,
        'semifinal_matches': semifinal_matches,
        'final_matches': final_matches,
        'tournament': tournament,
        'group_tables': group_tables,
        'top_scorers': top_scorers,
        'best_goalkeepers': best_goalkeepers,
    }

    return render(request, 'tournament/index.html', context)

def tournament_detail_view(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    groups = tournament.groups.all()

    matches = Match.objects.filter(group__tournament=tournament).select_related('team_a', 'team_b', 'group', 'venue').order_by('date')
    group_matches = matches.filter(fase='group')
    semifinal_matches = matches.filter(fase='semifinal')
    final_matches = matches.filter(fase='final')

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
        'group_matches': group_matches,
        'semifinal_matches': semifinal_matches,
        'final_matches': final_matches,
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


def fixture_view_tournament(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    matches = Match.objects.filter(group__tournament=tournament).select_related('team_a', 'team_b', 'group', 'venue').order_by('date')
    group_matches = matches.filter(fase='group')
    semifinal_matches = matches.filter(fase='semifinal')
    final_matches = matches.filter(fase='final')
    
    context = {
        'tournament': tournament,
        'group_matches': group_matches,
        'semifinal_matches': semifinal_matches,
        'final_matches': final_matches,

    }

    
    return render(request, 'tournament/fixture.html', context)

def fixture_view(request):
    tournament = Tournament.objects.filter(is_default=True).first()
    matches = Match.objects.filter(group__tournament=tournament).select_related('team_a', 'team_b', 'group', 'venue').order_by('date')
    group_matches = matches.filter(fase='group')
    semifinal_matches = matches.filter(fase='semifinal')
    final_matches = matches.filter(fase='final')
    
    context = {
        'tournament': tournament,
        'group_matches': group_matches,
        'semifinal_matches': semifinal_matches,
        'final_matches': final_matches,

    }

    
    return render(request, 'tournament/fixture.html', context)


def players_list_tournament(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    teams = Team.objects.filter(groups__tournament=tournament).distinct().prefetch_related('players')

    context = {
            'teams': teams,
            'tournament': tournament,
        }

    return render(request, 'tournament/players_list.html',context)

def players_list(request):
    tournament = Tournament.objects.filter(is_default=True).first()
    teams = Team.objects.filter(groups__tournament=tournament).distinct().prefetch_related('players')

    context = {
            'teams': teams,
            'tournament': tournament,
        }

    return render(request, 'tournament/players_list.html',context)


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
        if 'logo' in request.FILES and logo_form.is_valid():
            logo_form.save()
            messages.success(request, "Logo del equipo actualizado con éxito.")
            return redirect('tournament:manager_dashboard')
        else:
            messages.error(request, "Debes seleccionar un archivo de imagen válido.")
    elif request.method == 'POST' and 'delete_logo' in request.POST:
        if team.logo:
            team.logo.delete(save=False)  
            team.logo = None              
            team.save()
            messages.success(request, "El escudo ha sido eliminado.")
        return redirect('tournament:manager_dashboard')
        
    elif request.method == 'POST' and 'update_color' in request.POST:
        color_form = TeamColorForm(request.POST, instance=team)
        if color_form.is_valid():
            color_form.save()
            messages.success(request, "Color del uniforme actualizado con éxito.")
            return redirect('tournament:manager_dashboard')
    
    else:
        logo_form = TeamLogoForm(instance=team)

    context = {
        'team': team,
        'players': players,
        'logo_form': logo_form,
        'color_form': TeamColorForm(instance=team),
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
    player = get_object_or_404(Player, id=player_id, team=team) 

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


class TeamAutocomplete(Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Team.objects.none()

        qs = Team.objects.all()

        group_id = self.forwarded.get('group', None)

        if group_id:
            qs = qs.filter(groups__id=group_id)
        else:
            return Team.objects.none()

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs