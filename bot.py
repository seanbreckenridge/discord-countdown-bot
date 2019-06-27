import os
import re
from time import time
from random import choice

import json
from discord import Client
from asyncio import sleep
from discord.ext import commands

from server import *

def readable_channel_list(server_id, servers):
    """Returns a readable list of channels to be printed for list_channels"""
    channel_names = servers[server_id]
    channel_names = list(map(lambda x: "`{}`".format(x), channel_names))
    if len(channel_names) > 1:
        return ", ".join(channel_names[:-1]) + ", and " + channel_names[-1]
    else:
        return str(channel_names[0])


def emoji_countdown_list(count_from, num_emoji):
    """Returns a countdown list in emoji form."""
    output_emoji_list = []
    for num in range(count_from, 0, -1):
        s = ""
        for n in map(int, list(str(num))):
            s += num_emoji[n]
            s += " "
        output_emoji_list.append(s)
    return output_emoji_list

root_dir = os.path.dirname(os.path.realpath(__file__)) # get directory of bot.py
options_file = os.path.join(root_dir, 'options.json')
server_file = os.path.join(root_dir, 'servers.json')
token_file = os.path.join(root_dir, 'token.json')

__SERVERS = {}

#  load config
with open(options_file) as option_f:
    config = json.load(option_f)

#  start bot
bot = commands.Bot(command_prefix=commands.when_mentioned, pm_help=None,
                        case_insensitive=False)
bot.remove_command('help') # remove default help

# numbers to print countdown with
num_emoji = [":zero:", ":one:", ":two:", ":three:", ":four:",
                ":five:", ":six:", ":seven:", ":eight:", ":nine:", ":ten:"]

# messages to print when the countdown is over
go_messages = [":regional_indicator_g: :regional_indicator_o: :exclamation:", ":man_dancing:",
                    ":space_invader:", ":crossed_swords:", ":movie_camera:"]

def go():
    """returns a random 'go!' message"""
    return choice(go_messages)



@bot.event
async def on_ready():
    for server in bot.guilds:
        __SERVERS[server.id] = Server(server)

    # load server config
    if os.path.exists(server_file):
        with open(server_file) as server_f:
            server_json = json.load(servers)

            __SERVERS
            # TODO: update __SERVERS
            # TODO: use server specific config, allowing more go_messages and configurable limits
    else: # initialize json file

        
        for server in __SERVERS:




    print("Ready!")


@bot.command(pass_context=True)
async def start(ctx, *count_from):
    """Starts a countdown from the entered number. e.g. `@countdown start 10`/`@countdown 10`"""
    await do_start(ctx, *count_from)


async def do_start(ctx, *count_from):
    """Counts; function that is called when 'start' is called.
    To make error handling easier."""

    # check if this channel is allowed

    if len(count_from) == 0:
        count_from = 10 # default time of 10
    else:
        count_from = count_from[0] # else use arg
    try:
        num = int(count_from)
    except:
        await bot.send_message(ctx.message.channel, "Couldn't interpret `{}` as a number...".format(count_from))
        return
    if num > COUNTDOWN_MAX:
        await bot.send_message(ctx.message.channel, "{} is too damn high. {} is the maximum.".format(num, COUNTDOWN_MAX))
        return
    elif num < COUNTDOWN_MIN:
        await bot.send_message(ctx.message.channel, "{} is too damn low. {} is the minimum.".format(num, COUNTDOWN_MIN))
        return
    if check_rate_limit(ctx.message.author.id): # if this user is allowed to countdown
        is_counting = True
        await count(num, ctx.message.author.id, ctx.message.channel)
        is_counting = False
    else:
        await bot.send_message(ctx.message.channel, "Why you need so many counters :thinking:")


async def count(num, uid, channel):
    """Countdown; print messages to the channel while command isn't stopped/halted"""
    global is_counting
    global userid
    userid = uid
    for n in emoji_countdown_list(num, num_emoji):
        await sleep(1)
        if is_counting:
            await bot.send_message(channel, n)
        else:
            return
    await sleep(1)
    await bot.send_message(channel, go())

@bot.command(pass_context=True)
@commands.has_permissions(kick_members=True)
async def blacklist(ctx, channel_name):



async def reset_blacklist():




@bot.command(pass_context=True)
@commands.has_permissions(kick_members=True)
async def list_channels(ctx):
    """Tells you which channels on this server countdowns are allowed in. e.g. `@countdown list_channels`"""
    this_channel = get_channel_name(ctx)
    server_id = get_server_id(ctx)
    if server_id in servers and len(servers[server_id]) > 0:
        await bot.send_message(ctx.message.channel, "I'm allowed to run in {}.".format(readable_channel_list(server_id, servers)))
    else:
        await bot.send_message(ctx.message.channel, "I'm not allowed to run in any channels on {}.".format(ctx.message.server))


@bot.command(pass_context=True)
async def help(ctx):
    await bot.send("placeholder help message. use a embed here")


@bot.command(pass_context=True)
@bot.event
async def on_command_error(error, ctx):
    """Prints errors if it's allowed; parses through errors to start/stop if possible."""
    if check_if_allowed_channel(ctx, servers):
        message = ctx.message.content.split(">", maxsplit=1)[1]
        lowered = message.lower().strip()
        message_parts = re.split("\s+", lowered)
        if message_parts[0] == 'start':
            if len(message_parts) < 2: # if no number was provided
                await do_start(ctx, 10)
                return
            else:
                await do_start(ctx, message_parts[1])
                return
        elif message_parts[0] == 'stop':
            if ctx.message.author.id == userid:
                await stop_counting()
                return
        else: # check is user tried to start a countdown without 'start'.
            try:
                await do_start(ctx, int(message_parts[0]))
                return
            except:
                await bot.send_message(ctx.message.channel, "Not sure what you mean by '{}'.".format(message.strip()))
    else:
        print("Not allowed to print errors in {}: {}".format(str(ctx.message.channel), str(error)))

@bot.command(pass_context=True)
async def test(ctx):
    pass

token = None
with open(os.path.join(root_dir, 'token.json')) as token_file: # get token from file
    token = json.load(token_file)["token"]

bot.run(token)
