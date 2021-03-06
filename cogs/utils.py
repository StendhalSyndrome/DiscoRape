import discord
from discord.ext import commands
from ext.utility import load_json
from mtranslate import translate
from ext import embedtobox
from PIL import Image
import asyncio
import typing
import random
import io
import re
import aiohttp
import os
import time
from bs4 import BeautifulSoup
import urllib.request
# NOTE: Need this shit dunno if it's actually will work


class utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lang_conv = load_json("data/langs.json")

    @commands.command()
    async def setbanner(self, ctx, *, banner=None):
        """sets the guilds banner
        Parameters
        • banner - the attachment or url of the image to use as a banner
        """
        if ctx.message.attachments:
            image = await ctx.message.attachments[0].read()
        elif banner:
            async with aiohttp.ClientSession() as session:
                async with session.get(banner) as resp:
                    image = await resp.read()
        await ctx.guild.edit(banner=image)
        await ctx.send("Banner updated")

    @commands.command()
    async def setsplash(self, ctx, *, splash=None):
        """sets the guilds invite splash
        Parameters
        • splash - the attachment or url of the image to use as the invite splash
        """
        if ctx.message.attachments:
            image = await ctx.message.attachments[0].read()
        elif splash:
            async with aiohttp.ClientSession() as session:
                async with session.get(splash) as resp:
                    image = await resp.read()
        await ctx.guild.edit(splash=image)
        await ctx.send("Invite Splash updated")

    @commands.command()
    async def splash(self, ctx, *, guild=None):
        """gets a guild's invite splash(invite background)
        Parameters
        • guild - the name or id of the guild
        """
        if guild is None:
            guild = ctx.guild
        elif discord.utils.get(self.bot.guilds, id=int(guild)) is not None:
            guild = discord.utils.get(self.bot.guilds, id=int(guild))
        elif type(guild) == str:
            guild = discord.utils.get(self.bot.guilds, name=guild)
        splash = await guild.splash_url_as(format="png").read()
        with io.BytesIO(splash) as f:
            await ctx.send(file=discord.File(f, "splash.png"))

    @commands.command()
    async def banner(self, ctx, *, guild=None):
        """gets a guild's banner image
        Parameters
        • guild - the name or id of the guild
        """
        if guild is None:
            guild = ctx.guild
        elif type(guild) == int:
            guild = discord.utils.get(self.bot.guilds, id=guild)
        elif type(guild) == str:
            guild = discord.utils.get(self.bot.guilds, name=guild)
        banner = await guild.banner_url_as(format="png").read()
        with io.BytesIO(banner) as f:
            await ctx.send(file=discord.File(f, "banner.png"))

    @commands.command()
    async def translate(self, ctx, language, *, text):
        """translates the string into a given language
        Parameters
        • language - the language to translate to
        • text - the text to be translated
        """
        await ctx.send(translate(text, language))

    @commands.command()
    async def addemoji(self, ctx, emoji_name, emoji_url=None):
        """adds an emoji to a server
        Parameters
        • emoji_name – the name of the emoji
        • emoji_url – the url or attachment of an image to turn into an emoji
        """
        if ctx.message.attachments:
            image = await ctx.message.attachments[0].read()
        elif emoji_url:
            async with aiohttp.ClientSession() as session:
                async with session.get(emoji_url) as resp:
                    image = await resp.read()
        emoji = await ctx.guild.create_custom_emoji(name=emoji_name, image=image)
        await ctx.send(f"Emoji {emoji.name} created!")

    @commands.command()
    async def delemoji(self, ctx, emoji: discord.Emoji):
        """deletes an emoji
        Parameters
        • emoji - the name or id of the emoji
        """
        name = emoji.name
        await emoji.delete()
        await ctx.send(content=f"Deleted emoji: {name}", delete_after=2)

    @commands.command()
    async def editemoji(self, ctx, emoji: discord.Emoji, new_name):
        """edits the name of an emoji
        Parameters
        • emoji - the name or id of the emoji
        • new_name - the new name to use for the emoji
        """
        await emoji.edit(name=new_name)
        await ctx.send(
            content=f"Edited emoji {emoji_name} to {new_name}", delete_after=2
        )

    @commands.command(name="logout")
    async def _logout(self, ctx):
        """
        restart the bot
        """
        await ctx.send("`Selfbot Logging out`")
        await self.bot.logout()

    @commands.command()
    async def nick(self, ctx, user: discord.Member, *, nickname: str = None):
        """change a user's nickname
        Parameter
        • user - the name or id of the user
        • nickname - the nickname to change to
        """
        prevnick = user.nick or user.name
        await user.edit(nick=nickname)
        newnick = nickname or user.name
        await ctx.send(f"Changed {prevnick}'s nickname to {newnick}")

    @commands.command(aliases=["ca", "cactivity"])
    async def customactivity(self, ctx, Type: str = "playing", *, text: str = None):
        """sets a custom activity
        Parameters
        • Type - "playing", "streaming", "listeningto" or "watching", defaults to playing
        • text - The text to display as presence
        """
        types = {
            "playing": "Playing",
            "streaming": "Streaming",
            "listeningto": "Listening to",
            "watching": "Watching",
        }
        if text is None:
            await self.bot.change_presence(activity=text, afk=True)
        else:
            if Type == "playing":
                await self.bot.change_presence(
                    activity=discord.Game(name=text), afk=True
                )
            elif Type == "streaming":
                await self.bot.change_presence(
                    activity=discord.Streaming(
                        name=text, url=f"https://twitch.tv/{text}"
                    ),
                    afk=True,
                )
            elif Type == "listeningto":
                await self.bot.change_presence(
                    activity=discord.Activity(
                        type=discord.ActivityType.listening, name=text
                    ),
                    afk=True,
                )
            elif Type == "watching":
                await self.bot.change_presence(
                    activity=discord.Activity(
                        type=discord.ActivityType.watching, name=text
                    ),
                    afk=True,
                )
            em = discord.Embed(color=0xFFD500, title="Presence")
            em.description = f"Presence : {types[Type]} {text}"
            if ctx.author.guild_permissions.embed_links:
                await ctx.send(embed=em)
            else:
                await ctx.send(f"Presence : {types[Type]} {text}")

    @commands.command()
    async def choose(self, ctx, *, choices: commands.clean_content):
        """choose! use , in between
        Parameters
        • choices - the choices to choose from separated using ,"""
        choices = choices.split(",")
        choices[0] = " " + choices[0]
        await ctx.send(str(random.choice(choices))[1:])

    def get_user_from_global_cache(self, user):
        for u in self.bot.users:
            if user == u.name:
                return user

    @commands.command(aliases=["a", "pic"])
    async def avatar(self, ctx, *, user=None):
        """gets the display picture of a user
        Parameters
        • user – The tag, name or id of the user
        """
        user = user or ctx.author
        if type(user) != discord.Member:
            user = str(user)
            r = re.compile(r"@(.*#\d{4})|(\d{18})")
            r = r.search(user)
            if r:
                if r.group(2):
                    user = int(r.group(2))
                elif r.group(1):
                    user = r.group(1)
        if type(user) == str and type(user) != int:
            user = ctx.guild.get_member_named(user)
        if type(user) == str:
            user = get_user_from_global_cache(user)
        elif type(user) == int:
            user = await self.bot.fetch_user(user)
        if user.is_avatar_animated():
            format = "gif"
        else:
            format = "png"
        avatar = await user.avatar_url_as(format=format).read()
        with io.BytesIO(avatar) as file:
            await ctx.send(file=discord.File(file, f"DP.{format}"))
        await ctx.delete()

    @commands.command(aliases=["gi"])
    async def guildicon(self, ctx, *, guild=None):
        """gets a guild's icon
        Parameters
        • guild - The name(case sensitive) or id of the guild/server"""
        guild = guild or ctx.guild
        format = "png"
        try:
            guild = int(guild)
        except:
            pass
        if type(guild) == int:
            guild = discord.utils.get(self.bot.guilds, id=int(guild))
        elif type(guild) == str:
            guild = discord.utils.get(self.bot.guilds, name=guild)
        if guild.is_icon_animated():
            format = "gif"
        icon = await guild.icon_url_as(format=format).read()
        with io.BytesIO(icon) as file:
            await ctx.send(file=discord.File(file, f"icon.{format}"))

    @commands.command()
    async def reload(self, ctx, cog=None):
        """Reloads one or all of the cogs

        Paramaters
        • cog - The name of the cog you want to reload e.g crypto
        If not name is specified it'll reload all cogs"""
        if not cog:
            # No cog, means we reload all cogs
            async with ctx.typing():
                embed = discord.Embed(
                    title="Reloading all cogs!",
                    color=0x808080,
                    timestamp=ctx.message.created_at,
                )
                for ext in os.listdir("./cogs/"):
                    if ext.endswith(".py") and not ext.startswith("_"):
                        try:
                            self.bot.unload_extension(f"cogs.{ext[:-3]}")
                            self.bot.load_extension(f"cogs.{ext[:-3]}")
                            embed.add_field(
                                name=f"Reloaded: `{ext}`", value="\uFEFF", inline=False
                            )
                        except Exception as e:
                            embed.add_field(
                                name=f"Failed to reload: `{ext}`", value=e, inline=False
                            )
                        await asyncio.sleep(0.5)
                await ctx.send(embed=embed)
        else:
            # reload the specific cog
            async with ctx.typing():
                embed = discord.Embed(
                    title="Reloading all cogs!",
                    color=0x808080,
                    timestamp=ctx.message.created_at,
                )
                ext = f"{cog.lower()}.py"
                if not os.path.exists(f"./cogs/{ext}"):
                    # if the file does not exist
                    embed.add_field(
                        name=f"Failed to reload: `{ext}`",
                        value="This cog does not exist.",
                        inline=False,
                    )

                elif ext.endswith(".py") and not ext.startswith("_"):
                    try:
                        self.bot.unload_extension(f"cogs.{ext[:-3]}")
                        self.bot.load_extension(f"cogs.{ext[:-3]}")
                        embed.add_field(
                            name=f"Reloaded: `{ext}`", value="\uFEFF", inline=False
                        )
                    except Exception:
                        desired_trace = traceback.format_exc()
                        embed.add_field(
                            name=f"Failed to reload: `{ext}`",
                            value=desired_trace,
                            inline=False,
                        )
                        await ctx.send(embed=embed)

    @commands.command()
    async def ping(self, ctx):
        """Gives you client latency"""
        start = time.perf_counter()
        message = await ctx.send("Ping...")
        end = time.perf_counter()
        duration = (end - start) * 1000
        await message.edit(
            content="Pong! :ping_pong:\nLatency is **{:.2f}ms**".format(duration)
        )
        await ctx.message.delete()

    @commands.command()
    async def urban(self, ctx, message):
        """Looks up shit on urban dictionary

        Note: Only works with single words not sentences
        """
        term = message
        url = "https://www.urbandictionary.com/define.php?term="
        url+= ("+"+term)
        try:
            html = urllib.request.urlopen(url)
            soup = BeautifulSoup(html, 'html.parser')
            definition = soup.find(class_='meaning').get_text()
            await ctx.send(f"`Defenition:\n      {definition}`")
        except:
            msg = "Phrase doesn't exist in the dictionary surprisingly."
            await ctx.send(msg)




def setup(bot):
    bot.add_cog(utility(bot))
