from datetime import datetime, timedelta, date
from definitions import Item, SharkErrors
from typing import Union

dateFormat = "%d/%m/%Y"


class Mission:

    def __init__(self, id: str, name: str, description: str, action: str, quota: int, duration: timedelta,
                 reward: Item.Item):
        self.id = id
        self.name = name
        self.description = description
        self.action = action
        self.quota = quota
        self.duration = duration
        self.reward = reward


class MemberMission:

    def __init__(self, member, missionid: str, progress: int, resetsOn: date, claimed: bool):
        self.member = member
        self.mission = get(missionid)
        self._progress = progress
        self.resetsOn = resetsOn
        self._claimed = claimed

    @property
    def progress(self) -> int:
        self.verify_reset()
        return self._progress

    @progress.setter
    def progress(self, value: int) -> None:
        self.verify_reset()
        if value > self.mission.quota:
            self._progress = self.mission.quota
        elif value < 0:
            self._progress = 0
        else:
            self._progress = value

    def verify_reset(self) -> None:
        if self.expired:
            self.reset()

    def reset(self) -> None:
        self.resetsOn = datetime.now().date() - ((datetime.now().date() - self.resetsOn) % self.mission.duration)
        self.resetsOn += self.mission.duration
        self._progress = 0
        self._claimed = False

    @property
    def expired(self) -> bool:
        return datetime.now().date() > self.resetsOn

    @property
    def completed(self) -> bool:
        self.verify_reset()
        return self.progress == self.mission.quota

    @property
    def can_claim(self) -> bool:
        return self.completed and not self._claimed

    @property
    def claimed(self) -> bool:
        self.verify_reset()
        return self._claimed

    @claimed.setter
    def claimed(self, value: bool) -> None:
        self._claimed = value

    @property
    def data(self) -> dict:
        return {
            "missionid": self.mission.id,
            "progress": self.progress,
            "resetsOn": datetime.strftime(self.resetsOn, dateFormat),
            "claimed": self.claimed
        }


class MemberMissions:

    def __init__(self, member, data):
        self.member = member
        missionsdata = {mission.id: None for mission in missions}
        for missiondata in data:
            missionsdata[missiondata["missionid"]] = missiondata
        self.missions = []
        for missionid, missiondata in missionsdata.items():
            if missiondata is None:
                self.missions.append(
                    MemberMission(
                        member=self.member,
                        missionid=missionid,
                        progress=0,
                        resetsOn=datetime(2022, 8, 29).date(),
                        claimed=False
                    )
                )
            else:
                self.missions.append(
                    MemberMission(
                        member=self.member,
                        missionid=missionid,
                        progress=missiondata["progress"],
                        resetsOn=datetime.strptime(missiondata["resetsOn"], dateFormat).date(),
                        claimed=missiondata["claimed"]
                    )
                )

    def get(self, missionid: str) -> MemberMission:
        for mission in self.missions:
            if mission.mission.id == missionid:
                return mission
        raise SharkErrors.MissionNotFoundError(self.member.id, missionid)

    def get_of_action(self, action: str) -> list[MemberMission]:
        return [mission for mission in self.missions if mission.mission.action == action]

    def log_action(self, action: str):
        for mission in [mission for mission in self.missions if mission.mission.action == action]:
            mission.progress += 1

    @property
    def data(self) -> list[dict]:
        return [mission.data for mission in self.missions]


missions = [
    Mission(
        id="dailyCount",
        name="Daily Count",
        description="Count 3 times a day",
        action="count",
        quota=3,
        duration=timedelta(days=1),
        reward=Item.get("LOOT1")
    ),
    Mission(
        id="weeklyCount",
        name="Weekly Count",
        description="Count 10 times a week",
        action="count",
        quota=10,
        duration=timedelta(days=7),
        reward=Item.get("LOOT5")
    )
]


def get(missionid: str) -> Mission:
    for mission in missions:
        if mission.id == missionid:
            return mission
    raise SharkErrors.MissionNotFoundError(missionid)
