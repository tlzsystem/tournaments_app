from django.db.models import Q, Count, Sum
from .models import  Team,   Player

def calculate_team_points(group):

    stats = {}
    for team in group.teams.all():
        stats[team.id] = {
            'team': team,
            'pj': 0,  # Partidos jugados
            'pg': 0,  # Partidos ganados 
            'pe': 0,  # Partidos empatados
            'pp': 0,  # Partidos perdidos
            'gf': 0,  # Goles a favor
            'gc': 0,  # Goles en contra
            'dg': 0,  # Diferencia de goles
            'pts': 0, # Puntos
        }

        matches = group.matches.filter(fase='group', status='completed')
    for match in matches:
        if not match.team_a or not match.team_b:
            continue
        team_a_stats = stats[match.team_a.id]
        team_b_stats = stats[match.team_b.id]

        team_a_stats['pj'] += 1
        team_b_stats['pj'] += 1

        team_a_stats['gf'] += match.score_team_a
        team_a_stats['gc'] += match.score_team_b 
        team_b_stats['gf'] += match.score_team_b
        team_b_stats['gc'] += match.score_team_a

        if match.score_team_a > match.score_team_b:
            team_a_stats['pg'] += 1
            team_b_stats['pp'] += 1
            team_a_stats['pts'] += 3
        elif match.score_team_a < match.score_team_b:
            team_b_stats['pg'] += 1
            team_a_stats['pp'] += 1
            team_b_stats['pts'] += 3
        else:
            team_a_stats['pe'] += 1
            team_b_stats['pe'] += 1
            team_a_stats['pts'] += 1
            team_b_stats['pts'] += 1


    table = list(stats.values())
    for item in table:
        item['dg'] = item['gf'] - item['gc']
    table.sort(key=lambda x: (x['pts'], x['dg'], x['gf']), reverse=True)

    return table
            
def get_top_scorers(tournament, limit=5):
    return Player.objects.filter(
        team__groups__tournament=tournament).annotate(
        goals_scored=Count('goal_events', filter=Q(goal_events__match__group__tournament=tournament, goal_events__is_own_goal=False))
    ).filter(goals_scored__gt=0).order_by('-goals_scored')[:limit]
        
        
def get_best_goalkeepers(tournament):
    teams = Team.objects.filter(groups__tournament=tournament).distinct()
    goalkeepers_ranking = []
    
    for team in teams:
        home_goals = team.matches_as_team_a.filter(group__tournament=tournament, status='completed').aggregate(total_goals=Sum('score_team_b'))['total_goals'] or 0
        away_goals = team.matches_as_team_b.filter(group__tournament=tournament, status='completed').aggregate(total_goals=Sum('score_team_a'))['total_goals'] or 0
        total_matches_home_played = team.matches_as_team_a.filter(group__tournament=tournament, status='completed').count()
        total_matches_away_played = team.matches_as_team_b.filter(group__tournament=tournament, status='completed').count()
        total_matches_played = total_matches_home_played + total_matches_away_played
        total_goals_conceded = home_goals + away_goals
        goalkeper = team.players.filter(is_goalkeeper=True).first()
        
        goalkeepers_ranking.append({
            'team': team,  
            'goalkeeper': goalkeper,
            'goals_conceded': total_goals_conceded,
            'matches_played': total_matches_played,
            'average_goals_conceded': total_goals_conceded / total_matches_played if total_matches_played > 0 else 0
        })
    
    goalkeepers_ranking.sort(key=lambda x: (x['average_goals_conceded'], -x['matches_played']))
    return goalkeepers_ranking
        
  