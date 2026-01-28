import threading
import json
from kivy.clock import Clock, mainthread
from kivy.properties import StringProperty, NumericProperty
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.screen import MDScreen
from kivymd.uix.behaviors import RoundedRectangularElevationBehavior
from kivymd.uix.list import OneLineListItem

# Import the MTG SDK
from mtgsdk import Card as MtgCard
from mtgsdk import Set as MtgSet




class MTGCardWidget(MDCard, RoundedRectangularElevationBehavior):
    card_name = StringProperty("")
    type_line = StringProperty("")
    oracle_text = StringProperty("")
    image_url = StringProperty("https://gatherer.wizards.com/Handlers/Image.ashx?type=card&name=Back")

class SetSelectionScreen(MDScreen):
    def on_enter(self, *args):
        Clock.schedule_once(self.populate_list)

    def populate_list(self, dt):
        list_view = self.ids.set_list
        if list_view.children:
            return
        
        self.sets = []
        try:
            with open("setlist.json","r") as f:
                self.sets = json.load(f)
        except Exception as e:
            print(f"Error loading setlist.json: {e}")
        
        for s in self.sets:
            item = OneLineListItem(
                text=f"{s['name']} ({s['release_date']})",
                on_release=lambda x, code=s['code']: self.select_set(code)
            )
            list_view.add_widget(item)

    def select_set(self, set_code):
        app = MDApp.get_running_app()
        viewer = app.root.get_screen('card_viewer')
        viewer.current_set = set_code
        viewer.current_page = 1
        app.root.current = "card_viewer"
        app.root.transition.direction = "left"
        viewer.load_cards()


class CardViewerScreen(MDScreen):
    current_page = NumericProperty(1)
    current_set = StringProperty("")

    def go_back(self):
        self.manager.transition.direction = "right"
        self.manager.current = "set_selection"

    def change_page(self, direction):
        new_page = self.current_page + direction
        if new_page < 1:
            return
        self.current_page = new_page
        self.load_cards()

    def load_cards(self):
        self.ids.status_label.text = f"Loading {self.current_set} - Page {self.current_page}..."
        self.ids.card_grid.clear_widgets()
        self.ids.scroll_view.scroll_y = 1
        threading.Thread(target=self.fetch_thread, daemon=True).start()

    def fetch_thread(self):
        try:
            cards = MtgCard.where(set=self.current_set)\
                           .where(page=self.current_page)\
                           .where(pageSize=15)\
                           .all()
            self.update_ui(cards)
        except Exception as e:
            print(e)
            self.update_status(f"Error: {e}")

    @mainthread
    def update_ui(self, cards):
        if not cards:
            self.update_status("No more cards found in this set.")
            return
            
        grid = self.ids.card_grid
        for card in cards:
            w = MTGCardWidget()
            w.card_name = card.name
            w.type_line = card.type if card.type else ""
            w.oracle_text = card.text if card.text else ""
            if card.image_url:
                w.image_url = card.image_url
            grid.add_widget(w)
            
        self.update_status(f"Loaded {len(cards)} cards.")

    @mainthread
    def update_status(self, text):
        self.ids.status_label.text = text


class MTGApp(MDApp):
    def build(self):
        # Kivy automatically loads 'mtg.kv' because the class is named 'MTGApp'
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Amber"
        
        # We don't need to return anything; 
        # Kivy has already instantiated the root widget from mtg.kv 
        # and assigned it to self.root
        return self.root

if __name__ == '__main__':
    MTGApp().run()
