import random
import time
from string import punctuation

from slackclient import SlackClient

import slack as sl
from espn import get_league, matchup_command, scoreboard_command, winner_loser_command


def handle_command(command, user, week):
    """
    Get the response that @fantasy_bot will send back to the user depending on what they requested.

    Args:
        command (str) - One of the valid commands directed to @fantasy_bot
        user (str) - The name of the user who messaged @fantasy_bot
        week (int/None) - Week number of the season, if a user inquired about a specific week

    Return:
        response (str) - The message text that @fantasy_bot will send back to the user.
    """
    # Fetch ESPN league data
    league = get_league()

    if command == 'matchup':
        response = matchup_command(league, user, week)

    elif command in ('loser', 'winner'):
        response = winner_loser_command(league, week, command)

    elif command == 'scoreboard':
        response = scoreboard_command(league, week)

    else:
        response = "Congrats on finding a hole in You're Boi's logic :awkwardseal: You dog!"

    return response


def listen():
    """
    Parse Slack Real Time Messaging output for messages directed to @fantasy_bot. If such a message exists:
        * Perform the relevant validation
        * Parse the message text for important keywords
        * Respond to the user
    """
    rtm_output = sc.rtm_read()  # Listen to the Slack output (empty list if no output)
    bot_output = sl.parse_rtm_output(rtm_output)  # Only grab RTM output that is directed at the bot

    if bot_output:

        # Steps:
        # 1) Make sure it is a valid user trying to speak to the bot, respond otherwise
        # 2) Make sure the user sent a valid command to the bot, respond otherwise
        # 3) Add an emoji reaction to the user's message
        # 4) Check if the user passed a week number to inquire about
        # 5) Respond to the user appropriately based on what they requested

        # Get the first name of the user who wrote to the bot
        user_first_name = sl.get_user_first_name(sc, bot_output)

        # Only accept input from known users
        if not sl.validate_user(sc, bot_output, user_first_name):
            return

        # Grab the message string directed at '@fantasy_bot', removing the @ mention and unnecessary characters
        message = bot_output['text'].replace(sl.AT_BOT, '').strip().lower()
        message = ''.join(ch for ch in message if ch not in set(punctuation))

        # Make sure the user messaged the bot with a valid command
        if not sl.validate_command(sc, bot_output, user_first_name, message):
            return

        # Add an emoji to the Slack message directed at @fantasy_bot
        sl.add_reaction(sc, bot_output, random.choice(sl.BOT_REACTIONS))

        # See if the user asked about a week (-2 if not, -1 if nonsensical week, or the week number)
        week = sl.get_week(message)
        if week == -1:
            sl.nonsense_week_reponse(sc, bot_output, user_first_name)
            return

        # At this point, week is either None or the integer week number that it is.

        # Identify which command the user sent to the bot (will pick the first one)
        command = sl.get_command(message)

        # Identify if the user was asking about a specific user
        user_referenced = sl.check_specific_user(message, user_first_name, command)

        # At this point, user_referenced is the name of a VALID_USER

        response = handle_command(command, user_referenced, week)

        sl.respond_to_user(sc, bot_output, response)


if __name__ == "__main__":

    sc = SlackClient(sl.SLACK_API_TOKEN)

    read_websocket_delay = 1  # 1 second delay between reading from the Slack RTM firehose

    if sc.rtm_connect():
        print 'Fantasy Bot connected and running!'

        while True:
            listen()
            time.sleep(read_websocket_delay)
    else:
        print 'Connection failed. Invalid Slack token or Bot ID?'
