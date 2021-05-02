import discord
from discord.ext import commands

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from google.cloud.firestore import Increment


'''firebaseCred = credentials.Certificate('.\\firebase.json')
firebase_admin.initialize_app(firebaseCred)'''

db = firestore.client()


class LeaderboardCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # When client comes online
    @commands.Cog.listener()
    async def on_ready(self):
        # Prints to console that its online
        print(f'LeaderboardCog is online!')

    # On member join, add to database
    @commands.Cog.listener()
    async def on_member_join(self, member):
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

    '''
    @client.event
    async def on_guild_leave(server):
        # db.collection('leaderboard').document(str(server.id).delete()
    
    '''

    @commands.Cog.listener()
    async def on_guild_join(self, server):
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

                db.collection(u'leaderboard/' + str(server.id) + '/users') \
                    .document(str(user.id)) \
                    .set(data, merge=True)

                print('Added user', user.name, user.id, 'to the database of guild', server.name, server.id)

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

    @commands.command(name='leaderboard', aliases=['lb'], brief='Displays top pain.', pass_context=True)
    async def leaderboard(self, ctx):
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

    @commands.command(name='lookup', brief='Looks up target user\'s pain.', pass_context=True)
    async def lookup(self, ctx, name):
        user = self.bot.get_user(int(name.strip('<@!>')))

        if is_bot(user):
            await ctx.send('That user is a bot!')
            return

        userLookup = db.collection('leaderboard/' + str(ctx.guild.id) + '/users')\
            .where(u'userID', u'==', user.id).stream()

        for find in userLookup:
            findPain = str(find.get(u'pain'))
            response = str(user.name) + '\'s Pain: **' + findPain + '**'
            await ctx.send(response)

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
        db.collection(u'leaderboard/' + str(member.guild.id) + '/users').document(str(member.id)) \
            .update({u'pain': Increment(1)})
    except():
        print('Error writing to document')


def setup(bot):
    bot.add_cog(LeaderboardCog(bot))
