"""Functions for parsing slack user output and making Slack API calls"""

import os

from pprint import pprint


SLACK_API_TOKEN = os.environ.get('SLACK_API_TOKEN')

BOT_ID = os.environ.get('BOT_ID')
AT_BOT = "<@{bot_id}>".format(bot_id=BOT_ID)

# # Slack 'name' are keys for sure - ESPN first names values? Better way to match?
# USERS = {
#     'asmist': 'andrew',
#     'baverill': 'brittany',
#     'ellis': 'ellis',
#     'dsmith': 'drew',
#     # 'eunji': 'eunji',  # Not playing this year
#     'grant': 'grant',
#     'keshav': 'keshav',
#     'kstanley': 'kyle',
#     'liz': 'liz',
#     'mike': 'M',
#     'nkubasek': 'nik',
#     # 'ksawyer': 'katherine',  # Not playing this year
#     # 'hmoeller': 'hunter',  # Not playing this year
#     'ptracy': 'peter',
#     'regina': 'regina',
#     'slombardo': 'sal',  # Or might be 'slombardo435' for slack name?
#     'tiffany': 'tiffany',
#     # 'vishal': 'vishal',  # Not playing this year
# }

USERS = [
    'Andrew',
    'Brittany',
    'Ellis',
    'Drew',
    'Grant',
    'Keshav',
    'Kyle',
    'Liz',
    'Mike',
    'Nik',
    'Peter',
    'Regina',
    'Sal',
    'Tiffany'
]

VALID_COMMANDS = ['matchup', 'loser', 'winner', 'scoreboard']

BOT_REACTIONS = ['football', 'ellis', 'vikings']


def add_reaction(slack_client, bot_output, reaction):
    """Adds emoji reactions (as @fantasy_bot user) to messages directed at the Slack bot."""
    slack_client.api_call('reactions.add', name=reaction, channel=bot_output['channel'], timestamp=bot_output['ts'])


def respond_to_user(slack_client, rtm_output, message):
    """Send a slack message as the bot to the user in the channel in which they messaged the bot."""
    slack_client.api_call('chat.postMessage', channel=rtm_output['channel'], text=message, as_user=True)


def parse_rtm_output(rtm_output):
    """
    The Slack Real Time Messaging API is an events firehose. This parsing function returns None unless a message is
    directed at the Bot, in which case the RTM output is returned (a list).
    """
    # TODO: If multiple messages directed at the bot in a second, will this only find the first?
    if rtm_output:
        for output in rtm_output:
            if 'text' in output and AT_BOT in output['text']:
                return output


def get_user_first_name(slack_client, bot_output):
    """Get the name of the Slack user who messaged the bot."""
    user_id = bot_output['user']
    response = slack_client.api_call('users.info', user=user_id)

    if response['ok']:
        return response['user']['profile']['first_name'].title()
    else:
        raise Exception('Slack API call for user name failed')


def validate_user(slack_client, bot_output, first_name):
    """Check if the user who messaged the bot is a valid user. Return True if so, False otherwise."""
    # If they are not a valid user, repsond to them and return False
    if first_name not in USERS:
        response = ("Hey {name}! You're not a user I recognize. "
                    "Hit up *you're boi* to get credentialed :money_mouth_face:".format(name=first_name))
        respond_to_user(slack_client, bot_output, response)
        return False
    else:
        return True


def validate_command(slack_client, bot_output, first_name, message):
    """Check if the user supplied a valid command to the bot. If they did not, respond to them to let them know."""
    if not any(command in message for command in VALID_COMMANDS):
        response = "Not sure what you mean, {name}. I'm just a bot!".format(name=first_name)
        respond_to_user(slack_client, bot_output, response)
        return False
    else:
        return True


def get_week(message):
    """
    Checks to see if the slack user specified a week of the season in their command (in integer or word form).

    Return (one of):
        * None if no week found
        * -1 if the week was non-sensical (<= 0 or > 14)
        * The week number requested.
    """
    if 'week' in message and 'this week' not in message:

        # Get the word/number directly following the word 'week' as a string, stripped of bad characters
        possible_int_as_str = message.split('week')[1].split()[0].strip().strip('?').strip('!').lower()

        # First check if there is a week number integer in the string
        week_number = None
        try:
            week_number = int(possible_int_as_str)
        except ValueError:
            print 'Tried to find a week integer and failed.'

            # Next check if there is a week number word in the string
            number_words = {
                'one':1, 'two':2, 'three':3, 'four':4, 'five':5, 'six':6, 'seven':7,
                'eight':8,'nine':9,'ten':10, 'eleven':11,'twelve':12,'thirteen':13,'fourteen':14
            }

            try:
                week_number = number_words[possible_int_as_str]
            except KeyError:
                print 'Tried to find a week number word and failed.'
                pass

        if week_number is None:
            return
        elif week_number <= 0 or week_number > 14:  # If it's a nonsensical week number, return -1
            return -1
        else:
            return week_number


def nonsense_week_reponse(slack_client, bot_output, first_name):
    response = ("Hey, {name} - seems like you're trying to reference a specific week. "
                "I can only handle regular season, weeks 1 - 13!".format(name=first_name))
    respond_to_user(slack_client, bot_output, response)


def get_command(message):
    # Find the first valid command keyword issued to the bot
    words = message.split()
    for word in words:
        if word.lower() in VALID_COMMANDS:
            return word.lower()


def check_specific_user(message, keyword):
    # Get the name of the user right before the keyword (e.g. 'matchup')
    words = message.split()
    keyword_index = words.index(keyword) # find the keyword index in the list of words
    potential_user = words[keyword_index - 1].split("'")[0].title()
    if potential_user in USERS:
        return potential_user

