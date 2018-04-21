from discord import Client
from asyncio import sleep
from discord.ext import commands
import os
import re
from time import time
from random import choice
from json import loads
from helper_functions import *

is_counting = False # if the bot is currently counting down
userid = None # the id of the user who is currently counting down
rate_limit = {} # stops users from spamming countdowns
servers = {} # permissions for channels in each server
bot_self_name = None # the name of the bot

#  load options
with open('options.json') as options_file:
    options = loads(options_file.read().strip())
#  load token
with open('.token', 'r') as token_file: # get token from file
    token = token_file.readline().rstrip('\n')

#  create folder if it doesn't exist
create_folder(options['server_folder'])

#  populate server/channel permissions
servers = populate_permissions(options['server_folder'])

#  start client
client = commands.Bot(command_prefix=commands.when_mentioned)
client.remove_command('help') # remove default help

#  only allows a user to use the countdown 5 times in a 6 hour time farme
COUNTDOWN_MAX = options['countdown_max']
COUNTDOWN_MIN = options['countdown_min']
X_TIMES = options['x_times']
EVERY_X_HOURS = options['every_x_hours']
EVERY_X_SECONDS = EVERY_X_HOURS * 60 * 60

num_emoji = options['num_emoji'] # list with emoji 0 - 9
go_messages = options['go_messages'] # list with go! messages


def go():
    """returns a random 'go!' message"""
    return choice(go_messages)


def remove_outdated_limits():
    """Remove outdated rate limits on users."""
    now = time()
    for user in rate_limit: # for each user
        rate_limit[user] = [old_time for old_time in rate_limit[user] if int(now - old_time) < EVERY_X_SECONDS]


def check_rate_limit(uid):
    """Check if user is allowed to print a countdown"""
    remove_outdated_limits()
    if uid in rate_limit and len(rate_limit[uid]) >= X_TIMES: # if user is past threshhold
        return False # can't start another timer
    else: # add current time to users' list
        if uid in rate_limit:
            rate_limit[uid].append(time())
        else:
            rate_limit[uid] = [time()]
        return True # approved


@client.event
async def on_ready():
    print("Ready!")


@client.command(pass_context=True)
async def start(ctx, *count_from):
    """Starts a countdown from the entered number. e.g. `@countdown start 10`/`@countdown 10`"""
    await do_start(ctx, *count_from)


async def do_start(ctx, *count_from):
    """Counts; function that is called when 'start' is called.
    To make error handling easier."""
    global is_counting
    this_channel = get_channel_name(ctx)
    server_id = get_server_id(ctx)
    if not check_if_allowed_channel(ctx, servers): # not allowed to print in this channel
        return
    if is_counting: # if already counting somewhere else, don't start
        await client.send_message(ctx.message.channel, "Already counting somewhere else... ")
        return
    if len(count_from) == 0:
        count_from = 10 # default time of 10
    else:
        count_from = count_from[0] # else use arg
    try:
        num = int(count_from)
    except:
        await client.send_message(ctx.message.channel, "Couldn't interpret `{}` as a number...".format(count_from))
        return
    if num > COUNTDOWN_MAX:
        await client.send_message(ctx.message.channel, "{} is too damn high. {} is the maximum.".format(num, COUNTDOWN_MAX))
        return
    elif num < COUNTDOWN_MIN:
        await client.send_message(ctx.message.channel, "{} is too damn low. {} is the minimum.".format(num, COUNTDOWN_MIN))
        return
    if check_rate_limit(ctx.message.author.id): # if this user is allowed to countdown
        is_counting = True
        await count(num, ctx.message.author.id, ctx.message.channel)
        is_counting = False
    else:
        await client.send_message(ctx.message.channel, "Why you need so many counters :thinking:")



async def count(num, uid, channel):
    """Countdown; print messages to the channel while command isn't stopped/halted"""
    global is_counting
    global userid
    userid = uid
    for n in emoji_countdown_list(num, num_emoji):
        await sleep(1)
        if is_counting:
            await client.send_message(channel, n)
        else:
            return
    await sleep(1)
    await client.send_message(channel, go())

async def stop_counting():
    """Stops the countdown."""
    global is_counting
    is_counting = False


@client.command(pass_context=True)
async def stop(ctx):
    """Stops the countdown. This can only be done if you started the countdown. e.g. `@countdown stop`"""
    if ctx.message.author.id == userid: # if user which called stop is the one who started the current countdown
        stop_counting()


@client.command()
@commands.has_permissions(kick_members=True)
async def halt():
    """Stops the countdown disregarding who started it. e.g. `@countdown halt`"""
    await stop_counting()


@client.command(pass_context=True)
@commands.has_permissions(kick_members=True)
async def allow(ctx, channel_name):
    """Allows countdowns in a channel. e.g. `@countdown allow general`"""
    this_channel = get_channel_name(ctx)
    server_id = get_server_id(ctx)
    if server_id not in servers: # if server is not known
        open(os.path.join(options['server_folder'], server_id), 'a').close() # create file
        servers[server_id] = []
    if channel_name not in servers[server_id]: # if channel not already allowed
        if channel_name in get_channel_names(ctx): # if this channel exists
            servers[server_id].append(channel_name) # add it to the list
            with open(os.path.join(options['server_folder'], server_id), 'a') as f:
                f.write("{}\n".format(channel_name)) # append it into the file
            await client.send_message(ctx.message.channel, "Successfully added `{}`.".format(channel_name))
        else:
            await client.send_message(ctx.message.channel, "Couldn't find the channel `{}`.".format(channel_name))
    else:
        await client.send_message(ctx.message.channel, "I'm already allowed in {}.".format(channel_name))


@client.command(pass_context=True)
@commands.has_permissions(kick_members=True)
async def disallow(ctx, channel_name):
    """Disallows countdown in a channel. All channels are disallowed by default. e.g. `@countdown disallow general`"""
    this_channel = get_channel_name(ctx)
    server_id = get_server_id(ctx)
    if channel_name not in get_channel_names(ctx): # if that channel doesn't exist
        await client.send_message(ctx.message.channel, "Couldn't find the channel `{}`.".format(channel_name))
        return
    if channel_name in servers[server_id]: # if that channel is allowed
        servers[server_id].remove(channel_name) # remove from list
        #  remove from file
        open(os.path.join(options['server_folder'], server_id), 'a').close() # make sure file exists
        with open(os.path.join(options['server_folder'], server_id), 'r') as f:
            allowed_channels = f.readlines()
        with open(os.path.join(options['server_folder'], server_id), 'w') as f:
            for c in allowed_channels:
                if c != "{}\n".format(channel_name): # remove disallowed channel
                    f.write(c)
        await client.send_message(ctx.message.channel, "Successfully removed `{}`.".format(channel_name))
    else:
        await client.send_message(ctx.message.channel, "I'm already not allowed in `{}`".format(channel_name))


@client.command(pass_context=True)
@commands.has_permissions(kick_members=True)
async def list_channels(ctx):
    """Tells you which channels on this server countdowns are allowed in. e.g. `@countdown list_channels`"""
    this_channel = get_channel_name(ctx)
    server_id = get_server_id(ctx)
    if server_id in servers and len(servers[server_id]) > 0:
        await client.send_message(ctx.message.channel, "I'm allowed to run in {}.".format(readable_channel_list(server_id, servers)))
    else:
        await client.send_message(ctx.message.channel, "I'm not allowed to run in any channels on {}.".format(ctx.message.server))


@client.command(pass_context=True)
@commands.has_permissions(kick_members=True)
async def purge_channel_list(ctx):
    """Purges the list of allowed channels. e.g. `@countdown purge_channel_list`"""
    this_channel = get_channel_name(ctx)
    server_id = get_server_id(ctx)
    if server_id in servers:
        servers[server_id] = [] # clears the list of channels
    open(os.path.join(options['server_folder'], server_id), 'w').close() # deletes file that represents this server
    await client.send_message(ctx.message.channel, "Purged list of allowed channels.")


@client.command(pass_context=True)
@commands.has_permissions(kick_members=True)
async def reset_rate_limits(ctx):
    """Resets rate limits for all users. e.g. `@countdown reset_rate_limits`"""
    global rate_limit
    rate_limit = {}
    await client.send_message(ctx.message.channel, "Reset all limits successfully.")


@client.command(pass_context=True)
async def help(ctx):
    if check_if_allowed_channel(ctx, servers):
        functions = [start, stop]
        moderator_funcs = [allow, disallow, list_channels, purge_channel_list, halt, reset_rate_limits]
        help_text = "**Countdown Commands**\n\n" + "\n\n".join(['`{0}`: {1}'.format(f.name, f.short_doc) for f in functions]) + \
                    "\n\n`help`: Displays this help message. e.g. `@countdown help`" + \
                    "\n\n*Moderator Commands*\n\n" + "\n\n".join(['`{0}`: {1}'.format(f.name, f.short_doc) for f in moderator_funcs]) + \
                    "\nRate is currently {} time(s) every {} hours.".format(X_TIMES, EVERY_X_HOURS)
        await client.send_message(ctx.message.channel, help_text)




@client.command(pass_context=True)
@client.event
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
                await client.send_message(ctx.message.channel, "Not sure what you mean by '{}'.".format(message.strip()))
    else:
        print("Not allowed to print errors in {}: {}".format(str(ctx.message.channel), str(error)))


client.run(token)
