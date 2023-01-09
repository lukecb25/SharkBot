from typing import Self

class VERSION:

    @classmethod
    def _get_version(cls) -> int:
        return int(cls.__name__[-1])

    @classmethod
    def _get_last_version(cls) -> Self:
        return versions[cls._get_version() - 2]

    @classmethod
    def convert(cls, member_data: dict) -> dict:
        if member_data["data_version"] != cls._get_version() - 1:
            member_data = cls._get_last_version().convert(member_data)
        member_data["data_version"] = cls._get_version()
        return cls._convert(member_data)

    @staticmethod
    def _convert(member_data: dict) -> dict:
        return member_data


class Version1(VERSION):

    @staticmethod
    def _convert(member_data: dict) -> dict:
        return member_data

class Version2(VERSION):

    @staticmethod
    def _convert(member_data: dict) -> dict:
        old_stats = member_data["stats"]
        new_stats = {
            "coinflips": {
                "wins": old_stats["coinflipWins"],
                "losses": old_stats["coinflipLosses"],
                "mercies": old_stats["coinflipMercies"],
            },
            "boxes": {
                "claimed": old_stats["claimedBoxes"],
                "bought": old_stats["boughtBoxes"],
                "opened": old_stats["openedBoxes"],
                "counting": old_stats["countingBoxes"]
            },
            "claims": old_stats["claims"],
            "incorrect_counts": old_stats["incorrectCounts"],
            "sold_items": old_stats["soldItems"],
            "completed_missions": old_stats["completedMissions"]
        }
        member_data["stats"] = new_stats
        return member_data

versions = [
    Version1,
    Version2
]