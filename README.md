# Countdown Bot

A discord bot to count down in numeric emojis.

<img src="https://raw.githubusercontent.com/seanbreckenridge/discord-countdown-bot/master/screencaps/count.png" alt="botscreencap" width=275>

### Installation

Required Permissions:

- Send Messages
- Manage Roles

To add it to a server, use `https://discordapp.com/oauth2/authorize?&client_id=YOUR_CLIENT_ID_HERE&scope=bot&permissions=268437568`, replacing `YOUR_CLIENT_ID_HERE`. See [here](https://github.com/reactiflux/discord-irc/wiki/Creating-a-discord-bot-&-getting-a-token) for a tutorial on creating a discord bot account.

This uses [`pipenv`](https://github.com/pypa/pipenv) to manage the environment. To install:

```
git clone https://github.com/seanbreckenridge/discord-countdown-bot
cd discord-countdown-bot
pipenv install
```

If you're not on python 3.6 or above, use [`pyenv`](https://github.com/pyenv/pyenv) to install another version of python:

```
pyenv install 3.6.8
pipenv --python ~/.pyenv/versions/3.6.8/bin/python3.6
pipenv install
```

To enter the virtual environment, use `pipenv shell`.

_Token_ should be stored in a file named `token.yaml` in the root directory. See [`token.yaml.dist`](./token.yaml.dist) as an example.

### Usage:

`python3 bot.py` to run the bot.

You can overwrite the `COUNTDOWN_MIN`/`COUNTDOWN_MAX` (the minimum and maximum one can call countdowns for) by providing alternatives as environment variables:

```
COUNTDOWN_MAX=20 COUNTDOWN_MIN=5 python3 bot.py
COUNTDOWN_MAX=10 python3 bot.py
```

`@countdown help` for:

<img src="https://raw.githubusercontent.com/seanbreckenridge/discord-countdown-bot/master/screencaps/help.png" alt="botscreencaphelp" width=500>
