from django.contrib import admin
from tennis_data.models import (Tournament, Player,
                                Ranking, Match, Set,
                                Odds)

class TournamentAdmin(admin.ModelAdmin):
    list_display = ('atp_number', 'name',
                    'location', 'series',
                    'court', 'surface',
                    'best_of')
    list_filter = ('name', 'series',
                   'court', 'surface',
                   'best_of')


class RankingAdmin(admin.ModelAdmin):
    list_display = ('player', 'tournament',
                    'rank')
    list_filter = ('player', 'tournament')


class MatchAdmin(admin.ModelAdmin):
    list_display = ('winner', 'loser',
                    'tournament', 'date',
                    'round', 'winner_points',
                    'loser_points', 'status',
                    'sets')
    list_filter = ('tournament', 'status')

    def sets(self, obj):
        sets = obj.set_of.all()
        return u', '.join(['%s-%s' % (s.winner_games,
                           s.loser_games) for s in sets])


class SetAdmin(admin.ModelAdmin):
    list_display = ('winner', 'loser',
                    'set_number', 'winner_games',
                    'loser_games')

    def winner(self, obj):
        return obj.match.winner

    def loser(self, obj):
        return obj.match.loser


class OddsAdmin(admin.ModelAdmin):
    exclude = ('max_winner', 'max_loser',
               'avg_winner', 'avg_loser')
    list_display = ('match',
                    'b365_winner', 'b365_loser',
                    'ex_winner', 'ex_loser',
                    'lb_winner', 'lb_loser',
                    'ps_winner', 'ps_loser',
                    'sj_winner', 'sj_loser',
                    'max_winner', 'max_loser',
                    'avg_winner', 'avg_loser')



admin.site.register(Tournament, TournamentAdmin)
admin.site.register(Player)
admin.site.register(Ranking, RankingAdmin)
admin.site.register(Match, MatchAdmin)
admin.site.register(Set, SetAdmin)
admin.site.register(Odds, OddsAdmin)