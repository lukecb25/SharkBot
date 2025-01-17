import os.path
from typing import Optional, Any
import discord
from discord.ext import commands

import SharkBot

_PARENT_CACHE_FOLDER = "data/live/bungie/cache"

class BungieData:
    _COMPONENTS = [0]
    _LOADING_ICON_URL = "https://cdn.dribbble.com/users/2081/screenshots/4645074/loading.gif"
    _THUMBNAIL_URL = None
    _EMBED_COLOUR = None
    _EMBED_TITLE = None

    def __init__(self, member):
        self.member: SharkBot.Member.Member = member
        self._cached_data: Optional[Any] = None

    # Change in Subclass

    @staticmethod
    def _process_data(data):
        return data

    @staticmethod
    def _process_cache_write(data):
        return data

    @staticmethod
    def _process_cache_load(data):
        return data

    @classmethod
    def _format_cache_embed_data(cls, embed: discord.Embed, data, **kwargs):
        cls._format_embed_data(embed, data, **kwargs)

    @staticmethod
    def _format_embed_data(embed: discord.Embed, data, **kwargs):
        embed.description = f"\n```{SharkBot.Utils.JSON.dumps(data)}```"

    # Caching Methods

    @classmethod
    def _cache_folder_path(cls) -> str:
        return f"{_PARENT_CACHE_FOLDER}/{cls.__name__.lower()}"

    @property
    def _cache_file(self) -> str:
        return f"{self._cache_folder_path()}/{self.member.id}.json"

    def get_cache(self) -> Optional[Any]:
        if self._cached_data is None:
            if os.path.isfile(self._cache_file):
                self._cached_data = self._process_cache_load(SharkBot.Utils.JSON.load(self._cache_file))
        return self._cached_data

    def write_cache(self, data):
        self._cached_data = data
        SharkBot.Utils.JSON.dump(self._cache_file, self._process_cache_write(data))

    def wipe_cache(self):
        if os.path.isfile(self._cache_file):
            os.remove(self._cache_file)

    # Data Fetching

    async def fetch_data(self, write_cache: bool = True):
        data = await self.member.bungie.get_profile_response(*self._COMPONENTS)
        data = self._process_data(data)
        if write_cache:
            self.write_cache(data)
        return data

    # Embeds

    @property
    def _embed_title(self) -> str:
        if self._EMBED_TITLE is None:
            return self.__class__.__name__
        else:
            return self._EMBED_TITLE

    def generate_cache_embed(self, ctx: commands.Context, **kwargs) -> discord.Embed:
        embed = discord.Embed()
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
        cached_data = self.get_cache()
        if cached_data is not None:
            try:
                self._format_cache_embed_data(embed, cached_data, **kwargs)
            except Exception:
                pass
        embed.title=f"Fetching {self._embed_title} Data..."
        embed.description="Data may be outdated until I fetch the updated data."
        embed.set_thumbnail(url=self._LOADING_ICON_URL)
        return embed

    async def generate_embed(self, ctx: commands.Context, **kwargs) -> discord.Embed:
        embed = discord.Embed(
            title=self._embed_title
        )
        embed.set_thumbnail(url=self._THUMBNAIL_URL)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
        embed.colour = self._EMBED_COLOUR
        data = await self.fetch_data()
        self._format_embed_data(embed, data, **kwargs)
        return embed

    async def send_embeds(self, ctx: commands.Context, **kwargs):
        cache_embed = self.generate_cache_embed(ctx, **kwargs)
        messages = await SharkBot.Utils.Embed.reply(cache_embed, ctx)
        try:
            data_embed = await self.generate_embed(ctx, **kwargs)
            await SharkBot.Utils.Embed.reply_with_replace(data_embed, ctx, messages)
        except (SharkBot.Errors.BungieAPI.InternalServerError, SharkBot.Errors.BungieAPI.TokenRefreshFailedError) as e:
            raise SharkBot.Errors.BungieAPI.FollowupMessageError(ctx, cache_embed, messages, e, self)