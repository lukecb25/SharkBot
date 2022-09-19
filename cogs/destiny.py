import discord
from discord.ext import commands

import SharkBot


class Destiny(commands.Cog):

	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot

	@commands.hybrid_group()
	async def destiny(self, ctx: commands.Context) -> None:
		await ctx.send("Destiny Command")

	@destiny.command()
	async def sector(self, ctx: commands.Context) -> None:
		currentSector = SharkBot.Destiny.LostSector.get_current()
		reward = SharkBot.Destiny.LostSectorReward.get_current()

		embed = discord.Embed()
		embed.title = f"{currentSector.name} - {currentSector.destination}"
		embed.set_thumbnail(
			url="https://www.bungie.net/common/destiny2_content/icons/6a2761d2475623125d896d1a424a91f9.png"
		)
		if currentSector.embed_url is not None:
			embed.set_image(url=currentSector.embed_url)
			embed.set_footer(text="Image courtesy of kyberscorner.com")
		embed.add_field(
			name="Champions",
			value=currentSector.champion_list,
			inline=False
		)
		embed.add_field(
			name="Shields",
			value=currentSector.shield_list,
			inline=False
		)
		embed.add_field(
			name="Reward",
			value=reward.text,
			inline=False
		)

		await ctx.send(embed=embed)

	@destiny.command()
	async def sector_list(self, ctx: commands.Context) -> None:
		embed = discord.Embed()
		embed.title = "Lost Sectors"
		embed.set_thumbnail(
			url="https://www.bungie.net/common/destiny2_content/icons/6a2761d2475623125d896d1a424a91f9.png"
		)
		for lostSector in SharkBot.Destiny.LostSector.lostSectors:
			embed.add_field(
				name=f"{lostSector.name} - {lostSector.destination}",
				value=f"Champions: *{lostSector.champion_list}*\nShields: *{lostSector.shield_list}*",
				inline=False
			)

		await ctx.send(embed=embed)


async def setup(bot):
	await bot.add_cog(Destiny(bot))
	print("Destiny Cog loaded")


async def teardown(bot):
	print("Destiny Cog unloaded")
	await bot.remove_cog(Destiny(bot))
