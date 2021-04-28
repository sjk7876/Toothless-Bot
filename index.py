import os

import discord
from discord.ext import commands
from discord.ext.commands import Bot

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from google.cloud.firestore import Increment

from dotenv import load_dotenv

import uwuify


firebaseCred = credentials.Certificate('.\\firebase.json')
firebase_admin.initialize_app(firebaseCred)

db = firestore.client()

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
        if guild.me.guild_permissions.administrator:
            continue
        if not guild.me.guild_permissions.manage_messages:
            print('I need to be able to manage messages in ' + guild.name + ' - ' + str(guild.id))
        if not guild.me.guild_permissions.add_reactions:
            print('I need to be able to add reactions in ' + guild.name + ' - ' + str(guild.id))
        if not guild.me.guild_permissions.read_message_history:
            print('I need to be able to read message history in ' + guild.name + ' - ' + str(guild.id))


# On member join, add to database
@client.event
async def on_member_join(member):
    try:
        data = {
            u'username': member.name,
            u'userID': member.id,
            u'pain': int(0)
        }
        db.collection(u'leaderboard/' + str(member.guild.id) + '/users')\
            .document(str(member.id))\
            .set(data, merge=True)
        print('Added new member: ', member.name, ':', member.id)
    except():
        print('Error writing document')

    # await member.send(content='It\'s Pain Time.')


@client.event
async def on_guild_join(server):
    print('Joined guild -', server.name, server.id)
    try:
        db.collection(u'leaderboard/' + str(server.id) + '/users')
        db.collection(u'leaderboard').document(str(server.id)).set({u'ServerName': str(server.name)})

        print('Added guild -', server.name, server.id)

    except AttributeError:
        print('Server already exists.')

    try:
        for user in server.members:
            if is_bot(user):
                print('User', user.name, 'is a bot.')
                continue

            data = {
                u'username': str(user.name),
                u'userID': user.id,
                u'pain': 0
            }

            db.collection(u'leaderboard/' + str(server.id) + '/users')\
                .document(str(user.id))\
                .set(data, merge=True)

            print('Added user', user.name, user.id, 'to the database of guild', server.name, server.id)

    except():
        print('Couldn\t add that guy.')


'''
@client.event
async def on_guild_leave(server):
    # db.collection('leaderboard').document(str(server.id).delete()

'''

# EDIT!!! ignore message if in DM for now


# On every message scan it
@client.event
async def on_message(ctx):
    print(f'{ctx.author}: {ctx.content}')

    # Ignore if from bot
    if is_bot(ctx.author):
        return

    # Respond if it contains keyword
    if 'owo' in ctx.content.lower():
        if ctx.channel.guild.me.guild_permissions.text.manage_messages:
            message = ctx.message
            await message.delete(delay=0.75)

        await ctx.channel.send('die.')

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

    # pain jazz
    if 'pain' in ctx.content.lower():
        addPain(ctx.author)
        await ctx.add_reaction('✅')

    """if ctx.channel.guild.me.guild_permissions.manage_messages:
        for i in BAD_WORDS:
            if i in str(ctx.content).lower():
                message = ctx.message
                await message.delete(delay=0.75)
                await ctx.channel.send('no bad words.')
                return"""

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
    await ctx.send('david is the best <3\nand so are you {}'.format(ctx.author.mention))


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
    await ctx.send("Latency of the bot is {} ms".format(round(client.latency*1000), 10))


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
    response = ''
    lowestPain = db.collection('leaderboard/' + str(ctx.guild.id) + '/users')\
        .order_by(u'pain', direction=firestore.Query.DESCENDING)\
        .limit(3)\
        .stream()
    i = 1
    for user in lowestPain:
        response += f"{i}. <@{str(user.get(u'userID'))}> - {user.get(u'pain')}\n"
        i += 1
    embed = discord.Embed(title='Top 3 Pain', description=response)
    await ctx.send(embed=embed)


@client.command(name='lookup',
                brief='Looks up target user\'s pain.',
                pass_context=True)
async def lookup(ctx, name):
    user = client.get_user(int(name.strip('<@!>')))
    print(user)
    print(user.id)

    userLookup = db.collection('leaderboard/' + str(ctx.guild.id) + '/users')
        # .document(str(user.id))
    response = ''
    print('a')
    doc_ref = user
    doc = doc_ref.get('/' + str(user.id))
    if doc.exists:
        print(f'Document data: {doc.to_dict()}')
    else:
        print(u'No such document!')

    """
    # print(f'{userLookup.id} => {userLookup.to_dict()}')
    response = f"<@{str(userLookup.get(str(user.id), u'userID'))}> - " \
               f"{userLookup.get(str(user.id), u'pain')}"
    print('b')

    title = str(user.name) + '\'s Pain'
    embed = discord.Embed(title=title, description=response)
    await ctx.send(embed=embed)
    print('c')"""


# Shut down bot
@client.command(hidden=True)
@commands.is_owner()
async def shutdown(ctx):
    await ctx.bot.logout()


def is_bot(user):
    if user.bot:
        return True


def addPain(member):
    # Check if user has a database
    try:
        db.collection(u'leaderboard/' + str(member.guild.id) + '/users').document(str(member.id)) \
            .update({u'pain': Increment(1)})
    except():
        print('Error writing to document')


# Runs the client
client.run(TOKEN)
