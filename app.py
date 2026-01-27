import threading
from kivy.clock import Clock  # <--- Make sure you import this at the top
from kivy.lang import Builder
from kivy.clock import mainthread
from kivy.properties import StringProperty, NumericProperty, ObjectProperty
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.behaviors import RoundedRectangularElevationBehavior
from kivymd.uix.list import OneLineListItem

# Import the MTG SDK
from mtgsdk import Card as MtgCard
from mtgsdk import Set as MtgSet

# -------------------------------------------------------------------------
# KV Layout String
# -------------------------------------------------------------------------
KV = '''
<MTGCardWidget>:
    orientation: "vertical"
    size_hint: None, None
    size: "280dp", "400dp"
    radius: [12]
    elevation: 3
    padding: "8dp"
    md_bg_color: 0.15, 0.15, 0.15, 1

    BoxLayout:
        size_hint_y: None
        height: "30dp"
        MDLabel:
            text: root.card_name
            theme_text_color: "Custom"
            text_color: 1, 1, 1, 1
            bold: True
            shorten: True
            shorten_from: 'right'

    AsyncImage:
        source: root.image_url
        size_hint_y: None
        height: "180dp"
        allow_stretch: True
        keep_ratio: True
        nocache: True

    MDLabel:
        text: root.type_line
        size_hint_y: None
        height: "25dp"
        theme_text_color: "Custom"
        text_color: 0.8, 0.8, 0.8, 1
        font_style: "Caption"

    ScrollView:
        MDLabel:
            text: root.oracle_text
            font_style: "Caption"
            theme_text_color: "Custom"
            text_color: 0.9, 0.9, 0.9, 1
            size_hint_y: None
            height: self.texture_size[1]

# --- Screen 1: Set Selection ---
<SetSelectionScreen>:
    BoxLayout:
        orientation: "vertical"
        
        MDTopAppBar:
            title: "Select a Set"
            elevation: 4

        ScrollView:
            MDList:
                id: set_list

# --- Screen 2: Card Viewer ---
<CardViewerScreen>:
    BoxLayout:
        orientation: "vertical"
        
        MDTopAppBar:
            id: top_bar
            title: "Card Viewer"
            elevation: 4
            left_action_items: [["arrow-left", lambda x: root.go_back()]]
            right_action_items: [["refresh", lambda x: root.load_cards()]]

        # Status Label
        MDLabel:
            id: status_label
            text: "Loading..."
            halign: "center"
            size_hint_y: None
            height: "30dp"
            theme_text_color: "Hint"

        # Card Grid
        ScrollView:
            id: scroll_view
            GridLayout:
                id: card_grid
                cols: 1
                spacing: "20dp"
                padding: "20dp"
                size_hint_y: None
                height: self.minimum_height
                row_default_height: "420dp"
                row_force_default: True

        # Pagination Footer
        MDBoxLayout:
            size_hint_y: None
            height: "60dp"
            md_bg_color: 0.1, 0.1, 0.1, 1
            padding: "10dp"
            spacing: "20dp"

            MDIconButton:
                icon: "chevron-left"
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
                pos_hint: {"center_y": 0.5}
                on_release: root.change_page(-1)
                disabled: root.current_page <= 1

            MDLabel:
                text: f"Page {root.current_page}"
                halign: "center"
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
                pos_hint: {"center_y": 0.5}

            MDIconButton:
                icon: "chevron-right"
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
                pos_hint: {"center_y": 0.5}
                on_release: root.change_page(1)

MDScreenManager:
    SetSelectionScreen:
        name: "set_selection"
    CardViewerScreen:
        name: "card_viewer"
'''

class MTGCardWidget(MDCard, RoundedRectangularElevationBehavior):
    card_name = StringProperty("")
    type_line = StringProperty("")
    oracle_text = StringProperty("")
    image_url = StringProperty("https://gatherer.wizards.com/Handlers/Image.ashx?type=card&name=Back")

class SetSelectionScreen(MDScreen):
    def on_enter(self, *args):
        """
        Called when the screen is displayed.
        We use Clock.schedule_once to ensure the UI is fully built
        before we try to access self.ids.
        """
        Clock.schedule_once(self.populate_list)

    def populate_list(self, dt):
        """
        Actual logic to add items to the list. 
        'dt' is delta-time, automatically passed by Clock.
        """
        # 1. Check if we have already populated the list to avoid duplicates
        #    (ids might not be ready if we didn't use Clock, but now they are)
        list_view = self.ids.set_list
        
        # If the list is already full, don't add them again
        if list_view.children:
            return

        sets = [
            {"code": "KTK", "name": "Khans of Tarkir"},
            {"code": "WOE", "name": "Wilds of Eldraine"},
            {"code": "LEA", "name": "Alpha"},
            {"code": "NEO", "name": "Kamigawa: Neon Dynasty"},
            {"code": "MH2", "name": "Modern Horizons 2"},
            {"code": "MID", "name": "Innistrad: Midnight Hunt"},
        ]
        
        for s in sets:
            item = OneLineListItem(
                text=f"{s['name']} ({s['code']})",
                on_release=lambda x, code=s['code']: self.select_set(code)
            )
            list_view.add_widget(item)

    def select_set(self, set_code):
        app = MDApp.get_running_app()
        viewer = app.root.get_screen('card_viewer')
        viewer.current_set = set_code
        viewer.current_page = 1
        
        # Switch screens
        app.root.current = "card_viewer"
        app.root.transition.direction = "left"
        
        # Trigger load
        viewer.load_cards()


class CardViewerScreen(MDScreen):
    current_page = NumericProperty(1)
    current_set = StringProperty("")

    def go_back(self):
        self.manager.transition.direction = "right"
        self.manager.current = "set_selection"

    def change_page(self, direction):
        """
        Direction: +1 for next, -1 for prev
        """
        new_page = self.current_page + direction
        if new_page < 1:
            return
        
        self.current_page = new_page
        self.load_cards()

    def load_cards(self):
        self.ids.status_label.text = f"Loading {self.current_set} - Page {self.current_page}..."
        self.ids.card_grid.clear_widgets()
        
        # Scroll to top
        self.ids.scroll_view.scroll_y = 1
        
        # Start Thread
        threading.Thread(target=self.fetch_thread, daemon=True).start()

    def fetch_thread(self):
        try:
            # Using pageSize=10 to keep it fast
            cards = MtgCard.where(set=self.current_set)\
                           .where(page=self.current_page)\
                           .where(pageSize=10)\
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
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Teal"
        return Builder.load_string(KV)

if __name__ == '__main__':
    MTGApp().run()
