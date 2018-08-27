import os
import random
import time
from pprint import pprint

from slackclient import SlackClient

from espn_fantasy import get_league
from slack import AT_BOT, add_reaction, BOT_REACTIONS, is_valid_command, is_valid_user, parse_rtm_output


SLACK_API_TOKEN = os.environ.get('SLACK_API_TOKEN')


def get_league():
    client = ESPNFF(ESPN_USERNAME, ESPN_PASSWORD)

    try:
        client.authorize()
    except AuthorizationError:
        print 'Failed to authorize.'

    # Use the custom ESPNFF client to fetch the private league (handles 'swid' and 's2' for you)
    return client.get_league(LEAGUE_ID, LEAGUE_YEAR)


def listen():
    rtm_output = sc.rtm_read()  # Listen to the Slack output (empty list if no output)
    bot_output = parse_rtm_output(rtm_output)  # Only grab RTM output that is directed at the bot

    if bot_output:

        # Steps:
        # 1) Make sure it is a valid user trying to speak to the bot, respond otherwise
        # 2) Make sure the user sent a valid command to the bot, respond otherwise
        # 3) Add an emoji reaction to the user's message
        # 4) Check if the user passed a week number to inquire about
        # 5) Respond to the user appropriately based on what they requested

        # Only accept input from known users
        if not is_valid_user(sc, bot_output):
            return

        # Grab the message string directed at '@fantasy_bot', removing the @ mention
        message = bot_output['text'].replace(AT_BOT, '').strip().lower()

        # Make sure the user messaged the bot with a valid command
        if not is_valid_command(sc, bot_output, message):
            return

        # Add an emoji to the Slack message directed at @fantasy_bot
        add_reaction(sc, bot_output, random.choice(BOT_REACTIONS))


if __name__ == "__main__":

    sc = SlackClient(SLACK_API_TOKEN)

    read_websocket_delay = 1  # 1 second delay between reading from the Slack RTM firehose

    if sc.rtm_connect():
        print "Fantasy Bot connected and running!"

        while True:
            listen()
            time.sleep(read_websocket_delay)
    else:
        print "Connection failed. Invalid Slack token or Bot ID?"
