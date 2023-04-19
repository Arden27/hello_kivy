from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.clock import Clock

from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout

from functools import partial

class TimerForm(BoxLayout):
    def __init__(self, popup_instance, timer_app, edit_item=None, **kwargs):
        super(TimerForm, self).__init__(**kwargs)
        self.popup_instance = popup_instance
        self.timer_app = timer_app
        self.edit_item = edit_item
        self.orientation = 'vertical'

        form_fields = [
            ("Number of people", "people", "1", "int"),
            ("Number of boats", "boats", "1", "int")
        ]

        for field in form_fields:
            label, attr_name, default, input_filter = field
            self.add_widget(Label(text=label))
            setattr(self, attr_name, TextInput(text=default, multiline=False, input_filter=input_filter, size_hint_y=None, height=30))
            btn_box = BoxLayout(size_hint_y=None, height=30)
            btn_box.add_widget(Button(text="+", on_release=lambda _, i=attr_name: self.increment(getattr(self, i))))
            btn_box.add_widget(Button(text="-", on_release=lambda _, i=attr_name: self.decrement(getattr(self, i))))
            self.add_widget(getattr(self, attr_name))
            self.add_widget(btn_box)
        
        self.add_widget(Label(text="Time (seconds)"))
        self.time = TextInput(multiline=False)
        self.add_widget(self.time)
        
        self.add_widget(Label(text="Price"))
        self.price = TextInput(multiline=False)
        self.add_widget(self.price)
        
        self.submit = Button(text="Submit", on_release=self.submit_form)
        self.add_widget(self.submit)
    
    def increment(self, text_input):
        value = int(text_input.text)
        value += 1
        text_input.text = str(value)

    def decrement(self, text_input):
        value = int(text_input.text)
        value -= 1
        if value < 1:
            value = 1
        text_input.text = str(value)
    
    def submit_form(self, instance):
        try:
            time = float(self.time.text)
        except ValueError:
            time = 0

        self.form_data = {
            'people': self.people.text,
            'boats': self.boats.text,
            'time': time,
            'price': self.price.text
        }

        if self.edit_item is not None:
            self.timer_app.update_history(self.edit_item, self.form_data)
        else:
            self.timer_app.start_timer(self.form_data)
        self.popup_instance.dismiss()

class HistoryPopup(Popup):
    def __init__(self, timer_app, **kwargs):
        super(HistoryPopup, self).__init__(**kwargs)
        self.timer_app = timer_app

        self.title = "History"
        self.size_hint = (0.8, 0.8)

        self.history_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.history_layout.bind(minimum_height=self.history_layout.setter('height'))

        total_people = 0
        total_boats = 0
        total_price = 0

        for item in self.timer_app.deleted_timers:
            history_item = BoxLayout(size_hint_y=None, height=30)
            history_text = f"People: {item['people']}, Boats: {item['boats']}, Price: {item['price']}, Time: {item['time']}"
            history_item.add_widget(Label(text=history_text, size_hint_x=0.8))
            history_item.add_widget(Button(text="Edit", size_hint_x=0.2, on_release=partial(self.timer_app.edit_form, item)))
            self.history_layout.add_widget(history_item)

            # Update the totals
            total_people += int(item['people'])
            total_boats += int(item['boats'])
            total_price += float(item['price'])

        self.scroll_view = ScrollView(size_hint=(1, 1))
        self.scroll_view.add_widget(self.history_layout)

        self.box_layout = BoxLayout(orientation="vertical")
        self.box_layout.add_widget(self.scroll_view)

        self.totals_label = Label(text=f"Total people: {total_people}, \nTotal boats: {total_boats}, \nTotal price: {total_price}")
        self.box_layout.add_widget(self.totals_label)
        
        self.box_layout.add_widget(Button(text="Close", size_hint_y=0.1, on_release=self.dismiss))

        self.add_widget(self.box_layout)

class TimerLabel(BoxLayout):
    def __init__(self, time, timer_app, form_data, **kwargs):
        super(TimerLabel, self).__init__(**kwargs)
        self.timer_app = timer_app
        self.form_data = form_data
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 60

        self.timer_info_box = BoxLayout(orientation="vertical", size_hint=(0.9, 1))
        self.label_data = Label(text=f"People: {form_data['people']}, Boats: {form_data['boats']}, Price: {form_data['price']}", size_hint_y=None, height=20)
        self.timer_info_box.add_widget(self.label_data)

        self.label = Label(text=f"{time} seconds remaining", size_hint_y=None, height=20)
        self.timer_info_box.add_widget(self.label)
        self.update_event = Clock.schedule_interval(self.update, 1)
        self.remaining_time = time

        self.delete_button = Button(text='[x]', 
                                    size_hint=(0.05, None), 
                                    height=20, 
                                    color=(0.6, 0, 0, 1), 
                                    background_color=(1, 1, 1, 1), 
                                    background_normal='', 
                                    bold=True,
                                    on_release=self.delete_timer)
        
        self.add_widget(self.timer_info_box)
        self.add_widget(self.delete_button)

    def update(self, dt):
        try:
            self.remaining_time -= 1
            if self.remaining_time <= 0:
                self.label.text = "Time's up!"
                self.label.color = [1, 0, 0, 1]
                Clock.unschedule(self.update_event)
            else:
                self.label.text = f"{self.remaining_time} seconds remaining"
        except ValueError:
            self.label.text = "Invalid time value"
            Clock.unschedule(self.update_event)

    def delete_timer(self, instance):
        Clock.unschedule(self.update_event)
        self.timer_app.timer_list.remove_widget(self)
        self.form_data['time'] = self.remaining_time
        self.timer_app.deleted_timers.append(self.form_data)

class TimerApp(BoxLayout):
    def __init__(self, **kwargs):
        super(TimerApp, self).__init__(**kwargs)
        self.orientation = 'vertical'

        self.history_popup = None

        self.deleted_timers = []

        self.anchor_layout = AnchorLayout(anchor_x='center', anchor_y='bottom', size_hint=(1, 1))
        self.scroll_view = ScrollView(size_hint=(1, None), size=(Window.width, Window.height * 0.5))
        self.timer_list = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.timer_list.bind(minimum_height=self.timer_list.setter('height'))

        self.scroll_view.add_widget(self.timer_list)
        self.anchor_layout.add_widget(self.scroll_view)

        self.float_layout = FloatLayout()
        self.float_layout.add_widget(self.anchor_layout)
        self.float_layout.add_widget(Button(text="+", size_hint=(0.25, 0.1), pos_hint={'x': 0.75, 'top': 1}, on_press=self.show_form))

        self.add_widget(self.float_layout)

    def show_form(self, instance):
        form_popup = Popup(title="Add Timer", size_hint=(0.8, 0.8))
        form = TimerForm(popup_instance=form_popup, timer_app=self)
        form_popup.add_widget(form)
        form_popup.open()

    def show_history(self):
        self.history_popup = HistoryPopup(timer_app=self)
        self.history_popup.open()

    def start_timer(self, form_data):
        timer = TimerLabel(time=form_data['time'], timer_app=self, form_data=form_data)
        self.timer_list.add_widget(timer, index=len(self.timer_list.children))

    def update_history(self, old_item, new_form_data):
        if old_item in self.deleted_timers:
            index = self.deleted_timers.index(old_item)
            self.deleted_timers[index] = new_form_data
            if self.history_popup is not None:
                self.history_popup.dismiss()
                self.history_popup = None
                self.show_history()

    def edit_form(self, item, *args):
        form_data = item
        form_popup = Popup(title="Edit Timer", size_hint=(0.8, 0.8))
        form = TimerForm(popup_instance=form_popup, timer_app=self, edit_item=item)
        form.people.text = str(form_data['people'])
        form.boats.text = str(form_data['boats'])
        form.time.text = str(form_data['time'])
        form.price.text = str(form_data['price'])
        form_popup.add_widget(form)
        form_popup.open()

class MyApp(App):
    def build(self):
        timer_app = TimerApp()
        float_layout = FloatLayout()
        float_layout.add_widget(timer_app)
        float_layout.add_widget(Button(text="History", size_hint=(0.25, 0.1), pos_hint={'x': 0, 'top': 1}, on_press=lambda _: timer_app.show_history()))
        return float_layout

if __name__ == '__main__':
    MyApp().run()