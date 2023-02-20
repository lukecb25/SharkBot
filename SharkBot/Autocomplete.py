import SharkBot
from discord import Interaction
from discord.app_commands import Choice

def items_to_choices(items: list[SharkBot.Item.Item]) -> list[Choice]:
    return [
        Choice(
            name=f"[{item.id}] {item.name}",
            value=item.id
        ) for item in list(set(items))[0:25]
    ]

class Autocomplete:

    @staticmethod
    async def inventory_item(interaction: Interaction, current: str):
        member = SharkBot.Member.get(interaction.user.id, create=False)
        return items_to_choices(
            member.inventory.filter(lambda i: SharkBot.Utils.item_startswith(i, current.lower()))
        )