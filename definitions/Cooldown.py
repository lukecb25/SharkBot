from datetime import datetime, timedelta

timeFormat = "%S:%M:%H/%d:%m:%Y"


class Cooldown:

    def __init__(self, name: str, expiry: str, duration: timedelta):
        self.name = name
        self.expiry = datetime.strptime(expiry, timeFormat)
        self.duration = duration

    @property
    def expired(self):
        return datetime.now() > self.expiry

    def extend(self):
        self.expiry += self.duration

    def reset(self):
        self.expiry = datetime.now() + self.duration

    @property
    def timestring(self):
        return datetime.strftime(self.expiry, timeFormat)

    @property
    def timeremaining(self):
        return datetime.now() - self.expiry


class NewCooldown:

    def __init__(self, name: str, duration: timedelta):
        self.name = name
        self.expiry = datetime.now() + duration
        self.duration = duration
