from kivy.app import App
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.properties import StringProperty
from kivy.storage.jsonstore import JsonStore
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager

import os

# Ensure proper file path for JsonStore
store_path = os.path.join(os.path.dirname(__file__), 'data.json')
store = JsonStore(store_path)

class Custombtn(Button):
    key_name = StringProperty()

class Interface(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.fetching_data)

    def truncate_string(self, str_input, max_length):
        """Truncates a string to fit within a maximum length."""
        str_end = '...'
        if len(str_input) > max_length:
            return str_input[:max_length - len(str_end)] + str_end
        return str_input

    def deleting(self, obj_btn):
        """Handles deleting an item."""
        key_name = obj_btn.key_name
        if key_name in self.ids:
            self.ids.gridLayout.remove_widget(self.ids[key_name])
            del self.ids[key_name]
        store.delete(key_name)

    def fetching_data(self, dt):
        """Fetches data from the JsonStore and populates the grid layout."""
        try:
            keys = store.keys()
            if not keys:
                print("No data found in JsonStore.")
                return
            for key in keys:
                layout = BoxLayout(size_hint_y=None, height=dp(80))
                self.ids[key] = layout
                title = Custombtn(key_name=key, text=self.truncate_string(key, 10))
                delete = Custombtn(
                    key_name=key,
                    on_press=self.deleting,
                    text="Delete",
                    size_hint=(None, None),
                    size=(dp(80), dp(80))
                )
                title.bind(on_press=self.detail_screen)
                layout.add_widget(title)
                layout.add_widget(delete)
                self.ids.gridLayout.add_widget(layout)
        except Exception as e:
            print(f"Error while fetching data: {e}")

    def back_btn(self):
        """Handles navigating back to the main screen and saving data."""
        self.current = "MainScreen"
        key = self.ids.noticeTitle.text
        data = self.ids.inputData.text
        store.put(key, data=data)

    def detail_screen(self, btn_obj):
        """Displays details for the selected item."""
        self.current = "Details Screen"
        key = btn_obj.key_name
        self.ids.noticeTitle.text = key
        self.ids.inputData.text = store.get(key)["data"]

    def addItem(self, obj):
        """Adds a new item to the store and updates the UI."""
        self.popup.dismiss()
        key = self.textInput.text.strip()
        if not key:
            print("Cannot add an empty key.")
            return
        if key in store:
            print(f"Key '{key}' already exists.")
            return
        layout = BoxLayout(size_hint_y=None, height=dp(80))
        self.ids[key] = layout
        title = Custombtn(key_name=key, text=self.truncate_string(key, 10))
        delete = Custombtn(
            key_name=key,
            on_press=self.deleting,
            text="Delete",
            size_hint=(None, None),
            size=(dp(80), dp(80))
        )
        title.bind(on_press=self.detail_screen)
        layout.add_widget(title)
        layout.add_widget(delete)
        store.put(key, data="")
        self.ids.gridLayout.add_widget(layout)

    def show_popup(self):
        """Displays a popup for adding a new item."""
        layout = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(10))
        btn = Button(text="Submit")
        btn.bind(on_press=self.addItem)
        self.textInput = TextInput(multiline=False)
        layout.add_widget(self.textInput)
        layout.add_widget(btn)
        self.popup = Popup(title="Add New Item", size_hint=(0.8, None), height=dp(180), content=layout)
        self.popup.open()

class TodoApp(App):
    pass

TodoApp().run()
