import discord
from discord.ext import commands

from definitions import Item, Member
from .OpenButton import OpenButton


class BuyView(discord.ui.View):
    def __init__(self, boughtItems: list[Item.Lootbox], memberid: int, embed: discord.Embed, timeout=180):
        super().__init__(timeout=timeout)
        self.boughtItems = boughtItems
        self.member = Member.get(memberid)
        self.embed = embed
        self.add_item(OpenButton(self.member, self.embed, self.boughtItems))


