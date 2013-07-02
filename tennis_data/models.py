from django.db import models
from django.core.validators import MinValueValidator
from tennis_data.settings import EPS


class Tournament(models.Model):
    """ Storing data related to a tournament. """

    atp_number = models.PositiveIntegerField()
    name = models.CharField(max_length=60)
    location = models.CharField(max_length=60)
    series = models.CharField(max_length=60)
    court = models.CharField(max_length=60)
    surface = models.CharField(max_length=60)
    best_of = models.PositiveIntegerField()

    def __unicode__(self):
        return unicode(self.name)


class Player(models.Model):
    """ Player related data. Currently only the name. """

    name = models.CharField(max_length=60, unique=True)

    def __unicode__(self):
        return unicode(self.name)


class Ranking(models.Model):
    """ The rank of a player in a tournament. """

    player = models.ForeignKey('Player', related_name="ranking_of")
    tournament = models.ForeignKey('Tournament', related_name="ranking_of")
    rank = models.PositiveIntegerField()


class Match(models.Model):
    """ Details of a match. """

    winner = models.ForeignKey('Player', related_name="winner_of")
    loser = models.ForeignKey('Player', related_name="loser_of")
    tournament = models.ForeignKey('Tournament', related_name="match_of")
    date = models.DateField()
    round = models.CharField(max_length=60)
    winner_points = models.PositiveIntegerField()
    loser_points = models.PositiveIntegerField()
    status = models.CharField(max_length=60)

    class Meta:
        verbose_name_plural = "Matches"

    def __unicode__(self):
        return u'%s(W) vs. %s(L) @ %s %s' % (self.winner,
                                             self.loser,
                                             self.tournament,
                                             self.round)


class Set(models.Model):
    """ Data related to a set of a match. """

    match = models.ForeignKey('Match', related_name="set_of")
    set_number = models.PositiveIntegerField()
    winner_games = models.PositiveIntegerField()
    loser_games = models.PositiveIntegerField()

    def __unicode__(self):
        return u'set #%s@%s: %s-%s' % (self.set_number,
                                       self.match,
                                       self.winner_games,
                                       self.loser_games)


DEFAULT_ODD = 1.0 + EPS


class Odds(models.Model):
    """ Odds for a given match by various gambling companies. """

    match = models.ForeignKey('Match', related_name="odds_of")
    b365_winner = models.FloatField(validators=[MinValueValidator(DEFAULT_ODD)],
                                    default=DEFAULT_ODD)
    b365_loser = models.FloatField(validators=[MinValueValidator(DEFAULT_ODD)],
                                   default=DEFAULT_ODD)
    ex_winner = models.FloatField(validators=[MinValueValidator(DEFAULT_ODD)],
                                  default=DEFAULT_ODD)
    ex_loser = models.FloatField(validators=[MinValueValidator(DEFAULT_ODD)],
                                 default=DEFAULT_ODD)
    lb_winner = models.FloatField(validators=[MinValueValidator(DEFAULT_ODD)],
                                  default=DEFAULT_ODD)
    lb_loser = models.FloatField(validators=[MinValueValidator(DEFAULT_ODD)],
                                 default=DEFAULT_ODD)
    ps_winner = models.FloatField(validators=[MinValueValidator(DEFAULT_ODD)],
                                  default=DEFAULT_ODD)
    ps_loser = models.FloatField(validators=[MinValueValidator(DEFAULT_ODD)],
                                 default=DEFAULT_ODD)
    sj_winner = models.FloatField(validators=[MinValueValidator(DEFAULT_ODD)],
                                  default=DEFAULT_ODD)
    sj_loser = models.FloatField(validators=[MinValueValidator(DEFAULT_ODD)],
                                 default=DEFAULT_ODD)
    max_winner = models.FloatField(validators=[MinValueValidator(DEFAULT_ODD)])
    max_loser = models.FloatField(validators=[MinValueValidator(DEFAULT_ODD)])
    avg_winner = models.FloatField(validators=[MinValueValidator(DEFAULT_ODD)])
    avg_loser = models.FloatField(validators=[MinValueValidator(DEFAULT_ODD)])

    def save(self):
        """ Calculating the max and avg values for the winners and losers. """

        winner_list = [self.b365_winner, self.ex_winner,
                       self.lb_winner, self.ps_winner,
                       self.sj_winner]
        loser_list = [self.b365_loser, self.ex_loser,
                      self.lb_loser, self.ps_loser,
                      self.sj_loser]

        self.max_winner = max(winner_list)
        self.max_loser = max(loser_list)
        self.avg_winner = sum(winner_list) / len(winner_list)
        self.avg_loser = sum(loser_list) / len(loser_list)
        super(Odds, self).save()

    class Meta:
        verbose_name_plural = "Oddses"
