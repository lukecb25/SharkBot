from datetime import datetime, timedelta, time

import discord
from discord.ext import tasks, commands

import random

from humanize import number

import SharkBot


import logging

cog_logger = logging.getLogger("cog")

class Fun(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.check_birthdays.start()

    def cog_unload(self) -> None:
        self.check_birthdays.cancel()

    @commands.hybrid_command(
        aliases=["cf"],
        brief="Bet an amount of SharkCoins on a coin flip to get double or nothing back!"
    )
    async def coinflip(self, ctx, amount: int) -> None:
        member = SharkBot.Member.get(ctx.author.id, discord_user=ctx.author)
        embed = discord.Embed()
        embed.title = "Coin Flip"
        embed.description = f"You bet **${amount:,}**!"
        embed.set_thumbnail(url="https://i.pinimg.com/originals/d7/49/06/d74906d39a1964e7d07555e7601b06ad.gif")

        if amount < 0:
            embed.colour = discord.Color.red()
            embed.add_field(
                name="Negative Bet!",
                value="You can't bet a negative amount of money!"
            )
            await ctx.reply(embed=embed)
            return

        if amount == 0:
            embed.colour = discord.Color.red()
            embed.add_field(
                name="Zero Bet!",
                value="You can't bet zero SharkCoins!!"
            )
            await ctx.reply(embed=embed)
            return

        if member.balance < amount:
            embed.colour = discord.Color.red()
            embed.add_field(
                name="Not Enough Money!",
                value=f"You don't have **${amount:,}**!"
            )
            await ctx.reply(embed=embed)
            return

        roll = random.randint(1, 16)
        if roll <= 7:  # Win
            member.balance += amount
            member.stats.coinflips.wins += 1
            embed.colour = discord.Color.green()
            embed.add_field(
                name="You win!",
                value=f"You won **${amount:,}**!"
            )
        elif roll <= 9:  # Mercy Loss
            embed.colour = discord.Color.blurple()
            member.stats.coinflips.mercies += 1
            embed.add_field(
                name="You lose!",
                value=f"You lost, but I'm feeling nice, so I'll let you keep your money!"
            )
        else:  # Loss
            member.balance -= amount
            member.stats.coinflips.losses += 1
            embed.colour = discord.Color.dark_red()
            embed.add_field(
                name="You lose!",
                value=f"You lost **${amount:,}**!"
            )
        await ctx.reply(embed=embed)
        await member.missions.log_action("coinflip", ctx, amount)

    @commands.hybrid_group()
    async def birthday(self, ctx: commands.Context):
        member = SharkBot.Member.get(ctx.author.id, discord_user=ctx.author)
        date = datetime.now().date()

        embed = discord.Embed()
        embed.title = "Birthday"
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)

        if member.birthday is None:
            embed.description = "Your birthday is not set! Set it with *$birthday set `dd` `mm` `yyyy`*."
        elif date == member.birthday:
            embed.description = "Your birthday is today! Happy Birthday!!!"
        else:
            embed.description = f"Your birthday is set to `{datetime.strftime(member.birthday, SharkBot.Member.BIRTHDAY_FORMAT)}`"

        await ctx.send(embed=embed)

    @birthday.command()
    async def set(self, ctx: commands.Context, day: int, month: int, year: int):
        member = SharkBot.Member.get(ctx.author.id, discord_user=ctx.author)

        embed = discord.Embed()
        embed.title = "Set Birthday"
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)

        if len(str(year)) != 4:
            embed.description = "Please use the format `dd` `mm` `yyyy`"
            await ctx.send(embed=embed)
            return

        try:
            member.birthday = datetime(year, month, day).date()
            embed.description = f"Set your Birthday to `{datetime.strftime(member.birthday, SharkBot.Member.BIRTHDAY_FORMAT)}`."
            await ctx.send(embed=embed)
        except ValueError:
            embed.description = "Please enter a valid date."
            await ctx.send(embed=embed)

    @tasks.loop(time=time(hour=12))
    async def check_birthdays(self):
        today = datetime.today()
        presents = [
            SharkBot.Item.get("LOOTSHARK"),
            SharkBot.Item.get("LOOTSHARK"),
            SharkBot.Item.get("LOOTSHARK"),
            SharkBot.Item.get("LOOTM"),
            SharkBot.Item.get("E10")
        ]
        channel = await self.bot.fetch_channel(SharkBot.IDs.channels["SharkBot Commands"])

        for member in SharkBot.Member.members:
            if member.birthday is None:
                continue
            if member.birthday.day == today.day and member.birthday.month == today.month:
                if member.lastClaimedBirthday < today.year:
                    member.lastClaimedBirthday = today.year
                    responses = member.inventory.add_items(presents)
                    member.write_data()
                    age = number.ordinal(today.year - member.birthday.year)
                    user = await channel.guild.fetch_member(member.id)

                    embed = discord.Embed()
                    embed.title = "Birthday Time!"
                    embed.description = f"It's **{user.display_name}**'s {age} Birthday! I got them:\n"
                    embed.description += "\n".join(str(response) for response in responses)
                    embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)

                    await channel.send(f"{user.mention}", embed=embed)

    @commands.hybrid_command()
    async def remind_me(self, ctx: commands.Context, minutes: int, message: str):
        await ctx.reply("Noted.", mention_author=False)
        await discord.utils.sleep_until(datetime.now() + timedelta(minutes=minutes))
        await ctx.send(f"{ctx.author.mention}\n\"{message}\"")


async def setup(bot):
    await bot.add_cog(Fun(bot))
    print("Fun Cog Loaded")
    cog_logger.info("Fun Cog Loaded")


async def teardown(bot):
    await bot.remove_cog(Fun(bot))
    print("Fun Cog Unloaded")
    cog_logger.info("Fun Cog Unloaded")