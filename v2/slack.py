"""Functions for parsing slack user output and making Slack API calls"""

import os

from pprint import pprint


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
    # 'Charlotte',  # Not playing this year
    'Ellis',
    'Drew',
    # 'Eunji',  # Not playing this year
    'Grant',
    'Keshav',
    'Kyle',
    'Liz',
    'Mike',
    'Nik',
    # 'katherine',  # Not playing this year
    # 'hunter',  # Not playing this year
    'Peter',
    'Regina',
    'Sal',
    'Tiffany'
    # 'Vishal'  # Not playing this year
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


def get_user_name(slack_client, bot_output):
    """Get the name of the Slack user who messaged the bot."""
    user_id = bot_output['user']
    response = slack_client.api_call('users.info', user=user_id)

    if response['ok']:
        return response['user']['profile']['first_name'].title()
    else:
        raise Exception('Slack API call for user name failed')


def is_valid_user(slack_client, bot_output):
    """Check if the user who messaged the bot is a valid user. If they are not, respond to let them know."""
    user_name = get_user_name(slack_client, bot_output)

    if user_name not in USERS:
        response = ("Hey {name}! You're not a user I recognize. " 
                    "Hit up *you're boi* to get credentialed :money_mouth_face:".format(name=user_name))
        respond_to_user(slack_client, bot_output, response)
        return False
    else:
        return True


def is_valid_command(slack_client, bot_output, message):
    """Check if the user supplied a valid command to the bot. If they did not, respond to them to let them know."""
    if not any(command in message for command in VALID_COMMANDS):
        user_name = get_user_name(slack_client, bot_output)
        response = "Not sure what you mean, {name}. I'm just a bot!".format(name=user_name)
        respond_to_user(slack_client, bot_output, response)
        return False
    else:
        return True
