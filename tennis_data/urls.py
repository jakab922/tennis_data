from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^warmup/$', 'tennis_data.views.warmup'),
    url(r'^api/players/$', 'tennis_data.api.players'),
    url(r'^api/player/(?P<player_id>\d+)/matches/$', 'tennis_data.api.player_matches'),
    url(r'^api/tournaments/$', 'tennis_data.api.tournaments'),
    url(r'^api/tournament/(?P<tournament_id>\d+)/players/$', 'tennis_data.api.tournament_players'),
    url(r'^api/matches/$', 'tennis_data.api.matches'),
    url(r'^api/match/(?P<match_id>\d+)/odds/$', 'tennis_data.api.match_odds'),
    # Examples:
    # url(r'^$', 'tennis_data.views.home', name='home'),
    # url(r'^tennis_data/', include('tennis_data.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^admin/', include(admin.site.urls)),
)
