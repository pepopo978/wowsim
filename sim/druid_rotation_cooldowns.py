from sim.cooldowns import Cooldown


class ArcaneEclipseCooldown(Cooldown):
    PRINTS_ACTIVATION = True
    TRACK_UPTIME = True

    @property
    def cooldown(self):
        return 30

    @property
    def duration(self):
        return 15

class NatureEclipseCooldown(Cooldown):
    PRINTS_ACTIVATION = True
    TRACK_UPTIME = True

    @property
    def cooldown(self):
        return 30

    @property
    def duration(self):
        return 15
