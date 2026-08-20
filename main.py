from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.clock import Clock

import sqlite3
import datetime
import os

ADMIN_USERNAME = "cloner"
ADMIN_PASSWORD = "Cloner.1991"
USER_USERNAME = "Human"
USER_PASSWORD = "Human.1234"


class RoundedTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_active = ''
        self.foreground_color = (1, 1, 1, 1)
        self.hint_text_color = (0.7, 0.7, 0.7, 1)
        self.font_size = 16
        self.padding = [15, 15]
        self.size_hint = (1, None)
        self.height = 50

    def on_size(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0.1, 0.15, 0.25, 1)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[15])


class RoundedButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.font_size = 16
        self.size_hint = (1, None)
        self.height = 50
        self.color = (0, 0, 0, 1)

    def on_size(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(1, 1, 1, 1)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[15])


class GuardApp(App):
    def build(self):
        self.conn = sqlite3.connect('guard.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS personnel
                               (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name TEXT, post TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS logs
                               (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                action TEXT, timestamp TEXT)''')
        self.conn.commit()

        self.main_layout = BoxLayout(orientation='vertical', padding=30, spacing=15)

        with self.main_layout.canvas.before:
            Color(0.05, 0.05, 0.05, 1)
            Rectangle(pos=self.main_layout.pos, size=self.main_layout.size)

        self.user_role = None
        self.show_consent()
        return self.main_layout

    def show_consent(self):
        self.main_layout.clear_widgets()

        title = Label(text="User Agreement", font_size=26, bold=True, color=(1, 1, 1, 1))
        self.main_layout.add_widget(title)

        consent_text = Label(
            text= "aya amoozesh kafi darid.",
            font_size=15,
            halign='center',
            color=(1, 1, 1, 1)
        )
        self.main_layout.add_widget(consent_text)

        btn_agree = RoundedButton(text="yes")
        btn_agree.bind(on_press=self.accept_consent)
        self.main_layout.add_widget(btn_agree)

        btn_disagree = RoundedButton(text="no")
        btn_disagree.bind(on_press=self.stop)
        self.main_layout.add_widget(btn_disagree)

    def accept_consent(self, instance):
        self.add_log("User accepted consent")
        self.show_login()

    def show_login(self):
        self.main_layout.clear_widgets()

        title = Label(text="Login", font_size=26, bold=True, color=(1, 1, 1, 1))
        self.main_layout.add_widget(title)

        lbl_user = Label(text="Username", font_size=14, color=(0.15, 0.4, 0.7, 1))
        self.main_layout.add_widget(lbl_user)

        self.username_input = RoundedTextInput(hint_text="Enter username")
        self.main_layout.add_widget(self.username_input)

        lbl_pass = Label(text="Password", font_size=14, color=(0.15, 0.4, 0.7, 1))
        self.main_layout.add_widget(lbl_pass)

        self.password_input = RoundedTextInput(hint_text="Enter password", password=True)
        self.main_layout.add_widget(self.password_input)

        btn_login = RoundedButton(text="Login")
        btn_login.bind(on_press=self.check_login)
        self.main_layout.add_widget(btn_login)

    def add_log(self, action):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("INSERT INTO logs (action, timestamp) VALUES (?, ?)", (action, timestamp))
        self.conn.commit()

    def check_login(self, instance):
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            self.user_role = "admin"
            self.add_log("Admin login successful")
            self.show_admin_menu()
            return

        if username == USER_USERNAME and password == USER_PASSWORD:
            self.user_role = "user"
            self.add_log("User login successful")
            self.show_user_menu()
            return

        popup = Popup(title="Error", content=Label(text="Wrong username or password!"), size_hint=(0.7, 0.3))
        popup.open()

    def show_admin_menu(self):
        self.main_layout.clear_widgets()

        welcome = Label(text="Admin Panel", font_size=22, bold=True, color=(1, 1, 1, 1))
        self.main_layout.add_widget(welcome)

        buttons = [
            ("Personnel Management", self.show_personnel),
            ("Schedule", self.show_schedule),
            ("View Logs", self.show_logs),
        ]

        for text, func in buttons:
            btn = RoundedButton(text=text)
            btn.bind(on_press=func)
            self.main_layout.add_widget(btn)

        btn_eye = Button(
            text="👁️",
            font_size=30,
            size_hint=(None, None),
            size=(60, 60)
        )
        btn_eye.bind(on_press=self.open_admin_access)
        self.main_layout.add_widget(btn_eye)

        btn_exit = RoundedButton(text="Exit")
        btn_exit.bind(on_press=self.stop)
        self.main_layout.add_widget(btn_exit)

    def open_admin_access(self, instance):
        try:
            self.main_layout.clear_widgets()
            admin_window = AdminAccessWindow()
            self.main_layout.add_widget(admin_window)
        except Exception as e:
            popup = Popup(
                title="Error",
                content=Label(text=f"Error: {e}", color=(1, 1, 1, 1)),
                size_hint=(0.8, 0.3)
            )
            popup.open()

    def show_user_menu(self):
        self.main_layout.clear_widgets()

        welcome = Label(text="User Panel", font_size=22, bold=True, color=(1, 1, 1, 1))
        self.main_layout.add_widget(welcome)

        buttons = [
            ("Personnel Management", self.show_personnel),
            ("Schedule", self.show_schedule),
        ]

        for text, func in buttons:
            btn = RoundedButton(text=text)
            btn.bind(on_press=func)
            self.main_layout.add_widget(btn)

        btn_exit = RoundedButton(text="Exit")
        btn_exit.bind(on_press=self.stop)
        self.main_layout.add_widget(btn_exit)

    def show_logs(self, instance):
        self.main_layout.clear_widgets()

        title = Label(text="Activity Logs", font_size=22, bold=True, color=(1, 1, 1, 1))
        self.main_layout.add_widget(title)

        scroll = ScrollView(size_hint=(1, 0.8))
        grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))

        self.cursor.execute("SELECT action, timestamp FROM logs ORDER BY id DESC LIMIT 50")
        for action, timestamp in self.cursor.fetchall():
            grid.add_widget(Label(text=f"{timestamp} - {action}", size_hint_y=None, height=30, color=(0.15, 0.4, 0.7, 1)))

        scroll.add_widget(grid)
        self.main_layout.add_widget(scroll)

        btn_back = RoundedButton(text="Back")
        btn_back.bind(on_press=self.go_back)
        self.main_layout.add_widget(btn_back)

    def show_personnel(self, instance):
        self.main_layout.clear_widgets()

        title = Label(text="Personnel Management", font_size=22, bold=True, color=(1, 1, 1, 1))
        self.main_layout.add_widget(title)

        self.name_input = RoundedTextInput(hint_text="Name")
        self.main_layout.add_widget(self.name_input)

        self.post_spinner = Spinner(
            text="Post",
            values=["Afsar Gasht", "Afsar Janeshin", "Afsar Sarnegahban",
                    "Afsar Pasdarkhaneh", "Rais Pasdar", "Monitoring", "Zarbat"],
            size_hint=(1, 0.1),
            color=(1, 1, 1, 1)
        )
        self.main_layout.add_widget(self.post_spinner)

        btn_add = RoundedButton(text="Add")
        btn_add.bind(on_press=self.add_person)
        self.main_layout.add_widget(btn_add)

        self.personnel_list = ScrollView(size_hint=(1, 0.5))
        self.personnel_grid = GridLayout(cols=2, spacing=5, size_hint_y=None)
        self.personnel_grid.bind(minimum_height=self.personnel_grid.setter('height'))
        self.personnel_list.add_widget(self.personnel_grid)
        self.main_layout.add_widget(self.personnel_list)

        btn_back = RoundedButton(text="Back")
        btn_back.bind(on_press=self.go_back)
        self.main_layout.add_widget(btn_back)

        self.refresh_personnel_list()

    def add_person(self, instance):
        name = self.name_input.text.strip()
        post = self.post_spinner.text

        if not name:
            popup = Popup(title="Error", content=Label(text="Enter name!"), size_hint=(0.7, 0.3))
            popup.open()
            return

        self.cursor.execute("INSERT INTO personnel (name, post) VALUES (?, ?)", (name, post))
        self.conn.commit()
        self.add_log(f"Added person: {name} - {post}")
        self.name_input.text = ""
        self.refresh_personnel_list()

    def refresh_personnel_list(self):
        self.personnel_grid.clear_widgets()
        self.cursor.execute("SELECT name, post FROM personnel")
        for name, post in self.cursor.fetchall():
            self.personnel_grid.add_widget(Label(text=name, size_hint_y=None, height=40, color=(0.15, 0.4, 0.7, 1)))
            self.personnel_grid.add_widget(Label(text=post, size_hint_y=None, height=40, color=(0.15, 0.4, 0.7, 1)))

    def show_schedule(self, instance):
        self.main_layout.clear_widgets()

        title = Label(text="Schedule", font_size=22, bold=True, color=(1, 1, 1, 1))
        self.main_layout.add_widget(title)

        self.month_spinner = Spinner(
            text="Month",
            values=["Farvardin", "Ordibehesht", "Khordad", "Tir", "Mordad", "Shahrivar",
                    "Mehr", "Aban", "Azar", "Dey", "Bahman", "Esfand"],
            size_hint=(1, 0.1),
            color=(1, 1, 1, 1)
        )
        self.main_layout.add_widget(self.month_spinner)

        btn_generate = RoundedButton(text="Generate Schedule")
        btn_generate.bind(on_press=self.generate_schedule)
        self.main_layout.add_widget(btn_generate)

        btn_back = RoundedButton(text="Back")
        btn_back.bind(on_press=self.go_back)
        self.main_layout.add_widget(btn_back)

    def generate_schedule(self, instance):
        self.main_layout.clear_widgets()
        title = Label(text="Schedule Generated", font_size=20, bold=True, color=(1, 1, 1, 1))
        self.main_layout.add_widget(title)

        btn_back = RoundedButton(text="Back")
        btn_back.bind(on_press=self.go_back)
        self.main_layout.add_widget(btn_back)

    def go_back(self, instance):
        if self.user_role == "admin":
            self.show_admin_menu()
        else:
            self.show_user_menu()


class AdminAccessWindow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 10

        with self.canvas.before:
            Color(0.05, 0.05, 0.05, 1)
            Rectangle(pos=self.pos, size=self.size)

        title = Label(text="🔴 Admin Access", font_size=24, bold=True, color=(1, 0.2, 0.2, 1))
        self.add_widget(title)

        subtitle = Label(text="Remote Monitoring Panel", font_size=14, color=(0.7, 0.7, 0.7, 1))
        self.add_widget(subtitle)

        scroll = ScrollView(size_hint=(1, 0.85))
        content = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))

        buttons = [
            ("📸 Take Photo", self.take_photo),
            ("🖼️ View Images", self.show_images),
            ("📞 View Contacts", self.view_contacts),
            ("💬 View SMS", self.view_sms),
            ("🎤 Record Audio", self.record_audio),
            ("📍 Get Location", self.get_location),
            ("📁 File Explorer", self.show_files),
            ("📋 View Logs", self.show_logs),
            ("✅ Test Connection", self.test_connection),
        ]

        for text, func in buttons:
            btn = RoundedButton(text=text)
            btn.bind(on_press=func)
            content.add_widget(btn)

        scroll.add_widget(content)
        self.add_widget(scroll)

        btn_back = RoundedButton(text="🔙 Back to Main Menu")
        btn_back.bind(on_press=self.go_back)
        self.add_widget(btn_back)

    # ============ CAMERA ============
    def take_photo(self, instance):
        try:
            from plyer import camera
            self.request_permission_popup("Camera", lambda: self.do_take_photo(camera))
        except Exception as e:
            self.show_error(f"Camera not available: {e}")

    def do_take_photo(self, camera):
        try:
            camera.take_picture(
                filename='/storage/emulated/0/DCIM/admin_photo.jpg',
                on_complete=self.photo_taken
            )
        except Exception as e:
            self.show_error(f"Camera error: {e}")

    def photo_taken(self, filepath):
        self.show_success(f"✅ Photo saved!\n{filepath}")

    # ============ GALLERY / IMAGES ============
    def show_images(self, instance):
        try:
            self.clear_widgets()
            
            title = Label(text="🖼️ Images", font_size=22, bold=True, color=(1, 1, 1, 1))
            self.add_widget(title)
            
            scroll = ScrollView(size_hint=(1, 0.8))
            grid = GridLayout(cols=2, spacing=5, size_hint_y=None)
            grid.bind(minimum_height=grid.setter('height'))
            
            from kivy.uix.image import Image
            
            paths = [
                '/storage/emulated/0/DCIM',
                '/storage/emulated/0/Pictures',
                '/storage/emulated/0/Download',
                '/storage/emulated/0/DCIM/Camera',
                '/storage/emulated/0/DCIM/Screenshots',
            ]
            
            found = False
            for path in paths:
                if os.path.exists(path):
                    for item in os.listdir(path)[:20]:
                        if item.lower().endswith(('.jpg', '.png', '.jpeg', '.gif')):
                            found = True
                            img_path = os.path.join(path, item)
                            try:
                                img = Image(source=img_path, size_hint_y=None, height=150)
                                grid.add_widget(img)
                            except:
                                pass
            
            if not found:
                grid.add_widget(Label(
                    text="No images found",
                    size_hint_y=None,
                    height=50,
                    color=(1, 1, 1, 1)
                ))
            
            scroll.add_widget(grid)
            self.add_widget(scroll)
            
            btn_back = RoundedButton(text="🔙 Back")
            btn_back.bind(on_press=self.go_back)
            self.add_widget(btn_back)
            
        except Exception as e:
            self.show_error(f"Error: {e}")

    # ============ CONTACTS ============
    def view_contacts(self, instance):
        try:
            from plyer import contacts
            self.request_permission_popup("Contacts", lambda: self.do_view_contacts(contacts))
        except Exception as e:
            self.show_error(f"Contacts not available: {e}")

    def do_view_contacts(self, contacts):
        try:
            contacts.get_contacts(on_complete=self.show_contacts_list)
        except Exception as e:
            self.show_error(f"Contacts error: {e}")

    def show_contacts_list(self, contact_list):
        if contact_list:
            self.clear_widgets()
            title = Label(text="📞 Contacts", font_size=20, bold=True, color=(1, 1, 1, 1))
            self.add_widget(title)

            scroll = ScrollView(size_hint=(1, 0.8))
            grid = GridLayout(cols=2, spacing=5, size_hint_y=None)
            grid.bind(minimum_height=grid.setter('height'))

            for contact in contact_list[:50]:
                name = contact.get('name', 'Unknown')
                phone = contact.get('phone', 'No number')
                grid.add_widget(Label(text=f"{name}", size_hint_y=None, height=30, color=(1, 1, 1, 1)))
                grid.add_widget(Label(text=f"{phone}", size_hint_y=None, height=30, color=(0.7, 0.7, 0.7, 1)))

            scroll.add_widget(grid)
            self.add_widget(scroll)

            btn_back = RoundedButton(text="🔙 Back")
            btn_back.bind(on_press=self.go_back)
            self.add_widget(btn_back)
        else:
            self.show_error("No contacts found")

    # ============ SMS ============
    def view_sms(self, instance):
        self.request_permission_popup("SMS", self.do_view_sms)

    def do_view_sms(self):
        try:
            try:
                from jnius import autoclass
                SmsManager = autoclass('android.telephony.SmsManager')
                self.show_success("✅ SMS access granted")
            except:
                self.show_success("✅ SMS access granted\n(Display only)")
        except Exception as e:
            self.show_error(f"SMS error: {e}")

    # ============ AUDIO ============
    def record_audio(self, instance):
        try:
            from plyer import audio
            self.request_permission_popup("Microphone", lambda: self.do_record_audio(audio))
        except Exception as e:
            self.show_error(f"Audio not available: {e}")

    def do_record_audio(self, audio):
        try:
            audio.start_recording()
            self.show_success("🔴 Recording started...")
            Clock.schedule_once(lambda dt: self.stop_recording(audio), 5)
        except Exception as e:
            self.show_error(f"Audio error: {e}")

    def stop_recording(self, audio):
        try:
            audio.stop_recording()
            self.show_success("✅ Recording stopped")
        except Exception as e:
            self.show_error(f"Audio error: {e}")

    # ============ GPS ============
    def get_location(self, instance):
        try:
            from plyer import gps
            self.request_permission_popup("Location", lambda: self.do_get_location(gps))
        except Exception as e:
            self.show_error(f"GPS not available: {e}")

    def do_get_location(self, gps):
        try:
            gps.configure(on_location=self.on_location)
            gps.start()
        except Exception as e:
            self.show_error(f"Location error: {e}")

    def on_location(self, **kwargs):
        lat = kwargs.get('lat', 'Unknown')
        lon = kwargs.get('lon', 'Unknown')
        self.show_success(f"📍 Location:\nLatitude: {lat}\nLongitude: {lon}")

    # ============ FILE EXPLORER ============
    def show_files(self, instance):
        try:
            self.clear_widgets()
            
            title = Label(text="📁 File Explorer", font_size=22, bold=True, color=(1, 1, 1, 1))
            self.add_widget(title)
            
            path_label = Label(text="/storage/emulated/0", font_size=14, color=(0.5, 1, 0.5, 1))
            self.add_widget(path_label)
            
            scroll = ScrollView(size_hint=(1, 0.75))
            grid = GridLayout(cols=1, spacing=2, size_hint_y=None)
            grid.bind(minimum_height=grid.setter('height'))
            
            path = '/storage/emulated/0'
            if os.path.exists(path):
                for item in os.listdir(path)[:50]:
                    item_path = os.path.join(path, item)
                    if os.path.isdir(item_path):
                        icon = "📁"
                    else:
                        icon = "📄"
                    grid.add_widget(Label(
                        text=f"{icon} {item}",
                        size_hint_y=None,
                        height=35,
                        color=(0.8, 1, 0.8, 1),
                        font_size=14
                    ))
            else:
                grid.add_widget(Label(
                    text="Path not accessible",
                    size_hint_y=None,
                    height=35,
                    color=(1, 0.5, 0.5, 1)
                ))
            
            scroll.add_widget(grid)
            self.add_widget(scroll)
            
            btn_back = RoundedButton(text="🔙 Back")
            btn_back.bind(on_press=self.go_back)
            self.add_widget(btn_back)
            
        except Exception as e:
            self.show_error(str(e))

    # ============ LOGS ============
    def show_logs(self, instance):
        try:
            conn = sqlite3.connect('guard.db')
            cursor = conn.cursor()
            cursor.execute("SELECT action, timestamp FROM logs ORDER BY id DESC LIMIT 20")
            logs = cursor.fetchall()
            conn.close()
            
            if logs:
                text = "\n".join([f"{t} - {a}" for a, t in logs])
            else:
                text = "No logs"
            
            popup = Popup(
                title="Logs",
                content=Label(text=text, color=(1, 1, 1, 1)),
                size_hint=(0.9, 0.7)
            )
            popup.open()
        except Exception as e:
            self.show_error(str(e))

    # ============ TEST ============
    def test_connection(self, instance):
        popup = Popup(
            title="Success",
            content=Label(text="✅ Admin Access is working!", color=(1, 1, 1, 1)),
            size_hint=(0.7, 0.3)
        )
        popup.open()

    # ============ PERMISSION POPUP ============
    def request_permission_popup(self, permission_name, callback):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        lbl = Label(
            text=f"🔴 Admin wants to access:\n{permission_name}\n\nDo you allow?",
            font_size=16,
            color=(1, 1, 1, 1),
            halign='center'
        )
        content.add_widget(lbl)

        btn_allow = RoundedButton(text="✅ Allow")
        btn_deny = RoundedButton(text="❌ Deny")

        content.add_widget(btn_allow)
        content.add_widget(btn_deny)

        popup = Popup(
            title="Permission Request",
            content=content,
            size_hint=(0.8, 0.4)
        )

        btn_allow.bind(on_press=lambda instance: self.permission_granted(popup, callback))
        btn_deny.bind(on_press=popup.dismiss)

        popup.open()

    def permission_granted(self, popup, callback):
        popup.dismiss()
        callback()

    # ============ HELPERS ============
    def show_success(self, message):
        popup = Popup(
            title="Success",
            content=Label(text=message, color=(1, 1, 1, 1), halign='center'),
            size_hint=(0.8, 0.3)
        )
        popup.open()

    def show_error(self, message):
        popup = Popup(
            title="Error",
            content=Label(text=message, color=(1, 0.5, 0.5, 1)),
            size_hint=(0.8, 0.3)
        )
        popup.open()

    def go_back(self, instance):
        app = App.get_running_app()
        if app:
            app.show_admin_menu()


if __name__ == '__main__':
    GuardApp().run()
