fantasy_bot V2
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
# Slack variables
export SLACK_API_TOKEN=<token_string>
export BOT_ID=<id_string>

# ESPN variables
export LEAGUE_ID=<id_int>
export LEAGUE_YEAR=<year_int>
export ESPN_USERNAME=<username_string>
export ESPN_PASSWORD=<password_string>
```

Running the bot
---------------
```
python run_bot.py
```
