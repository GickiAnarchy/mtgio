import json
import os

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout


class SetsScreen(MDScreen):
    def on_enter(self):
        self.sets = self.app.sets
    
    
    @property
    def app(self):
        return MDApp.get_running_app()