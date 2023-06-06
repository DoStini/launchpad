def note_to_midi(note):
    note_map = {
        'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
        'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
        'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
    }

    # Split the note into its pitch and octave parts
    pitch = note[:-1]
    octave = int(note[-1])

    # Calculate the MIDI note number
    midi_note = (octave + 1) * 12 + note_map[pitch]

    return midi_note