import random
import threading
import time
from mido import MidiFile, open_output, Message
from fluidsynth import Synth
import numpy as np
import musical_scales
import utils

fs = Synth()
fs.start(driver="pulseaudio")

FONT = "/usr/share/soundfonts/airfont_320_neo.sf2"

id = fs.sfload(FONT)
fs.program_select(0, id, 0, 1)

random_playing = False

# mid: MidiFile = MidiFile("midis/fuguecm.mid")
mid = MidiFile("midis/Dm/diamond.mid")

def markov():
    notes = list(map(lambda msg: msg.note, filter(lambda msg: msg.type == "note_on", mid)))

    transitions = {}

    for x in range(len(notes) - 1):
        note = notes[x]
        current = transitions.get(note, {})

        after = notes[x+1]
        count = current.get(after, 0)

        current[after] = count + 1

        transitions[note] = current

    probabilities = {}

    for note, note_transitions in transitions.items():
        cnt = sum(note_transitions.values())
        notes = []
        probs = []
        for next_note, num in note_transitions.items():
            notes.append(next_note)
            probs.append(num / cnt)

        probabilities[note] = {
            "notes": notes,
            "probabilities": probs
        }



    # events = list(mid)

    # midi_port.send(Message(type="program_change", channel=5, program=40, time=0))

    # # for event in events:
    # #     print

    # print(events)

    def predict_next_note(probabilities, note):
        transition = probabilities[note]
        return np.random.choice(transition["notes"], 1, p = transition["probabilities"])[0]


    NUM_NOTES = 200
    MAX_REPEATED = 4


    repeated = 0

    note = list(probabilities.keys())[0]

    for idx in range(100):
        time.sleep(np.random.choice(duration_times, p=duration_probs))
        fs.noteoff(0, note)

        prev = note
        note = predict_next_note(probabilities, note)

        if prev == note:
            repeated += 1
        else:
            repeated = 0

        if repeated == MAX_REPEATED:
            while True:
                new = predict_next_note(probabilities, note)
                if new != note:
                    note = new
                    break
            repeated = 0

        # print(msg)
        fs.noteon(0, note, 60)
        # fs.noteon(0, msg.note - 12, msg.velocity)



duration_times = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]
duration_probs = [0.5, 0.2, 0.1, 0.05, 0.05, 0.05, 0.03, 0.02]

class RandomGenerator(threading.Thread):
    def __init__(self, event):
        threading.Thread.__init__(self)
        self.stopped = event

        self.MAX_STEP = 3
        self.possible_notes = musical_scales.scale("D", "pentatonic minor", 2)

    def run(self):
        note_idx = int(len(self.possible_notes) / 2)
        note = 0

        while not self.stopped.wait(np.random.choice(duration_times, p=duration_probs)):
            fs.noteoff(0, note)
            note = utils.note_to_midi(self.possible_notes[note_idx].midi)
            print(note)
            fs.noteon(0, note, 60)

            new_note_idx = note_idx + random.randint(-self.MAX_STEP, self.MAX_STEP)

            if new_note_idx >= len(self.possible_notes):
                note_idx = len(self.possible_notes) - (new_note_idx % len(self.possible_notes)) - 1
            elif new_note_idx < 0:
                note_idx = -new_note_idx
            else:
                note_idx = new_note_idx
        fs.all_notes_off(0)

# class RandomGenerator(threading.Thread):
#     def play(self):
#         global random_playing

#         MAX_STEP = 3
#         random_playing = True
#         possible_notes = musical_scales.scale("D", "pentatonic minor", 2)

#         note_idx = int(len(possible_notes) / 2)
#         note = 0
#         while random_playing:
#             time.sleep(np.random.choice(duration_times, p=duration_probs))
#             fs.noteoff(0, note)
#             note = utils.note_to_midi(possible_notes[note_idx].midi)
#             print(note)
#             fs.noteon(0, note, 60)

#             new_note_idx = note_idx + random.randint(-MAX_STEP, MAX_STEP)

#             if new_note_idx >= len(possible_notes):
#                 note_idx = len(possible_notes) - (new_note_idx % len(possible_notes)) - 1
#             elif new_note_idx < 0:
#                 note_idx = -new_note_idx
#             else:
#                 note_idx = new_note_idx

#     def stop(self):
#         global random_playing
#         random_playing = False
#         fs.all_notes_off(0)

# mid.play()

# input("")
