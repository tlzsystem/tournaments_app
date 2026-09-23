from datetime import datetime
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from .models import Tournament, Team, Group, Match, Venue, Player


class FixtureViewTests(TestCase):
    def setUp(self):
        self.tournament = Tournament.objects.create(
            name='Liga Local',
            description='Torneo de prueba',
            start_date='2026-01-01',
            end_date='2026-12-31',
        )
        self.group = Group.objects.create(name='Grupo A', tournament=self.tournament)
        self.team_a = Team.objects.create(name='Equipo A', shirt_color='rojo')
        self.team_b = Team.objects.create(name='Equipo B', shirt_color='azul')
        self.team_c = Team.objects.create(name='Equipo C', shirt_color='verde')
        self.venue = Venue.objects.create(name='Estadio Central')

        self.group.teams.add(self.team_a, self.team_b, self.team_c)

        self.match_1 = Match.objects.create(
            team_a=self.team_a,
            team_b=self.team_b,
            group=self.group,
            date=timezone.make_aware(datetime(2026, 2, 10, 20, 0, 0)),
            venue=self.venue,
            score_team_a=2,
            score_team_b=1,
            status='completed',
        )
        self.match_2 = Match.objects.create(
            team_a=self.team_c,
            team_b=self.team_a,
            group=self.group,
            date=timezone.make_aware(datetime(2026, 2, 12, 18, 30, 0)),
            venue=self.venue,
            score_team_a=0,
            score_team_b=0,
            status='scheduled',
        )

    def test_fixture_lists_all_matches(self):
        response = self.client.get(reverse('tournament:fixture', args=[self.tournament.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Fixture')
        self.assertContains(response, 'Equipo A')
        self.assertContains(response, 'Equipo B')
        self.assertContains(response, 'Equipo C')
        self.assertContains(response, '2 - 1')
        self.assertContains(response, '0 - 0')
        self.assertContains(response, 'Estadio Central')


class PlayersViewTests(TestCase):
    def setUp(self):
        self.tournament = Tournament.objects.create(
            name='Liga Local',
            description='Torneo de prueba',
            start_date='2026-01-01',
            end_date='2026-12-31',
        )
        self.group = Group.objects.create(name='Grupo A', tournament=self.tournament)
        self.team_a = Team.objects.create(name='Equipo A', shirt_color='rojo')
        self.team_b = Team.objects.create(name='Equipo B', shirt_color='azul')
        self.group.teams.add(self.team_a, self.team_b)

        self.player_a = Player.objects.create(
            name='Juan',
            last_name='Pérez',
            number=10,
            position='forward',
            team=self.team_a,
        )
        self.player_b = Player.objects.create(
            name='Luis',
            last_name='García',
            number=7,
            position='midfielder',
            team=self.team_b,
        )

    def test_tournament_players_page_lists_all_players(self):
        response = self.client.get(reverse('tournament:players', args=[self.tournament.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Jugadores')
        self.assertContains(response, 'Equipo A')
        self.assertContains(response, 'Equipo B')
        self.assertContains(response, self.player_a.name)
        self.assertContains(response, self.player_b.name)


class TournamentDashboardFixtureTests(TestCase):
    def setUp(self):
        self.tournament = Tournament.objects.create(
            name='Liga Local',
            description='Torneo de prueba',
            start_date='2026-01-01',
            end_date='2026-12-31',
        )
        self.group = Group.objects.create(name='Grupo A', tournament=self.tournament)
        self.team_a = Team.objects.create(name='Equipo A', shirt_color='rojo')
        self.team_b = Team.objects.create(name='Equipo B', shirt_color='azul')
        self.group.teams.add(self.team_a, self.team_b)

        self.match = Match.objects.create(
            team_a=self.team_a,
            team_b=self.team_b,
            group=self.group,
            fase='group',
            date=timezone.make_aware(datetime(2026, 2, 10, 20, 0, 0)),
            venue=None,
            score_team_a=2,
            score_team_b=1,
            status='completed',
        )

    def test_dashboard_shows_match_in_fixture_section(self):
        response = self.client.get(reverse('tournament:tournament_index'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Fase de Grupos')
        self.assertContains(response, '10/02')
        self.assertContains(response, 'Equipo A')
        self.assertContains(response, 'Equipo B')
