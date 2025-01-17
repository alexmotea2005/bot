# Copyright (C) 2025 Motea Catalin
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#!./.venv/bin/python

import discord      # base discord module
import code         # code.interact
import os           # environment variables
import inspect      # call stack inspection
import random       # dumb random number generator
import argparse     # command-line argument parser

from discord.ext import commands  # Bot class and utils

################################################################################
############################### HELPER FUNCTIONS ###############################
################################################################################

# log_msg - fancy print
#   @msg   : string to print
#   @level : log level from {'debug', 'info', 'warning', 'error'}
def log_msg(msg: str, level: str):
    dsp_sel = {
        'debug': ('\033[34m', '-'),
        'info': ('\033[32m', '*'),
        'warning': ('\033[33m', '?'),
        'error': ('\033[31m', '!'),
    }

    _extra_ansi = {
        'critical': '\033[35m',
        'bold': '\033[1m',
        'unbold': '\033[2m',
        'clear': '\033[0m',
    }

    caller = inspect.stack()[1]

    if level not in dsp_sel:
        print('%s%s[@] %s:%d %sBad log level: "%s"%s' %
              (_extra_ansi['critical'], _extra_ansi['bold'],
               caller.function, caller.lineno,
               _extra_ansi['unbold'], level, _extra_ansi['clear']))
        return

    print('%s%s[%s] %s:%d %s%s%s' %
          (_extra_ansi['bold'], *dsp_sel[level],
           caller.function, caller.lineno,
           _extra_ansi['unbold'], msg, _extra_ansi['clear']))

################################################################################
############################## BOT IMPLEMENTATION ##############################
################################################################################

# Parse command-line arguments
def get_token():
    parser = argparse.ArgumentParser(description="Music Bot - Command-line argument parser")
    parser.add_argument('-t', '--token', type=str, help="Provide the bot token manually")
    args = parser.parse_args()

    token = args.token or os.getenv("BOT_TOKEN")

    if not token:
        log_msg("Error: No token provided! Use -t/--token or set BOT_TOKEN environment variable.", "error")
        exit(1)

    return token


# Bot instantiation
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    log_msg('logged on as <%s>' % bot.user, 'info')

@bot.event
async def on_message(msg):
    if msg.author == bot.user:
        return

    log_msg('message from <%s>: "%s"' % (msg.author, msg.content), 'debug')
    await bot.process_commands(msg)

@bot.command(brief='Generate random number between 1 and <arg>')
async def roll(ctx, max_val: int):
    if max_val < 1:
        raise Exception('argument <max_val> must be at least 1')

    await ctx.send(random.randint(1, max_val))

@bot.command()
async def join(ctx):
    await ctx.author.voice.channel.connect()

@bot.command()
async def leave(ctx):
    await ctx.voice_client.disconnect()

@bot.command()
async def play(ctx):
    source = discord.FFmpegPCMAudio("a.mp3")
    ctx.voice_client.play(source)

@bot.command()
async def stop(ctx):
    await ctx.voice_client.stop()

@roll.error
async def roll_error(ctx, error):
    await ctx.send(str(error))

################################################################################
############################# PROGRAM ENTRY POINT ##############################
################################################################################

if __name__ == '__main__':
    token = get_token()  # Get bot token from CLI args or environment
    bot.run(token)  # Launch bot
 
