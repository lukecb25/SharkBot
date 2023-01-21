import discord
from datetime import datetime, date, time, timedelta
from discord.ext import commands, tasks

import SharkBot


class Destiny(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.check_tokens.start()
        self.reset.start()

    def cog_unload(self) -> None:
        self.reset.cancel()
        self.check_tokens.cancel()

    @tasks.loop(time=time(hour=13))
    async def check_tokens(self):
        for member in SharkBot.Member.members:
            if member.bungie.refresh_token_expiring:
                await member.bungie.soft_refresh()
                dev = self.bot.get_user(SharkBot.IDs.dev)
                if dev is None:
                    dev = await self.bot.fetch_user(SharkBot.IDs.dev)
                await dev.send(f"Performed auto-token refresh for {member.id}")


    @tasks.loop(time=SharkBot.Destiny.reset_time)
    async def reset(self) -> None:
        channel = await self.bot.fetch_channel(SharkBot.IDs.channels["Destiny Reset"])
        embeds = SharkBot.Destiny.Reset.get_embeds()
        for embed in embeds:
            await channel.send(embed=embed)

    @commands.hybrid_group()
    async def destiny(self, ctx: commands.Context) -> None:
        await ctx.send("Destiny Command")

    @destiny.command()
    @commands.has_role(SharkBot.IDs.roles["Mod"])
    async def send_embeds(self, ctx: commands.Context, channel: discord.TextChannel, include_weekly: bool = False):
        await ctx.send("Sending Destiny Reset Embeds")
        if channel.id == SharkBot.IDs.channels["Destiny Reset"]:
            await ctx.send("Deleting old embeds")
            async for message in channel.history(limit=10, after=(datetime.today() - timedelta(days=1))):
                if message.author.id != SharkBot.IDs.users["SharkBot"]:
                    continue
                await message.delete()
        embeds = SharkBot.Destiny.Reset.get_embeds(include_weekly)
        for embed in embeds:
            await channel.send(embed=embed)

    @destiny.command(
        description="Shows info about today's active Lost Sector"
    )
    async def sector(self, ctx: commands.Context) -> None:
        current_sector = SharkBot.Destiny.LostSector.get_current()
        reward = SharkBot.Destiny.LostSectorReward.get_current()

        if current_sector is None:
            embed = discord.Embed()
            embed.title = "Today's Lost Sector"
            embed.description = "Lost Sector Unknown (Season just started)"
            embed.set_thumbnail(
                url="https://www.bungie.net/common/destiny2_content/icons/6a2761d2475623125d896d1a424a91f9.png"
            )
            await ctx.reply(embed=embed)
            return

        embed = discord.Embed()
        embed.title = f"{current_sector.name}\n{current_sector.destination}"
        embed.description = f"{current_sector.burn} Burn {reward}"
        embed.set_thumbnail(
            url="https://www.bungie.net/common/destiny2_content/icons/6a2761d2475623125d896d1a424a91f9.png"
        )
        embed.add_field(
            name="Legend <:light_icon:1021555304183386203> 1580",
            value=f"{current_sector.legend.details}"
        )
        embed.add_field(
            name="Master <:light_icon:1021555304183386203> 1610",
            value=f"{current_sector.master.details}"
        )

        await ctx.send(embed=embed)

    @destiny.command(
        description="Shows info about today's Nightfall"
    )
    @discord.app_commands.choices(
        nightfall=[
            discord.app_commands.Choice(name=nf.name, value=nf.name) for nf in SharkBot.Destiny.Nightfall.nightfalls
        ]
    )
    async def nightfall(self, ctx: commands.Context, nightfall: str = SharkBot.Destiny.Nightfall.get_current().name):
        current_nightfall = SharkBot.Destiny.Nightfall.get(nightfall)

        if current_nightfall is None:
            embed = discord.Embed()
            embed.title = "This Week's Nightfall"
            embed.description = "Nightfall Rotation Unknown (Season just started)"
            embed.set_thumbnail(
                url="https://www.bungie.net/common/destiny2_content/icons/a72e5ce5c66e21f34a420271a30d7ec3.png"
            )
            await ctx.reply(embed=embed, mention_author=False)
            return

        embed = discord.Embed()
        embed.title = f"{current_nightfall.name}\n{current_nightfall.destination}"
        embed.set_thumbnail(
            url="https://www.bungie.net/common/destiny2_content/icons/a72e5ce5c66e21f34a420271a30d7ec3.png"
        )
        embed.add_field(
            name="Legend <:light_icon:1021555304183386203> 1580",
            value=f"{current_nightfall.legend.details}"
        )
        embed.add_field(
            name="Master <:light_icon:1021555304183386203> 1610",
            value=f"{current_nightfall.master.details}"
        )

        await ctx.send(embed=embed)

    @destiny.command(
        description="Shows info about this season's GMs"
    )
    async def grandmaster(self, ctx: commands.Context) -> None:
        current = SharkBot.Destiny.Nightfall.get_current()

        if datetime.utcnow() < date(2023, 1, 17):
            embed = discord.Embed()
            embed.title = "Grandmaster Nightfalls"
            embed.description = "Grandmaster Nightfalls release on January 17th, 2023"
            await ctx.reply(embed=embed, mention_author=False)
            return

        embed = discord.Embed()
        embed.title = "Grandmaster Nightfalls"
        embed.description = f"Power Level Requirement: <:light_icon:1021555304183386203>1605"
        embed.colour = discord.Colour.dark_red()

        embed.add_field(
            name=f"{current.name} - {current.destination} (This Week)",
            value=current.gm_icons,
            inline=False
        )

        for nightfall in SharkBot.Destiny.Nightfall.rotation_from(current)[:5]:
            embed.add_field(
                name=f"{nightfall.name} - {nightfall.destination}",
                value=nightfall.gm_icons,
                inline=False
            )

        await ctx.reply(embed=embed, mention_author=False)

    @destiny.command(
        hidden=True
    )
    async def sector_list(self, ctx: commands.Context) -> None:
        embed = discord.Embed()
        embed.title = "Lost Sectors"
        embed.set_thumbnail(
            url="https://www.bungie.net/common/destiny2_content/icons/6a2761d2475623125d896d1a424a91f9.png"
        )
        for lostSector in SharkBot.Destiny.LostSector.lost_sectors:
            embed.add_field(
                name=f"{lostSector.name} - {lostSector.destination}",
                value=f"Champions: *{lostSector.champion_list}*\nShields: *{lostSector.shield_list}*",
                inline=False
            )

        await ctx.send(embed=embed)

    @destiny.command(
        description="Gives details about the current Season"
    )
    async def season(self, ctx: commands.Context) -> None:
        season = SharkBot.Destiny.Season.current
        embed = discord.Embed()
        embed.title = f"Season {season.number} - {season.name}"
        embed.description = f"**{season.calendar_string}**\n{season.time_remaining_string} left in the Season"
        embed.set_thumbnail(
            url=season.icon
        )

        await ctx.reply(embed=embed, mention_author=False)

    @destiny.command(
        description="Gives a countdown to the release of Lightfall"
    )
    async def countdown(self, ctx: commands.Context) -> None:
        embed = discord.Embed()
        embed.title = "Lightfall Countdown"
        embed.description = SharkBot.Destiny.lightfall_countdown.time_remaining_string
        embed.description += "until Lightfall releases"
        embed.add_field(
            name="Release Date",
            value="28th February 2023 (Also Chaos' 21st Birthday!)"
        )

        await ctx.reply(embed=embed, mention_author=False)

    @destiny.command(
        description="Gives information about this week's raids."
    )
    async def raid(self, ctx: commands.Context) -> None:
        seasonal = SharkBot.Destiny.Raid.seasonal
        featured = SharkBot.Destiny.Raid.get_current()

        embed = discord.Embed()
        embed.title = "Raids"
        embed.set_thumbnail(
            url="https://www.bungie.net/common/destiny2_content/icons/9230cd18bcb0dd87d47a554afb5edea8.png"
        )
        embed.add_field(
            name="Seasonal",
            value=seasonal.name,
            inline=False
        )
        embed.add_field(
            name="Featured",
            value=featured.name,
            inline=False
        )

        await ctx.reply(embed=embed, mention_author=False)

    @destiny.command(
        description="Gives information about this week's dungeons."
    )
    async def dungeon(self, ctx: commands.Context) -> None:
        seasonal = SharkBot.Destiny.Dungeon.seasonal
        featured = SharkBot.Destiny.Dungeon.get_current()

        embed = discord.Embed()
        embed.title = "Dungeons"
        embed.set_thumbnail(
            url="https://www.bungie.net/common/destiny2_content/icons/082c3d5e7a44343114b5d056c3006e4b.png"
        )
        embed.add_field(
            name="Seasonal",
            value=seasonal.name,
            inline=False
        )
        embed.add_field(
            name="Featured",
            value=featured.name,
            inline=False
        )

        await ctx.reply(embed=embed, mention_author=False)

    @destiny.command(
        description="Gives the XP requirements for the given artifact power bonus."
    )
    async def bonus(self, ctx: commands.Context, level: int):
        embed = discord.Embed()
        embed.title = "Artifact Power Bonus"
        embed.colour = discord.Colour.teal()
        embed.set_thumbnail(
            url="https://www.bungie.net/common/destiny2_content/icons/7b513c9215111507dbf31e3806cc1fcf.jpg"
        )

        def calc_xp(targetlevel: int) -> int:
            return ((targetlevel-2) * 110000) + 55000

        if level < 1:
            embed.description = "Power Bonus must be greater than zero, dangus"
        else:
            if level == 1:
                embed.description = "+1 given by default"
                bonus_range = list(range(2, 6))
            else:
                bonus_range = list(range(level, level+5))

            for lvl in bonus_range:
                xp = calc_xp(lvl)
                total_xp = sum([calc_xp(x) for x in range(2, lvl+1)])
                embed.add_field(
                    name=f"`+{'{:,}'.format(lvl)}` Bonus",
                    value=f"`{'{:,}'.format(xp)}` xp\n`{'{:,}'.format(total_xp)}` xp total",
                    inline=False
                )

        await ctx.send(embed=embed)

    @destiny.command(
        description="Authorizes SharkBot to get your Destiny 2 data from Bungie"
    )
    async def auth(self, ctx: commands.Context):
        embed = discord.Embed()
        embed.title = "Bungie Auth"
        embed.description = "In order to fetch your Destiny 2 Profile, you need to authorize SharkBot with Bungie\n"
        embed.description += "The link below will take you to the SharkBot OAuth2 portal, where you can sign in with your Bungie Account"
        embed.add_field(
            name="Bungie Auth Link",
            value=f"https://sharkbot.online/bungie_auth/discord/{ctx.author.id}"
        )

        await ctx.author.send(embed=embed)
        if ctx.channel.id != ctx.author.id:
            await ctx.reply("Check your DMs, I've sent you a link to Authorize SharkBot with Bungie's API")

    @destiny.command(
        description="De-Authorizes SharkBot from your Bungie Account"
    )
    async def deauth(self, ctx: commands.Context):
        member = SharkBot.Member.get(ctx.author.id)
        embed = discord.Embed()
        embed.title = "Bungie Deauthentication"
        embed.description = "Removing credentials from SharkBot..."
        embed.colour = discord.Colour.blurple()

        reply_message = await ctx.reply(embed=embed, mention_author=False)

        exists = member.bungie.delete_credentials()
        if exists:
            embed.description = "Removed Bungie Authentication."
            embed.colour = discord.Colour.green()
        else:
            embed.description = "Your Bungie Account is already not authorised with SharkBot"
            embed.colour = discord.Colour.red()

        await reply_message.edit(embed=embed)


    @destiny.command(
        description="Shows your Progress with your craftable weapons"
    )
    async def patterns(self, ctx: commands.Context, season: str = "*"):
        season = season.lower()
        if season == "*":
            seasons = [16, 17, 18, 19]
        elif season in ["16", "risen"]:
            seasons = [16]
        elif season in ["17", "haunted"]:
            seasons = [17]
        elif season in ["18", "plunder"]:
            seasons = [18]
        elif season in ["19", "seraph"]:
            seasons = [19]
        else:
            await ctx.reply(f"`{season}` is not a valid season for craftable weapons!")
            return
        member = SharkBot.Member.get(ctx.author.id)
        embed = discord.Embed()
        embed.title = "Fetching..."
        embed.description = "Fetching your Destiny Profile Data..."
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        message = await ctx.reply(embed=embed, mention_author=False)
        responses_dict = await member.bungie.get_craftables_data()
        output = {}
        for weapon_type, responses in responses_dict.items():
            data = []
            for response in responses:
                if response.weapon_season not in seasons:
                    continue
                if not response.complete:
                    data.append(f"{SharkBot.Icon.get('season_' + str(response.weapon_season))} **{response.weapon_name}** - {response.progress}/{response.quota}")
            output[weapon_type] = data
        for weapon_type, data in output.items():
            if len(data) == 0:
                embed.add_field(
                    name=f"__{weapon_type}__",
                    value=f"You have finished all your **{weapon_type}**!",
                    inline=False
                )
            else:
                embed.add_field(
                    name=f"__{weapon_type}__",
                    value="\n".join(data),
                    inline=False
                )
        embed.title = "Weapon Patterns"
        for e in SharkBot.Utils.split_embeds(embed):
            await ctx.reply(embed=e, mention_author=False)
        await message.delete()


    @destiny.command(
        description="Shows your Progress with your craftable weapons"
    )
    async def monument(self, ctx: commands.Context, *, year: str = "*"):
        year = year.lower()
        if year == "*":
            years = ["1", "2", "3", "4", "5"]
        elif year in ["1", "one", "rw", "red war"]:
            years = ["1"]
        elif year in ["2", "two", "forsaken"]:
            years = ["2"]
        elif year in ["3", "three", "shadowkeep"]:
            years = ["3"]
        elif year in ["4", "four", "beyond", "beyond light"]:
            years = ["4"]
        elif year in ["5", "five", "wq", "witch queen"]:
            years = ["5"]
        else:
            await ctx.reply(f"`{year}` is not a valid Year for me to look for!")
            return
        member = SharkBot.Member.get(ctx.author.id)
        embed = discord.Embed()
        embed.title = "Fetching..."
        embed.description = "Fetching your Destiny Profile Data..."
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        message = await ctx.reply(embed=embed, mention_author=False)
        monument_dict = await member.bungie.get_monument_data()
        output = {}
        for year_num, year_data in monument_dict.items():
            data = []
            if year_num not in years:
                continue
            for weapon_name, owned in year_data.items():
                if not owned:
                    data.append(f"- {weapon_name}")
            output[year_num] = data
        for year_num, data in output.items():
            if len(data) == 0:
                embed.add_field(
                    name=f"__**Year {year_num}**__",
                    value=f"*You have finished all your **Year {year_num}** Exotics!*",
                    inline=False
                )
            else:
                embed.add_field(
                    name=f"__**Year {year_num}**__",
                    value="\n".join(data),
                    inline=False
                )
        embed.title = "Monument to lost light"
        for e in SharkBot.Utils.split_embeds(embed):
            await ctx.reply(embed=e, mention_author=False)
        await message.delete()



async def setup(bot):
    await bot.add_cog(Destiny(bot))
    print("Destiny Cog loaded")


async def teardown(bot):
    print("Destiny Cog unloaded")
    await bot.remove_cog(Destiny(bot))
