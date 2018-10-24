# Countdown Bot

A simple bot that counts down in numeric emojis.

<img src="https://raw.githubusercontent.com/seanbrecke/discord-countdown-bot/master/screencaps/count.png" alt="botscreencap" width=275>

### Requirements:

Tested in `python 3.5.3` and `3.6.4`.

Requires `pip3 install --user discord pyyaml asyncio`

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

### Options

This bot requires very basic permissions when creating an bot account. Read Text/See Voice Channels, Send Messages, and maybe Embed Links, Attach Files, and Add Reactions for possible future updates.

_Token_ should be stored in a file named `.token` in the root directory.

Min and Max for countdown values can be edited in `config.yaml`: `countdown_min` and `countdown_max`.
