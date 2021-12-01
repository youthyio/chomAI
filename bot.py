import logger
import inspect
import discord
from openai_api import ApiHandler
from functools import wraps
from Prompts import language_map
from discord.ext import commands
from config import DISCORD_TOKEN, PREFIX, OPENAI_TOKEN, PASSCODE, NICKNAMES, MAGIC_SECRET
from helpers import user_parse, help_message
from Errors import *
import aiohttp
import aiofiles

bot = commands.Bot(command_prefix=PREFIX, help_command=None)

thumbs_up = "👍"
complete = ":chom:673029634438332436"

def check_auth(method):
    @wraps(method)
    async def _impl(self, *method_args, **method_kwargs):
        if self.authorized:
            method_output = method(self, *method_args, **method_kwargs)
            return await method_output
        else:
            return await self.ask_owner(method_args[0])

    return _impl

def personality(method):
    @wraps(method)
    async def _impl(self, *method_args, **method_kwargs):
        self.personality = method.__name__
        method_output = method(self, *method_args, **method_kwargs)
        return await method_output

    return _impl

class GPTBot(commands.Cog):
    def __init__(self, bot): 
        self.bot = bot
        self.__logger = logger.get_logger("openai_logger")
        self.__api = ApiHandler(self.__logger)
        self.personality = "normal"
        self.language = "EN"
        self.authorized = False
        self.passcode = "{}".format(PASSCODE)   

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """
        """

        if hasattr(ctx.command, 'on_error'):
            return
        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return
        ignored = (commands.CommandNotFound,)
        error = getattr(error, 'original', error)
        if isinstance(error, ignored):
            return
        if isinstance(error, commands.DisabledCommand):
            await ctx.send(f'{ctx.command} has been disabled.')
        elif isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
            except discord.HTTPException:
                pass
        elif isinstance(error, commands.PrivateMessageOnly):
            try:
                await ctx.author.send(f'{ctx.command} can only be used in Private Messages.')
            except discord.HTTPException:
                pass

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        owner_id = guild.owner_id
        guild_id = guild.id
        guild_name = guild.name

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        guild_id = guild.id

    @commands.Cog.listener("on_message")
    async def greet(self,message):
        for x in message.mentions:
            if(x==self.bot.user):
                try:
                    if (self.personality == "normal"):
                        answer = await self.__api.answer(message.clean_content, language=self.language)
                        return await message.channel.send(discord.utils.escape_mentions(answer))
                    else:
                        answer = await self.__api.personality(message.clean_content,self.personality,language="EN")
                        return await message.channel.send(discord.utils.escape_mentions(answer))
                except Exception as e:
                    print("Error: {}".format(e))

    async def cog_before_invoke(self, ctx):
        await ctx.message.add_reaction(thumbs_up)

    async def cog_after_invoke(self, ctx):
        await ctx.message.remove_reaction(thumbs_up, self.bot.user)
        await ctx.message.add_reaction(complete)

    async def check_server_token(self, ctx):
        guild_id = ctx.guild.id

    @staticmethod
    async def prompt_setup(ctx):
        await ctx.send("Owner of this server hasn't configured the bot yet. If you're the owner, send this bot a DM "
                       "with command !setup.")

    @staticmethod
    async def empty_warning(ctx):
        await ctx.send("No empty prompts tf <:chom:673029634438332436>")

    @staticmethod
    async def openai_down_warning(ctx):
        await ctx.send("OpenAI seems to be down. It's aight, settle down and I'll see if it works again <:chom:673029634438332436>")

    @staticmethod
    async def credit_warning(ctx):
        user_id, user_name = user_parse(ctx)
        await ctx.send("{}, your daily allowance is over. f in the chat.".format(user_name))

    @staticmethod
    async def not_admin_warning(ctx):
        user_id, user_name = user_parse(ctx)
        await ctx.send("{}, this command is only usable by admins.".format(user_name))

    @staticmethod
    async def ask_owner(ctx):
        user_id, user_name = user_parse(ctx)
        await ctx.send("{}, ayo if you know the pass, you know the command 😏".format(user_name))

    @commands.command()
    @check_auth
    async def answer(self, ctx, *prompt: str):
        self.personality = "normal"
        usage = len(list("".join(prompt)))
        user_id, user_name = user_parse(ctx)
        if usage == 0:
            raise EmptyPromptError
        answer = await self.__api.answer(prompt, language=self.language)
        return await ctx.send(discord.utils.escape_mentions(answer))

    @commands.command()
    @check_auth
    async def question(self, ctx, *prompt: str):
        usage = len(list("".join(prompt)))
        if usage == 0:
            raise EmptyPromptError
        answer = await self.__api.answer(prompt, language=self.language)
        return await ctx.send(discord.utils.escape_mentions(answer))

    @commands.command()
    @check_auth
    async def generate(self, ctx, *prompt: str):
        usage = len(list("".join(prompt)))
        user_id, user_name = user_parse(ctx)
        if usage == 0:
            raise EmptyPromptError
        answer = await self.__api.generate(prompt, language=self.language)
        return await ctx.send(discord.utils.escape_mentions(answer))

    @commands.command()
    @check_auth
    async def complete(self, ctx, *prompt: str):
        usage = len(list("".join(prompt)))
        user_id, user_name = user_parse(ctx)
        if usage == 0:
            raise EmptyPromptError
        answer = await self.__api.complete(prompt, language=self.language)
        return await ctx.send(discord.utils.escape_mentions(answer))

    @commands.command()
    @check_auth
    async def foulmouth(self, ctx, *prompt: str):
        user_id, user_name = user_parse(ctx)
        usage = len(list("".join(prompt)))
        if usage == 0:
            raise EmptyPromptError
        answer = await self.__api.foulmouth_answer(prompt, language=self.language)
        return await ctx.send(discord.utils.escape_mentions(answer))

    @commands.command()
    @check_auth
    async def sentiment(self, ctx, *prompt: str):
        user_id, user_name = user_parse(ctx)
        usage = len(list("".join(prompt)))
        if usage == 0:
            raise EmptyPromptError
        answer = await self.__api.sentiment(prompt, language=self.language)
        return await ctx.send(discord.utils.escape_mentions(answer))

    @commands.command()
    @check_auth
    async def emojify(self, ctx, *prompt: str):
        user_id, user_name = user_parse(ctx)
        usage = len(list("".join(prompt)))
        if usage == 0:
            raise EmptyPromptError
        answer = await self.__api.emojify(prompt, language=self.language)
        return await ctx.send(discord.utils.escape_mentions(answer))

    @commands.command()
    @check_auth
    async def sarcasm(self, ctx, *prompt: str):
        user_id, user_name = user_parse(ctx)
        usage = len(list("".join(prompt)))
        if usage == 0:
            raise EmptyPromptError
        answer = await self.__api.sarcastic_answer(prompt, language=self.language)
        return await ctx.send(discord.utils.escape_mentions(answer))

    @commands.command()
    @check_auth
    async def headline(self, ctx, *prompt: str):
        user_id, user_name = user_parse(ctx)
        usage = len(list("".join(prompt)))
        if usage == 0:
            raise EmptyPromptError
        answer = await self.__api.headline(prompt, language=self.language)
        return await ctx.send(discord.utils.escape_mentions(answer))

    async def person_talks(self, ctx, *prompt: str):
        await ctx.send("I'm gonna be talking as {} from now on".format(self.personality))
        answer = await self.__api.personality(prompt, self.personality, language=self.language)
        return await ctx.send(discord.utils.escape_mentions(answer))

    @commands.command()
    @check_auth
    @personality
    async def hood(self, ctx, *prompt: str):
        await self.person_talks(ctx,prompt) 

    @commands.command()
    @check_auth
    @personality
    async def pedantic(self, ctx, *prompt: str):
        await self.person_talks(ctx,prompt)

    @commands.command()
    @check_auth
    @personality
    async def bain(self, ctx, *prompt: str):
        await self.person_talks(ctx,prompt)

    @commands.command()
    @check_auth
    async def tldr(self, ctx, *prompt: str):
        user_id, user_name = user_parse(ctx)
        usage = len(list("".join(prompt)))
        if usage == 0:
            raise EmptyPromptError
        answer = await self.__api.tldr(prompt, language=self.language)
        return await ctx.send(discord.utils.escape_mentions(answer))

    @commands.command()
    @commands.guild_only()
    @check_auth
    async def join(self, ctx):
        connected = ctx.author.voice
        if connected:
            await ctx.send("Coming in...")
            try:
                await connected.channel.connect()
            except Exception as e:
                await ctx.send(e)
        else:
            await ctx.send("What channel bro?")

    @commands.command()
    @commands.guild_only()
    @check_auth
    async def leave(self, ctx):
        await ctx.voice_client.disconnect()

    @commands.command()
    async def ping(self, ctx):
        return await ctx.send(discord.utils.escape_mentions("I'm alive and well!"))

    @commands.command()
    async def passcode(self,ctx, *prompt:str):
        if "".join(prompt) == "{}".format(PASSCODE):
            self.authorized = not self.authorized
        message = 'TIENES ACESSO!' if self.authorized else "I won't say anything now. Talk to the hand yo."
        return await ctx.send(message)

if __name__ == "__main__":
    bot.add_cog(GPTBot(bot))
    bot.run(DISCORD_TOKEN)
