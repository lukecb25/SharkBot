import random
from datetime import timedelta, datetime

import discord
from discord.ext import tasks, commands

import SharkBot

class Effects(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command()
    async def effects(self, ctx: commands.Context):
        member = SharkBot.Member.get(ctx.author.id)

        embed = discord.Embed()
        embed.title = f"{ctx.author.display_name}'s Effects"
        embed.set_thumbnail(
            url=ctx.author.display_avatar.url
        )
        effects = member.effects.details
        if len(effects) > 0:
            embed.description = f"You have `{len(effects)}` effects active."
            for effect in effects:
                embed.add_field(
                    name=effect[0],
                    value=effect[1],
                    inline=False
                )
        else:
            embed.description = "You have no active effects."

        for e in SharkBot.Utils.split_embeds(embed):
            await ctx.reply(embed=e, mention_author=False)

    @commands.command()
    async def use(self, ctx: commands.Context, item: str, num: int = 1):
        member = SharkBot.Member.get(ctx.author.id)
        item = SharkBot.Item.search(item)
        if num < 1:
            await ctx.reply(f"You can't use `{num}` of something!")
            return
        if item.type != "Consumable":
            await ctx.reply(f"**{item}** is not a consumable item!")
            return
        has_count = member.inventory.count(item)
        if has_count == 0:
            await ctx.reply(f"I'm afraid you don't have any **{item}**!")
            return
        elif has_count < num:
            await ctx.reply(f"I'm afraid you only have **{has_count}x {item}**!")
            return

        for i in range(num):
            member.inventory.remove(item)

        embed = discord.Embed()
        embed.title = f"{ctx.author.display_name} used {num}x {item}"

        if item.name == "Loaded Dice":
            _UseHandler.use_loaded_dice(member, embed, num)
        if item.name == "Counting Charm":
            _UseHandler.use_counting_charm(member, embed, num)
        elif item.name == "Binder":
            _UseHandler.use_binder(member, embed)
        elif item.name == "God's Binder":
            _UseHandler.use_god_binder(member, embed)
        elif item.name == "Lucky Clover":
            _UseHandler.use_lucky_clover(member, embed, num)
        elif item.name.startswith("Money Bag"):
            size = item.name.split(" ")[-1][1:-1]
            _UseHandler.use_money_bag(member, embed, size, num)
        elif item.name.startswith("Overclocker"):
            _UseHandler.use_overclocker(member, embed, num, item.name)
        elif item.name.startswith("XP Elixir"):
            size = item.name.split(" ")[-1][1:-1]
            _UseHandler.use_xp_elixir(member, embed, size, num)
        else:
            raise SharkBot.Errors.Effects.UnknownConsumableError(item.id, item.name)

        await ctx.reply(embed=embed, mention_author=False)
        member.write_data()


class _UseHandler:

    @staticmethod
    def use_loaded_dice(member: SharkBot.Member.Member, embed: discord.Embed, num: int):
        member.effects.add("Loaded Dice", charges=num)
        embed.description = f"You now have `{member.effects.get('Loaded Dice').charges}x` Active"

    @staticmethod
    def use_binder(member: SharkBot.Member.Member, embed: discord.Embed):
        embed.description = "You used a Binder. Fuck you, I haven't implemented that yet."

    @staticmethod
    def use_god_binder(member: SharkBot.Member.Member, embed: discord.Embed):
        embed.description = "You used a God's Binder. Fuck you, I haven't implemented that yet."

    @staticmethod
    def use_money_bag(member: SharkBot.Member.Member, embed: discord.Embed, size: str, num: int):
        if size == "Small":
            low = 5
            high = 10
            hours = 1
        elif size == "Medium":
            low = 10
            high = 25
            hours = 2
        elif size == "Large":
            low = 25
            high = 50
            hours = 4
        elif size == "Huge":
            low = 50
            high = 100
            hours = 8
        elif size == "Ultimate":
            low = 100
            high = 250
            hours = 16
        else:
            raise SharkBot.Errors.Effects.InvalidSizeError("Money Bag", size)

        amount = sum(random.randint(low, high) for i in range(0, num))
        hours = hours * num
        member.balance += amount
        member.effects.add("Money Bag", expiry=timedelta(hours=hours))
        embed.description = f"You got **${amount}**, and will gain triple money from counting for a bonus `{hours} Hours`"

    @staticmethod
    def use_xp_elixir(member: SharkBot.Member.Member, embed: discord.Embed, size: str, num: int) -> int:
        if size == "Small":
            low = 1
            high = 3
            hours = 1
        elif size == "Medium":
            low = 3
            high = 5
            hours = 2
        elif size == "Large":
            low = 5
            high = 7
            hours = 4
        elif size == "Huge":
            low = 7
            high = 10
            hours = 8
        elif size == "Ultimate":
            low = 11
            high = 20
            hours = 16
        else:
            raise SharkBot.Errors.Effects.InvalidSizeError("XP Elixir", size)

        amount = sum(random.randint(low, high) for i in range(0, num))
        hours = hours * num
        member.effects.add("XP Elixir", expiry=timedelta(hours=hours))
        embed.description = f"You got `{amount} xp`, and will gain double XP from counting for a bonus `{hours} Hours`"
        return amount

    @staticmethod
    def use_lucky_clover(member: SharkBot.Member.Member, embed: discord.Embed, num: int):
        member.effects.add("Lucky Clover", charges=num)
        embed.description = "Whenever a correct count would not give you a Lootbox, you will instead be guaranteed one, and spend one **Lucky Clover** charge."
        embed.description += f"\nYou now have `{member.effects.get('Lucky Clover').charges} Charges`"

    @staticmethod
    def use_overclocker(member: SharkBot.Member.Member, embed: discord.Embed, num: int, name: str):
        index = _overclocker_order.index(name)
        sub_effects = _overclocker_order[index+1:]
        if len(sub_effects) == 0:
            sub_effects = None

        hours = 4 * num
        member.effects.add(name, expiry=timedelta(hours=hours), sub_effects=sub_effects)
        until = member.effects.get(name).expiry - datetime.utcnow()
        embed.description = f"Each count for an additional `{hours} Hours` will reduce your cooldowns.\n"
        embed.description += "Any Overclocker of a lesser power will be paused until this one ends.\n"
        embed.description += f"**{name}** will be active for the next `{SharkBot.Utils.td_to_string(until)}`"

    @staticmethod
    def use_counting_charm(member: SharkBot.Member.Member, embed: discord.Embed, num: int):
        member.effects.add("Counting Charm", charges=num)
        embed.description = "When you count correctly, you will be guaranteed an item you have not collected, and spend one **Counting Charm** charge."
        embed.description += f"\nYou now have `{member.effects.get('Counting Charm').charges} Charges`"



_overclocker_order = [
    "Overclocker (Ultimate)",
    "Overclocker (Huge)",
    "Overclocker (Large)",
    "Overclocker (Medium)",
    "Overclocker (Small)"
]

async def setup(bot):
    await bot.add_cog(Effects(bot))
    print("Effects Cog loaded")


async def teardown(bot):
    print("Effects Cog unloaded")
    await bot.remove_cog(Effects(bot))
