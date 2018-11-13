"""Functions for parsing slack user output and making Slack API calls"""

import os


SLACK_API_TOKEN = os.environ.get('SLACK_API_TOKEN')

BOT_ID = os.environ.get('BOT_ID')
AT_BOT = "<@{bot_id}>".format(bot_id=BOT_ID)

# {name: ESPN team_id}
USERS = {
    'Andrew': 1,
    'Brittany': 30,
    'Charlotte': 29,
    'Ellis': 17,
    'Drew': 19,
    'Grant': 7,
    'Keshav': 24,
    'Kyle': 27,
    'Liz': 18,
    'Mike': 11,
    'Niklas': 25,
    'Peter': 5,
    'Regina': 28,
    'Sal': 26,
    'Tiffany': 29
}

VALID_COMMANDS = ['matchup', 'loser', 'winner', 'scoreboard']

BOT_REACTIONS = ['football', 'ellis', 'vikings']


def add_reaction(slack_client, rtm_output, reaction):
    """Add an emoji reaction (as @fantasy_bot) to messages directed at the bot."""
    slack_client.api_call('reactions.add', name=reaction, channel=rtm_output['channel'], timestamp=rtm_output['ts'])


def respond_to_user(slack_client, rtm_output, message):
    """Send a slack message (as @fantasy_bot) to the user in the channel in which they messaged the bot."""
    slack_client.api_call('chat.postMessage', channel=rtm_output['channel'], text=message, as_user=True)


def parse_rtm_output(rtm_output):
    """
    Parse the Slack Real Time Messaging fire hose output for messages directed at @fantasy_bot. Return any such RTM
    output data if it exists.
    """
    if rtm_output:
        for output in rtm_output:
            if 'text' in output and AT_BOT in output['text']:
                return output


def get_user_first_name(slack_client, rtm_output):
    """Get the name of the Slack user who messaged the bot."""
    user_id = rtm_output['user']
    response = slack_client.api_call('users.info', user=user_id)

    if response['ok']:
        return response['user']['profile']['first_name'].title()
    else:
        raise Exception('Slack API call for user name failed')


def validate_user(slack_client, rtm_output, first_name):
    """Check if the user who messaged the bot is a valid user. Return True if so, False otherwise."""
    # If they are not a valid user, repsond to them and return False
    if first_name not in USERS:
        response = ("Hey {name}! You're not a user I recognize. "
                    "Hit up *you're boi* to get credentialed :money_mouth_face:".format(name=first_name))
        respond_to_user(slack_client, rtm_output, response)
        return False
    else:
        return True


def validate_command(slack_client, rtm_output, first_name, message):
    """Check if the user supplied a valid command to the bot. If they did not, respond to them to let them know."""
    if not any(command in message for command in VALID_COMMANDS):
        response = "Not sure what you mean, {name}. I'm just a bot!".format(name=first_name)
        respond_to_user(slack_client, rtm_output, response)
        return False
    else:
        return True


def get_week(message):
    """
    Checks to see if the slack user specified a week of the season in their command (in integer or word form).

    Return (one of):
        * None if no week found
        * -1 if the week was non-sensical (< 1 or > 13)
        * The week number requested.
    """
    if 'week' in message and 'this week' not in message:

        # Get the word/number directly following the word 'week' as a string
        possible_int_as_str = message.split('week')[1].split()[0].strip().lower()

        # First check if there is a week number integer in the string
        week_number = None
        try:
            week_number = int(possible_int_as_str)
        except ValueError:
            print 'Tried to find a week integer and failed.'

            # Next check if there is a week number word in the string
            number_words = {
                'one':1, 'two':2, 'three':3, 'four':4, 'five':5, 'six':6, 'seven':7,
                'eight':8,'nine':9,'ten':10, 'eleven':11,'twelve':12,'thirteen':13
            }

            try:
                week_number = number_words[possible_int_as_str]
            except KeyError:
                print 'Tried to find a week number word and failed.'
                pass

        if week_number is None:
            return
        elif week_number < 1 or week_number > 13:  # If it's a nonsensical week number, return -1
            return -1
        else:
            return week_number


def nonsense_week_reponse(slack_client, rtm_output, first_name):
    response = ("Hey, {name} - seems like you're trying to reference a specific week. "
                "I can only handle the regular season! (weeks 1 - 13)".format(name=first_name))
    respond_to_user(slack_client, rtm_output, response)


def get_command(message):
    # Find the first valid command keyword issued to the bot
    words = message.split()
    for word in words:
        if word.lower() in VALID_COMMANDS:
            return word.lower()


def check_specific_user(message, inquiring_user, keyword):
    # Get the name of the user right before the keyword (e.g. 'matchup')
    words = message.split()
    keyword_index = words.index(keyword)  # find the keyword index in the list of words

    # See if the word immediately preceding the keyword is one of the users.
    # If not, return the name of the inquiring user
    potential_user = words[keyword_index - 1].title()

    # We've stripped out apostrophes, so `Tiffanys` needs to evaluate to `Tiffany`
    if potential_user in USERS:
        return potential_user
    elif potential_user.rstrip('s') in USERS:
        return potential_user.rstrip('s')
    else:
        return inquiring_user
