from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Tournament, Team, Match, GoalEvent, Player, Group, Venue, CustomUser


class GoalEventInline(admin.TabularInline):
    model = GoalEvent
    extra = 1
    fields = ('player', 'team',  'is_own_goal')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        resolved = request.resolver_match
        match_id = resolved.kwargs.get('object_id')
        if match_id:
            try:
                match = Match.objects.get(pk=match_id)
                if db_field.name == "team":
                    kwargs["queryset"] = Team.objects.filter(id__in=[match.team_a.id, match.team_b.id])
                    
                if db_field.name == "player":
                    kwargs["queryset"] = Player.objects.filter(team__in=[match.team_a, match.team_b], active=True)
            except Match.DoesNotExist:
                pass
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('team_a', 'team_b', 'date', 'venue', 'score_team_a', 'score_team_b', 'status')
    search_fields = ('team_a__name', 'team_b__name', 'venue__name')
    list_filter = ('status', 'group', 'fase')
    inlines = [GoalEventInline]

@admin.register(GoalEvent)
class GoalEventAdmin(admin.ModelAdmin):
    list_display = ('match', 'player', 'team', 'is_own_goal')


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    ordering = ('email',)
    search_fields = ('email', 'first_name', 'last_name')
    list_display = ('email',  'first_name', 'last_name', 'team', 'is_staff', 'is_active','is_team_manager')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Información de Torneo', {'fields': ('team',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información de Torneo', {'fields': ('team',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'team', 'is_team_manager'),
        }),
    )
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información Personal', {'fields': ('first_name', 'last_name')}),
        ('Información de Torneo', {'fields': ('team', 'is_team_manager')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas importantes', {'fields': ('last_login', 'date_joined') if hasattr(CustomUser, 'date_joined') else ('last_login',)}),
    )


admin.site.register(Tournament)
admin.site.register(Team)
admin.site.register(Player)
admin.site.register(Group)
admin.site.register(Venue)