import discord
from discord.ext import commands
import SharkBot


class SharkError(Exception):

    # noinspection PyUnusedLocal
    @staticmethod
    async def handler(ctx: commands.Context) -> bool:
        return False


class MemberFileNotFoundError(SharkError):
    pass


class AccountAlreadyLinkedError(SharkError):
    pass


class AccountNotLinkedError(SharkError):
    pass


class AccountAlreadyInUseError(SharkError):
    pass


class ItemNotInInventoryError(SharkError):
    pass


class ItemNotInCollectionError(SharkError):
    pass


class CollectionNotFoundError(SharkError):

    def __init__(self, search: str):
        self.search = search

    async def handler(self, ctx: commands.Context) -> bool:
        embed = discord.Embed()
        embed.title = "Collection Not Found"
        embed.description = f"I'm afraid I couldn't find `{self.search.title()}`"
        similar = SharkBot.Utils.get_similar_collections(self.search)
        if similar is not None:
            embed.description += f"\nDid you mean `{similar.title()}`?"
        embed.colour = discord.Colour.red()
        await ctx.reply(embed=embed, mention_author=False)

        return True


class RarityNotFoundError(SharkError):
    pass


class ItemNotFoundError(SharkError):

    def __init__(self, search: str):
        self.search = search

    async def handler(self, ctx: commands.Context) -> bool:
        embed = discord.Embed()
        embed.title = "Item Not Found"
        embed.description = f"I'm afraid I couldn't find `{self.search.title()}`"
        similar = SharkBot.Utils.get_similar_items(self.search)
        if similar is not None:
            embed.description += f"\nDid you mean `{similar.title()}`?"
        embed.colour = discord.Colour.red()
        await ctx.reply(embed=embed, mention_author=False)

        return True


class TestError(SharkError):
    pass


class MissionNotFoundError(SharkError):
    pass


class MissionTypeNotFoundError(SharkError):
    pass


class LootpoolNotFoundError(SharkError):
    pass


class UnknownLootpoolNodeType(SharkError):
    pass


class InvalidCodeError(SharkError):

    def __init__(self, code: str):
        self.code = code

    async def handler(self, ctx: commands.Context) -> bool:
        await ctx.send(f"That is not a valid code to redeem!")

        return True


class CodeAlreadyExistsError(SharkError):

    def __init__(self, search: str):
        self.search = search

    async def handler(self, ctx: commands.Context) -> bool:
        await ctx.send(f"Code `{self.search}` already exists")

        return True


class CodeDoesNotExistError(SharkError):

    def __init__(self, search: str):
        self.search = search

    async def handler(self, ctx: commands.Context) -> bool:
        await ctx.send(f"Code `{self.search}` does not exist!")

        return True


class ZIPBackup:

    class BackupDoesNotExistError(SharkError):
        pass


class BankBalanceBelowZeroError(SharkError):
    pass

class BalanceBelowZeroError(SharkError):
    pass

class ItemNotInVaultError(SharkError):
    pass

class Effects:

    class InvalidEffectDataError(SharkError):
        pass

    class EffectNotActiveError(SharkError):
        pass

    class NotEnoughChargesError(SharkError):
        pass

    class EffectDoesNotHaveChargesError(SharkError):
        pass

    class InvalidSizeError(SharkError):
        pass

    class UnknownConsumableError(SharkError):
        pass


class BungieAPI:

    class InternalServerError(SharkError):

        async def handler(self, ctx: commands.Context) -> bool:
            embed = discord.Embed()
            embed.title = "Something went wrong!"
            embed.colour = discord.Colour.red()
            embed.description = f"Something's fucky with the backend, I've told <@220204098572517376> to have a look!"
            await ctx.reply(embed=embed)

            return True


    class SetupNeededError(SharkError):
        def __init__(self, member_id: int):
            self.member_id = member_id

        async def handler(self, ctx: commands.Context) -> bool:
            embed = discord.Embed()
            embed.title = "Bungie not Authorised!"
            embed.colour = discord.Colour.blurple()
            embed.description = f"You need to authorise SharkBot with Bungie to get this data! Use </bungie_auth:1079377403295563837> to get started!"
            await ctx.reply(embed=embed)

            return True


class SourceNotFoundError(SharkError):

    def __init__(self, search: str):
        self.search = search

    async def handler(self, ctx: commands.Context) -> bool:
        embed = discord.Embed()
        embed.title = "Source Not Found!"
        embed.description = f"I'm afraid I couldn't find `{self.search}` as a choice for red border weapons!"
        embed.colour = discord.Colour.red()
        await ctx.reply(embed=embed, mention_author=False)

        return True


class LeaderboardNotFoundError(SharkError):

    def __init__(self, search: str):
        self.search = search

    async def handler(self, ctx: commands.Context) -> bool:
        embed = discord.Embed()
        embed.title = "Leaderboard Not Found!"
        embed.description = f"I'm afraid I couldn't find `{self.search}` as a leaderboard!"
        embed.add_field(
            name="__Available Leaderboards__",
            value="\n".join(f"- `{lb.name}`" for lb in SharkBot.Leaderboard.Leaderboard.leaderboards)
        )
        embed.colour = discord.Colour.red()
        await ctx.reply(embed=embed, mention_author=False)

        return True


class ItemIsNotLootboxError(SharkError):
    pass


class ItemIsNotConsumableError(SharkError):
    pass


class CountBoxMessageExistsError(SharkError):
    pass




class Manifest:

    class ManifestNotFoundError(SharkError):
        pass

    class DefinitionDoesNotExistError(SharkError):
        pass

    class DefinitionFileNotFoundError(SharkError):
        pass

    class HashNotFoundError(SharkError):
        pass

    class FetchFailedError(SharkError):

        def __init__(self, file: str, status: int):
            self.file = file
            self.status = status