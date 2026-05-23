from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.image import Image
from kivy.clock import Clock
from datetime import datetime
import pytz
from timezone_manager import TimeZoneManager

class DigitalClockApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.timezone_manager = TimeZoneManager()
        self.update_timer = None
        self.time_format = '24h'  # 24h or 12h
    
    def build(self):
        self.title = '🌍 Digital Clock - Multi Timezone'
        
        sm = ScreenManager()
        
        # Clock screen (main)
        clock_screen = ClockScreen(name='clock')
        clock_screen.app = self
        sm.add_widget(clock_screen)
        
        # Timezone manager screen
        tz_screen = TimezoneManagerScreen(name='timezone_manager')
        tz_screen.app = self
        sm.add_widget(tz_screen)
        
        # Timezone details screen
        tz_detail_screen = TimezoneDetailScreen(name='timezone_detail')
        tz_detail_screen.app = self
        sm.add_widget(tz_detail_screen)
        
        # Settings screen
        settings_screen = SettingsScreen(name='settings')
        settings_screen.app = self
        sm.add_widget(settings_screen)
        
        return sm

class ClockScreen(Screen):
    """Main clock display screen."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        self.update_timer = None
        self.clock_labels = {}
    
    def on_enter(self):
        self.update_clocks()
        self.update_timer = Clock.schedule_interval(lambda dt: self.update_clocks(), 0.5)
    
    def on_leave(self):
        if self.update_timer:
            self.update_timer.cancel()
    
    def update_clocks(self):
        """Update all timezone clocks."""
        self.clear_widgets()
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Header
        header_layout = BoxLayout(size_hint_y=0.1, spacing=10)
        header_layout.add_widget(Label(text='🌍 Multi Timezone Clock', bold=True, font_size='20sp'))
        
        settings_btn = Button(text='⚙️ Settings', size_hint_x=0.2)
        settings_btn.bind(on_press=self.go_to_settings)
        header_layout.add_widget(settings_btn)
        
        manage_btn = Button(text='➕ Manage', size_hint_x=0.2)
        manage_btn.bind(on_press=self.go_to_manager)
        header_layout.add_widget(manage_btn)
        
        layout.add_widget(header_layout)
        
        # Clocks display
        scroll = ScrollView(size_hint_y=0.8)
        clocks_layout = GridLayout(cols=1, spacing=15, size_hint_y=None, padding=(10, 10))
        clocks_layout.bind(minimum_height=clocks_layout.setter('height'))
        
        for timezone in self.app.timezone_manager.selected_timezones:
            clock_widget = self.create_clock_widget(timezone)
            clocks_layout.add_widget(clock_widget)
        
        scroll.add_widget(clocks_layout)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
    
    def create_clock_widget(self, timezone: str) -> BoxLayout:
        """Create a clock widget for a timezone."""
        widget_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=80, spacing=5, padding=(10, 10))
        
        # Background color based on timezone
        from kivy.graphics import Color, Rectangle
        colors = {
            'UTC': (0.2, 0.6, 1, 0.3),
            'America/New_York': (1, 0.3, 0.3, 0.3),
            'Europe/London': (0.3, 1, 0.3, 0.3),
            'Asia/Tokyo': (1, 1, 0.3, 0.3),
            'Australia/Sydney': (0.3, 1, 1, 0.3),
        }
        
        default_color = (0.7, 0.7, 0.7, 0.2)
        color = colors.get(timezone, default_color)
        
        with widget_layout.canvas.before:
            Color(*color)
            Rectangle(size=widget_layout.size, pos=widget_layout.pos)
        
        # Timezone name and abbreviation
        now = self.app.timezone_manager.get_current_time(timezone)
        if now:
            tz_abbr = now.strftime('%Z')
            tz_offset = now.strftime('%z')
            offset_str = f"{tz_offset[:3]}:{tz_offset[3:]}"
            
            header_text = f"{timezone.replace('_', ' ')}  [{tz_abbr}]  UTC{offset_str}"
            widget_layout.add_widget(Label(text=header_text, size_hint_y=0.4, bold=True, font_size='12sp'))
            
            # Time display
            if self.app.time_format == '12h':
                time_str, am_pm = self.app.timezone_manager.format_time_12h(now)
                time_text = f"{time_str} {am_pm}"
            else:
                time_text = self.app.timezone_manager.format_time(now, '%H:%M:%S')
            
            time_label = Label(text=time_text, size_hint_y=0.4, bold=True, font_size='32sp')
            widget_layout.add_widget(time_label)
            
            # Date
            date_text = now.strftime('%A, %B %d, %Y')
            widget_layout.add_widget(Label(text=date_text, size_hint_y=0.2, font_size='10sp'))
            
            # Click to see details
            detail_btn = Button(text='View Details', size_hint_y=0.2, size_hint_x=1)
            detail_btn.bind(on_press=lambda x, tz=timezone: self.go_to_timezone_detail(tz))
            widget_layout.add_widget(detail_btn)
        
        return widget_layout
    
    def go_to_manager(self, instance):
        """Go to timezone manager screen."""
        self.manager.current = 'timezone_manager'
    
    def go_to_settings(self, instance):
        """Go to settings screen."""
        self.manager.current = 'settings'
    
    def go_to_timezone_detail(self, timezone: str):
        """Go to timezone detail screen."""
        detail_screen = self.manager.get_screen('timezone_detail')
        detail_screen.timezone = timezone
        self.manager.current = 'timezone_detail'

class TimezoneManagerScreen(Screen):
    """Screen to manage timezones."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        self.selected_region = 'Americas'
    
    def on_enter(self):
        self.display_ui()
    
    def display_ui(self):
        """Display timezone manager UI."""
        self.clear_widgets()
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Header
        header_layout = BoxLayout(size_hint_y=0.1, spacing=10)
        header_layout.add_widget(Label(text='➕ Add Timezones', bold=True, font_size='18sp'))
        back_btn = Button(text='← Back', size_hint_x=0.2)
        back_btn.bind(on_press=self.go_back)
        header_layout.add_widget(back_btn)
        layout.add_widget(header_layout)
        
        # Region selection
        region_layout = BoxLayout(size_hint_y=0.1, spacing=5)
        region_layout.add_widget(Label(text='Region:', size_hint_x=0.2))
        
        preset_tz = self.app.timezone_manager.get_preset_timezones()
        region_spinner = Spinner(
            text=self.selected_region,
            values=tuple(preset_tz.keys()),
            size_hint_x=0.8
        )
        region_spinner.bind(text=self.on_region_selected)
        region_layout.add_widget(region_spinner)
        layout.add_widget(region_layout)
        
        # Timezones list
        scroll = ScrollView(size_hint_y=0.7)
        tz_layout = GridLayout(cols=1, spacing=8, size_hint_y=None, padding=(5, 5))
        tz_layout.bind(minimum_height=tz_layout.setter('height'))
        
        preset_tz = self.app.timezone_manager.get_preset_timezones()
        for tz in preset_tz[self.selected_region]:
            tz_widget = self.create_timezone_item(tz)
            tz_layout.add_widget(tz_widget)
        
        scroll.add_widget(tz_layout)
        layout.add_widget(scroll)
        
        # Custom timezone input
        custom_layout = BoxLayout(size_hint_y=0.12, spacing=10)
        self.custom_tz_input = TextInput(hint_text='Custom timezone (e.g., Asia/Bangkok)', multiline=False)
        custom_layout.add_widget(self.custom_tz_input)
        
        add_custom_btn = Button(text='Add Custom', size_hint_x=0.3)
        add_custom_btn.bind(on_press=self.add_custom_timezone)
        custom_layout.add_widget(add_custom_btn)
        
        layout.add_widget(custom_layout)
        
        self.add_widget(layout)
    
    def create_timezone_item(self, timezone: str) -> BoxLayout:
        """Create a timezone item widget."""
        item_layout = BoxLayout(size_hint_y=None, height=50, spacing=10, padding=(5, 5))
        
        # Timezone info
        tz_info = self.app.timezone_manager.get_timezone_info(timezone)
        if tz_info:
            info_text = f"{timezone}  [{tz_info['timezone_name']}]"
            item_layout.add_widget(Label(text=info_text, size_hint_x=0.7))
            
            # Add/Remove button
            is_selected = timezone in self.app.timezone_manager.selected_timezones
            btn_text = '✓ Remove' if is_selected else '+ Add'
            btn_color = (0.2, 1, 0.2, 1) if is_selected else (0.5, 0.5, 1, 1)
            
            btn = Button(text=btn_text, size_hint_x=0.3)
            btn.background_color = btn_color
            btn.bind(on_press=lambda x, tz=timezone: self.toggle_timezone(tz))
            item_layout.add_widget(btn)
        
        return item_layout
    
    def on_region_selected(self, spinner, text):
        """Handle region selection."""
        self.selected_region = text
        self.display_ui()
    
    def toggle_timezone(self, timezone: str):
        """Add or remove a timezone."""
        if timezone in self.app.timezone_manager.selected_timezones:
            self.app.timezone_manager.remove_timezone(timezone)
        else:
            self.app.timezone_manager.add_timezone(timezone)
        self.display_ui()
    
    def add_custom_timezone(self, instance):
        """Add custom timezone."""
        tz = self.custom_tz_input.text.strip()
        if tz:
            if self.app.timezone_manager.add_timezone(tz):
                self.custom_tz_input.text = ''
                self.display_ui()
            else:
                self.show_error(f"Invalid timezone: {tz}")
    
    def show_error(self, message):
        """Show error popup."""
        popup = Popup(title='Error', size_hint=(0.8, 0.3))
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(Label(text=message))
        close_btn = Button(text='OK', size_hint_y=0.3)
        close_btn.bind(on_press=popup.dismiss)
        layout.add_widget(close_btn)
        popup.content = layout
        popup.open()
    
    def go_back(self, instance):
        """Go back to clock screen."""
        self.manager.current = 'clock'

class TimezoneDetailScreen(Screen):
    """Screen showing detailed timezone information."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        self.timezone = None
        self.update_timer = None
    
    def on_enter(self):
        self.update_display()
        self.update_timer = Clock.schedule_interval(lambda dt: self.update_display(), 1)
    
    def on_leave(self):
        if self.update_timer:
            self.update_timer.cancel()
    
    def update_display(self):
        """Update timezone detail display."""
        self.clear_widgets()
        
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        # Header
        header_layout = BoxLayout(size_hint_y=0.1, spacing=10)
        header_layout.add_widget(Label(text=f'📍 {self.timezone}', bold=True, font_size='18sp'))
        back_btn = Button(text='← Back', size_hint_x=0.2)
        back_btn.bind(on_press=self.go_back)
        header_layout.add_widget(back_btn)
        layout.add_widget(header_layout)
        
        # Timezone info
        tz_info = self.app.timezone_manager.get_timezone_info(self.timezone)
        if tz_info:
            info_layout = GridLayout(cols=2, size_hint_y=0.4, spacing=10, padding=10)
            
            # Time
            dt = tz_info['time']
            if self.app.time_format == '12h':
                time_str, am_pm = self.app.timezone_manager.format_time_12h(dt)
                time_display = f"{time_str} {am_pm}"
            else:
                time_display = self.app.timezone_manager.format_time(dt, '%H:%M:%S')
            
            info_layout.add_widget(Label(text='Current Time:', bold=True, size_hint_y=None, height=40))
            info_layout.add_widget(Label(text=time_display, font_size='18sp', size_hint_y=None, height=40))
            
            # Date
            date_display = dt.strftime('%A, %B %d, %Y')
            info_layout.add_widget(Label(text='Date:', bold=True, size_hint_y=None, height=40))
            info_layout.add_widget(Label(text=date_display, size_hint_y=None, height=40))
            
            # Timezone abbreviation
            info_layout.add_widget(Label(text='Timezone:', bold=True, size_hint_y=None, height=40))
            info_layout.add_widget(Label(text=tz_info['timezone_name'], size_hint_y=None, height=40))
            
            # UTC Offset
            offset_str = tz_info['utc_offset']
            offset_formatted = f"UTC{offset_str[:3]}:{offset_str[3:]}"
            info_layout.add_widget(Label(text='UTC Offset:', bold=True, size_hint_y=None, height=40))
            info_layout.add_widget(Label(text=offset_formatted, size_hint_y=None, height=40))
            
            # DST Status
            dst_status = 'Yes (DST Active)' if tz_info['is_dst'] else 'No Standard Time'
            info_layout.add_widget(Label(text='Daylight Saving:', bold=True, size_hint_y=None, height=40))
            info_layout.add_widget(Label(text=dst_status, size_hint_y=None, height=40))
            
            layout.add_widget(info_layout)
        
        # Time comparison
        comparison_layout = BoxLayout(orientation='vertical', size_hint_y=0.3, padding=10, spacing=10)
        comparison_layout.add_widget(Label(text='⏱️ Time Difference from UTC:', bold=True, size_hint_y=0.2))
        
        diff = self.app.timezone_manager.get_time_difference('UTC', self.timezone)
        if diff is not None:
            if diff > 0:
                diff_text = f"+{diff} hours ahead of UTC"
            elif diff < 0:
                diff_text = f"{diff} hours behind UTC"
            else:
                diff_text = "Same as UTC"
            
            comparison_layout.add_widget(Label(text=diff_text, font_size='16sp', size_hint_y=0.8))
        
        layout.add_widget(comparison_layout)
        
        # Remove button
        remove_btn = Button(text='✗ Remove this Timezone', size_hint_y=0.1)
        remove_btn.bind(on_press=self.remove_timezone)
        layout.add_widget(remove_btn)
        
        self.add_widget(layout)
    
    def remove_timezone(self, instance):
        """Remove timezone."""
        popup = Popup(title='Remove Timezone?', size_hint=(0.8, 0.3))
        p_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        p_layout.add_widget(Label(text=f'Remove {self.timezone}?'))
        
        btn_layout = BoxLayout(size_hint_y=0.3, spacing=10)
        
        def confirm_remove(x):
            self.app.timezone_manager.remove_timezone(self.timezone)
            popup.dismiss()
            self.go_back(None)
        
        yes_btn = Button(text='Yes, Remove')
        yes_btn.bind(on_press=confirm_remove)
        btn_layout.add_widget(yes_btn)
        
        no_btn = Button(text='Cancel')
        no_btn.bind(on_press=popup.dismiss)
        btn_layout.add_widget(no_btn)
        
        p_layout.add_widget(btn_layout)
        popup.content = p_layout
        popup.open()
    
    def go_back(self, instance):
        """Go back to clock screen."""
        self.manager.current = 'clock'

class SettingsScreen(Screen):
    """Settings screen."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
    
    def on_enter(self):
        self.display_settings()
    
    def display_settings(self):
        """Display settings."""
        self.clear_widgets()
        
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        # Header
        header_layout = BoxLayout(size_hint_y=0.1, spacing=10)
        header_layout.add_widget(Label(text='⚙️ Settings', bold=True, font_size='18sp'))
        back_btn = Button(text='← Back', size_hint_x=0.2)
        back_btn.bind(on_press=self.go_back)
        header_layout.add_widget(back_btn)
        layout.add_widget(header_layout)
        
        # Time format selection
        settings_layout = GridLayout(cols=1, size_hint_y=0.6, spacing=15, padding=10)
        
        # Time format
        layout.add_widget(Label(text='Time Format:', size_hint_y=0.1, bold=True))
        
        format_layout = BoxLayout(size_hint_y=0.15, spacing=10)
        
        format_24h_btn = ToggleButton(
            text='24-Hour',
            group='time_format',
            state='down' if self.app.time_format == '24h' else 'normal'
        )
        format_24h_btn.bind(on_press=lambda x: self.set_time_format('24h'))
        format_layout.add_widget(format_24h_btn)
        
        format_12h_btn = ToggleButton(
            text='12-Hour (AM/PM)',
            group='time_format',
            state='down' if self.app.time_format == '12h' else 'normal'
        )
        format_12h_btn.bind(on_press=lambda x: self.set_time_format('12h'))
        format_layout.add_widget(format_12h_btn)
        
        layout.add_widget(format_layout)
        
        # About section
        layout.add_widget(Label(text='About:', size_hint_y=0.1, bold=True))
        
        about_layout = BoxLayout(orientation='vertical', size_hint_y=0.3, padding=10)
        about_layout.add_widget(Label(text='Digital Clock - Multi Timezone', halign='center'))
        about_layout.add_widget(Label(text='Version 1.0.0', halign='center', font_size='10sp'))
        about_layout.add_widget(Label(text='Built with Kivy & Python', halign='center', font_size='10sp'))
        about_layout.add_widget(Label(text='\u00a9 2026 - All Rights Reserved', halign='center', font_size='9sp'))
        
        layout.add_widget(about_layout)
        
        self.add_widget(layout)
    
    def set_time_format(self, format_type):
        """Set time format."""
        self.app.time_format = format_type
    
    def go_back(self, instance):
        """Go back to clock screen."""
        self.manager.current = 'clock'

if __name__ == '__main__':
    DigitalClockApp().run()
