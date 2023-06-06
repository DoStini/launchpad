import os
import threading
import tkinter as tk
from tkinter import ttk
from glob import glob
import generator

from Button import Button

SOUND1 = ""
SOUND2 = ""
SOUND3 = ""
SOUND4 = ""
SOUND5 = ""
KEY = ""

SOUNDS = []

KEYS = list(map(lambda path: path.split("/")[1], glob("samples/*", recursive = False)))

def gui(callback):
    global SOUND1, SOUND2, SOUND3, SOUND4, SOUND5, KEYS, sound_1, sound_2, sound_3, sound_4, sound_5

    root = tk.Tk()
    frm = ttk.Frame(root, padding=10)
    frm.grid()
    # ttk.Button(frm, text="Quit", command=root.destroy).grid(column=1, row=0)


    sound_1_val = tk.StringVar(value=SOUND1)
    sound_2_val = tk.StringVar(value=SOUND2)
    sound_3_val = tk.StringVar(value=SOUND3)
    sound_4_val = tk.StringVar(value=SOUND4)
    sound_5_val = tk.StringVar(value=SOUND5)
    key_val = tk.StringVar(value=KEY)
    random_instrument_val = tk.StringVar(value="")


    def close():
        global done
        root.destroy()
        done = True


    def on_change(_1, _2, _3):
        global SOUND1, SOUND2, SOUND3, SOUND4, SOUND5, KEY
        SOUND1 = sound_1_val.get()
        SOUND2 = sound_2_val.get()
        SOUND3 = sound_3_val.get()
        SOUND4 = sound_4_val.get()
        SOUND5 = sound_5_val.get()
        generator.set_random_instrument(random_instrument_val.get())

    ttk.Label(frm, text="Key").grid(column=0, row=0)
    key = tk.OptionMenu(frm, key_val, KEY, *KEYS)
    key.grid(column=1, row=0)

    ttk.Label(frm, text="Sound 0").grid(column=0, row=1)
    sound_1 = tk.OptionMenu(frm, sound_1_val, SOUND1, *SOUNDS)
    sound_1.grid(column=1, row=1)

    ttk.Label(frm, text="Sound 1").grid(column=0, row=2)
    sound_2 = tk.OptionMenu(frm, sound_2_val, SOUND2, *SOUNDS)
    sound_2.grid(column=1, row=2)

    ttk.Label(frm, text="Sound 2").grid(column=0, row=3)
    sound_3 = tk.OptionMenu(frm, sound_3_val, SOUND3, *SOUNDS)
    sound_3.grid(column=1, row=3)

    ttk.Label(frm, text="Sound 3").grid(column=0, row=4)
    sound_4 = tk.OptionMenu(frm, sound_4_val, SOUND4, *SOUNDS)
    sound_4.grid(column=1, row=4)

    ttk.Label(frm, text="Sound 4").grid(column=0, row=5)
    sound_5 = tk.OptionMenu(frm, sound_5_val, SOUND5, *SOUNDS)
    sound_5.grid(column=1, row=5)


    ttk.Label(frm, text="Sound 5 Instrument").grid(column=0, row=6)
    markov_instrument = tk.OptionMenu(frm, random_instrument_val, "", *generator.INSTRUMENTS.keys())
    markov_instrument.grid(column=1, row=6)

    ttk.Label(frm, text="Sound 6 Instrument").grid(column=0, row=7)
    random_instrument = tk.OptionMenu(frm, random_instrument_val, "", *generator.INSTRUMENTS.keys())
    random_instrument.grid(column=1, row=7)

    
    
    def reset_menus():
        global sound_1, sound_2, sound_3, sound_4, sound_5, markov_instrument, random_instrument

        sound_1.destroy()
        sound_2.destroy()
        sound_3.destroy()
        sound_4.destroy()
        sound_5.destroy()

        sound_1 = tk.OptionMenu(frm, sound_1_val, SOUND1, *SOUNDS)
        sound_1.grid(column=1, row=1)
        sound_2 = tk.OptionMenu(frm, sound_2_val, SOUND2, *SOUNDS)
        sound_2.grid(column=1, row=2)
        sound_3 = tk.OptionMenu(frm, sound_3_val, SOUND3, *SOUNDS)
        sound_3.grid(column=1, row=3)
        sound_4 = tk.OptionMenu(frm, sound_4_val, SOUND4, *SOUNDS)
        sound_4.grid(column=1, row=4)
        sound_5 = tk.OptionMenu(frm, sound_5_val, SOUND5, *SOUNDS)
        sound_5.grid(column=1, row=5)

        ttk.Label(frm, text="Sound 5 Instrument").grid(column=0, row=6)
        markov_instrument = tk.OptionMenu(frm, random_instrument_val, "", *generator.INSTRUMENTS.keys())
        markov_instrument.grid(column=1, row=6)

        ttk.Label(frm, text="Sound 6 Instrument").grid(column=0, row=7)
        random_instrument = tk.OptionMenu(frm, random_instrument_val, "", *generator.INSTRUMENTS.keys())
        random_instrument.grid(column=1, row=7)

    def change_keys(_1, _2, _3):
        global KEY, SOUNDS
        KEY = key_val.get()
        SOUNDS = list(map(lambda path: path.split("/")[2], glob(f"samples/{KEY}/*", recursive = False)))
        reset_menus()

    key_val.trace("w", change_keys)
    sound_1_val.trace("w", on_change)
    sound_2_val.trace("w", on_change)
    sound_3_val.trace("w", on_change)
    sound_4_val.trace("w", on_change)
    sound_5_val.trace("w", on_change)
    random_instrument_val.trace("w", on_change)
    # random_instrument_val.trace("w", on_change)


    tk.Button(frm, text='Save configuration', command=lambda: callback(KEY, SOUND1, SOUND2, SOUND3, SOUND4, SOUND5)).grid(column=0,row=12)
    tk.Button(frm, text='Quit', command=close).grid(column=0,row=13)

    root.mainloop()

def init(save_callback):
    threading.Thread(target=gui, args=(save_callback,)).start()