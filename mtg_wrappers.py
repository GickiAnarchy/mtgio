"""
    Created by: FatherAnarchy        email: fatheranarchy@programmer.net
    
    mtgsdk wrappers used for GUI and file handling purposes. 
    
    *This is not a complete program and will be updated in the future.

"""
from mtgsdk import Card, Set
import os
import json
from time import perf_counter
import pickle
import requests
import datetime



D_SETS = os.path.abspath(os.path.join(os.path.dirname(__file__),".", "Sets"))
if not os.path.isdir(D_SETS):
    print(f"created {D_SETS}")
    os.makedirs(D_SETS)
D_IMAGES = os.path.abspath(os.path.join(os.path.dirname(__file__),".", "Images"))
if not os.path.isdir(D_IMAGES):
    print(f"created {D_IMAGES}")
    os.makedirs(D_IMAGES)



#        #        #        #        #        #
#        #        #        #        #        #
class MTGCard:
    def __init__(self, card:Card):
        self.card = card
        self.name = card.name
        self.code = card.set
        self.set_name = card.set_name
        self.type = card.type
        self.url = card.image_url
        self.multi_id = card.multiverse_id
        self.cmc = card.cmc
        self.mana = card.mana_cost
        self.text = card.text
        self.colors = card.colors
        self.color = card.color_identity
        self.image = f"{D_IMAGES}/{self.code}/{self.multi_id}.jpg"


    def __repr__(self):
        return self.name


    @property
    def hasImage(self):
        return os.path.isfile(self.image)
    @property
    def card(self):
        return self._card
    @card.setter
    def card(self, new_card):
        self._card = new_card
    @property
    def color(self):
        return self._color
    @color.setter
    def color(self, new_color):
        self._color = new_color
    @property
    def colors(self):
        return self._colors
    @colors.setter
    def colors(self, new_colors):
        self._colors = new_colors
    @property
    def mana(self):
        return self._mana
    @mana.setter
    def mana(self, new_mana):
        self._mana = new_mana
    @property
    def type(self):
        return self._type
    @type.setter
    def type(self, new_type):
        self._type = new_type
    @property
    def text(self):
        return self._text
    @text.setter
    def text(self, new_text):
        self._text = new_text
    @property
    def url(self):
        return self._url
    @url.setter
    def url(self, new_url):
        self._url = new_url
    @property
    def multi_id(self):
        return self.id
    @multi_id.setter
    def multi_id(self, new_id):
        self.id = new_id
    @property
    def code(self):
        return self._code
    @code.setter
    def code(self, new_code):
        self._code = new_code
    @property
    def set_name(self):
        return self._set_name
    @set_name.setter
    def set_name(self, new_set_name):
        self._set_name = new_set_name
    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, new_name):
        self._name = new_name
    @property
    def image(self):
        return self._image
    @image.setter
    def image(self, new_image):
        self._image = new_image
    @property
    def cmc(self):
        return self._cmc
    @cmc.setter
    def cmc(self, new_cmc):
        self._cmc = new_cmc



#        #        #        #        #        #
#        #        #        #        #        #
class MTGSet:
    def __init__(self, pset:Set):
        self.set = pset
        self.name = pset.name
        self.code = pset.code
        self.cards = []
        self.ids = []
        self.urls = []
        


    def getIDs(self):
        print(f"Finding ids for {str(self.num_of_cards)} cards")
        for c in self.cards:
            if c.multi_id not in self.ids:
                self.ids.append(c.multi_id)
            elif c.multi_id in self.ids:
                print(f"{c.multi_id} is in ids already")

    def checkList(self, card):
        checkFor = f"{card.multi_id}"
        for c in self.cards:
            if c.multi_id == checkFor:
                print(f"{checkFor} - {c.name} is already in the list")
                return False
        return True
    
    def add_card(self, card):
        if self.checkList(card):
            self.cards.append(card)
            print(f"added {card.multi_id} -- {card.name} to {self.name} cards")

    def getAPI(self):
        start_time = perf_counter()
        self.cards.clear()
        tempList = Card.where(set = self.code).all()
        for c in tempList:
            wrapped = MTGCard(c)
            self.add_card(wrapped)
        end_time = perf_counter()
        print(f"API took {end_time - start_time :0.2f}")

    def getURLS(self):
        for c in self.cards:
            self.urls.append(c.url)
            print(c.url + "\n")
        return self.urls

    def getCardNames(self):
        names = []
        for card in self.cards:
            names.append(card.name)
        return names

    @property
    def set(self):
        return self._set
    @set.setter
    def set(self, new_set):
        self._set = new_set
    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, new_name):
        self._name = new_name
    @property
    def code(self):
        return self._code
    @code.setter
    def code(self, new_code):
        self._code = new_code
    @property
    def num_of_cards(self):
        return len(self.cards)
    @property
    def card_list(self):
        return self.cards


#
#
class MTGFiler:
    def __init__(self):
        self.setslist = []



    def createSet(self, code, ret = False):
        s = Set.find(code)
        set = MTGSet(s)
        set.getAPI()
        self.pickleSet(set)
        if ret:
            return set
        else:
            return

    def pickleSet(self, set:MTGSet):
        with open(f"{D_SETS}/{set.code}.fa", "wb") as file:
            pickle.dump(set, file)
            file.close()

    def unpickleSet(self, set):
        if not os.path.isfile(f"{D_SETS}/{set}.fa"):
            self.createSet(set)
            print(f"Created and pickled set {set}")
        with open(f"{D_SETS}/{set}.fa", "rb") as file:
            ret = pickle.load(file)
            file.close()
        return ret

    def readSetCodes(self):
        print("in: readSetCodes")
        with open(".allsets.txt", "r") as sets_reader:
            str = sets_reader.read()
            self.setslist = str.split(sep = f'{", "}')
            sets_reader.close()
        return self.setslist

    def downloadImg(self, set):
        if set.num_of_cards <= 0:
            set.getAPI()
        dir = f"{D_IMAGES}/{set.code}"
        cardList = set.card_list
        if not os.path.isdir(dir):
            print(f"created {dir}")
            os.makedirs(dir)
        for card in cardList:
            file = f"{dir}/{card.multi_id}.jpg"
            if (card.multi_id == None) or (os.path.isfile(file)):
                print(f"skipping {file}")
                continue
            with open(file, 'wb') as f:
                f.write(requests.get(card.url).content)
                f.close()
            print(f"{file} is downloaded")

    def download(self, card):
        dir = f"{D_IMAGES}/{card.code}"
        if not os.path.isdir(dir):
            print(f"created {dir}")
            os.makedirs(dir)
        file = f"{dir}/{card.multi_id}.jpg"
        if (card.multi_id == None) or (os.path.isfile(file)):
            print(f"skipping {file}")
            return
        with open(file, 'wb') as f:
            f.write(requests.get(card.url).content)
            f.close()
            print(f"{file} is downloaded")

    def log(self, msg, f = False):
        if os.path.isfile(".log.txt"):
            mode = "a"
        if not os.path.isfile(".log.txt") or f == True: 
            mode = "w"
        with open(".log.txt", mode = mode) as logFile:
            s = f"{self.getNow()}\n{msg}\n"
            logFile.write(s)
            logFile.close()

    def getNow(self):
        dt = datetime.datetime.now()
        dDate = f"{dt.month}-{dt.day}"
        dTime = f"{dt.hour}:{dt.minute}:{dt.second}"
        dNow = f"{dDate}\t{dTime}"
        return dNow
