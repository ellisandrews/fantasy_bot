import os

from espnff.client import ESPNFF
from espnff.exception import AuthorizationError

from slack import USERS


LEAGUE_ID = os.environ.get('LEAGUE_ID')
LEAGUE_YEAR = os.environ.get('LEAGUE_YEAR')
ESPN_USERNAME = os.environ.get('ESPN_USERNAME')
ESPN_PASSWORD = os.environ.get('ESPN_PASSWORD')


def get_league():
    client = ESPNFF(ESPN_USERNAME, ESPN_PASSWORD)

    try:
        client.authorize()
    except AuthorizationError:
        print 'Failed to authorize.'

    # Use the custom ESPNFF client to fetch the private league (handles 'swid' and 's2' for you)
    return client.get_league(LEAGUE_ID, LEAGUE_YEAR)


def map_user_to_team(league, user):
    """
    Tries to find the fantasy team of the slack user talking to the bot.
    """
    for team in league.teams:
        if team.team_id == USERS[user]:
            return team


def get_winner_or_loser(scoreboard, winner_or_loser):
    # Parse Scoreboard matchups to get dictionary of {Team: score}
    team_scores = {}
    for matchup in scoreboard:
        team_scores[matchup.home_team] = matchup.home_score
        team_scores[matchup.away_team] = matchup.away_score

    # TODO: If there is a tie, say it was a tie!
    # Get the Team with the lowest or highest score depending on which arg was passed in
    if winner_or_loser == 'loser':
        team = min(team_scores, key=team_scores.get)
    else:
        team = max(team_scores, key=team_scores.get)

    # Return the Team and what their score was
    return team, team_scores[team]


def matchup_command(league, user, week):

    # Get the relevant Team from the user name
    user_team = map_user_to_team(league, user)

    # Search for the user's matchup in the relevant week
    user_matchup = None
    for matchup in league.scoreboard(week=week):
        if user_team in (matchup.home_team, matchup.away_team):
            user_matchup = matchup

    if user_matchup:
        response = "{home_team} *{home_score}*\n{away_team} *{away_score}*".format(
            home_team=user_matchup.home_team.team_name.strip(),
            home_score=user_matchup.home_score,
            away_team=user_matchup.away_team.team_name.strip(),
            away_score=user_matchup.away_score
        )
    else:
        response = "Hmm, I couldn't find the matchup you were looking for :thinking_face:"

    return response


def winner_loser_command(league, week, winner_or_loser):
    team, score = get_winner_or_loser(league.scoreboard(week=week), winner_or_loser)

    # Find the team owner name with the lowest score
    owner = None
    for user_name, team_id in USERS.iteritems():
        if team_id == team.team_id:
            owner = user_name

    # Custom handling of a joint team to always make Tiffany the owner of the team
    if owner in ('Charlotte', 'Tiffany'):
        owner = 'Tiffany'

    # If owner somehow not found, handle that case
    if not owner:
        response = "Hmm, I couldn't find a team owner for your request :("
    else:
        if winner_or_loser == 'loser':
            exclamation = 'Sad'
        else:
            exclamation = 'Rad'

        response = "{owner} is the overall {winner_or_loser} with {score} points - {exclamation}!".format(
            owner=owner, winner_or_loser=winner_or_loser, score=score, exclamation=exclamation
        )

    return response


def scoreboard_command(league, week):

    # Format scoreboard matchup data nicely for the slack response, and construct slack response string to be populated
    # with that data
    matchup_data = {}
    response = ''

    count = 1
    for matchup in league.scoreboard(week=week):

        matchup_data["home_team_{}".format(count)] = matchup.home_team.team_name
        matchup_data["home_score_{}".format(count)] = matchup.home_score
        matchup_data["away_team_{}".format(count)] = matchup.away_team.team_name
        matchup_data["away_score_{}".format(count)] = matchup.away_score

        matchup_skeleton = "[home_team_{0}] *[home_score_{0}]*\n[away_team_{0}] *[away_score_{0}]*\n\n".format(count)
        matchup_skeleton = matchup_skeleton.replace('[', '{')
        matchup_skeleton = matchup_skeleton.replace(']', '}')

        response += matchup_skeleton

        count += 1

    return response.format(**matchup_data)
