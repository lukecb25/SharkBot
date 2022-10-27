from typing import Union

import discord

import SharkBot.Utils
from SharkBot import Collection, Rarity, Errors, LootPool, Utils


class Item:

    def __init__(self, item_id: str, name: str, description: str, collection: Collection, rarity: Rarity):
        self.id = item_id
        self.name = name
        self.description = description
        self.collection = collection
        self.rarity = rarity

    @property
    def embed(self) -> discord.Embed:
        embed = discord.Embed()
        embed.title = self.name
        embed.colour = self.collection.colour
        embed.description = self.description
        embed.set_footer(text=f"{self.rarity.name} | {self.id}")

        return embed

    @property
    def value(self) -> int:
        return self.rarity.value

    @property
    def text(self) -> str:
        return f"{self.rarity.icon} {self.name}"


class Lootbox(Item):

    def __init__(self, item_id: str, name: str, description: str, collection: Collection, rarity: Rarity,
                 loot_pool_code: str) -> None:

        super().__init__(item_id, name, description, collection, rarity)
        self.lootPool = LootPool.LootPool(loot_pool_code)

    def roll(self) -> Item:
        return self.lootPool.roll()


class FakeItem(Item):

    def __init__(self, item: Item) -> None:
        super().__init__(
            item_id=item.id,
            name="???",
            description="???",
            collection=item.collection,
            rarity=item.rarity
        )


converters = {}


def load_converters() -> None:
    global converters
    with open("data/static/collectibles/converters.txt", "r") as infile:
        converters = {line[0]: line[1] for line in [line.split(":") for line in infile.read().split("\n")]}


def get(item_id: str) -> Union[Item, Lootbox]:
    """
    Fetches the Item with the given Item ID

    :param item_id: The Item ID to search with
    :return: The Item with the given ID
    """

    item_id = item_id.upper()
    for collection in Collection.collections:
        for item in collection.items:
            if item_id == item.id:
                return item
    if item_id in converters:
        return get(converters[item_id])
    raise Errors.ItemNotFoundError(item_id)


def search(searchString: str) -> Union[Item, Lootbox]:
    """
    Fetches the Item with the given Item ID or Name

    :param searchString: The string to search with
    :return: The Item with the given ID or Name
    """

    searchString = searchString.upper()
    for collection in Collection.collections:
        for item in collection.items:
            if searchString == item.id or searchString == item.name.upper():
                return item
    for item in Collection.lootboxes.items:
        if searchString + " LOOTBOX" == item.name.upper():
            return item
    if searchString in converters:
        return get(converters[searchString])
    raise Errors.ItemNotFoundError(searchString)


def get_order_index(item: Union[str, Item]) -> int:
    if type(item) == str:
        item = get(item)

    return items.index(item)


def import_item_file(filename: str) -> None:
    with open(filename, "r") as infile:
        raw_file_data = infile.read()

    item_data_set = [line.split("|") for line in raw_file_data.split("\n") if line != ""]

    for item_data in item_data_set:
        item = Item(
            item_id=item_data[0],
            name=item_data[1],
            description=item_data[2],
            collection=Collection.get(item_data[3]),
            rarity=Rarity.get(item_data[3])
        )
        items.append(item)
        item.collection.add_item(item)


def import_lootbox_file(filename: str) -> None:
    with open(filename, "r") as infile:
        raw_file_data = infile.read()

    item_data_set = [line.split("|") for line in raw_file_data.split("\n") if line != ""]

    for item_data in item_data_set:
        item = Lootbox(
            item_id=item_data[0],
            name=item_data[1],
            description=item_data[2],
            collection=Collection.lootboxes,
            rarity=Rarity.get(item_data[3]),
            loot_pool_code=item_data[4]
        )

        items.append(item)
        item.collection.add_item(item)


items = []

for filepath in SharkBot.Utils.get_dir_filepaths("data/static/collectibles/items"):
    import_item_file(filepath)

for filepath in SharkBot.Utils.get_dir_filepaths("data/static/collectibles/lootboxes"):
    import_lootbox_file(filepath)

load_converters()

currentEventBoxID: Union[str, None] = "LOOTH"
if currentEventBoxID is None:
    currentEventBox = None
else:
    currentEventBox = get(currentEventBoxID)
