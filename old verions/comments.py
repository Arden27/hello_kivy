class TimerApp(BoxLayout):
    def __init__(self, **kwargs):
        super(TimerApp, self).__init__(**kwargs)  # Call the base class constructor and pass any additional keyword arguments
        self.orientation = 'vertical'  # Set the orientation of the main BoxLayout to vertical

        # Create an AnchorLayout for positioning the ScrollView, with anchor points set to center and bottom
        self.anchor_layout = AnchorLayout(anchor_x='center', anchor_y='bottom', size_hint=(1, 1))
        
        # Create a ScrollView with a size hint for the width, and a fixed size for the height (50% of the window height)
        self.scroll_view = ScrollView(size_hint=(1, None), size=(Window.width, Window.height * 0.5))
        
        # Create a GridLayout for the timer list with a single column, 10 units of spacing between children, and no size hint for the height
        self.timer_list = GridLayout(cols=1, spacing=10, size_hint_y=None)
        
        # Bind the minimum height of the timer list to its height property, allowing it to grow with its contents
        self.timer_list.bind(minimum_height=self.timer_list.setter('height'))

        # Add the timer list to the ScrollView
        self.scroll_view.add_widget(self.timer_list)
        
        # Add the ScrollView to the AnchorLayout
        self.anchor_layout.add_widget(self.scroll_view)

        # Create a FloatLayout to allow for overlapping widgets (the "+" button will overlap the ScrollView)
        self.float_layout = FloatLayout()
        
        # Add the AnchorLayout containing the ScrollView to the FloatLayout
        self.float_layout.add_widget(self.anchor_layout)
        
        # Create a "+" button with a size hint, position hint, and callback function for when it's pressed
        self.float_layout.add_widget(Button(text="+", size_hint=(0.1, 0.1), pos_hint={'x': 0.9, 'top': 1}, on_press=self.show_form))

        # Add the FloatLayout containing the AnchorLayout and "+" button to the main BoxLayout
        self.add_widget(self.float_layout)

    # Method to show the form popup when the "+" button is pressed
    def show_form(self, instance):
        # Create a Popup with a title and size hint
        form_popup = Popup(title="Add Timer", size_hint=(0.8, 0.8))
        
        # Create a TimerForm instance and pass it the popup instance and a reference to the TimerApp instance
        form = TimerForm(popup_instance=form_popup, timer_app=self)
        
        # Add the form to the popup
        form_popup.add_widget(form)
        
        # Open the popup
        form_popup.open()

    # Method to start a timer and add it to the timer list
    def start_timer(self, form_data):
        # Create a TimerLabel instance with the time from the form_data
        timer = TimerLabel(time=form_data['time'])
        
        # Add the timer to the timer list at the correct index
        self.timer_list.add_widget(timer, index=len(self.timer_list.children))
