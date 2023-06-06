import random
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
fs.program_select(0, id, 0, 33)
fs.program_select(1, id, 0, 1)

# mid: MidiFile = MidiFile("midis/fuguecm.mid")
mid = MidiFile("midis/Dm/diamond.mid")
mid.play()
input("")
print(mid.ticks_per_beat)

def markov():
    notes = list(map(lambda msg: msg.note, filter(lambda msg: msg.type == "note_on", mid)))
    # note_msgs = list(filter(lambda msg: msg.type == "note_on" or msg.type == "note_off", mid))


    # for note_idx, note in note_msgs:
    #     duration = 0

    #     if not

    #     for idx, off in enumerate(note_off_msgs):
    #         duration += note.time
    #         if note.note == off.note:
    #             durations.append(duration)
    #             break
    #     del note_off_msgs[idx]


    # print(note_off_msgs)
    # print(durations)

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
        time.sleep(0.25)
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



def random_in_scale():
    MAX_STEP = 3

    possible_notes = musical_scales.scale("D", "harmonic minor", 2)

    note_idx = int(len(possible_notes) / 2)

    for x in range(100):
        time.sleep(0.25)
        note = utils.note_to_midi(possible_notes[note_idx].midi)
        print(note)
        fs.noteon(0, note, 60)

        note_idx =  (note_idx + random.randint(-MAX_STEP, MAX_STEP)) % len(possible_notes)

# mid.play()

# input("")
markov()
