from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.togglebutton import ToggleButton
from kivy.clock import Clock
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import requests
import json
from typing import Optional
import websockets
import asyncio

API_BASE_URL = "http://127.0.0.1:8000"
WEBRTC_URL = "ws://127.0.0.1:8001"

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        title = Label(text='CHIDOSKI', size_hint_y=0.2, bold=True, font_size='32sp')
        layout.add_widget(title)
        
        # Login form
        login_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=0.6)
        
        self.username_input = TextInput(hint_text='Username', multiline=False, size_hint_y=0.15)
        self.password_input = TextInput(hint_text='Password', password=True, multiline=False, size_hint_y=0.15)
        
        login_layout.add_widget(Label(text='Login', size_hint_y=0.1, bold=True, font_size='18sp'))
        login_layout.add_widget(self.username_input)
        login_layout.add_widget(self.password_input)
        
        login_btn = Button(text='Login', size_hint_y=0.2)
        login_btn.bind(on_press=self.on_login)
        login_layout.add_widget(login_btn)
        
        layout.add_widget(login_layout)
        
        # Register form
        register_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=0.3)
        
        self.reg_username_input = TextInput(hint_text='Username', multiline=False, size_hint_y=0.15)
        self.reg_email_input = TextInput(hint_text='Email', multiline=False, size_hint_y=0.15)
        self.reg_fullname_input = TextInput(hint_text='Full Name', multiline=False, size_hint_y=0.15)
        self.reg_password_input = TextInput(hint_text='Password', password=True, multiline=False, size_hint_y=0.15)
        
        register_layout.add_widget(Label(text='Or Register', size_hint_y=0.1, bold=True, font_size='18sp'))
        register_layout.add_widget(self.reg_username_input)
        register_layout.add_widget(self.reg_email_input)
        register_layout.add_widget(self.reg_fullname_input)
        register_layout.add_widget(self.reg_password_input)
        
        reg_btn = Button(text='Register', size_hint_y=0.2)
        reg_btn.bind(on_press=self.on_register)
        register_layout.add_widget(reg_btn)
        
        layout.add_widget(register_layout)
        
        self.add_widget(layout)
    
    def on_login(self, instance):
        username = self.username_input.text
        password = self.password_input.text
        
        try:
            response = requests.post(f"{API_BASE_URL}/auth/login", json={
                "username": username,
                "password": password
            })
            
            if response.status_code == 200:
                data = response.json()
                self.app.token = data['access_token']
                self.app.user_id = data['user']['id']
                self.app.user_data = data['user']
                self.manager.current = 'home'
            else:
                self.show_error("Login failed: " + response.text)
        except Exception as e:
            self.show_error(f"Error: {str(e)}")
    
    def on_register(self, instance):
        try:
            response = requests.post(f"{API_BASE_URL}/auth/register", json={
                "username": self.reg_username_input.text,
                "email": self.reg_email_input.text,
                "full_name": self.reg_fullname_input.text,
                "password": self.reg_password_input.text
            })
            
            if response.status_code == 200:
                data = response.json()
                self.app.token = data['access_token']
                self.app.user_id = data['user']['id']
                self.app.user_data = data['user']
                self.manager.current = 'home'
            else:
                self.show_error("Registration failed: " + response.text)
        except Exception as e:
            self.show_error(f"Error: {str(e)}")
    
    def show_error(self, message):
        popup = Popup(title='Error', size_hint=(0.9, 0.3))
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(Label(text=message))
        close_btn = Button(text='Close', size_hint_y=0.3)
        close_btn.bind(on_press=popup.dismiss)
        layout.add_widget(close_btn)
        popup.content = layout
        popup.open()

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        self.refresh_timer = None
    
    def on_enter(self):
        self.refresh_ui()
        self.refresh_timer = Clock.schedule_interval(lambda dt: self.refresh_ui(), 5)
    
    def on_leave(self):
        if self.refresh_timer:
            self.refresh_timer.cancel()
    
    def refresh_ui(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Header
        header = BoxLayout(size_hint_y=0.1, spacing=10)
        header.add_widget(Label(text=f"Welcome, {self.app.user_data['full_name']}", bold=True))
        logout_btn = Button(text='Logout', size_hint_x=0.2)
        logout_btn.bind(on_press=self.on_logout)
        header.add_widget(logout_btn)
        layout.add_widget(header)
        
        # Navigation buttons
        nav_layout = GridLayout(cols=2, size_hint_y=0.15, spacing=10)
        
        chats_btn = Button(text='💬 Chats')
        chats_btn.bind(on_press=self.go_to_chats)
        nav_layout.add_widget(chats_btn)
        
        friends_btn = Button(text='👥 Friends')
        friends_btn.bind(on_press=self.go_to_friends)
        nav_layout.add_widget(friends_btn)
        
        games_btn = Button(text='🎮 Games')
        games_btn.bind(on_press=self.go_to_games)
        nav_layout.add_widget(games_btn)
        
        profile_btn = Button(text='👤 Profile')
        profile_btn.bind(on_press=self.go_to_profile)
        nav_layout.add_widget(profile_btn)
        
        layout.add_widget(nav_layout)
        
        # Content area
        content_layout = BoxLayout(orientation='vertical', size_hint_y=0.75)
        content_layout.add_widget(Label(text='Welcome to CHIDOSKI!\n\nChat • Video Call • Games', halign='center', valign='center'))
        layout.add_widget(content_layout)
        
        self.add_widget(layout)
    
    def on_logout(self, instance):
        self.app.token = None
        self.app.user_id = None
        self.manager.current = 'login'
    
    def go_to_chats(self, instance):
        self.manager.current = 'chats'
    
    def go_to_friends(self, instance):
        self.manager.current = 'friends'
    
    def go_to_games(self, instance):
        self.manager.current = 'games'
    
    def go_to_profile(self, instance):
        self.manager.current = 'profile'

class ChatsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        self.conversations = []
    
    def on_enter(self):
        self.load_conversations()
    
    def load_conversations(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Header
        header = BoxLayout(size_hint_y=0.1, spacing=10)
        header.add_widget(Label(text='Chats', bold=True, font_size='18sp'))
        back_btn = Button(text='← Back', size_hint_x=0.2)
        back_btn.bind(on_press=self.go_back)
        header.add_widget(back_btn)
        layout.add_widget(header)
        
        # New chat button
        new_chat_btn = Button(text='+ New Chat', size_hint_y=0.1)
        new_chat_btn.bind(on_press=self.new_chat)
        layout.add_widget(new_chat_btn)
        
        # Conversations list
        try:
            response = requests.get(f"{API_BASE_URL}/conversations", headers={
                "Authorization": f"Bearer {self.app.token}"
            })
            
            if response.status_code == 200:
                self.conversations = response.json()
                
                scroll = ScrollView(size_hint_y=0.8)
                conv_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
                conv_layout.bind(minimum_height=conv_layout.setter('height'))
                
                for conv in self.conversations:
                    btn = Button(text=conv.get('name', 'Unnamed'), size_hint_y=None, height=50)
                    btn.bind(on_press=lambda x, cid=conv['id']: self.open_chat(cid))
                    conv_layout.add_widget(btn)
                
                scroll.add_widget(conv_layout)
                layout.add_widget(scroll)
        except Exception as e:
            layout.add_widget(Label(text=f"Error loading chats: {str(e)}"))
        
        self.add_widget(layout)
    
    def go_back(self, instance):
        self.manager.current = 'home'
    
    def new_chat(self, instance):
        self.manager.current = 'new_chat'
    
    def open_chat(self, conversation_id):
        self.app.current_conversation_id = conversation_id
        self.manager.current = 'chat_detail'

class ChatDetailScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        self.messages = []
    
    def on_enter(self):
        self.load_messages()
    
    def load_messages(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Header
        header = BoxLayout(size_hint_y=0.1, spacing=10)
        header.add_widget(Label(text='Chat', bold=True, font_size='18sp'))
        video_btn = Button(text='📹 Video Call', size_hint_x=0.3)
        video_btn.bind(on_press=self.start_video_call)
        header.add_widget(video_btn)
        back_btn = Button(text='← Back', size_hint_x=0.2)
        back_btn.bind(on_press=self.go_back)
        header.add_widget(back_btn)
        layout.add_widget(header)
        
        # Messages display
        try:
            response = requests.get(
                f"{API_BASE_URL}/conversations/{self.app.current_conversation_id}/messages",
                headers={"Authorization": f"Bearer {self.app.token}"}
            )
            
            if response.status_code == 200:
                self.messages = response.json()
                
                scroll = ScrollView(size_hint_y=0.7)
                msg_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
                msg_layout.bind(minimum_height=msg_layout.setter('height'))
                
                for msg in self.messages:
                    msg_text = f"{msg['sender_id']}: {msg['content']}"
                    msg_layout.add_widget(Label(text=msg_text, size_hint_y=None, height=50))
                
                scroll.add_widget(msg_layout)
                layout.add_widget(scroll)
        except Exception as e:
            layout.add_widget(Label(text=f"Error loading messages: {str(e)}"))
        
        # Message input
        input_layout = BoxLayout(size_hint_y=0.15, spacing=10)
        self.message_input = TextInput(hint_text='Type a message...', multiline=True)
        input_layout.add_widget(self.message_input)
        
        send_btn = Button(text='Send', size_hint_x=0.2)
        send_btn.bind(on_press=self.send_message)
        input_layout.add_widget(send_btn)
        
        layout.add_widget(input_layout)
        
        self.add_widget(layout)
    
    def send_message(self, instance):
        try:
            message_text = self.message_input.text
            if not message_text:
                return
            
            response = requests.post(
                f"{API_BASE_URL}/conversations/{self.app.current_conversation_id}/messages",
                json={"content": message_text},
                headers={"Authorization": f"Bearer {self.app.token}"}
            )
            
            if response.status_code == 200:
                self.message_input.text = ""
                self.load_messages()
        except Exception as e:
            print(f"Error sending message: {str(e)}")
    
    def start_video_call(self, instance):
        # Start video call logic
        self.manager.current = 'video_call'
    
    def go_back(self, instance):
        self.manager.current = 'chats'

class VideCallScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
    
    def on_enter(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(Label(text='📹 Video Call Screen', bold=True, font_size='18sp'))
        layout.add_widget(Label(text='Video call would be displayed here\n(WebRTC integration)', halign='center', valign='center'))
        
        end_btn = Button(text='End Call', size_hint_y=0.2)
        end_btn.bind(on_press=self.end_call)
        layout.add_widget(end_btn)
        
        self.clear_widgets()
        self.add_widget(layout)
    
    def end_call(self, instance):
        self.manager.current = 'chat_detail'

class FriendsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        self.friends = []
    
    def on_enter(self):
        self.load_friends()
    
    def load_friends(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Header
        header = BoxLayout(size_hint_y=0.1, spacing=10)
        header.add_widget(Label(text='Friends', bold=True, font_size='18sp'))
        back_btn = Button(text='← Back', size_hint_x=0.2)
        back_btn.bind(on_press=self.go_back)
        header.add_widget(back_btn)
        layout.add_widget(header)
        
        # Add friend button
        add_friend_btn = Button(text='+ Add Friend', size_hint_y=0.1)
        add_friend_btn.bind(on_press=self.add_friend_dialog)
        layout.add_widget(add_friend_btn)
        
        # Friends list
        try:
            response = requests.get(f"{API_BASE_URL}/friends", headers={
                "Authorization": f"Bearer {self.app.token}"
            })
            
            if response.status_code == 200:
                self.friends = response.json()
                
                scroll = ScrollView(size_hint_y=0.8)
                friends_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
                friends_layout.bind(minimum_height=friends_layout.setter('height'))
                
                for friend in self.friends:
                    friend_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
                    friend_layout.add_widget(Label(text=friend['friend_id']))
                    
                    chat_btn = Button(text='Chat', size_hint_x=0.3)
                    chat_btn.bind(on_press=lambda x, fid=friend['friend_id']: self.chat_friend(fid))
                    friend_layout.add_widget(chat_btn)
                    
                    friends_layout.add_widget(friend_layout)
                
                scroll.add_widget(friends_layout)
                layout.add_widget(scroll)
        except Exception as e:
            layout.add_widget(Label(text=f"Error loading friends: {str(e)}"))
        
        self.add_widget(layout)
    
    def add_friend_dialog(self, instance):
        popup = Popup(title='Add Friend', size_hint=(0.9, 0.3))
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        friend_id_input = TextInput(hint_text='Friend User ID', multiline=False)
        layout.add_widget(friend_id_input)
        
        add_btn = Button(text='Add', size_hint_y=0.3)
        def add_friend(x):
            try:
                requests.post(
                    f"{API_BASE_URL}/friends/add/{friend_id_input.text}",
                    headers={"Authorization": f"Bearer {self.app.token}"}
                )
                popup.dismiss()
                self.load_friends()
            except Exception as e:
                print(f"Error adding friend: {str(e)}")
        add_btn.bind(on_press=add_friend)
        layout.add_widget(add_btn)
        
        popup.content = layout
        popup.open()
    
    def chat_friend(self, friend_id):
        # Create or open conversation with friend
        self.manager.current = 'chats'
    
    def go_back(self, instance):
        self.manager.current = 'home'

class GamesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
    
    def on_enter(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Header
        header = BoxLayout(size_hint_y=0.1, spacing=10)
        header.add_widget(Label(text='Games', bold=True, font_size='18sp'))
        back_btn = Button(text='← Back', size_hint_x=0.2)
        back_btn.bind(on_press=self.go_back)
        header.add_widget(back_btn)
        layout.add_widget(header)
        
        # Games list
        games_layout = GridLayout(cols=2, size_hint_y=0.8, spacing=10)
        
        chess_btn = Button(text='♟️ Chess')
        chess_btn.bind(on_press=self.play_game)
        games_layout.add_widget(chess_btn)
        
        cards_btn = Button(text='🂡 Cards')
        cards_btn.bind(on_press=self.play_game)
        games_layout.add_widget(cards_btn)
        
        dice_btn = Button(text='🎲 Dice')
        dice_btn.bind(on_press=self.play_game)
        games_layout.add_widget(dice_btn)
        
        layout.add_widget(games_layout)
        
        self.clear_widgets()
        self.add_widget(layout)
    
    def play_game(self, instance):
        self.manager.current = 'game_lobby'
    
    def go_back(self, instance):
        self.manager.current = 'home'

class GameLobbyScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
    
    def on_enter(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(Label(text='🎮 Game Lobby', bold=True, font_size='18sp'))
        layout.add_widget(Label(text='Waiting for opponent...', halign='center', valign='center'))
        
        back_btn = Button(text='← Back', size_hint_y=0.2)
        back_btn.bind(on_press=self.go_back)
        layout.add_widget(back_btn)
        
        self.clear_widgets()
        self.add_widget(layout)
    
    def go_back(self, instance):
        self.manager.current = 'games'

class ProfileScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
    
    def on_enter(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Header
        header = BoxLayout(size_hint_y=0.1, spacing=10)
        header.add_widget(Label(text='Profile', bold=True, font_size='18sp'))
        back_btn = Button(text='← Back', size_hint_x=0.2)
        back_btn.bind(on_press=self.go_back)
        header.add_widget(back_btn)
        layout.add_widget(header)
        
        # Profile info
        profile_layout = GridLayout(cols=2, size_hint_y=0.4, spacing=10)
        profile_layout.add_widget(Label(text='Username:', bold=True))
        profile_layout.add_widget(Label(text=self.app.user_data['username']))
        profile_layout.add_widget(Label(text='Email:', bold=True))
        profile_layout.add_widget(Label(text=self.app.user_data['email']))
        profile_layout.add_widget(Label(text='Full Name:', bold=True))
        profile_layout.add_widget(Label(text=self.app.user_data['full_name']))
        layout.add_widget(profile_layout)
        
        # Bio
        bio_layout = BoxLayout(orientation='vertical', size_hint_y=0.3)
        bio_layout.add_widget(Label(text='Bio:', bold=True))
        self.bio_input = TextInput(text=self.app.user_data.get('bio', ''), multiline=True)
        bio_layout.add_widget(self.bio_input)
        layout.add_widget(bio_layout)
        
        # Save button
        save_btn = Button(text='Save Changes', size_hint_y=0.15)
        save_btn.bind(on_press=self.save_profile)
        layout.add_widget(save_btn)
        
        self.add_widget(layout)
    
    def save_profile(self, instance):
        try:
            requests.put(
                f"{API_BASE_URL}/users/me",
                params={"bio": self.bio_input.text},
                headers={"Authorization": f"Bearer {self.app.token}"}
            )
            print("Profile updated successfully")
        except Exception as e:
            print(f"Error updating profile: {str(e)}")
    
    def go_back(self, instance):
        self.manager.current = 'home'

class CHIDOSKIApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.token = None
        self.user_id = None
        self.user_data = None
        self.current_conversation_id = None
    
    def build(self):
        self.title = 'CHIDOSKI'
        
        sm = ScreenManager()
        
        login_screen = LoginScreen(name='login')
        login_screen.app = self
        sm.add_widget(login_screen)
        
        home_screen = HomeScreen(name='home')
        home_screen.app = self
        sm.add_widget(home_screen)
        
        chats_screen = ChatsScreen(name='chats')
        chats_screen.app = self
        sm.add_widget(chats_screen)
        
        chat_detail_screen = ChatDetailScreen(name='chat_detail')
        chat_detail_screen.app = self
        sm.add_widget(chat_detail_screen)
        
        video_call_screen = VideCallScreen(name='video_call')
        video_call_screen.app = self
        sm.add_widget(video_call_screen)
        
        friends_screen = FriendsScreen(name='friends')
        friends_screen.app = self
        sm.add_widget(friends_screen)
        
        games_screen = GamesScreen(name='games')
        games_screen.app = self
        sm.add_widget(games_screen)
        
        game_lobby_screen = GameLobbyScreen(name='game_lobby')
        game_lobby_screen.app = self
        sm.add_widget(game_lobby_screen)
        
        profile_screen = ProfileScreen(name='profile')
        profile_screen.app = self
        sm.add_widget(profile_screen)
        
        new_chat_screen = Screen(name='new_chat')
        sm.add_widget(new_chat_screen)
        
        return sm

if __name__ == '__main__':
    CHIDOSKIApp().run()
