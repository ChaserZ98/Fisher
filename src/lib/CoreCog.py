import os

import discord
from discord.app_commands import locale_str, TranslationContextLocation
from discord.ext import commands

from utils.discord_utils import is_owner

class CoreCog(commands.Cog, name='core'):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot
        self.loadable_cog_path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'cogs'))
        self.add_command()

        self.localized_group_name = {
            'sync': {
                'en-US': 'sync',
                'zh-CN': '同步'
            }
        }
        self.localized_command_name = {
            'guild': {
                'en-US': 'guild',
                'zh-CN': '单服'
            },
            'globally': {
                'en-US': 'globally',
                'zh-CN': '全服'
            }
        }
    
    def add_command(self):
        @self.bot.hybrid_group(name=locale_str('sync'), description='Syncronize the slash commands')
        @is_owner(self.bot.config['owners'])
        async def sync(ctx: commands.Context) -> None:
            if ctx.invoked_subcommand is None:
                tokens = ctx.message.content.split(" ")
                if len(tokens) > 1:
                    embed = discord.Embed(
                        description=f"Invalid subcommand: {tokens[1]}",
                        color=0x9C84EF
                    )
                    await ctx.send(embed=embed, ephemeral=True)
                    raise commands.CommandError(f"Invalid subcommand: {tokens[1]}")
                await sync_guild(ctx, guild_id=ctx.guild.id)
        
        @sync.command(name=locale_str('guild'), description='Syncronize slash commands for a specific server, default as the current server')
        async def sync_guild(ctx: commands.Context, guild_id: int=commands.parameter(default=lambda ctx: ctx.guild.id)) -> None:
            guild = self.bot.get_guild(guild_id)
            self.bot.tree.copy_global_to(guild=guild)
            await self.bot.tree.sync(guild=guild)
            embed = discord.Embed(
                description=f"Slash commands have been synchronized in {guild}",
                color=0x9C84EF
            )
            await ctx.send(embed=embed, ephemeral=True)
        
        @sync.command(name=locale_str('globally'), description="Syncronize slash commands across all servers")
        async def sync_globally(ctx: commands.Context):
            await self.bot.tree.sync()
            embed = discord.Embed(
                description="Slash commands have been globally synchronized.",
                color=0x9C84EF
            )
            await ctx.send(embed=embed, ephemeral=True)
        
        # @self.bot.command(name='lang')
        # @discord.app_commands.choices(
        #     lang=[
        #         discord.app_commands.Choice(name='en-US', value=1),
        #         discord.app_commands.Choice(name='zh-CN', value=2)
        #     ]
        # )
        # async def lang(ctx: commands.Context):

        
        @self.bot.command(name='test')
        async def test(ctx: commands.Context) -> None:
            ctx.author

        # @self.bot.hybrid_command(name='enable')
        # @discord.app_commands.describe(cog_name="additional cog you want to enable")
        # @is_owner(self.bot.config['owners'])
        # async def enable_cog(self, ctx, *, cog_name: str):
        #     cog_name = cog_name.lower()

    

async def setup(bot: commands.Bot):
    corecog = CoreCog(bot)
    await bot.add_cog(corecog)
    bot.tree.translator.update_corpus(TranslationContextLocation.group_name, corecog.localized_group_name)
    bot.tree.translator.update_corpus(TranslationContextLocation.command_name, corecog.localized_command_name)

# if __name__ == '__main__':
#     print(os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'cogs')))
#     print(os.listdir(os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'cogs'))))