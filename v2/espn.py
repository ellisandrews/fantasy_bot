import os

from espnff.client import ESPNFF
from espnff.exception import AuthorizationError


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
