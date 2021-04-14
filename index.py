import os

import discord
from discord.ext import commands
from discord.ext.commands import Bot
   
import firebase_admin
from firebase_admin import credentials
from google.cloud import firestore

from dotenv import load_dotenv

import uwuify


firebaseCred = credentials.Certificate('.\\firebase.json')
firebase_admin.initialize_app(firebaseCred)

db = firebase_admin

intents = discord.Intents.default()
intents.members = True
intents.presences = True

# Loads env file
load_dotenv()

# Sets variables from env file
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
BOT_PREFIX = ['.']
BAD_WORDS = ['ass', 'bitch', 'fuck', 'cunt', 'shit', 'wank', 'dick', 'fag']

# Sets prefix for bot
client = Bot(command_prefix=BOT_PREFIX, intents=intents)

# Pain leaderboard jazz
fileLength = len(open('pain_leaderboard.txt').readlines())
fileReader = open('pain_leaderboard.txt', 'r')

painLB = []
fileReader.seek(0)
a = ['', 0]

for n in range(fileLength):
    if n % 2 == 0:
        a[0] = fileReader.readline().replace('\n', '')

    if n % 2 == 1:
        a[1] = int(fileReader.readline().replace('\n', ''))
        painLB.append(a)
        a = ['', 0]
    n += 1

fileReader.close()


# When client comes online
@client.event
async def on_ready():
    # Prints to console that its online
    print(f'{client.user.name} is online!')
    # await client.get_channel(823772094944641046).send('{} is online!'.format(client.user.name))

    # Sets bot status
    game = discord.Game('messing with PyCharm')
    await client.change_presence(status=discord.Status.online, activity=game)

    for guild in client.guilds:
        if guild.me.guild_permissions.administrator:
            continue
        if not guild.me.guild_permissions.manage_messages:
            print('I need to be able to manage messages in ' + guild.name + ' - ' + str(guild.id))
        if not guild.me.guild_permissions.add_reactions:
            print('I need to be able to add reactions in ' + guild.name + ' - ' + str(guild.id))
        if not guild.me.guild_permissions.read_message_history:
            print('I need to be able to read message history in ' + guild.name + ' - ' + str(guild.id))


# On every message scan it
@client.event
async def on_message(ctx):
    print(f'{ctx.author}: {ctx.content}')

    # Ignore if from bot
    if is_me(ctx):
        return

    # Respond if it contains keyword
    if 'owo' in ctx.content.lower():
        if ctx.channel.guild.me.guild_permissions.text.manage_messages:
            message = ctx.message
            await message.delete(delay=0.75)

        await ctx.channel.send('die.')

    if 'pog' in ctx.content.lower():
        emoji = None
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

    # pain jazz
    if 'pain' in ctx.content.lower():
        addPain(str(ctx.author.id))
        # emoji = discord.utils.get(ctx.guild.emojis, name="poggers")
        await ctx.add_reaction('✅')

    if ctx.channel.guild.me.guild_permissions.manage_messages:
        for i in BAD_WORDS:
            if i in str(ctx.content).lower():
                message = ctx.message
                await message.delete(delay=0.75)
                await ctx.channel.send('no bad words.')
                return

    # Let other commands work
    await client.process_commands(ctx)


# Purge command
@client.command(name='purge',
                description='Deletes previous X number of messages.',
                brief='Purges chat.',
                pass_context=True)
@commands.has_permissions(manage_messages=True)
async def purge(ctx, numToDelete: int):
    if numToDelete > 100:  # Checks if above max
        await ctx.send("You can't purge more than 100 messages at a time.")
        return

    await ctx.channel.purge(limit=numToDelete+1)
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
                aliases=['uwuify', 'owoify', 'owo'],
                usage='[message to uwuify]',
                pass_context=True)
async def uwu(ctx, *msg: str):
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
                description="It's David time.",
                brief="All about David.",
                aliases=['david1', 'david2'],
                pass_context=True)
async def david(ctx):
    response = 'david is the best <3'
    await ctx.send(response)
    await ctx.send('and so are you {}'.format(ctx.author.mention))


# Commands for !square - square a number
@client.command(name='square',
                description='Squares the input.',
                brief='Squares the input.',
                pass_context=True)
async def square(ctx, number):
    squared_value = int(number) * int(number)
    await ctx.channel.send(str(number) + " squared is " + str(squared_value))

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
    await ctx.send("Latency of the bot is {} ms".format(round(client.latency*1000), 5))


@commands.has_permissions(manage_messages=True)
@client.command(name='poll',
                brief='Creates a poll.',
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
        description += '\n {} {}'.format(reactions[x], option)

    embed = discord.Embed(title=question, description=''.join(description))

    react_message = await ctx.channel.send(embed=embed)
    print('uwu')
    print(reactions)

    for reaction in reactions[:len(options)]:
        await react_message.add_reaction(reaction)


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


@client.command(name='leaderboard',
                aliases=['lb'],
                brief='Displays top pain.',
                pass_context=True)
async def leaderboard(ctx):
    topIndex = 0
    painLBRows = len(painLB)
    print(painLB)

    for i in range(painLBRows):
        if painLB[i][1] > painLB[topIndex][1]:
            topIndex = i

    #embed = discord.Embed(title='Most Pain', description=''.join(description))

    response = 'Top User: <@' + str(painLB[topIndex][0]) + \
               '>\n# Of Pain: ' + str(painLB[topIndex][1])

    await ctx.send(response)


@client.command(name='lookup',
                brief='Looks up target user\'s pain.',
                pass_context=True)
async def lookup(ctx, name):
    userID = name.strip('<>@!')
    for i in range(len(painLB)):
        if userID == painLB[i][0]:
            response = '<@' + str(painLB[i][0]) + '> has ' + str(painLB[i][1]) + ' pain.'
            await ctx.channel.send(response)
            return

        i += 1
    response = name + ' has not had any pain.'
    await ctx.channel.send(response)


@commands.has_permissions(administrator=True)
@client.command(hidden=True,
                aliases=['save'],
                pass_context=True)
async def save_leaderboard(ctx):
    if ctx.channel.guild.me.guild_permissions.manage_messages:
        message = ctx.message
        await message.delete(delay=0.75)
    savePainLB()
    await ctx.channel.send('Leaderboard has been saved.')


@save_leaderboard.error
async def save_leaderboardError(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        if ctx.channel.guild.me.guild_permissions.manage_messages:
            message = ctx.message
            await message.delete(delay=0.75)
        await ctx.send('lol mate what u doin that isn\'t a real command')


# Shut down bot
@client.command(hidden=True)
@commands.is_owner()
async def shutdown(ctx):
    savePainLB()
    await ctx.bot.logout()


def is_me(ctx):
    return ctx.author == client.user


def addPain(userID: str):
    if len(painLB) == 0:
        painLB.append([userID, 1])

    for i in range(len(painLB)):
        if userID == painLB[i][0]:
            painLB[i][1] += 1
            return
        i += 1

    painLB.append([userID, 1])


def savePainLB():
    fileRead = open('pain_leaderboard.txt', 'w')
    fileRead.seek(0)

    global painLB

    painLBRows = len(painLB)
    painLBCols = len(painLB[0])

    for i in range(painLBRows):
        for j in range(painLBCols):
            x = str(painLB[i][j]) + '\n'
            fileRead.write(x)
    fileRead.close()

    print('Leaderboard is saved.')


# Runs the client
client.run(TOKEN)
