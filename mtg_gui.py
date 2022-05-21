#!/usr/bin/env python3
"""
    Created by: FatherAnarchy        email: fatheranarchy@programmer.net
    
    A basic GUI using mtgsdk to show information on the differtent cards in Magic: The Gathering.
    
    *This is not a complete program and will be updated in the future.

"""
from mtg_wrappers import MTGCard, MTGSet, MTGFiler
import PySimpleGUI as sg
import os
import random
from PIL import Image, ImageTk
import requests
import io
import certifi


class MTG_GUI:
    def __init__(self):
        self.filer = MTGFiler()
        self.setCodes = self.filer.readSetCodes()
        self.set = self.filer.unpickleSet(self.setCodes[0])
        self.setCards = []
        self.cardNames = []
        self.card = None
        self.log = self.filer.log


    def make_window(self):

        ran = random.choice(sg.theme_list())        
        sg.theme(ran)

        self.layout_top = [ 
            [
                sg.Text("Choose A Card Set: "), 
                sg.Combo(self.setCodes, s = (6, 8), enable_events=True, readonly=True, k='-CODE-'), 
                sg.Text(size = (5, 1), key = '-CARD_COUNT-')
            ],
            [
                sg.Combo(self.set.card_list, default_value = '-Choose a Card-', s = (30, 8), enable_events = True, readonly = True, k = '-CARD-')
            ] 
        ]

        self.layout_L = [
                [
                sg.Text("Name: "), 
                sg.Text(size = (25,1), key = 'cardName'), 
                sg.Text("Mana Cost: "),
                sg.Text(size = (25,1), key = 'cardMana')
                ],
                [
                sg.Text("Text: "), 
                sg.Text(size = (20, 4), key = 'cardText')
                ]
            ]

        self.layout_R = [
                [sg.Text(size = (20, 3), key = '-URL-')],
                [sg.Image(key = '-IMAGE-')]
            ]

        self.layout_middle = [sg.Column(self.layout_L), sg.Column(self.layout_R)]

        self.layout_bottom = [
                sg.Button("Download Image", disabled = True,  key = '-DL-'),
                sg.Button("Rebuild Set", disabled = True,  key = '-REBUILD-'),                
                sg.Button("Exit")
            ]

        self.layout = [[self.layout_top], [self.layout_middle], [self.layout_bottom]]

        return sg.Window("MTG", self.layout, grab_anywhere=True, resizable=True, margins=(0,0))


    def run(self):
        window = self.make_window()        
        self.setCards = self.set.card_list

        while True:
            event, values = window.read()
            print(event, values)
            self.log(f"\tEVENT: {event}\n\tValues: {values}")


            if event in (None, 'Exit'):
                break

            if event == '-CODE-':
                self.set = self.filer.unpickleSet(values['-CODE-'])
                window['-CARD-'].update(values = self.set.card_list)
                window['-CARD_COUNT-'].update(f"{str(self.set.num_of_cards)} cards")
                window['-REBUILD-'].update(disabled = False)

            if event == '-CARD-':
                self.card = values['-CARD-']
                try:
                    window['-DL-'].update(disabled = self.card.hasImage)
                except Exception as e:
                    self.log(e)
                    window['-DL-'].update(disabled = True)
                window['cardName'].update(self.card.name)
                try:
                    window['cardMana'].update(self.card.mana)
                except AttributeError:
                    self.set.getAPI()
                    self.filer.pickleSet(self.set)
                    window.refresh()
                if self.card.url != None:
                    response = requests.get(self.card.url)
                    image_bytes = io.BytesIO(response.content)
                    img = Image.open(image_bytes)
                    img.save(image_bytes, format = "PNG")
                    img2 = ImageTk.PhotoImage(img)
                    del img
                    window['-URL-'].update(self.card.url)
                    window['-IMAGE-'].update(data = img2)
                window['cardText'].update(self.card.text)
                window.refresh()

            if event == '-DL-':
                card = values['-CARD-']
                self.filer.download(card)
                window['-DL-'].update(disabled = True)
            
            if event == '-REBUILD-':
                code = values['-CODE-']
                self.set = self.filer.createSet(code, ret = True)
                window['-REBUILD-'].update(disabled = True)
                window.refresh()

        window.close()            



if __name__ == "__main__":
    gui = MTG_GUI()
    gui.run()
else:
   print("mtg_gui executed when imported")