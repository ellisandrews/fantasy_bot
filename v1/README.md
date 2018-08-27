fantasy_bot V1
===========
ESPN Fantasy Football Slack Bot

Setup
---------------
Intall the requirements
```
pip install -r requirements.txt
```

Set up the following environment variables:
```
export SLACK_API_TOKEN=<slack_api_token>
export BOT_ID=<slackbot_id>
export LEAGUE_ID=<espn_league_id>
export ESPN_S2=<espn_s2> (from browser cookies, to access private league)
export SWID=<espn_swid> (from browser cookies, to access private leauge)
```

Running the bot
---------------
```
python fantasy_bot.py
```

Note:
-----
As of 9/28/17 the `espnff` package upon which this bot is built has not released an update for accessing private leagues. To work around this issue, I updated the source code for that package according to [this PR](https://github.com/rbarton65/espnff/pull/29).
