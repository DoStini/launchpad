from pygame import mixer, init

init()
mixer.init()

mixer.set_num_channels(20)

class Looper:
    def __init__(self) -> None:
        self.loops: dict[str, mixer.Channel] = {}
        self.last_channel = -1
        self.sounds: dict[str, mixer.Sound] = {}

    def set_sound(self, sound: str):
        self.sounds[sound] = mixer.Sound(sound)

    def toggle(self, sound: str):
        channel = self.loops.get(sound)
        if channel != None:
            del self.loops[sound]
            channel.fadeout(500)
            # channel.stop()
            return

        channel = mixer.find_channel()
        self.loops[sound] = channel
        snd = self.sounds[sound]
        channel.play(snd, loops=-1, fade_ms=500)
