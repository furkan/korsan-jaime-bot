# korsan-jaime-bot

This telegram bot's purpose is to keep track of payments and debts among 3 housemates.

## Usage

Follow the procedures to install the bot, then type `/help`.

## Requirements

`pip3 install -r requirements.txt`

## Additional Files

There must be two additional files in the same folder with `kjbot.py`:

`balance.txt` and `config.py`

### Structure of balance.txt

Just one line will suffice:

`0,0,0,`

The bot will change the numbers to what they must be as payments take place.

### Structure of config.py

```python
chat_id = 123456789

user1_id = "123456789"
user2_id = "123456788"
user3_id = "123456787"

user1_name = "furkan"
user2_name = "albert"
user3_name = "nikola"

# '/paid 100 fa' works the same as '/paid 100 furkan'
user1_nicknames = ['furkan', 'aldemir', 'fa', 'f']
user2_nicknames = ['albert', 'einstein', 'ae', 'e']
user3_nicknames = ['nikola', 'tesla', 'nt', 'n', 't']

token = "OBTAINED_FROM_BOTFATHER"

SECRET = 'TOTALLY_MADE_UP_FOR_FLASK_WEBHOOKS'

URL = 'WHEREVER_THE_BOT_IS_HOSTED'

```

#### Obtaining user_id

[userinfobot](https://telegram.me/userinfobot)

#### Obtaining chat_id of the group

Add this bot to your group: [Chat ID Echo](https://telegram.me/chatid_echo_bot)

#### Obtaining token

[BotFather](https://telegram.me/botfather)

## Running the bot

From the console: `python3 main.py`

As a docker compose service: `docker compose up -d`
