# chatbot_screen.py - Chatbot screen implementation for the frontend

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.properties import StringProperty, ListProperty, BooleanProperty, ObjectProperty, NumericProperty
from kivy.lang import Builder

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.app import App
from kivy.animation import Animation
from functools import partial
import threading
import json

# Kivy will automatically load the new <SuggestionButton> rule from the .kv file.
# We just need a placeholder class here for Kivy to recognize it.
class SuggestionButton(Button):
    pass

class ChatMessage(BoxLayout):
    """Individual chat message widget"""
    message_text = StringProperty('')
    is_user = BooleanProperty(True)

    def __init__(self, message_text='', is_user=True, **kwargs):
        super().__init__(**kwargs)
        self.message_text = message_text
        self.is_user = is_user
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.padding = dp(5)
        self.spacing = dp(5)
        self.height = self.minimum_height # Set initial height

        # Create message bubble
        self.create_message_bubble()

    def create_message_bubble(self):
        """Create the message bubble based on sender"""
        if self.is_user:
            self.add_widget(BoxLayout(size_hint_x=0.3))

        msg_container = BoxLayout(
            orientation='vertical',
            size_hint_x=0.7,
            size_hint_y=None
        )
        msg_container.bind(minimum_height=msg_container.setter('height'))


        msg_label = Label(
            text=self.message_text,
            size_hint_y=None,
            text_size=(dp(230), None), # Reduced width to account for padding
            halign='left',
            valign='top',
            markup=True,
            color=(0.1, 0.1, 0.1, 1),
            padding=(dp(10), dp(10))
        )
        msg_label.bind(texture_size=msg_label.setter('size'))

        msg_box = BoxLayout(
            size_hint_y=None,
            padding=(0, 0)
        )
        msg_label.bind(height=lambda instance, value: setattr(msg_box, 'height', value))


        with msg_box.canvas.before:
            from kivy.graphics import Color, RoundedRectangle

            if self.is_user:
                Color(0.86, 0.97, 0.78, 1)  # WhatsApp user green
            else:
                Color(1, 1, 1, 1)  # White for bot

            self.bg_rect = RoundedRectangle(
                pos=msg_box.pos,
                size=msg_box.size,
                radius=[dp(12)]
            )
            msg_box.bind(pos=self.update_bg, size=self.update_bg)

        msg_box.add_widget(msg_label)
        msg_container.add_widget(msg_box)

        timestamp = Label(
            text='Just now',
            size_hint_y=None,
            height=dp(15),
            font_size=dp(9),
            color=(0.5, 0.5, 0.5, 1),
            halign='right' if self.is_user else 'left'
        )
        msg_container.add_widget(timestamp)

        self.add_widget(msg_container)

        if not self.is_user:
            self.add_widget(BoxLayout(size_hint_x=0.3))

        msg_container.bind(height=self.setter('height'))

    def update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

class ChatbotScreen(Screen):
    """Chatbot screen for AI-powered bill assistance"""
    session_id = StringProperty('')
    current_ai = StringProperty('gemini')
    messages = ListProperty([])

    def on_enter(self):
        self.ids.chat_container.clear_widgets()
        self.setup_chat()
        self.load_preferences()
        self.show_welcome_message()
        self.load_suggestions()

    def setup_chat(self):
        app = App.get_running_app()

        def create_session():
            try:
                response = app.api.create_chat_session(self.current_ai)
                if response and response.status_code == 201:
                    data = response.json()
                    Clock.schedule_once(lambda dt: self.on_session_created(data), 0)
                else:
                    Clock.schedule_once(lambda dt: self.show_error("Failed to start chat"), 0)
            except Exception as e:
                Clock.schedule_once(lambda dt, err=str(e): self.show_error(err), 0)

        threading.Thread(target=create_session).start()

    def on_session_created(self, data):
        self.session_id = data.get('session_id', '')
        self.current_ai = data.get('ai_provider', 'gemini')
        self.ids.ai_provider_label.text = f"AI: {self.current_ai.title()}"

    def load_preferences(self):
        app = App.get_running_app()

        def get_preferences():
            try:
                response = app.api.get_chat_preferences()
                if response and response.status_code == 200:
                    data = response.json()
                    Clock.schedule_once(lambda dt: self.on_preferences_loaded(data), 0)
            except Exception as e:
                print(f"Failed to load preferences: {e}")

        threading.Thread(target=get_preferences).start()

    def on_preferences_loaded(self, data):
        self.current_ai = data.get('preferred_ai', 'gemini')

        if self.current_ai == 'gemini' and not data.get('has_gemini_key'):
            self.show_api_key_prompt('Gemini')
        elif self.current_ai == 'openai' and not data.get('has_openai_key'):
            self.show_api_key_prompt('OpenAI')

    def show_welcome_message(self):
        def add_welcome_delayed(dt):
            welcome_msg = ChatMessage(
                message_text="Hello! I'm your AI assistant for managing bills and reminders. I can help you:\n\n" +
                             "• Check your upcoming bills\n" +
                             "• Add new reminders\n" +
                             "• Track loan payments\n" +
                             "• Analyze spending patterns\n\n" +
                             "How can I assist you today?",
                is_user=False
            )
            self.ids.chat_container.add_widget(welcome_msg)

            def fix_scroll(dt2):
                self.ids.chat_scroll.scroll_y = 0

            Clock.schedule_once(fix_scroll, 0.1)

        Clock.schedule_once(add_welcome_delayed, 0.2)

    def load_suggestions(self):
        app = App.get_running_app()

        def get_suggestions():
            try:
                response = app.api.get_chat_suggestions()
                if response and response.status_code == 200:
                    suggestions = response.json().get('suggestions', [])
                    Clock.schedule_once(lambda dt: self.on_suggestions_loaded(suggestions), 0)
            except Exception as e:
                print(f"Failed to load suggestions: {e}")

        threading.Thread(target=get_suggestions).start()

    # *** MODIFIED METHOD ***
    def on_suggestions_loaded(self, suggestions):
        self.ids.suggestions_box.clear_widgets()
        for suggestion in suggestions:
            # Create an instance of our new custom button.
            # All styling is now handled by the <SuggestionButton> rule in the .kv file.
            btn = SuggestionButton(text=suggestion)
            btn.bind(on_release=partial(self.send_suggestion, suggestion))
            self.ids.suggestions_box.add_widget(btn)

    def send_suggestion(self, suggestion_text, *args):
        self.ids.message_input.text = suggestion_text
        self.send_message()

    def send_message(self):
        message_text = self.ids.message_input.text.strip()

        if not message_text:
            return

        if not self.session_id:
            self.show_error("Chat session not initialized")
            return

        self.ids.message_input.text = ''

        user_msg = ChatMessage(message_text=message_text, is_user=True)
        self.ids.chat_container.add_widget(user_msg)
        self.ids.chat_scroll.scroll_y = 0

        self.show_typing_indicator()

        app = App.get_running_app()
        app.api.send_chat_message(self.session_id, message_text, self.on_response_received)

    def on_response_received(self, response, error=None):
        self.hide_typing_indicator()

        if error:
            self.show_error(f"Failed to get response: {error}")
            return

        if response and response.status_code == 200:
            try:
                data = response.json()
                response_text = data.get('response', 'Sorry, I couldn\'t process that.')
                bot_msg = ChatMessage(message_text=response_text, is_user=False)
                self.ids.chat_container.add_widget(bot_msg)

                def fix_scroll(dt):
                    self.ids.chat_scroll.scroll_y = 0

                Clock.schedule_once(fix_scroll, 0.1)

                if data.get('function_executed'):
                    self.load_suggestions()
            except json.JSONDecodeError:
                self.show_error("Failed to parse server response.")
        else:
            try:
                error_data = response.json()
                error_message = error_data.get('message', 'Failed to get a valid response from the server.')
                self.show_error(error_message)
            except (json.JSONDecodeError, AttributeError):
                self.show_error("An unknown error occurred.")

    def show_typing_indicator(self):
        if not hasattr(self, 'typing_indicator'):
            self.typing_indicator = ChatMessage(
                message_text="AI is typing...",
                is_user=False
            )
            self.ids.chat_container.add_widget(self.typing_indicator)

    def hide_typing_indicator(self):
        if hasattr(self, 'typing_indicator') and self.typing_indicator in self.ids.chat_container.children:
            self.ids.chat_container.remove_widget(self.typing_indicator)
            del self.typing_indicator

    def switch_ai_provider(self):
        content = BoxLayout(orientation='vertical', spacing=dp(20), padding=dp(20))

        content.add_widget(Label(
            text='Select AI Provider:',
            size_hint_y=None,
            height=dp(30)
        ))

        gemini_btn = Button(
            text='Google Gemini',
            size_hint_y=None,
            height=dp(50),
            background_color=(0.26, 0.38, 0.89, 1) if self.current_ai == 'gemini' else (0.3, 0.3, 0.3, 1)
        )
        gemini_btn.bind(on_release=lambda x: self.select_ai('gemini', popup))
        content.add_widget(gemini_btn)

        openai_btn = Button(
            text='OpenAI GPT-4',
            size_hint_y=None,
            height=dp(50),
            background_color=(0.26, 0.38, 0.89, 1) if self.current_ai == 'openai' else (0.3, 0.3, 0.3, 1)
        )
        openai_btn.bind(on_release=lambda x: self.select_ai('openai', popup))
        content.add_widget(openai_btn)

        popup = Popup(
            title='Choose AI Assistant',
            content=content,
            size_hint=(0.8, 0.4)
        )
        popup.open()

    def select_ai(self, provider, popup):
        popup.dismiss()
        self.current_ai = provider

        app = App.get_running_app()
        app.api.update_chat_preferences({'preferred_ai': provider}, lambda r, e=None: None)

        self.ids.ai_provider_label.text = f"AI: {provider.title()}"

        self.setup_chat()

    def show_api_key_prompt(self, provider):
        content = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(15))

        content.add_widget(Label(
            text=f'Please enter your {provider} API key:',
            size_hint_y=None,
            height=dp(30)
        ))

        api_input = TextInput(
            multiline=False,
            password=True,
            size_hint_y=None,
            height=dp(40)
        )
        content.add_widget(api_input)

        btn_box = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))

        save_btn = Button(text='Save')
        cancel_btn = Button(text='Cancel')

        btn_box.add_widget(cancel_btn)
        btn_box.add_widget(save_btn)
        content.add_widget(btn_box)

        popup = Popup(
            title=f'{provider} API Key Required',
            content=content,
            size_hint=(0.9, 0.4)
        )

        save_btn.bind(on_release=lambda x: self.save_api_key(provider, api_input.text, popup))
        cancel_btn.bind(on_release=popup.dismiss)

        popup.open()

    def save_api_key(self, provider, api_key, popup):
        popup.dismiss()

        if not api_key:
            self.show_error("API key cannot be empty")
            return

        app = App.get_running_app()

        key_field = 'gemini_api_key' if provider == 'Gemini' else 'openai_api_key'
        app.api.update_chat_preferences({key_field: api_key}, lambda r, e=None: None)

        self.setup_chat()

    def clear_chat(self):
        self.ids.chat_container.clear_widgets()
        self.setup_chat()
        self.show_welcome_message()
        self.load_suggestions()

    def show_error(self, message):
        popup = Popup(
            title='Error',
            content=Label(text=message),
            size_hint=(0.8, 0.3)
        )
        popup.open()
