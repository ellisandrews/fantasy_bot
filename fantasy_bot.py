import os
import time

from espn_fantasy import get_teams, get_scoreboard, get_user_matchup, get_winner_or_loser, output_scoreboard
from slackclient import SlackClient


# Get Slack @fantasy_bot ID and Slack API token from virtualenv
BOT_ID = os.environ.get("BOT_ID")
SLACK_API_TOKEN = os.environ.get("SLACK_API_TOKEN")

# Slack @fantasy_bot constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMANDS = ["my matchup", "loser", "winner", "scoreboard"]
VALID_USERS = ["ellis", "asmist", "vishal", "grant", "eunji", "charlotte", "mike", "adam", "liz", "dsmith", "ksawyer",
               "tom", "hmoeller", "ptracy", "libby", "keshav", "tiffany"]

MAP_USERS = {
    "ellis": "ellis",
    "asmist": "andrew",
    "vishal": "vishal",
    "grant": "grant",
    "eunji": "eunji",
    "charlotte": "charlotte",
    "mike": "M",
    "adam": "adam",
    "liz": "liz",
    "dsmith": "drew",
    "ksawyer": "katherine",
    "tom": "thomas",
    "hmoeller": "hunter",
    "ptracy": "peter",
    "libby": "libby",
    "keshav": "keshav",
    "tiffany": "charlotte"
}

# Instantiate Slack client
sc = SlackClient(SLACK_API_TOKEN)


def parse_rtm_output(slack_rtm_output):
    """
    The Slack Real Time Messaging API is an events firehose. This parsing function returns None unless a message is
    directed at the Bot, in which case the RTM output is returned (a list).
    """
    output_list = slack_rtm_output

    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                return output
    return None


def is_valid_command(command):
    """
    Receives messages directed at the Slack bot and returns True if they are valid commands, False otherwise.
    """
    for item in EXAMPLE_COMMANDS:
        if item in command:
            return True
    return False


def add_reaction(rtm_output, reaction):
    """
    Adds emoji reactions (as @fantasy_bot user) to messages directed at the Slack bot.
    """
    sc.api_call('reactions.add', name=reaction, channel=rtm_output['channel'], timestamp=rtm_output['ts'])


def respond_to_user(rtm_output, message):
    """
    Sends a slack message as the bot to the user in the channel in which they messaged the bot.
    """
    sc.api_call('chat.postMessage', channel=rtm_output['channel'], text=message, as_user=True)


def get_user_name(bot_output):
    user_id = bot_output['user']
    response = sc.api_call('users.info', user=user_id)
    if response['ok']:
        return response['user']['name']
    else:
        raise Exception('Slack API call for user name failed')


def user_validation(user_name):
    """
    Check to make sure the slack user talking to the bot is in the list of approved users.
    """
    return user_name in VALID_USERS


def map_user_to_team(slack_user):
    """
    Tries to find the fantasy team of the slack user talking to the bot.
    """
    # Grab all of the teams in the fantasy league
    teams = get_teams()
    # Mike is the only person not using their full name on espn.com

    slack_user = slack_user.lower()
    espn_name = MAP_USERS[slack_user]

    for team in teams:
        if team.owner.split()[0].lower().strip() == espn_name.lower().strip():
            return team


def parse_week(message):
    """
    Checks to see if the slack user specified a week of the season in their command.
    returns -1 if 'week' was in the message, but the bot couldn't understand the user command.
    NOTE: Should clean this function up, it's pretty gross
    """
    if 'week' in message and 'this week' not in message:
        possible_int = message.split('week')[1].split()[0].strip().strip('?').strip('!')
        week_number = None
        try:
            week_number = int(possible_int)
        except ValueError:
            print "Tried to find a week number and failed. Passing..."
            pass

        if not week_number or week_number > 13:
            return -1

        # Valid schedule weeks are 1 to 13 (look for 13, 12, 11, 10 first so doesn't just find 'week 1' in the command)
        for i in xrange(13, 0, -1):
            if 'week {0}'.format(i) in message:
                return i

    else:
        return None


def my_matchup_command(scoreboard, user_name):
    user_team = map_user_to_team(user_name.title())
    home_or_away, user_matchup = get_user_matchup(scoreboard, user_team)

    if user_matchup:
        response = "{home_team} *{home_score}*\n{away_team} *{away_score}*".format(
            home_team=user_matchup.home_team.team_name.strip(),
            home_score=user_matchup.home_score,
            away_team=user_matchup.away_team.team_name.strip(),
            away_score=user_matchup.away_score)
    else:
        response = "Hmm, I couldn't find your matchup this week :thinking_face:"

    return response


def loser_command(scoreboard):
    loser, score = get_winner_or_loser(scoreboard, 'loser')
    response = "{owner} is currently the overall loser with {score} points - Sad!".format(owner=loser, score=score)
    return response


def winner_command(scoreboard):
    winner, score = get_winner_or_loser(scoreboard, 'winner')
    response = "{owner} is currently the overall winner with {score} points - Swag!".format(owner=winner, score=score)
    return response


def scoreboard_command(scoreboard):
    data = output_scoreboard(scoreboard)

    # data = {
    #     'home_team_1': matchup_1.home_team.team_name,
    #     'home_score_1': matchup_1.home_score,
    #     'away_team_1': matchup_1.away_team.team_nam,
    #     'away_score_1': matchup_1.away_score,
    #     ...
    # }

    # Slack was adding a bunch of white space when I tried using triple quotes on this multi-line string
    response = ("{home_team_1} *{home_score_1}*\n{away_team_1} *{away_score_1}*\n\n"
                "{home_team_2} *{home_score_2}*\n{away_team_2} *{away_score_2}*\n\n"
                "{home_team_3} *{home_score_3}*\n{away_team_3} *{away_score_3}*\n\n"
                "{home_team_4} *{home_score_4}*\n{away_team_4} *{away_score_4}*\n\n"
                "{home_team_5} *{home_score_5}*\n{away_team_5} *{away_score_5}*\n\n"
                "{home_team_6} *{home_score_6}*\n{away_team_6} *{away_score_6}*\n\n"
                "{home_team_7} *{home_score_7}*\n{away_team_7} *{away_score_7}*\n\n"
                "{home_team_8} *{home_score_8}*\n{away_team_8} *{away_score_8}*").format(**data)

    return response


def main():
    """
    Not pretty but does the stuff.
    """
    # Listen to the Slack output
    rtm_output = sc.rtm_read()
    # Only grab RTM output that is directed at the bot
    bot_output = parse_rtm_output(rtm_output)

    # bot_output is None if there aren't messages directed at the bot
    if bot_output:

        #  Sample bot_output:
        #  {'channel': 'G65LB3LHJ',
        #   'source_team': 'T028G9BR3',
        #   'team': 'T028G9BR3',
        #   'text': "<@U66DH1L87> what's up?",
        #   'ts': '1503871906.000068',
        #   'type': 'message',
        #   'user': 'U1ESNAR42'}

        # Only accept input from known users
        user_name = get_user_name(bot_output)
        is_valid_user = user_validation(user_name)

        if is_valid_user:
            # This is just the message string after '@fantasy_bot' in Slack message
            message = bot_output['text'].split(AT_BOT)[1].strip().lower()

            # Verify that the user sent a valid command to @fantasy_bot
            if is_valid_command(message):

                # @fantasy_bot adds an emoji to Slack message directed at it
                add_reaction(bot_output, 'football')

                # Check to see if the user was inquiring about a specific week of the season
                week = parse_week(message)
                # Week == -1 if the bot didn't understand the user's reference to a week
                if week == -1:
                    response = ("Seems like you're referencing a specific week. I understand `this week` "
                                "and regular season weeks (`week 1`, `week 2`, ... `week 13`). "
                                "Maybe you meant to use one of those?")
                    respond_to_user(bot_output, response)
                    return

                # Get the scoreboard based on user week input
                if week:
                    scoreboard = get_scoreboard(week=week)
                else:
                    scoreboard = get_scoreboard()

                # Get the @fantasy_bot response based on what the user's command was
                if "my matchup" in message:
                    response = my_matchup_command(scoreboard, user_name)

                elif "loser" in message:
                    response = loser_command(scoreboard)

                elif "winner" in message:
                    response = winner_command(scoreboard)

                elif "scoreboard" in message:
                     response = scoreboard_command(scoreboard)

                else:
                    response = "Congrats on breaking the bot, you dog!"

                # Respond to the user based on what their command was
                respond_to_user(bot_output, response)

            # If invalid command in the Slack message, respond to the user letting them know
            else:
                response = "Not sure what you mean. I'm just a bot."
                respond_to_user(bot_output, response)

        # If user is invalid, respond to the user
        else:
            response = "Hey {name}! You're not a user I recognize. Hit up *you're boi* to get credentialed :money_mouth_face:".format(name=user_name.title())
            respond_to_user(bot_output, response)


if __name__ == "__main__":

    read_websocket_delay = 1  # 1 second delay between reading from the Slack RTM firehose

    if sc.rtm_connect():
        print "fantasy_bot connected and running!"

        while True:
            main()
            time.sleep(read_websocket_delay)
    else:
        print "Connection failed. Invalid Slack token or bot ID?"
