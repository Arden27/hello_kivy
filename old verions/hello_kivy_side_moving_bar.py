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

from kivy.uix.progressbar import ProgressBar
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

class CustomProgressBar(ProgressBar):
    def __init__(self, bg_color, **kwargs):
        super(CustomProgressBar, self).__init__(**kwargs)
        self.bg_color = bg_color
        with self.canvas.before:
            Color(*self.bg_color)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

class TimerLabel(BoxLayout):
    def __init__(self, time, timer_app, **kwargs):
        super(TimerLabel, self).__init__(**kwargs)
        self.timer_app = timer_app
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 30

        self.progress_bar = CustomProgressBar(bg_color=(0.6, 0.6, 0.6, 1), max=time, value=0, size_hint=(1, None), height=20)
        self.add_widget(self.progress_bar)

        self.label = Label(text=f"{time} seconds remaining", size_hint_x=0.8, size_hint_y=None, height=20)
        self.add_widget(self.label)
        self.update_event = Clock.schedule_interval(self.update, 1)
        self.remaining_time = time

        self.delete_button = Button(text='[x]', 
                                    size_hint=(0.05, None), 
                                    height=20, 
                                    color=(0.6, 0, 0, 1), 
                                    background_color=(1, 1, 1, 1), 
                                    background_normal='', 
                                    bold = True,
                                    on_release=self.delete_timer)
        self.add_widget(self.delete_button)

    def update(self, dt):
        self.remaining_time -= 1
        self.progress_bar.value = self.progress_bar.max - self.remaining_time
        if self.remaining_time <= 0:
            self.label.text = "Time's up!"
            self.label.color = [1, 0, 0, 1]
            Clock.unschedule(self.update_event)
        else:
            self.label.text = f"{self.remaining_time} seconds remaining"

    def delete_timer(self, instance):
        Clock.unschedule(self.update_event)
        self.timer_app.timer_list.remove_widget(self)

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

    def show_form(self, instance):
        form_popup = Popup(title="Add Timer", size_hint=(0.8, 0.8))
        form = TimerForm(popup_instance=form_popup, timer_app=self)
        form_popup.add_widget(form)
        form_popup.open()

    def start_timer(self, form_data):
        timer = TimerLabel(time=form_data['time'], timer_app=self)
        self.timer_list.add_widget(timer, index=len(self.timer_list.children))

class MyApp(App):
    def build(self):
        return TimerApp()

if __name__ == '__main__':
    MyApp().run()