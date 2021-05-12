import os
import random
import discord
from discord import Embed, Colour
from discord.ext import commands
from discord.ext.commands import Bot

import firebase_admin
from firebase_admin import credentials

from dotenv import load_dotenv

import uwuify
from pydactyl import PterodactylClient

from urllib.request import urlopen
import json

intents = discord.Intents.default()
intents.members = True
intents.presences = True

# Loads env file
load_dotenv()

# Sets variables from env file
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
TENOR_API_KEY = os.getenv('TENOR_API_KEY')
PTERODACTYL_API_KEY = os.getenv('PTERODACTYL_API_KEY')
BOT_PREFIX = ['.']

if not firebase_admin._apps:
    firebaseCred = credentials.Certificate('.\\firebase.json')
    firebase_admin.initialize_app(firebaseCred)

pterodactylAPI = PterodactylClient('https://panel.clumsy.host', PTERODACTYL_API_KEY)

botDescription = 'Best bot that does nothing special.'
helpCommand = commands.DefaultHelpCommand(no_category='Commands', LeaderboardCog='Commands')

# Sets prefix for bot
client = Bot(command_prefix=BOT_PREFIX, intents=intents, help_command=helpCommand, description=botDescription)

initial_extensions = ['cogs.leaderboard']

if __name__ == '__main__':
    for extension in initial_extensions:
        client.load_extension(extension)


# When client comes online
@client.event
async def on_ready():
    # Prints to console that its online
    print(f'{client.user.name} is online!')
    # await client.get_channel(823772094944641046).send('{} is online!'.format(client.user.name))

    # Sets bot status
    game = discord.Game('with PyCharm')
    await client.change_presence(status=discord.Status.online, activity=game)

    for guild in client.guilds:
        message = guild.name
        for channel in guild.text_channels:
            message += ' - ' + channel.name
        print(message)

        if guild.me.guild_permissions.administrator:
            continue
        if not guild.me.guild_permissions.manage_messages:
            print('I need to be able to manage messages in ' + guild.name + ' - ' + str(guild.id))
        if not guild.me.guild_permissions.add_reactions:
            print('I need to be able to add reactions in ' + guild.name + ' - ' + str(guild.id))
        if not guild.me.guild_permissions.read_message_history:
            print('I need to be able to read message history in ' + guild.name + ' - ' + str(guild.id))

    print('done: started')


# EDIT!!! ignore message if in DM for now


# On every message scan it
@client.event
async def on_message(ctx):
    print(f'{ctx.author}: {ctx.content}')

    # Ignore if from bot
    if is_bot(ctx.author):
        return

    if 'pog' in ctx.content.lower():
        emoji = discord.utils.get(ctx.guild.emojis, name="poggers")
        # await message.channel.send(emoji)
        if emoji is not None:
            await ctx.add_reaction(emoji)

    if '<3' in ctx.content.lower():
        await ctx.channel.send('<3')

    if '❤' in ctx.content.lower():
        await ctx.channel.send('<3')

    if 'bad bot' in ctx.content.lower():
        await ctx.channel.send('<3')

    if 'good bot' in ctx.content.lower():
        await ctx.channel.send('good human')

    if 'Toothless!' in ctx.content:
        await ctx.channel.send('{}, hi!'.format(ctx.author.mention))

    # Let other commands work
    await client.process_commands(ctx)


# Purge command
@client.command(name='purge',
                description='Deletes previous X number of messages.',
                brief='Purges the chat',
                pass_context=True)
@commands.has_permissions(manage_messages=True)
async def purge(ctx, numToDelete: int):
    if numToDelete > 100:  # Checks if above max
        await ctx.send("You can't purge more than 100 messages at a time.")
        return

    await ctx.channel.purge(limit=numToDelete + 1)
    await ctx.send('Purged {} messages from the chat.'.format(numToDelete))

    if ctx.channel.guild.me.guild_permissions.manage_messages:
        message = ctx.message
        await message.delete(delay=0.75)  # Deletes original command


# If user does not have admin perms for purge command
@purge.error
async def purgeError(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        if ctx.channel.guild.me.guild_permissions.manage_messages:
            message = ctx.message
            await message.delete(delay=0.75)
        await ctx.send("lol mate what u doin that isn\'t a real command")


@client.command(name='uwu',
                description='uwuify\'s text',
                brief='UwUify\'s text.',
                aliases=['uwuify', 'owoify', 'owo'],
                usage='[message to uwuify]',
                pass_context=True)
async def uwu(ctx, *msg: str):
    if msg == ():
        await ctx.channel.send('You need to add a message to convert.')
        return

    toSend = ''
    for text in msg:
        toSend += str(uwuify.uwu(text)) + ' '
    await ctx.channel.send(toSend)


'''
@client.command(name='avatar',
                aliases=['icon', 'logo'],
                description='Display the image and url of users\' avatar.',
                usage='[tagged users]',
                pass_context=True)
async def avatar(ctx):
    if not ctx.mentions.users.size:
        return ctx.channel.send('Your avatar: {}'.format(ctx.author.avatar_url))

    avatarList = ctx.mentions.users.map(f'{user.username}\'s avatar: {user.avatar_url}', users)

    await ctx.channel.send(list(avatarList))
'''


@client.command(name='ping',
                hidden=True,
                brief='pong',
                pass_context=True)
async def pong(ctx, username=None):
    await ctx.send('pong {}'.format(username))


@client.command(name='say',
                hidden=True,
                pass_context=True)
@commands.has_permissions(administrator=True)
async def speak(ctx, *, text):
    if ctx.channel.guild.me.guild_permissions.manage_messages:
        message = ctx.message
        await message.delete(delay=0.75)
    await ctx.send(f"{text}")


@speak.error
async def speakError(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        if ctx.channel.guild.me.guild_permissions.manage_messages:
            message = ctx.message
            await message.delete(delay=0.75)
        await ctx.send('lol mate what u doin that isn\'t a real command')


# Commands for !david
@client.command(name='david',
                description="It's David time",
                brief="All about David",
                aliases=['david1', 'david2'],
                pass_context=True)
async def david(ctx):
    await ctx.send('david is the best <3\nand so are you {}'.format(ctx.author.mention))


# Commands for !square - square a number
@client.command(name='square',
                description='Squares the input',
                brief='Squares the input',
                pass_context=True)
async def square(ctx, *number: int):
    if number == ():
        await ctx.channel.send('You need to add a message to convert.')
        return

    squared_value = int(number[0]) * int(number[0])
    await ctx.channel.send(str(number[0]) + " squared is " + str(squared_value))


'''
Don't hardcode the message id
'''


@client.event
async def on_raw_reaction_add(payload):
    message_id = payload.message_id

    if message_id == 824142392612487168:
        guild_id = payload.guild_id
        guild = discord.utils.find(lambda g: g.id == guild_id, client.guilds)

        if payload.emoji.name == '👍':
            role = discord.utils.get(guild.roles, name="up")

        elif payload.emoji.name == '👎':
            role = discord.utils.get(guild.roles, name="down")

        elif payload.emoji.name == 'dab':
            role = discord.utils.get(guild.roles, name="dab")

        else:
            role = discord.utils.get(guild.roles, name=payload.emoji.name)

        if role is not None:
            await payload.member.add_roles(role)


@client.event
async def on_raw_reaction_remove(payload):
    message_id = payload.message_id

    if message_id == 824142392612487168:
        guild_id = payload.guild_id
        guild = discord.utils.find(lambda g: g.id == guild_id, client.guilds)
        member = discord.utils.find(lambda m: m.id == payload.user_id, guild.members)

        if payload.emoji.name == '👍':
            role = discord.utils.get(guild.roles, name="up")

        elif payload.emoji.name == '👎':
            role = discord.utils.get(guild.roles, name="down")

        elif payload.emoji.name == 'dab':
            role = discord.utils.get(guild.roles, name="dab")

        else:
            role = discord.utils.get(guild.roles, name=payload.emoji.name)

        if role is not None:
            if member is not None:
                await member.remove_roles(role)


@client.command(name='latency',
                hidden=True,
                pass_context=True)
async def latency(ctx):
    await ctx.send("Latency of the bot is {} ms".format(round(client.latency * 1000), 10))


# creates poll
@commands.has_permissions(manage_messages=True)
@client.command(name='poll',
                brief='Creates a poll',
                pass_context=True)
async def poll(ctx, question: str, *options: str):
    if len(options) < 1:
        await ctx.channel.send("Poll must have at least one option.")
        return

    elif len(options) > 10:
        await ctx.channel.send("Poll cannot have more than 10 options.")
        return

    if len(options) == 2 and options[0] == 'yes' and options[1] == 'no':
        reactions = ['✅', '❌']
    else:
        reactions = ['1⃣', '2⃣', '3⃣', '4⃣', '5⃣', '6⃣', '7⃣', '8⃣', '9⃣', '🔟']

    description = []
    for x, option in enumerate(options):
        description += '\n {} {}'.format(reactions[x], option)  # displays text EX: option: :1:

    embed = Embed(title=question, description=''.join(description), colour=Colour.dark_orange())

    react_message = await ctx.channel.send(embed=embed)

    for reaction in reactions[:len(options)]:  # adds reaction emojis
        await react_message.add_reaction(reaction)


# triggers when user does not have permissions to run commands
@poll.error
async def pollError(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        if ctx.channel.guild.me.guild_permissions.manage_messages:
            message = ctx.message
            await message.delete(delay=0.75)
        await ctx.send('lol mate what u doin that isn\'t a real command')


@client.command(name='hugs',
                brief='hugs',
                pass_context=True)
async def hug(ctx, intensity: int = 1):
    msg = ''
    """Because everyone likes hugs
    Up to 10 intensity levels."""
    name = " *" + ctx.message.author.name + "*"
    if intensity <= 0:
        msg = "(っ˘̩╭╮˘̩)っ" + name
    elif intensity <= 3:
        msg = "(っ´▽｀)っ" + name
    elif intensity <= 6:
        msg = "╰(*´︶`*)╯" + name
    elif intensity <= 9:
        msg = "(つ≧▽≦)つ" + name
    elif intensity >= 10:
        msg = "(づ￣ ³￣)づ" + name + " ⊂(´・ω・｀⊂)"
    await ctx.send(msg)


@client.command(name='iss',
                brief='ISS Data.',
                description='Gives positional and other data about the ISS.',
                pass_context=True)
async def iss(ctx):
    """https://wheretheiss.at/w/developer"""
    url = urlopen("https://api.wheretheiss.at/v1/satellites/25544").read()  # url reader copies data
    issResponse = json.loads(url)  # json reader formats data
    print(issResponse)

    # retrieves specific data from formatted json
    response = '__International Space Station Data:__\n' \
               + 'Location: ' + str(issResponse['longitude']) + ', ' + str(issResponse['latitude']) \
               + '\nHeight: ' + str(round(issResponse['altitude'], 2)) + ' ' + str(issResponse['units']) \
               + '\nVelocity: ' + str(round(issResponse['velocity'], 2)) + ' ' + str(issResponse['units']) + ' per hour'

    link = 'https://api.wheretheiss.at/v1/coordinates/' + \
           str(issResponse['latitude']) + ',' + str(issResponse['longitude'])
    issResponse2 = json.loads(urlopen(link).read())

    response += '\n\nLink to Location: ' + str(issResponse2['map_url'])

    await ctx.send(response)


@client.command(name='utilization',
                description='Display server utilization information.',
                pass_context=True)
async def server_utilization(ctx):
    embed = serverUtilization(ctx, 'utilization')
    await ctx.send(embed=embed)


@client.command(name='cpu',
                description='Display server cpu utilization information.',
                pass_context=True)
async def cpu_utilization(ctx):
    embed = serverUtilization(ctx, 'cpu')
    await ctx.send(embed=embed)


@client.command(name='memory',
                aliases=['ram'],
                description='Display server memory utilization information.',
                pass_context=True)
async def memory_utilization(ctx):
    embed = serverUtilization(ctx, 'memory')
    await ctx.send(embed=embed)


@client.command(name='disk',
                description='Display server disk utilization information.',
                pass_context=True)
async def disk_utilization(ctx):
    embed = serverUtilization(ctx, 'disk')
    await ctx.send(embed=embed)


@client.command(name='gif',
                brief='Displays a random gif from parameter.',
                description='Displays a random gif from a top 25 list of the given search parameter.',
                pass_context=True)
async def gif(ctx, *msg: str):
    message = ''

    if not msg:  # If no parameter given, send random gif
        # https://g.tenor.com/v1/trending_terms?key=MOHWK7Y8WK7A&limit=20&locale=en_US
        r = urlopen(
            'https://g.tenor.com/v1/trending_terms?key=%s&limit=%s&locale=%s'
            % (TENOR_API_KEY, 20, 'en_US')
        ).read()  # gets top 20 trending keywords
        searchTerms = json.loads(r)

        search = searchTerms['results'][random.randint(0, 19)]  # chooses random keyword

        s = urlopen(
            'https://g.tenor.com/v1/search?q=%s&key=%s&limit=%s&contentfilter=%s&media_filter=%s'
            % (search.replace(' ', '-'), TENOR_API_KEY, 25, 'medium', 'minimal')
        ).read()  # gets top 25 gif data using random trending keyword
        msgGif = json.loads(s)  # loads the json

        await ctx.send(msgGif['results'][random.randint(0, 24)]['itemurl'])  # prints gif link

    else:
        for i in range(len(msg)):  # combines msg to one string
            message += msg[i] + '-'

        r = urlopen(
            'https://g.tenor.com/v1/search?q=%s&key=%s&limit=%s&contentfilter=%s&media_filter=%s'
            % (message, TENOR_API_KEY, 25, 'medium', 'minimal')
        ).read()  # gets top 25 gif data using users keyword
        msgGif = json.loads(r)  # loads the json

        await ctx.send(msgGif['results'][random.randint(0, 24)]['itemurl'])  # prints gif link


@client.command(name='guildlookup', pass_context=True)
async def GuildLookup(ctx):
    for guild in client.guilds:
        message = guild.name
        for channel in guild.text_channels:
            message += ' - ' + channel.name
        await ctx.channel.send(message)


def serverUtilization(ctx, x):
    message = ''

    utilization = pterodactylAPI.client.get_server_utilization('C9335213')
    limits = pterodactylAPI.client.get_server('C9335213')

    cpuUsage = str(round(utilization['resources']['cpu_absolute'], 2))
    memoryUsage = str(round(utilization['resources']['memory_bytes'] / 1000000, 1))
    diskUsage = str(round(utilization['resources']['disk_bytes'] / 1000000))

    if limits['limits']['memory'] is not 0:
        memoryLimit = str(limits['limits']['memory']) + 'MB'
    else:
        memoryLimit = 'Unlimited MB'

    if limits['limits']['disk'] is not 0:
        diskLimit = str(limits['limits']['disk']) + 'MB'
    else:
        diskLimit = 'Unlimited MB'

    if x != 'utilization':
        if x == 'cpu':
            message += '```CPU Usage: ' + cpuUsage + '%```'

        elif x == 'memory':
            message += '```Memory Usage: ' + memoryUsage + '/' + memoryLimit + '```'

        elif x == 'disk':
            message += '```Disk Usage: ' + diskUsage + '/' + diskLimit + '```'

    else:
        message = '```CPU Usage: ' + cpuUsage + '%' + \
                  '\nMemory Usage: ' + memoryUsage + '/' + memoryLimit + \
                  '\nDisk Usage: ' + diskUsage + '/' + diskLimit + '```'

    authorName = ctx.author.name + '#' + str(ctx.author.discriminator)
    embed = Embed(title='Utilization', description=message,
                  colour=Colour.dark_orange())
    embed.set_author(name='Toothless Bot', icon_url=client.user.avatar_url)
    embed.set_footer(text='Requested By ➤ \n{}'.format(authorName), icon_url=client.user.avatar_url)

    return embed


def is_bot(user):
    if user.bot:
        return True


# Runs the client
client.run(TOKEN)
