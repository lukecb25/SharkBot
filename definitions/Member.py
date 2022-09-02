import discord.ext.commands
import os

from definitions import SharkErrors, Item, Cooldown, MemberInventory
from datetime import datetime, timedelta
from handlers import firestoreHandler
import json


class Member:

    def __init__(self, member_data: dict) -> None:

        for item, value in defaultvalues.items():
            if item not in member_data:
                member_data[item] = value

        self.id = member_data["id"]
        self.balance = member_data["balance"]
        self._inventory = MemberInventory.MemberInventory(self, member_data["inventory"])
        self.collection = member_data["collection"]
        self.counts = member_data["counts"]
        self.cooldowns = {
            "hourly": Cooldown.Cooldown("hourly", member_data["cooldowns"]["hourly"], timedelta(hours=1)),
            "daily": Cooldown.Cooldown("daily", member_data["cooldowns"]["daily"], timedelta(days=1)),
            "weekly": Cooldown.Cooldown("weekly", member_data["cooldowns"]["weekly"], timedelta(weeks=1))
        }
        self.discordMember = None

    def write_data(self) -> None:

        member_data = {}
        member_data["id"] = self.id
        member_data["balance"] = self.balance
        member_data["inventory"] = self._inventory.itemids
        member_data["collection"] = self.collection
        member_data["counts"] = self.counts
        member_data["cooldowns"] = {
            "hourly": self.cooldowns["hourly"].timestring,
            "daily": self.cooldowns["daily"].timestring,
            "weekly": self.cooldowns["weekly"].timestring
        }

        with open(f"data/members/{self.id}.json", "w") as outfile:
            json.dump(member_data, outfile, indent=4)

    def upload_data(self) -> None:
        firestoreHandler.upload_member(
            {
                "id": self.id,
                "balance": self.get_balance(),
                "inventory": self._inventory.itemids,
                "collection": self.get_collection(),
                "counts": self.get_counts()
            }
        )

    ##--Inventory--###



    ##--Collection--##

    def get_collection(self) -> dict:
        return self.collection

    def add_to_collection(self, item: Item.Item) -> None:
        if item.id not in self.collection:
            self.collection.append(item.id)
        self.write_data()

    def remove_from_collection(self, item: Item.Item) -> None:
        if item.id not in self.collection:
            raise SharkErrors.ItemNotInCollectionError(item.id)
        self.collection.remove(item.id)
        self.write_data()

    ##--Balance--##

    def get_balance(self) -> int:
        return self.balance

    def add_balance(self, amount: int) -> None:
        self.balance += amount
        self.write_data()

    def set_balance(self, amount: int) -> None:
        self.balance = amount
        self.write_data()

    ##--Discord Member--##

    async def fetch_discord_member(self, bot) -> discord.Member:
        self.discordMember = bot.get_user(self.id)
        if self.discordMember is None:
            try:
                self.discordMember = await bot.fetch_user(self.id)
            except:
                self.discordMember = None

    ##--Counts--##

    def get_counts(self) -> int:
        return self.counts

    def add_counts(self, amount: int) -> None:
        self.counts += amount
        self.write_data()

    def set_counts(self, amount: int) -> None:
        self.counts = amount
        self.write_data()

    ##--Cleanup--##

    def delete_file(self) -> None:
        os.remove(f"data/members/{self.id}.json")
        global members
        del members[self.id]

    ##--Destructor--##

    def __del__(self) -> None:
        pass
        ##self.write_data()


class BlankMember(Member):

    def __init__(self, member_id) -> None:
        self.id = int(member_id)
        self.balance = defaultvalues["balance"]
        self._inventory = MemberInventory.MemberInventory(self, defaultvalues["inventory"])
        self.collection = defaultvalues["collection"]
        self.counts = defaultvalues["counts"]
        self.cooldowns = {
            "hourly": Cooldown.Cooldown("hourly", defaultvalues["cooldowns"]["hourly"], timedelta(hours=1)),
            "daily": Cooldown.Cooldown("daily", defaultvalues["cooldowns"]["daily"], timedelta(days=1)),
            "weekly": Cooldown.Cooldown("weekly", defaultvalues["cooldowns"]["weekly"], timedelta(weeks=1))
        }


def get(memberid: int) -> Member:
    memberid = int(memberid)
    if memberid not in members:
        member = BlankMember(memberid)
        members[memberid] = member
        member.write_data()

    member = members[memberid]
    return member


defaultvalues = {
    "id": 1234,
    "balance": 0,
    "inventory": [],
    "collection": [],
    "counts": 0,
    "cooldowns": {
        "hourly": datetime.strftime(Cooldown.NewCooldown("hourly", timedelta(hours=1)).expiry, Cooldown.timeFormat),
        "daily": datetime.strftime(Cooldown.NewCooldown("daily", timedelta(days=1)).expiry, Cooldown.timeFormat),
        "weekly": datetime.strftime(Cooldown.NewCooldown("weekly", timedelta(weeks=1)).expiry, Cooldown.timeFormat)
    }
}


def load_member_files() -> None:
    global members
    members = {}
    for filename in os.listdir("./data/members"):
        with open(f"data/members/{filename}", "r") as infile:
            data = json.load(infile)
            member = Member(data)
            members[int(data["id"])] = member


members = {}
load_member_files()
