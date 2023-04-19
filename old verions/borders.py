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
from kivy.graphics import Color, Rectangle

class TimerForm(BoxLayout):
    def __init__(self, popup_instance, timer_app, **kwargs):
        super(TimerForm, self).__init__(**kwargs)
        self.popup_instance = popup_instance
        self.timer_app = timer_app
        self.orientation = 'vertical'

        self.add_widget(Label(text="Number of people"))
        self.people = TextInput(multiline=False)
        self.add_widget(self.people)
        
        self.add_widget(Label(text="Number of boats"))
        self.boats = TextInput(multiline=False)
        self.add_widget(self.boats)
        
        self.add_widget(Label(text="Time (seconds)"))
        self.time = TextInput(multiline=False)
        self.add_widget(self.time)
        
        self.add_widget(Label(text="Price"))
        self.price = TextInput(multiline=False)
        self.add_widget(self.price)
        
        self.submit = Button(text="Submit", on_release=self.submit_form)
        self.add_widget(self.submit)
    
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

        self.popup_instance.dismiss()
        self.timer_app.start_timer(self.form_data)

class TimerLabel(Label):
    def __init__(self, time, **kwargs):
        super(TimerLabel, self).__init__(**kwargs)
        self.remaining_time = time
        self.text = f"{self.remaining_time} seconds remaining"
        self.update_event = Clock.schedule_interval(self.update, 1)
        self.size_hint_y = None
        self.height = 20


    def update(self, dt):
        self.remaining_time -= 1
        if self.remaining_time <= 0:
            self.text = "Time's up!"
            self.color = [1, 0, 0, 1]
            Clock.unschedule(self.update_event)
        else:
            self.text = f"{self.remaining_time} seconds remaining"

class TimerApp(BoxLayout):
    def __init__(self, **kwargs):
        super(TimerApp, self).__init__(**kwargs)
        self.orientation = 'vertical'

        self.anchor_layout = AnchorLayout(anchor_x='center', anchor_y='bottom', size_hint=(1, 1))
        self.scroll_view = ScrollView(size_hint=(1, None), size=(Window.width, Window.height * 0.5))
        self.timer_list = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.timer_list.bind(minimum_height=self.timer_list.setter('height'))

        self.scroll_view.add_widget(self.timer_list)
        self.anchor_layout.add_widget(self.scroll_view)

        self.float_layout = FloatLayout()
        self.float_layout.add_widget(self.anchor_layout)
        self.float_layout.add_widget(Button(text="+", size_hint=(0.1, 0.1), pos_hint={'x': 0.9, 'top': 1}, on_press=self.show_form))

        self.add_widget(self.float_layout)

        with self.canvas.before:
            Color(0, 0, 1, 1)  # Set the background color to blue
            self.rect = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self.update_rect, size=self.update_rect)

        # Draw a green border for the ScrollView
        with self.scroll_view.canvas.after:
            Color(0, 1, 0, 1)
            self.border = [
                Rectangle(pos=(self.scroll_view.x, self.scroll_view.y), size=(self.scroll_view.width, 2)),
                Rectangle(pos=(self.scroll_view.x, self.scroll_view.top - 2), size=(self.scroll_view.width, 2)),
                Rectangle(pos=(self.scroll_view.x, self.scroll_view.y), size=(2, self.scroll_view.height)),
                Rectangle(pos=(self.scroll_view.right - 2, self.scroll_view.y), size=(2, self.scroll_view.height))
            ]
        self.scroll_view.bind(pos=self.update_border, size=self.update_border)

    def update_border(self, instance, value):
        self.border[0].pos = (instance.x, instance.y)
        self.border[0].size = (instance.width, 2)
        self.border[1].pos = (instance.x, instance.top - 2)
        self.border[1].size = (instance.width, 2)
        self.border[2].pos = (instance.x, instance.y)
        self.border[2].size = (2, instance.height)
        self.border[3].pos = (instance.right - 2, instance.y)
        self.border[3].size = (2, instance.height)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def show_form(self, instance):
        form_popup = Popup(title="Add Timer", size_hint=(0.8, 0.8))
        form = TimerForm(popup_instance=form_popup, timer_app=self)
        form_popup.add_widget(form)
        form_popup.open()

    def start_timer(self, form_data):
        timer = TimerLabel(time=form_data['time'])
        self.timer_list.add_widget(timer, index=len(self.timer_list.children))

class MyApp(App):
    def build(self):
        return TimerApp()

if __name__ == '__main__':
    MyApp().run()