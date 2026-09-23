from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


class Tournament(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Team(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='team_logos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Player(models.Model):
    
    position_choices = [
        ('goalkeeper', 'Portero'),
        ('defender', 'Defensa'),
        ('midfielder', 'Centrocampista'),
        ('forward', 'Delantero'),
    ]

    name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    number = models.PositiveIntegerField()
    active = models.BooleanField(default=True)
    position = models.CharField(max_length=20, choices=position_choices)
    is_captain = models.BooleanField(default=False)
    is_goalkeeper = models.BooleanField(default=False)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='players')
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['team', 'number']
        
    def save(self, *args, **kwargs):
        if self.position == 'goalkeeper':
            self.is_goalkeeper = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} {self.last_name} # {self.number} - {self.team.name}"


class Group(models.Model):
    name = models.CharField(max_length=100, help_text="Nombre del grupo (e.g., Grupo A, Grupo B)")
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='groups')
    teams = models.ManyToManyField(Team, related_name='groups')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.tournament.name}"


class Venue(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Match(models.Model):

    fase_choices = [
        ('group', 'Fase Grupos'),
        ('semifinal', 'Semifinal'),
        ('final', 'Final'),
    ]

    status_choices = [
        ('scheduled', 'Programado'),
        ('live', 'En Vivo'),
        ('completed', 'Completado'),
    ]

    team_a = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches_as_team_a')
    team_b = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches_as_team_b')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='matches', null=True, blank=True)
    fase = models.CharField(max_length=20, choices=fase_choices, default='group')
    date = models.DateTimeField()
    venue = models.ForeignKey(Venue, on_delete=models.SET_NULL, null=True, blank=True, related_name='matches')
    score_team_a = models.PositiveIntegerField(default=0)
    score_team_b = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=status_choices, default='scheduled')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.team_a.name} vs {self.team_b.name} - [{self.fase}] - {self.venue}"

    def update_score(self):
        self.score_team_a = self.goal_events.filter(team=self.team_a).count()
        self.score_team_b = self.goal_events.filter(team=self.team_b).count()
        self.save()


class GoalEvent(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='goal_events')
    player = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name='goal_events')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='goal_events')
    is_own_goal = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def save(self, *args, **kwargs):
        if self.player and not self.is_own_goal and self.player.team != self.team:
            raise ValueError("The player must belong to the team that scored the goal.")
        super().save(*args, **kwargs)
        self.match.update_score()

    def delete(self, *args, **kwargs):
        match = self.match
        super().delete(*args, **kwargs)
        match.update_score()

    def __str__(self):
        return f"Goal by {self.player.name} {self.player.last_name} for {self.team.name}  in match {self.match}"

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El correo electrónico es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name="Correo electrónico")
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    is_team_manager = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    team = models.ForeignKey(
        'Team', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='managers',
        verbose_name="Equipo asignado"
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.email} ({self.team.name if self.team else 'Sin Equipo'})"