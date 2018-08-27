import os

from espnff import League


LEAGUE_ID = os.environ.get("LEAGUE_ID")
ESPN_S2 = os.environ.get("ESPN_S2")
SWID = os.environ.get("SWID")

league = League(LEAGUE_ID, 2017, espn_s2=ESPN_S2, swid=SWID)


def get_teams():
    return league.teams


# Documentation didn't show an example without the 'week' param, but prob defaults to current week
def get_power_rankings(week):
    return league.power_rankings(week)


# Can pass a 'week=x' param to scoreboard method
def get_scoreboard(**kwargs):
    return league.scoreboard(**kwargs)


def get_user_matchup(scoreboard, user_team):
    for matchup in scoreboard:
        if matchup.home_team == user_team:
            return 'home_team', matchup
        elif matchup.away_team == user_team:
            return 'away_team', matchup


def get_winner_or_loser(scoreboard, function):
    """
    Takes a scoreboard object and returns the person with the lowest score this week and their score.
    NOTE: If multiple people are tied for lowest score, this currently only returns one of them.
    """
    # assert function in ['winner', 'loser']

    board = [{matchup.home_team: matchup.home_score, matchup.away_team: matchup.away_score} for matchup in scoreboard]

    team_scores = {}
    for matchup in board:
        for team, score in matchup.iteritems():
            team_scores[team] = score

    if function == 'loser':
        team = min(team_scores, key=team_scores.get)
    else:
        team = max(team_scores, key=team_scores.get)

    owner = team.owner
    score = team_scores[team]

    if owner == 'Charlotte Alimanestianu':
        owner = 'Chalotte/Tiffany'

    return owner, score


def output_scoreboard(scoreboard):
    """
    Takes a scoreboard object and returns specially formatted data used to print the entire scoreboard.
    """
    output_dict = {}

    count = 1
    while count < 9:
        matchup = scoreboard[count - 1]

        formatted_data = {
            "home_team_{0}".format(count): matchup.home_team.team_name.strip(),
            "home_score_{0}".format(count): matchup.home_score,
            "away_team_{0}".format(count): matchup.away_team.team_name.strip(),
            "away_score_{0}".format(count): matchup.away_score
        }

        for k, v in formatted_data.iteritems():
            output_dict[k] = v

        count += 1

    return output_dict
