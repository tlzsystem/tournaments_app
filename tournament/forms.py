from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, Team, Player, Match, GoalEvent
from dal_select2.widgets import ModelSelect2
from django.core.exceptions import ValidationError

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        error_messages={
            'unique': 'Este correo electrónico ya se encuentra registrado. Por favor, inicia sesión o usa otro.'
        }
    )
    team = forms.ModelChoiceField(
        queryset=Team.objects.none(),
        required=True,
        empty_label="Selecciona tu equipo",
        label="Equipo que representas",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'team')
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['team'].queryset = Team.objects.filter(managers__isnull=True)
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_team_manager = True
        if commit:
            user.save()
            self.save_m2m()
        return user


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ejemplo@correo.com'})
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    

class TeamLogoForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['logo']
        widgets = {
            'logo': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
        }

class PlayerForm(forms.ModelForm):
    position = forms.ChoiceField(
        choices=[
            ('', ' - Selecciona una posición - ' ),
            *Player.position_choices,
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = Player
        fields = ['name', 'last_name', 'number', 'position', 'is_captain']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}),
            'number': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Dorsal'}),
        }
        
class TeamColorForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['shirt_color']
        widgets = {
            'shirt_color': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Color del uniforme (e.g., rojo, azul, verde)'}),
        }
        
        
class MatchAdminForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = '__all__'
        widgets = {
            'team_a': ModelSelect2(
                url='tournament:team-autocomplete',
                forward=['group']  
            ),
            'team_b': ModelSelect2(
                url='tournament:team-autocomplete',
                forward=['group']
            ),
        }
        
class GoalEventForm(forms.ModelForm):
    class Meta:
        model = GoalEvent
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        player = cleaned_data.get('player')
        team = cleaned_data.get('team')
        is_own_goal = cleaned_data.get('is_own_goal', False)

        if player and team:
            # Caso 1: Gol normal pero el jugador no pertenece al equipo asignado
            if not is_own_goal and player.team != team:
                raise ValidationError({
                    'player': f"El jugador {player.name} {player.last_name} pertenece a {player.team.name}, no a {team.name}."
                })

            # Caso 2: Autogol pero el equipo asignado es el mismo del jugador
            if is_own_goal and player.team == team:
                raise ValidationError({
                    'team': "En un autogol, el equipo asignado para sumar el punto debe ser el rival."
                })

        return cleaned_data