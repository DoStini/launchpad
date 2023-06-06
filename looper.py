from multiprocessing import Event
from threading import Thread
from pygame import mixer, init

from generator import RandomGenerator, MarkovGenerator

init()
mixer.init()

mixer.set_num_channels(20)

random_gen_queued: RandomGenerator = None
random_gen: RandomGenerator = None
random_gen_removed_queued = False
random_stop_flag: Event = None

markov_gen_queued: MarkovGenerator = None
markov_gen: MarkovGenerator = None
markov_gen_removed_queued = False
markov_stop_flag: Event = None

queue = []
remove_queue_sound = []
remove_queue_channel = []
loops: dict[str, mixer.Channel] = {}
sounds: dict[str, mixer.Sound] = {}

bar = 1

def get_beat():
    return bar

class TimerDeque(Thread):
    def __init__(self, time, event, looper):
        Thread.__init__(self)
        self.time = time
        self.stopped = event
        self.looper: Looper = looper

    def run(self):
        global bar
        while not self.stopped.wait(self.time):
            self.looper.release_queue()
            self.looper.release_remove_queue()

            bar = (bar % 4) + 1

class Looper:
    def __init__(self) -> None:
        self.last_channel = -1
        self.stopTimer = Event()

    def set_bpm(self, bpm: int):
        self.stopTimer.set()

        self.stopTimer = Event()
        thread = TimerDeque(60 / bpm * 4, self.stopTimer, self)
        thread.start()

    def toggle_random_generator(self):
        global random_gen_queued, random_gen_removed_queued, random_stop_flag
        if random_gen != None:
            random_gen_removed_queued = True
            return False
        random_stop_flag = Event()
        random_gen_queued = RandomGenerator(random_stop_flag)
        return True

    def toggle_markov_generator(self):
        global markov_gen_queued, markov_gen_removed_queued, markov_stop_flag
        if markov_gen != None:
            markov_gen_removed_queued = True
            return False
        markov_stop_flag = Event()
        markov_gen_queued = MarkovGenerator(markov_stop_flag)
        return True

    def set_sound(self, sound: str):
        sounds[sound] = mixer.Sound(sound)

    def toggle(self, sound: str) -> bool:
        channel = loops.get(sound)
        if channel != None:
            remove_queue_sound.append(sound)
            remove_queue_channel.append(channel)
            return False

        queue.append(sound)
        return True

    def release_remove_queue(self):
        global random_gen_removed_queued, random_gen, random_stop_flag, markov_gen_removed_queued, markov_gen, markov_stop_flag

        for channel in remove_queue_channel:
            channel.fadeout(500)
        for sound in remove_queue_sound:
            if loops[sound] is not None:
                del loops[sound]
        
        remove_queue_sound.clear()
        remove_queue_channel.clear()
        if random_gen_removed_queued:
            random_gen_removed_queued = False
            random_stop_flag.set()
            random_gen = None
        if markov_gen_removed_queued:
            markov_gen_removed_queued = False
            markov_stop_flag.set()
            markov_gen = None
            

    def release_queue(self):
        global random_gen, random_gen_queued, markov_gen, markov_gen_queued

        for sound in queue:
            channel = mixer.find_channel()
            loops[sound] = channel
            snd = sounds[sound]
            channel.play(snd, loops=-1, fade_ms=500)
        queue.clear()

        if random_gen_queued is not None:
            random_gen = random_gen_queued
            
            random_gen.start()
            random_gen_queued = None

        if markov_gen_queued is not None:
            markov_gen = markov_gen_queued
            
            markov_gen.start()
            markov_gen_queued = None

loooper = Looper()
loooper.set_bpm(120)
