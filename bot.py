import os
import re
import logging
import time
import random
from datetime import datetime
from typing import Dict

import pickledb
import yaml

from discord import Embed, Intents
from asyncio import sleep
from discord.ext import commands

class ChannelBlacklist:
    """Keeps track of which channels currently have countdowns.
    Channels should be removed from the dict once countdowns are finished,
    though API connection issues may prevent that, so they are automatically removed
    after the length of the countdown has elapsed * multiplication_factor
    """
    def __init__(self, logger, multiplication_factor):
        self.channels = {} # contains currently blacklisted channels and unix time at which they should be removed
        self.multiplication_factor = multiplication_factor
        self.logger = logger


    def _remove_hanging_countdowns(self):
        """Removes any countdowns whose end time is in the past"""
        cur_time = time.time()
        for channel_id in list(self.channels):
            print("time_at_next_countdown: ", self.channels[channel_id])
            print("cur_time", cur_time)
            if self.channels[channel_id] < cur_time:
                self.logger.info(f"Removed hanging countdown for channel id {channel_id}")
                del self.channels[channel_id]


    def start(self, channel_id:int, countdown_time:int):
        self._remove_hanging_countdowns()
        if channel_id not in self.channels: # if there is no countdown
            self.channels[channel_id] = int(time.time()) + (countdown_time * self.multiplication_factor)
            self.logger.info(f"Started countdown in {channel_id} for {countdown_time} ({countdown_time * self.multiplication_factor} till next countdown)")
        else:
            time_left = self.channels[channel_id] - int(time.time())
            self.logger.info(f"Forbidden start: cant start another countdown in {channel_id} for another {time_left} seconds.")
            raise RuntimeError(time_left) # how long ago in seconds the countdown started


    def stop(self, channel_id: int):
        if channel_id in self.channels:
            self.logger.info(f"Removing countdown in {channel_id}")
            del self.channels[channel_id]
        self._remove_hanging_countdowns()


# discord logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(message)s')
log = logging.getLogger(__name__)

# absolute filepaths
root_dir: str = os.path.dirname(os.path.realpath(__file__)) # get directory of bot.py
token_file: str = os.path.join(root_dir, 'token.yaml')
server_file: str = os.path.join(root_dir, 'server.db')
server_db = pickledb.load(server_file, auto_dump=True)


# default if environment variable is not present
COUNTDOWN_MIN = 3 if "COUNTDOWN_MIN" not in os.environ else int(os.environ["COUNTDOWN_MIN"])
COUNTDOWN_MAX = 15 if "COUNTDOWN_MAX" not in os.environ else int(os.environ["COUNTDOWN_MAX"])

# numbers to print countdown with
num_emoji = [":zero:", ":one:", ":two:", ":three:", ":four:",
                ":five:", ":six:", ":seven:", ":eight:", ":nine:", ":ten:"]

# default messages to print when the countdown is over
go_messages = [":regional_indicator_g: :regional_indicator_o: :exclamation:",
                    ":space_invader:", ":crossed_swords:", ":movie_camera:"]

# short countdown channel blacklist
short_blacklist: ChannelBlacklist = ChannelBlacklist(logger=log, multiplication_factor=2)
# e.g. if you start a countdown of length 10, you have to either wait till it
# finishes or 10 * 2 seconds before starting a new one

# in memory cache of when 'go' was last run in a channel. Used to facilitate
# @countdown time command
last_run_at: Dict[int, datetime] = {}

#  start bot
bot = commands.Bot(command_prefix=commands.when_mentioned, pm_help=None,
                        case_insensitive=False, intents=Intents.default())
bot.remove_command('help') # remove default help


def int_parsable(n):
    try:
        int(n)
        return True
    except ValueError:
        return False


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


def parse_countdown_start(arg_array): # throws ValueError
    """Parses the string for starting a countdown. Returns a list with length[, reaction_count]"""

    if len(arg_array) == 0:
        return [10]

    args = re.sub("\s", "", "".join(arg_array)) # join and remove whitespace
    # reaction-type
    if "," in args:
        time, _, reaction_count = args.partition(",")
        return [int(time), int(reaction_count)]
    else:
        return [int(args)]


def has_admin_privilege():
    """Check that returns true if the user can change role/bypass configuration"""
    async def predicate(ctx):
        return await (bot.is_owner(ctx.author) or \
               ctx.author.permissions_in(ctx.channel).administrator)
    return commands.check(predicate)


def can_countdown(ctx):
    """Returns a error message if user can't countdown; 'True' if everything is valid"""

    # check if mode is set on this server
    server_mode = server_db.get(f"{ctx.guild.id}mode")
    if server_mode == False:
        return f"The bot hasn't been setup properly. Run \"{bot.user.mention} help\" for more information"
    else:
        # mode exists, check if user has '#'
        if server_mode == "#":
            if '#' not in [r.name for r in ctx.guild.roles]:
                return f"The `#` role doesn't exist. Run \"{bot.user.mention} role\" to create it, or \"{bot.user.mention} bypass\" to allow everyone on the server to use the bot."
            else:
                if '#' not in [r.name for r in ctx.author.roles]:
                    return "You are not allowed to run this command."
                else:
                    return True
        # if everyone is allowed to use the bot on this server
        elif server_mode == "!":
            return True
        #
        else:
            return 'Unrecognized permissions. Ask an admin to run "{m} role" or "{m} bypass" to fix permissions.'.format(m=bot.user.mention)

@bot.event
async def on_ready():
    print("Ready!")


@bot.event
async def on_message(message):
    # replace multiple spaces between one to allow commands to be triggered
    # ordinarily, if multiple spaces are present after the mention, commands dont trigger
    message.content = re.sub("\s{2,}", " ", message.content)
    await bot.process_commands(message)

@bot.command()
async def start(ctx, *count_from):
    """Does a short countdown, requires the '#' role, which can be created with role"""
    resp = can_countdown(ctx)
    if not isinstance(resp, bool):
        return await ctx.channel.send(f"Error: {resp}")
    try:
        parsed = parse_countdown_start(count_from)
    except ValueError as ve:
        return await ctx.channel.send("Could not convert {} to a number.".format(re.sub("[@`\s]", "", str(ve).replace("invalid literal for int() with base 10: ", "")[1:-1])))
    if parsed[0] > COUNTDOWN_MAX:
        return await ctx.channel.send("{} is too damn high. {} is the maximum.".format(parsed[0], COUNTDOWN_MAX))
    elif parsed[0] < COUNTDOWN_MIN:
        return await ctx.channel.send("{} is too damn low. {} is the minimum.".format(parsed[0], COUNTDOWN_MIN))
    if len(parsed) == 1: # countdown starts now
        try:
            short_blacklist.start(ctx.channel.id, parsed[0])
        except RuntimeError as time_left:
            return await ctx.channel.send("Can't start another countdown in this channel for {}s ".format(time_left))
        await count(parsed[0], ctx)
        return short_blacklist.stop(ctx.channel.id)
    else: # wait for reactions
        return await ctx.channel.send("This feature hasn't been added yet.")


async def count(num, ctx):
    """Countdown; print messages to the channel while command isn't stopped/halted"""
    # track how long to sleep depending on current API latency
    send_at = time.time() + 1
    for i, countdown_message in zip(range(num, -1, -1), emoji_countdown_list(num, num_emoji)):
        if ctx.channel.id in short_blacklist.channels:
            # the 0.2 is a guess; for some reason the last message always seems to get delayed
            # it may just be an artifact of the API status right now, but leaving this here incase
            # its a predictable delay
            #sleep_for = send_at - time.time() if i != 0 else 0
            #print(i, sleep_for, "printing", countdown_message)
            sleep_for = send_at - time.time()
            await sleep(sleep_for)
            send_at = time.time() + 1
            await ctx.channel.send(countdown_message)
            # save when the go message was sent
            last_run_at[ctx.channel.id] = datetime.now()
        else:
            return


@bot.command()
async def stop(ctx):
    """Stops a short countdown in the channel"""
    resp = can_countdown(ctx)
    if not isinstance(resp, bool):
        return await ctx.channel.send(f"Error: {resp}")
    if ctx.channel.id in short_blacklist.channels: # if countdown in channel
        short_blacklist.stop(ctx.channel.id)
        log.info(f"{ctx.author} stopped countdown in {ctx.channel.id}")
    else:
        return await ctx.channel.send("Theres no countdown in this channel to stop.")

# helper for formatting into HH:MM:SS
def pad(i):
    return str(i).zfill(2)

def format_duration(seconds: int):
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    return ":".join(map(pad, (hours, minutes, seconds,)))

@bot.command(name="time")
async def time_cmd(ctx):
    """Prints how long its been since a 'go message' was sent in this chanel"""
    if ctx.channel.id in last_run_at:
        last_run: datetime = last_run_at[ctx.channel.id]
        message = None
        message_content: str = ""
        # align with a full second
        await sleep(1 - datetime.now().timestamp() % 1)
        for i in range(15):
            now: datetime = datetime.now()
            seconds_since_countdown: int = round((now - last_run).total_seconds())
            message_content = f"It's been {format_duration(seconds_since_countdown)} since the countdown ended"
            if message is None:
                message = await ctx.channel.send(message_content)
            else:
                await message.edit(content=message_content)
            # align with a full second
            await sleep(2 - datetime.now().timestamp() % 1)
        await message.edit(content=f"~~{message_content}~~")
    else:
        return await ctx.channel.send("Couldn't find when a countdown was last run in this channel...")

@bot.command()
@has_admin_privilege()
async def role(ctx):
    """Creates the '#' role, gives it to the caller"""
    # check if mode is being swapped from bypass
    if server_db.get(f"{ctx.guild.id}mode") == "!":
        await ctx.channel.send("Removed bypass. The bot now requires a user to have the `#` role to use.")
    server_db.set(f"{ctx.guild.id}mode", "#")
    if '#' in [r.name for r in ctx.guild.roles]:
        return await ctx.channel.send("The `#` role aleady exists. Anyone who has it can start/stop countdowns.")
    else:
        # check if bot has permissions to create roles
        if ctx.me.permissions_in(ctx.channel).manage_roles:
            new_role = await ctx.guild.create_role(name="#")
            await ctx.author.add_roles(new_role)
            return await ctx.channel.send("Created the role `#` and gave it to you. Giving the `#` role to a user will allow them to start/stop countdowns. If you want everyone on the server to be able to use {m}, you can run \"{m} bypass\"".format(m=bot.user.mention))
        else:
            return await ctx.channel.send("Insufficient permissions to create the role. Create a role named `#`; any user with that role can start/stop countdowns.")


@bot.command()
@has_admin_privilege()
async def bypass(ctx):
    """Allows everyone on this server to use the bot"""
    if server_db.get(f"{ctx.guild.id}mode") == "!":
        return await ctx.channel.send(f"Everyone on this server can already use {bot.user.mention}.")
    else:
        server_db.set(f"{ctx.guild.id}mode", "!")
        return await ctx.channel.send(f"Bypassed successfully. Anyone on the server can start/stop countdowns. If you wish to limit the use of the bot, run \"{bot.user.mention} role\"")


@bot.command()
@has_admin_privilege()
async def status(ctx):
    """Prints the current mode to the user"""
    if server_db.get(f"{ctx.guild.id}mode") == "!":
        return await ctx.channel.send("The bot is currently set to 'bypass' mode. Anyone on the server can use the bot.")
    elif server_db.get(f"{ctx.guild.id}mode") == "#":
        return await ctx.channel.send("The bot is currently set to 'role' mode. Anyone with the `#` role can use the bot.")
    else:
        return await ctx.channel.send(f"The bot hasn't been setup properly. Run \"{bot.user.mention} help\" for more information")


@bot.event
async def on_command_error(ctx, error):

    if isinstance(error, commands.CommandNotFound):

        # get message text
        message_parts = ctx.message.content.casefold().split()
        # if this started with a number
        try:
            parse_countdown_start(message_parts[1:])
        except ValueError as ve:
            log.info("Unknown command called: {}".format(message_parts))
            return await ctx.channel.send(f"That command doesn't exist. Run \"{bot.user.mention} help\" for a list.")

        # if message parsed as countdown start successfully
        message_parts.insert(1, "start")
        ctx.message.content = " ".join(message_parts)
        log.info("Invoking start from on_command_error with {} {}".format(message_parts, error))
        await bot.process_commands(ctx.message)

    elif isinstance(error, commands.CheckFailure):
        if ctx.command.name in ["role", "bypass", "status"]:
            return await ctx.channel.send("You are not allowed to run this command.")

    else:
        raise error


@bot.command()
async def help(ctx):
    embed=Embed(title="Countdown Help", color=0x4eb1ff)
    embed.add_field(name="Basic Commands", value='\u200b', inline=False)
    embed.add_field(name=f"@{ctx.guild.me.display_name} <n>", value="Start a countdown with length 'n'", inline=False)
    embed.add_field(name=f"@{ctx.guild.me.display_name} stop", value="Stops the countdown in the current channel", inline=False)
    embed.add_field(name=f"@{ctx.guild.me.display_name} time", value="Amount of time since a countdown was run in this channel", inline=False)
    embed.add_field(name="Configuration Commands (requires admin)", value='\u200b', inline=False)
    embed.add_field(name=f"@{ctx.guild.me.display_name} status", value="Prints the current configuration status", inline=False)
    embed.add_field(name=f"@{ctx.guild.me.display_name} role", value="Limits the bot usage to anyone with the `#` role.", inline=False)
    embed.add_field(name=f"@{ctx.guild.me.display_name} bypass", value="Allows everyone to use the bot", inline=False)
    await ctx.channel.send(embed=embed)


with open(token_file) as token_f: # get token from file
    token = yaml.load(token_f, Loader=yaml.FullLoader)["token"]

bot.run(token, reconnect=True)
