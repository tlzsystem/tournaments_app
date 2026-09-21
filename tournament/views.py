from django.shortcuts import render
from .models import Tournament
from .services import calculate_team_points, get_top_scorers, get_best_goalkeepers

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