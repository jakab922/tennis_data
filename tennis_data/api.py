from django.http import HttpResponse
from json import dumps
from tennis_data.models import (Tournament, Player,
                                Ranking, Match, Set,
                                Odds)
from functools import wraps
from itertools import izip


class APIError(Exception):
    pass


class IDError(APIError):
    msg = "We couldn't find any object with the given id!"


def jsonify(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        dictionary = function(*args, **kwargs)
        return HttpResponse(dumps(dictionary),
                            mimetype='application/json')
    return wrapper


def sanitize(function):
    @wraps(function)
    def wrapper(request, *args, **kwargs):
        if request.method != 'GET':
            return {
                'status': 'error',
                'msg': 'Only the GET HTTP method is supported'
            }
        else:
            try:
                data = function(request, *args, **kwargs)
            except APIError, e:
                return {
                    'status': 'error',
                    'msg': e.msg
                }
            return {
                'status': 'ok',
                'data': data
            }
    return wrapper


@jsonify
@sanitize
def players(request):
    player_data = Player.objects.all()
    return [
        {
            "id": player.pk,
            "name": player.name
        }
        for player in player_data
    ]


@jsonify
@sanitize
def player_matches(request, player_id):
    try:
        player = Player.objects.get(pk=player_id)
    except Player.DoesNotExist:
        raise IDError
    won_matches = player.winner_of.all()
    lost_matches = player.loser_of.all()
    ret = {}
    match_pairs = (('won', won_matches), ('lost', lost_matches))
    for match_type, matches in match_pairs:
        ret[match_type] = []
        for match in matches:
            current_match = {
                'id': match.pk,
                'tournament': {
                    'id': match.tournament.id,
                    'name': match.tournament.name
                },
                'date': match.date.isoformat(),
                'round': match.round,
                'winner_points': match.winner_points,
                'loser_points': match.loser_points,
                'status': match.status
            }
            current_sets = sorted(match.set_of.all(), key=lambda x: x.set_number)
            current_match['sets'] = [[s.winner_games, s.loser_games]
                                     for s in current_sets]
            ret[match_type].append(current_match)
    return ret


@jsonify
@sanitize
def tournaments(request):
    tournament_data = Tournament.objects.all()
    return [
        {
            "id": tournament.pk,
            "name": tournament.name
        }
        for tournament in tournament_data
    ]


@jsonify
@sanitize
def tournament_players(request, tournament_id):
    try:
        tournament = Tournament.objects.get(pk=tournament_id)
    except Tournament.DoesNotExist, e:
        raise IDError
    tournament_matches = tournament.match_of.all()
    tournament_players = set()
    for tournament_match in tournament_matches:
        tournament_players.add(tournament_match.winner)
        tournament_players.add(tournament_match.loser)
    rankings = []
    for tplayer in tournament_players:
        rankings.append(Ranking.objects.get(tournament=tournament,
                                            player=tplayer))
    return sorted([
        {
            'id': tplayer.id,
            'name': tplayer.name,
            'rank': ranking.rank
        }
        for ranking, tplayer in izip(rankings, tournament_players)
    ], key=lambda x: x['rank'])


@jsonify
@sanitize
def matches(request):
    match_data = Match.objects.all()
    return [
        {
            'id': match.id,
            'tournament': {
                'id': match.tournament.id,
                'name': match.tournament.name
            },
            'round': match.round,
            'date': match.date.isoformat()
        }
        for match in match_data
    ]


@jsonify
@sanitize
def match_odds(request, match_id):
    try:
        match = Match.objects.get(pk=match_id)
    except Match.DoesNotExist, e:
        raise IDError
    match_odds = match.odds_of.get()
    return {
        'b365_winner': match_odds.b365_winner,
        'b365_loser': match_odds.b365_loser,
        'ex_winner': match_odds.ex_winner,
        'ex_loser': match_odds.ex_loser,
        'lb_winner': match_odds.lb_winner,
        'lb_loser': match_odds.lb_loser,
        'ps_winner': match_odds.ps_winner,
        'ps_loser': match_odds.ps_loser,
        'sj_winner': match_odds.sj_winner,
        'sj_loser': match_odds.sj_loser,
        'max_winner': match_odds.max_winner,
        'max_loser': match_odds.max_loser,
        'avg_winner': match_odds.avg_winner,
        'avg_loser': match_odds.avg_loser,
    }
