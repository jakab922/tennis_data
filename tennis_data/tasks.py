from tennis_data.models import (Tournament, Player,
                                Ranking, Match, Set,
                                Odds, DEFAULT_ODD)
import urllib2
import tempfile
from zipfile import ZipFile
from xlrd import open_workbook, xldate_as_tuple
import datetime

CELL_MAP = {
    "atp": 0,
    "location": 1,
    "tournament": 2,
    "date": 3,
    "series": 4,
    "court": 5,
    "surface": 6,
    "round": 7,
    "best_of": 8,
    "winner": 9,
    "loser": 10,
    "wrank": 11,
    "lrank": 12,
    "wpoints": 13,
    "lpoints": 14,
    "w1": 15,
    "l1": 16,
    "w2": 17,
    "l2": 18,
    "w3": 19,
    "l3": 20,
    "w4": 21,
    "l4": 22,
    "w5": 23,
    "l5": 24,
    "wsets": 25,
    "lsets": 26,
    "comment": 27,
    "b365w": 28,
    "b365l": 29,
    "exw": 30,
    "exl": 31,
    "lbw": 32,
    "lbl": 33,
    "psw": 34,
    "psl": 35,
    "sjw": 36,
    "sjl": 37,
    "maxw": 38,
    "maxl": 39,
    "avgw": 40,
    "avgl": 41
}

def int_or_zero(possibly_integer):
    try:
        ret = int(possibly_integer)
    except ValueError:
        ret = 0
    return ret

def float_or_value(possibly_float, value):
    try:
        ret = float(possibly_float)
    except ValueError:
        ret = value
    return ret

class PopulateDatabase(object):
    """ This class is responsible for populating the database with the initial data. """

    file_url = "http://tennis-data.co.uk/2011/2011.zip"
    sheet_name = "2011"

    def __init__(self):
        """ Populates the database from the datasource. """

        self.workbook = self.create_xls_obj()
        for row in self.iterate_rows(self.workbook):
            self.create_tournament(row)
            self.create_players(row)
            self.create_rankings(row)
            self.create_match(row)
            self.create_sets(row)
            self.create_odds(row)

    def get_tournament_params(self, row):
        """ Extracting the tournament data from the row. """

        return {
            'atp_number': int_or_zero(row[CELL_MAP['atp']].value),
            'name': row[CELL_MAP['tournament']].value,
            'location': row[CELL_MAP['location']].value,
            'series': row[CELL_MAP['series']].value,
            'court': row[CELL_MAP['court']].value,
            'surface': row[CELL_MAP['surface']].value,
            'best_of': int_or_zero(row[CELL_MAP['best_of']].value)
        }

    def create_tournament(self, row):
        """ Creating a tournament if it doesn't exist. """

        tournament_params = self.get_tournament_params(row)
        Tournament.objects.get_or_create(**tournament_params)

    def create_players(self, row):
        """ Creating the loser and the winner player if they haven't existed before. """

        Player.objects.get_or_create(name=row[CELL_MAP["winner"]].value)
        Player.objects.get_or_create(name=row[CELL_MAP["loser"]].value)

    def create_rankings(self, row):
        """ Creating the ranking for the winner and loser players. """

        tournament_params = self.get_tournament_params(row)
        tournament = Tournament.objects.get(**tournament_params)
        for player_type, rank_name in (("winner", "wrank"), ("loser", "lrank")):
            player = Player.objects.get(name=row[CELL_MAP[player_type]].value)
            rank = int_or_zero(row[CELL_MAP[rank_name]].value)
            Ranking.objects.get_or_create(player=player,
                                          tournament=tournament,
                                          rank=rank)

    def get_match_params(self, row):
        """ Extracts the params related to the match from the row. """

        winner = Player.objects.get(name=row[CELL_MAP["winner"]].value)
        loser = Player.objects.get(name=row[CELL_MAP["loser"]].value)
        tournament_params = self.get_tournament_params(row)
        tournament = Tournament.objects.get(**tournament_params)
        date_tuple = xldate_as_tuple(row[CELL_MAP['date']].value,
                                     self.workbook.datemode)
        date = datetime.date(*date_tuple[:3])
        return {
            "winner": winner,
            "loser": loser,
            "tournament": tournament,
            "date": date,
            "round": row[CELL_MAP["round"]].value,
            "winner_points": int_or_zero(row[CELL_MAP["wpoints"]].value),
            "loser_points": int_or_zero(row[CELL_MAP["lpoints"]].value),
            "status": row[CELL_MAP["comment"]].value
        }


    def create_match(self, row):
        """ Creates a match from the raw data. """

        match_params = self.get_match_params(row)
        match = Match(**match_params)
        match.save()

    def create_sets(self, row):
        """ Creates the sets related to the match. """

        match_params = self.get_match_params(row)
        match = Match.objects.get(**match_params)
        prefixes = ["w", "l"]
        for i in xrange(1,6):
            set_pair = []
            for prefix in prefixes:
                cell_value = row[CELL_MAP[prefix + str(i)]].value
                if cell_value != '':
                    set_pair.append(cell_value)
            if set_pair == []:
                break
            else:
                current_set = Set(match=match,
                                  set_number=i,
                                  winner_games=set_pair[0],
                                  loser_games=set_pair[1])
                current_set.save()

    def create_odds(self, row):
        """ Creates the odds related to the match. """

        match_params = self.get_match_params(row)
        match = Match.objects.get(**match_params)
        odds_params = {'match': match}
        prefixes = [
            'b365',
            'ex',
            'lb',
            'ps',
            'sj',
            'max',
            'avg'
        ]
        suffix_pairs = (('w', '_winner'), ('l', '_loser'))
        for prefix in prefixes:
            for in_suffix, out_suffix in suffix_pairs:
                cell_value = row[CELL_MAP[prefix + in_suffix]].value
                cell_value = float_or_value(cell_value, DEFAULT_ODD)
                odds_params[prefix + out_suffix] = cell_value
        odds = Odds(**odds_params)
        odds.save()

    def iterate_rows(self, workbook):
        """ An iterator over the rows of the important sheet. """

        sheet = workbook.sheet_by_name(self.sheet_name)
        for i in xrange(1, sheet.nrows):
            print "yielding row %s" % i
            yield sheet.row(i)

    def create_xls_obj(self):
        """ Downloads the zipfile and creates and return the xls workbook. """

        response = urllib2.urlopen(self.file_url)
        zipfile_name = tempfile.mkstemp()[1]
        zipfile = open(zipfile_name, 'w')
        zipfile.write(response.read())
        zipfile.close()

        zipfile = ZipFile(zipfile_name)
        xlsfile_name = tempfile.mkstemp()[1]
        xlsfile = open(xlsfile_name, 'w')
        fromzip_file = zipfile.open(zipfile.infolist()[0])
        xlsfile.write(fromzip_file.read())
        xlsfile.close()
        zipfile.close()

        return open_workbook(xlsfile_name)

