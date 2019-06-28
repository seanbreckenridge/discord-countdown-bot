# Countdown Bot

A simple bot that counts down in numeric emojis.

<img src="https://raw.githubusercontent.com/seanbrecke/discord-countdown-bot/master/screencaps/count.png" alt="botscreencap" width=275>

### Installation

This bot requires very basic permissions when creating an bot account. Just 'Send Messages' is fine, this can be updated later.

If you're not on python 3.6, use [`pyenv`](https://github.com/pyenv/pyenv) to install another version of python:

`pyenv install 3.6.8`
`pipenv --python ~/.pyenv/versions/3.6.8/bin/python3.6`

This uses [`pipenv`](https://github.com/pypa/pipenv) to manage the environment; after:

```
git clone https://github.com/seanbreckenridge/discord-countdown-bot
cd discord-countdown-bot
```

... run `pipenv install` to create the virtual environment, and `pipenv shell` to enter it.

Requirements are listed in the [`Pipfile`](./Pipfile).

_Token_ should be stored in a file named `token.yaml` in the root directory. See token.yaml.dist as an example.

# add env for countdown min max

### Usage:

`python3 bot.py` to start.

Assuming the bot's name is `@countdown`:

__Commands__

`start`: Starts a countdown from the entered number. e.g. `@countdown start 10`

You can also do `@countdown 10`, which implies `@countdown start 10`.

`stop`: Stops the countdown. This can only be done if you started the countdown. e.g. `@countdown stop`

`help`: Displays a help message. e.g. `@countdown help`

__Moderator Commands__

`allow`: Allows countdowns in a channel. e.g. `@countdown allow general`

`disallow`: Disallows countdown in a channel. All channels are disallowed by default. e.g. `@countdown disallow general`

`list_channels`: Tells you which channels on this server countdowns are allowed in. e.g. `@countdown list_channels`

`purge_channel_list`: Purges the list of allowed channels. e.g. `@countdown purge_channel_list`

`halt`: Stops the countdown disregarding who started it. e.g. `@countdown halt`

`reset_rate_limits`: Resets rate limits for all users. e.g. `@countdown reset_rate_limits`

By default, rate (number of times a user can start a countdown) is 5 times every 6 hours.
