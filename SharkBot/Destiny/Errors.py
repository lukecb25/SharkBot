from SharkBot.Errors import SharkError


class ChampionNotFoundError(SharkError):
    pass


class ShieldNotFoundError(SharkError):
    pass


class LostSectorNotFoundError(SharkError):
    pass


class LostSectorRewardNotFoundError(SharkError):
    pass


class DungeonNotFoundError(SharkError):
    pass


class RaidNotFoundError(SharkError):
    pass


class NightfallNotFoundError(SharkError):
    pass
