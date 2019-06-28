import os
import logging
import time
import random
import traceback

import yaml

from discord import Client
from asyncio import sleep
from discord.ext import commands

logging.basicConfig(level=logging.INFO)

root_dir = os.path.dirname(os.path.realpath(__file__)) # get directory of bot.py
token_file = os.path.join(root_dir, 'token.yaml')

COUNTDOWN_MIN = 3
COUNTDOWN_MAX = 22

# numbers to print countdown with
num_emoji = [":zero:", ":one:", ":two:", ":three:", ":four:",
                ":five:", ":six:", ":seven:", ":eight:", ":nine:", ":ten:"]

# messages to print when the countdown is over
go_messages = [":regional_indicator_g: :regional_indicator_o: :exclamation:",
                    ":space_invader:", ":crossed_swords:", ":movie_camera:"]


#  start bot
bot = commands.Bot(command_prefix=commands.when_mentioned, pm_help=None,
                        case_insensitive=False)
bot.remove_command('help') # remove default help
bot_name = None


def explode(ctx):
    """Returns useful information from a context"""
    # server, channel, author, message_text = explode(ctx)
    return ctx.message.server, ctx.message.channel, ctx.message.author, ctx.message.content


async def say(ctx, message):
    await ctx.message.channel.send(message)


def emoji_countdown_list(count_from, num_emoji):
    """Returns a countdown list in emoji form to be printed for short countdowns."""
    output_emoji_list = []
    for num in range(count_from, 0, -1):
        s = ""
        for n in map(int, list(str(num))):
            s += num_emoji[n]
            s += " "
        output_emoji_list.append(s)
    output_emoji_list.append(random.choice(go_messages))
    return output_emoji_list


@bot.event
async def on_ready():
    # TODO: load in custom go_messages
    global bot_name
    bot_name = bot.user.name
    print("Ready!")


@bot.command(pass_context=True)
async def start(ctx, *count_from):
    """Starts a countdown from the entered number, assuming you have the counter role"""
    await do_start(ctx, *count_from)


async def do_start(ctx, *count_from):
    """Counts; function that is called when 'start' is called; to make error handling easier."""

    # TODO: check if this user is allowed

    if len(count_from) == 0:
        count_from = 10 # default time of 10
    else:
        count_from = count_from[0] # else use arg
    try:
        num = int(count_from)
    except:
        await say(ctx, "Couldn't interpret `{}` as a number...".format(count_from))
        return
    if num > COUNTDOWN_MAX:
        await say(ctx, "{} is too damn high. {} is the maximum.".format(num, COUNTDOWN_MAX))
        return
    elif num < COUNTDOWN_MIN:
        await say(ctx, "{} is too damn low. {} is the minimum.".format(num, COUNTDOWN_MIN))
        return
    else:
        await count(num, ctx.message.author.id, ctx)


async def count(num, uid, ctx):
    """Countdown; print messages to the channel while command isn't stopped/halted"""
    # track how long to sleep depending on current API latency
    send_at = time.time() + 1
    for i, countdown_message in zip(range(num, -1, -1), emoji_countdown_list(num, num_emoji)):
        if True:
            # the 0.2 is a guess; for some reason the last message always seems to get delayed
            # it may just be an artifact of the API status right now, but leaving this here incase
            # its a predictable delay
            #sleep_for = send_at - time.time() if i != 0 else 0
            #print(i, sleep_for, "printing", countdown_message)
            sleep_for = send_at - time.time()
            await sleep(sleep_for)
            send_at = time.time() + 1
            await say(ctx, countdown_message)
        else:
            return


async def exec():
    print(exec(input()))


@bot.command(pass_context=True)
async def help(ctx):
    await say(ctx, "placeholder help message. use a embed here")


# @bot.command(pass_context=True)
# @bot.event
# async def on_command_error(error, ctx):
#     """Prints errors if it's allowed; parses through errors to start/stop if possible."""
#     raise error

with open(token_file) as token_f: # get token from file
    token = yaml.load(token_f, Loader=yaml.FullLoader)["token"]

bot.run(token)
