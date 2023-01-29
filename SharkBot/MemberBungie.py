import json
import os.path
from datetime import datetime, timedelta
from typing import Optional, Union
import aiohttp
import secret

import SharkBot

class _CacheFolders:
    CORE = "data/live/bungie/cache"
    CRAFTABLES = CORE + "/craftables"

SharkBot.Utils.FileChecker.directory(_CacheFolders.CRAFTABLES)

with open("data/static/bungie/definitions/CraftableWeaponHashes.json", "r") as infile:
    _CRAFTABLE_WEAPON_HASHES: dict[str, str] = json.load(infile)

with open("data/static/bungie/definitions/LevelObjectiveHashes.json", "r") as infile:
    _data = json.load(infile)
    _WEAPON_LEVEL_RECORDS: list[str] = _data["records"]
    _LEVEL_OBJECTIVE_HASH: int = _data["objective"]


class _CraftablesResponse:

    def __init__(self, weapon_name: str, sources: list[str], record_data: dict[str, Union[int, bool]]):
        self.weapon_name = weapon_name
        self.sources = sources
        self.progress: int = record_data["progress"]
        self.quota: int = record_data["completionValue"]
        self.complete: bool = record_data["complete"]

    def is_from(self, source: str) -> bool:
        return source in self.sources

    def is_from_any(self, sources: list[str]) -> bool:
        return any([source in self.sources for source in sources])

    @property
    def data(self) -> dict:
        return {
            "weapon_name": self.weapon_name,
            "sources": self.sources,
            "record_data": {
                "progress": self.progress,
                "completionValue": self.quota,
                "complete": self.complete
            }
        }


class MemberBungie:

    def __init__(self, member, token: Optional[str] = None, token_expires: Optional[int] = None,
                 refresh_token_expires: Optional[int] = None, destiny_membership_id: Optional[str] = None,
                 destiny_membership_type: Optional[int] = None):
        self._member: SharkBot.Member.Member = member
        self._token = token
        self._token_expires = token_expires
        self._refresh_token_expires = refresh_token_expires
        self._destiny_membership_id = destiny_membership_id
        self._destiny_membership_type = destiny_membership_type

    def delete_credentials(self) -> bool:
        self._token = None
        self._token_expires = None
        self._refresh_token_expires = None
        self._destiny_membership_id = None
        self._destiny_membership_type = None

        db = SharkBot.Handlers.firestoreHandler.db
        doc_ref = db.collection(u"bungieauth").document(str(self._member.id))
        doc = doc_ref.get()

        if not doc.exists:
            return False
        else:
            doc_ref.delete()
            return True


    @property
    def refresh_token_expiring(self) -> bool:
        if self._refresh_token_expires is None:
            return False
        else:
            return self._refresh_token_expires < (datetime.utcnow() + timedelta(weeks=1)).timestamp()

    async def soft_refresh(self):
        try:
            await self._refresh_token()
        except Exception as e:
            pass

    async def _refresh_token(self) -> bool:
        async with aiohttp.ClientSession() as session:
            async with session.get(secret.BungieAPI.REFRESH_URL, data=secret.BungieAPI.refresh_headers(self._member.id)) as response:
                if response.ok:
                    return True
                else:
                    return False

    def _need_refresh(self) -> bool:
        if self._token_expires is None:
            return True
        else:
            return self._token_expires < datetime.utcnow().timestamp() - 60

    async def _get_token(self):
        if self._token is not None:
            if not self._need_refresh():
                return self._token

        doc_ref = SharkBot.Handlers.firestoreHandler.db.collection(u"bungieauth").document(str(self._member.id))
        doc = doc_ref.get()

        if not doc.exists:
            raise SharkBot.Errors.BungieAPI.SetupNeededError(self._member.id)

        if not await self._refresh_token():
            raise SharkBot.Errors.BungieAPI.InternalServerError(self._member.id)

        doc = doc_ref.get()

        data = doc.to_dict()
        self._token = data["access_token"]
        self._token_expires = datetime.utcnow().timestamp() + data["expires_in"]
        self._refresh_token_expires = data["refresh_expires_in"] + data["refreshed_at"]
        self._destiny_membership_id = data["destiny_membership_id"]
        self._destiny_membership_type = data["destiny_membership_type"]
        self._member.write_data()
        return self._token

    async def get_profile_response(self, *components: int) -> dict[str, dict]:
        _components_string = ",".join(str(component) for component in components)
        token = await self._get_token()
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f"https://www.bungie.net/Platform/Destiny2/{self._destiny_membership_type}/Profile/{self._destiny_membership_id}?components={_components_string}",
                    headers=secret.BungieAPI.bungie_headers(token)
            ) as response:
                if not response.ok:
                    self._token = None
                    raise SharkBot.Errors.BungieAPI.InternalServerError
                else:
                    data = await response.json()
                    return data["Response"]

    def get_cached_craftables_data(self) -> Optional[dict[str, list[_CraftablesResponse]]]:
        if not os.path.isfile(_CacheFolders.CRAFTABLES + f"/{self._member.id}.json"):
            return None
        else:
            with open(_CacheFolders.CRAFTABLES + f"/{self._member.id}.json", "r") as _infile:
                data = json.load(_infile)
            return {weapon_type: [_CraftablesResponse(**craftable_data) for craftable_data in type_data] for weapon_type, type_data in data.items()}

    def write_craftables_cache(self, raw_data: dict[str, list[_CraftablesResponse]]):
        data = {weapon_type: [response.data for response in responses] for weapon_type, responses in raw_data.items()}
        with open(_CacheFolders.CRAFTABLES + f"/{self._member.id}.json", "w+") as _outfile:
            json.dump(data, _outfile, indent=2)

    async def get_craftables_data(self) -> dict[str, list[_CraftablesResponse]]:
        _data = await self.get_profile_response(900)
        records = _data["profileRecords"]["data"]["records"]
        output = {}
        for weapon_type, weapon_records in _crafting_records.items():
            weapon_data = []
            for weapon in weapon_records:
                weapon_data.append(_CraftablesResponse(
                    weapon_name=weapon["name"],
                    sources=weapon["sources"],
                    record_data=records[weapon["record_hash"]]["objectives"][0]
                ))
            output[weapon_type] = weapon_data
        self.write_craftables_cache(output)
        return output

    async def get_monument_data(self) -> dict[str, dict[str, bool]]:
        data = await self.get_profile_response(800)
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

    async def get_weapon_levels_data(self) -> dict:
        data = await self.get_profile_response(102,201,205,309)
        return data

    @property
    def data(self) -> dict:
        return {
            "token": self._token,
            "token_expires": self._token_expires,
            "refresh_token_expires": self._refresh_token_expires,
            "destiny_membership_id": self._destiny_membership_id,
            "destiny_membership_type": self._destiny_membership_type
        }


with open("data/static/bungie/definitions/CraftingRecords.json", "r") as infile:
    _crafting_records: dict[str, list[dict[str, str | list[str] | int]]] = json.load(infile)


with open("data/static/bungie/definitions/ExoticArchiveSorted.json", "r") as infile:
    _monument_hashes: dict[str, dict[str, str]] = json.load(infile)
