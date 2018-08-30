import os
import random
import time
from pprint import pprint

from slackclient import SlackClient

import slack as sl
from espn import get_league


def listen():
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

        # Grab the message string directed at '@fantasy_bot', removing the @ mention
        message = bot_output['text'].replace(sl.AT_BOT, '').strip().lower()

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

        if command == 'matchup':
            whose_matchup = sl.check_specific_user(message, 'matchup')

            # At this point, whose matchup is either a VALID_USER first name or None (in which case ues user_first_name)


if __name__ == "__main__":

    sc = SlackClient(sl.SLACK_API_TOKEN)

    read_websocket_delay = 1  # 1 second delay between reading from the Slack RTM firehose

    if sc.rtm_connect():
        print "Fantasy Bot connected and running!"

        while True:
            listen()
            time.sleep(read_websocket_delay)
    else:
        print "Connection failed. Invalid Slack token or Bot ID?"
