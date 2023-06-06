import random
import threading
import time
from mido import MidiFile, open_output, Message
from fluidsynth import Synth
import numpy as np
import musical_scales
import utils

INSTRUMENTS = {
    "Acoustic Grand Piano": 0,
    "Bright Acoustic Piano": 1,
    "Electric Grand Piano": 2,
    "Honky-tonk Piano": 3,
    "Rhodes Piano": 4,
    "Chorused Piano": 5,
    "Harpsichord": 6,
    "Clavinet": 7,
    "Celesta": 8,
    "Glockenspiel": 9,
    "Music box": 10,
    "Vibraphone": 11,
    "Marimba": 12,
    "Xylophone": 13,
    "Tubular Bells": 14,
    "Dulcimer": 15,
    "Hammond Organ": 16,
    "Percussive Organ": 17,
    "Rock Organ": 18,
    "Church Organ": 19,
    "Reed Organ": 20,
    "Accordion": 21,
    "Harmonica": 22,
    "Tango Accordion": 23,
    "Acoustic Guitar (nylon)": 24,
    "Acoustic Guitar (steel)": 25,
    "Electric Guitar (jazz)": 26,
    "Electric Guitar (clean)": 27,
    "Electric Guitar (muted)": 28,
    "Overdriven Guitar": 29,
    "Distortion Guitar": 30,
    "Guitar Harmonics": 31,
    "Acoustic Bass": 32,
    "Electric Bass (finger)": 33,
    "Electric Bass (pick)": 34,
    "Fretless Bass": 35,
    "Slap Bass 1": 36,
    "Slap Bass 2": 37,
    "Synth Bass 1": 38,
    "Synth Bass 2": 39,
    "Violin": 40,
    "Viola": 41,
    "Cello": 42,
    "Contrabass": 43,
    "Tremolo Strings": 44,
    "Pizzicato Strings": 45,
    "Orchestral Harp": 46,
    "Timpani": 47,
    "String Ensemble 1": 48,
    "String Ensemble 2": 49,
    "Synth Strings 1": 50,
    "Synth Strings 2": 51,
    "Choir Aahs": 52,
    "Voice Oohs": 53,
    "Synth Voice": 54,
    "Orchestra Hit": 55,
    "Trumpet": 56,
    "Trombone": 57,
    "Tuba": 58,
    "Muted Trumpet": 59,
    "French Horn": 60,
    "Brass Section": 61,
    "Synth Brass 1": 62,
    "Synth Brass 2": 63,
    "Soprano Sax": 64,
    "Alto Sax": 65,
    "Tenor Sax": 66,
    "Baritone Sax": 67,
    "Oboe": 68,
    "English Horn": 69,
    "Bassoon": 70,
    "Clarinet": 71,
    "Piccolo": 72,
    "Flute": 73,
    "Recorder": 74,
    "Pan Flute": 75,
    "Bottle Blow": 76,
"Whistle": 78,
    "Ocarina": 79,
    "Lead 1 (square)": 80,
    "Lead 2 (sawtooth)": 81,
    "Lead 3 (calliope lead)": 82,
    "Lead 4 (chiffer lead)": 83,
    "Lead 5 (charang)": 84,
    "Lead 6 (voice)": 85,
    "Lead 7 (fifths)": 86,
    "Lead 8 (brass + lead)": 87,
    "Pad 1 (new age)": 88,
    "Pad 2 (warm)": 89,
    "Pad 3 (polysynth)": 90,
    "Pad 4 (choir)": 91,
    "Pad 5 (bowed)": 92,
    "Pad 6 (metallic)": 93,
    "Pad 7 (halo)": 94,
    "Pad 8 (sweep)": 95,
}


duration_times = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]
duration_probs = [0.5, 0.2, 0.1, 0.05, 0.05, 0.05, 0.03, 0.02]

fs = Synth()
fs.start(driver="pulseaudio")

FONT = "/usr/share/soundfonts/airfont_320_neo.sf2"

id = fs.sfload(FONT)
fs.program_select(0, id, 0, 1)
fs.program_select(1, id, 0, 1)

def set_random_instrument(instrument_value):
    fs.program_select(0, id, 0, INSTRUMENTS[instrument_value])

def set_markov_instrument(instrument_value):
    fs.program_select(1, id, 0, INSTRUMENTS[instrument_value])

random_playing = False

# mid: MidiFile = MidiFile("midis/fuguecm.mid")
mid = MidiFile("midis/Dm/diamond.mid")



class MarkovGenerator(threading.Thread):
    def __init__(self, event):
        threading.Thread.__init__(self)
        self.stopped = event
        self.repeated = 0
        self.MAX_REPEATED = 4

        notes = list(map(lambda msg: msg.note, filter(lambda msg: msg.type == "note_on", mid)))
        self.notes = notes


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

        self.probabilities = probabilities

    def predict_next_note(self, probabilities, note):
        transition = probabilities[note]
        return np.random.choice(transition["notes"], 1, p = transition["probabilities"])[0]

    def run(self):
        note = list(self.probabilities.keys())[0]

        while not self.stopped.wait(np.random.choice(duration_times, p=duration_probs)):
            fs.noteoff(1, note)

            prev = note
            note = self.predict_next_note(self.probabilities, note)
            print(note)

            if prev == note:
                self.repeated += 1
            else:
                self.repeated = 0

            if self.repeated == self.MAX_REPEATED:
                while True:
                    new = self.predict_next_note(self.probabilities, note)
                    if new != note:
                        note = new
                        break
                self.repeated = 0

            # print(msg)
            fs.noteon(1, note - 5, 120)


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
            fs.noteon(0, note, 120)

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
