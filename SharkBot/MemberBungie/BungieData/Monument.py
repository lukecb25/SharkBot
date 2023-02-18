from .BungieData import BungieData
import SharkBot

_monument_hashes = SharkBot.Utils.JSON.load("data/static/bungie/definitions/ExoticArchiveSorted.json")

class Monument(BungieData):
    _COMPONENTS = [800]

    @staticmethod
    def _process_data(data):
        profile_data = data["profileCollectibles"]["data"]["collectibles"]
        character_data = list(data["characterCollectibles"]["data"].values())[0]["collectibles"]
        output = {}
        for year_num, year_data in _monument_hashes.items():
            _data = {}
            for weapon_hash, weapon_name in year_data.items():
                if weapon_hash in profile_data:
                    state = profile_data[weapon_hash]["state"]
                else:
                    state = character_data[weapon_hash]["state"]
                _data[weapon_name] = state == 0
            output[year_num] = _data
        return output