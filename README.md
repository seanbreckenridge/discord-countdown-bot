# Countdown Bot

A simple bot that counts down in numeric emojis.

<img src="https://raw.githubusercontent.com/seanbrecke/discord-countdown-bot/master/screencaps/count.png" alt="botscreencap" width=275>

### Requirements:

Tested in `python 3.5.3 and 3.6.4`.

Requires `pip3 install discord`

### Usage:

`python3 bot.py` to start.

Assuming the bot's name is `@countdown`:

__Commands__

`start`: Starts a countdown from the entered numer. e.g. `@countdown start 10`

`stop`: Stops the countdown. This can only be done if you started the countdown. e.g. `@countdown stop`

`help`: Displays this help message. e.g. `@countdown help`

__Moderator Commands__

`allow`: Allows countdowns in a channel. e.g. `@countdown allow general`

`disallow`: Disallows countdown in a channel. All channels are disallowed by default. e.g. `@countdown disallow general`

`list_channels`: Tells you which channels on this server countdowns are allowed in. e.g. `@countdown list_channels`

`purge_channel_list`: Purges the list of allowed channels. e.g. `@countdown purge_channel_list`

`halt`: Stops the countdown disregarding who started it. e.g. `@countdown halt`

`reset_rate_limits`: Resets rate limits for all users. e.g. `@countdown reset_rate_limits`

By default, rate (number of times a user can start a countdown) is 5 times every 6 hours.

### Options

_Client Secret_ should be stored in a file named `.token`.

Min and Max for countdown values can be edited in `options.json`: `countdown_min` and `countdown_max`.
