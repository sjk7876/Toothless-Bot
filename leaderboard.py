import os

import discord
from discord import Embed, Colour
from discord.ext import commands, tasks

from firebase_admin import firestore
from google.cloud.firestore import Increment

LEADERBOARD = os.getenv('LEADERBOARD')


db = firestore.client()


class LeaderboardCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # When client comes online
    @commands.Cog.listener()
    async def on_ready(self):
        # Prints to console that its online
        print(f'LeaderboardCog is online!')
        self.update_status.start()

    # On member join, add to database
    @commands.Cog.listener()
    async def on_member_join(self, member):
        try:
            if is_bot(member):
                return

            data = {
                u'username': member.name,
                u'userID': member.id,
                u'pain': int(0)
            }
            db.collection(LEADERBOARD + '/' + str(member.guild.id) + '/users') \
                .document(str(member.id)) \
                .set(data, merge=True)
            print('Added new member: ', member.name, ':', member.id)
        except():
            print('Error writing document')

        # await member.send(content='It\'s Pain Time.')

    @commands.Cog.listener()
    async def on_guild_join(self, server):
        print('Joined guild -', server.name, server.id)

        if not db.collection(LEADERBOARD).document(str(server.id)).get().exists:
            try:
                db.collection(LEADERBOARD + '/' + str(server.id) + '/users')
                db.collection(LEADERBOARD).document(str(server.id)) \
                    .set({u'ServerName': str(server.name), u'total': 0})

                print('Added guild -', server.name, server.id)

            except AttributeError:
                print('Server already exists.')

        else:
            print('Guild -', server.name, server.id, 'already exists.')

        try:
            for user in server.members:
                if is_bot(user):
                    print('User', user.name, 'is a bot.')
                    continue

                if db.collection(LEADERBOARD + '/' + str(server.id) + '/users').document(str(user.id)).get().exists:
                    print('User ', user.name, ' - ', user.id, ' is already in the database of guild ',
                          server.name, server.id, sep='')
                    continue

                data = {
                    u'username': str(user.name),
                    u'userID': user.id,
                    u'pain': 0
                }

                db.collection(LEADERBOARD + '/' + str(server.id) + '/users') \
                    .document(str(user.id)) \
                    .set(data, merge=True)

                print('Added user ', user.name, ' - ', user.id, ' to the database of guild ', server.name, server.id,
                      sep='')

        except():
            print('Couldn\t add that guy.')

    # On every message scan it
    @commands.Cog.listener()
    async def on_message(self, ctx):
        # Ignore if from bot
        if is_bot(ctx.author):
            return

        # pain jazz
        if 'pain' == ctx.content.lower():
            addPain(ctx.author)
            await ctx.add_reaction('✅')

        # Let other commands work
        '''await self.bot.process_commands(ctx)'''

    @commands.command(name='leaderboard',
                      aliases=['lb'],
                      brief='Displays top pain',
                      pass_context=True)
    async def leaderboard(self, ctx):
        response = ''
        lowestPain = db.collection(LEADERBOARD + '/' + str(ctx.guild.id) + '/users') \
            .order_by(u'pain', direction=firestore.Query.DESCENDING) \
            .limit(3) \
            .stream()
        i = 1
        for user in lowestPain:
            response += f"{i}. <@{str(user.get(u'userID'))}> - {user.get(u'pain')}\n"
            i += 1
        embed = Embed(title='Top 3 Pain', description=response, colour=Colour.dark_orange())
        await ctx.send(embed=embed)

    @commands.command(name='lookup',
                      brief='Looks up target user\'s pain',
                      pass_context=True)
    async def lookup(self, ctx, name):
        user = self.bot.get_user(int(name.strip('<@!>')))

        if is_bot(user):
            await ctx.send('That user is a bot!')
            return

        userLookup = db.collection(LEADERBOARD + '/' + str(ctx.guild.id) + '/users') \
            .where(u'userID', u'==', user.id).stream()

        for find in userLookup:
            findPain = str(find.get(u'pain'))
            response = str(user.name) + '\'s Pain: **' + findPain + '**'
            await ctx.send(response)

    @commands.command(name='resetleaderboard',
                      aliases=['reset'],
                      brief='Resets the pain leaderboard.',
                      hidden=True,
                      pass_context=True)
    @commands.has_permissions(administrator=True)
    async def reset_leaderboard(self, ctx):
        print('Resetting ' + str(ctx.guild.name) + '\'s leaderboard')
        for member in ctx.guild.members:
            if is_bot(member):
                continue
            db.collection(LEADERBOARD + '/' + str(member.guild.id) + '/users').document(str(member.id)) \
                .update({u'pain': 0})

        total = db.collection(LEADERBOARD).document('totalPain').get().get(u'total') - \
                db.collection(LEADERBOARD).document(str(ctx.guild.id)).get().get(u'total')
        print(total)
        db.collection(LEADERBOARD).document('totalPain').update({u'total': total})
        db.collection(LEADERBOARD).document(str(ctx.guild.id)).update({u'total': 0})

    @commands.command(name='total',
                      brief='Displays the server\'s total pain.',
                      pass_context=True)
    async def total(self, ctx):
        await ctx.channel.send('Total pain of ' + ctx.guild.name + ' is: **' +
                         str(db.collection(LEADERBOARD).document(str(ctx.guild.id)).get().get(u'total')) + '**')

    @tasks.loop(seconds=30)
    async def update_status(self):
        pain = 0
        pain = db.collection(LEADERBOARD).document('totalPain').get().get(u'total')

        game = discord.Game('Total Pain: ' + str(pain))
        await self.bot.change_presence(status=discord.Status.online, activity=game)

    # Shut down bot
    @commands.command(hidden=True)
    @commands.is_owner()
    async def shutdown(self, ctx):
        await ctx.bot.logout()


def is_bot(user):
    if user.bot:
        return True


def addPain(member):
    # Check if user has a database
    try:
        db.collection(LEADERBOARD + '/' + str(member.guild.id) + '/users').document(str(member.id)) \
            .update({u'pain': Increment(1)})

        db.collection(LEADERBOARD).document('totalPain').update({u'total': Increment(1)})
        db.collection(LEADERBOARD).document(str(member.guild.id)).update({u'total': Increment(1)})
    except():
        print('Error writing to document')


def deleteGuild(guildDB):
    docs = guildDB.limit(5).stream()
    deleted = 0

    for doc in docs:
        doc.reference.delete()
        deleted = deleted + 1
        print('Deleted user')

    if deleted >= 5:
        return deleteGuild(guildDB)


def setup(bot):
    bot.add_cog(LeaderboardCog(bot))
