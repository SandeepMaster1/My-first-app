# main.py (fixed)

from kivy.lang import Builder
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import StringProperty, BooleanProperty, ListProperty
from kivy.core.window import Window

from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import ThreeLineListItem
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.toast import toast
from kivymd.uix.fitimage import FitImage

from plyer import filechooser

import pytesseract
from PIL import Image
import sqlite3
import re
import requests
from datetime import datetime
import random
import os

API_KEY = "AIzaSyDQbLtARCyzk8rPSkVxT7y6PlcKmY4wqo4"
MODEL = "gemini-1.5-flash"
BASE_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

KV = """
#:import dp kivy.metrics.dp
<ContentNavigationDrawer@MDBoxLayout>:
    orientation: "vertical"
    padding: "8dp"
    spacing: "8dp"

<HistoryListItem@OneLineListItem>:
    on_release: app.open_history_item(self.item_id)

ScreenManager:
    LoginScreen:
    SignupScreen:
    SignupVerifyScreen:
    ForgotPasswordScreen:
    ResetPasswordScreen:
    MainScreen:
    ProfileScreen:
    HistoryScreen:
    AboutHelpScreen:
    EditProfileScreen:

<LoginScreen@MDScreen>:
    name: "login"
    AnchorLayout:
        anchor_y: "top"
        MDBoxLayout:
            orientation: "vertical"
            padding: dp(16)
            spacing: dp(12)
            size_hint_y: None
            height: self.minimum_height

            MDTopAppBar:
                title: "DoubtCure"
                elevation: 10
            
            MDLabel:
                text: "Login to continue"
                halign: "center"
                theme_text_color: "Primary"
                font_style: "H6"
                size_hint_y: None
                height: self.texture_size[1] + dp(10)
                
            MDTextField:
	            id: login_phone
	            hint_text: "Phone number"
	            helper_text_mode: "on_focus"
	            icon_right: "phone"

	        MDTextField:
	            id: login_password
	            hint_text: "Password"
	            password: True
	            icon_right: "key"
	
	        MDRaisedButton:
	            text: "Login"
	            pos_hint: {"center_x": 0.5}
	            on_release: app.login(login_phone.text, login_password.text)
	
	        MDTextButton:
	            text: "Forgot Password?"
	            pos_hint: {"center_x": 0.5}
	            on_release: root.manager.current = "forgot"
	
	        MDTextButton:
	            text: "Create account"
	            pos_hint: {"center_x": 0.5}
	            on_release: root.manager.current = "signup"
	            
	        MDFlatButton:
                text: "Skip Login (limited)"
                pos_hint: {"center_x": .5}
                on_release: app.skip_login()            

<SignupScreen@MDScreen>:
    name: "signup"
    AnchorLayout:
        anchor_y: "top"
        MDBoxLayout:
            orientation: "vertical"
            padding: dp(16)
            spacing: dp(12)
            size_hint_y: None
            height: self.minimum_height
            
            MDTopAppBar:
                title: "DoubtCure"
                elevation: 10
	
	        MDLabel:
                text: "Creat Account"
                halign: "center"
                theme_text_color: "Primary"
                font_style: "H6"
                size_hint_y: None
                height: self.texture_size[1] + dp(10)

            MDTextField:
                id: su_name
                hint_text: "Full name"

            MDTextField:
                id: su_phone
                hint_text: "Phone number"

            MDTextField:
                id: su_email
                hint_text: "Email (optional)"

            MDTextField:
                id: su_class
                hint_text: "Class (optional)"

            MDTextField:
                id: su_exam
                hint_text: "Exam (optional)"

            MDTextField:
                id: su_password
                hint_text: "Password"
                password: True

            MDRaisedButton:
                text: "Send OTP"
                pos_hint: {"center_x": 0.5}
                on_release: app.send_signup_otp(su_name.text, su_phone.text, su_email.text, su_class.text, su_exam.text, su_password.text)

            MDTextButton:
                text: "Back to Login"
                pos_hint: {"center_x": 0.5}
                on_release: root.manager.current = "login"

<SignupVerifyScreen@MDScreen>:
    name: "signup_verify"
    AnchorLayout:
        anchor_y: "top"
        MDBoxLayout:
            orientation: "vertical"
            padding: dp(16)
            spacing: dp(12)
            size_hint_y: None
            height: self.minimum_height
            
            MDTopAppBar:
                title: "DoubtCure"
                elevation: 10
	
	        MDLabel:
                text: "Verify Phone (Signup)"
                halign: "center"
                theme_text_color: "Primary"
                font_style: "H6"
                size_hint_y: None
                height: self.texture_size[1] + dp(10)

	        MDTextField:
	            id: sv_otp
	            hint_text: "Enter OTP"
	
	        MDRaisedButton:
	            text: "Verify and Create Account"
	            pos_hint: {"center_x": 0.5}
	            on_release: app.verify_signup_otp(sv_otp.text)
	
	        MDTextButton:
	            text: "Resend OTP"
	            pos_hint: {"center_x": 0.5}
	            on_release: app.resend_signup_otp()

<ForgotPasswordScreen@MDScreen>:
    name: "forgot"
    AnchorLayout:
        anchor_y: "top"
        MDBoxLayout:
            orientation: "vertical"
            padding: dp(16)
            spacing: dp(12)
            size_hint_y: None
            height: self.minimum_height

            MDTopAppBar:
                title: "DoubtCure"
                elevation: 10

            MDLabel:
                text: "Forgot Password"
                halign: "center"
                theme_text_color: "Primary"
                font_style: "H6"
                size_hint_y: None
                height: self.texture_size[1] + dp(10)

            MDTextField:
                id: fp_phone
                hint_text: "Enter your registered phone no."

            MDRaisedButton:
                text: "Send OTP"
                pos_hint: {"center_x": 0.5}
                on_release: app.send_forgot_otp(fp_phone.text)

            MDTextField:
                id: fp_otp
                hint_text: "Enter OTP"

            MDRaisedButton:
                text: "Verify OTP"
                pos_hint: {"center_x": 0.5}
                on_release: app.verify_forgot_otp(fp_otp.text)
                
            MDTextButton:
                text: "Back to Login"
                pos_hint: {"center_x": 0.5}
                on_release: root.manager.current = "login"
	
<ResetPasswordScreen@MDScreen>:
    name: "reset"
    AnchorLayout:
        anchor_y: "top"
        MDBoxLayout:
            orientation: "vertical"
            padding: dp(16)
            spacing: dp(12)
            size_hint_y: None
            height: self.minimum_height

            MDTopAppBar:
                title: "DoubtCure"
                elevation: 10

            MDLabel:
                text: "Reset Password"
                halign: "center"
                theme_text_color: "Primary"
                font_style: "H6"
                size_hint_y: None
                height: self.texture_size[1] + dp(10)

	        MDTextField:
	            id: new_password
	            hint_text: "New Password"
	            password: True
	
	        MDRaisedButton:
	            text: "Reset Password"
	            pos_hint: {"center_x": 0.5}
	            on_release: app.reset_password(new_password.text)
            
<MainScreen@MDScreen>:
    name: "home"
    MDBoxLayout:
        orientation: "vertical"
        padding: "10dp"
        spacing: "10dp"

        MDTopAppBar:
            id: toolbar
            title: "DoubtCure"
            elevation: 10
            right_action_items: [["dots-vertical", lambda x: app.open_more_menu(x)]]
            left_action_items: [["account-circle", lambda x: app.open_profile()]]

        MDBoxLayout:
            orientation: "vertical"
            padding: "10dp"
            spacing: "10dp"

            MDTextField:
                id: subject_field
                hint_text: "Select Subject"
                text: "Select Subject"
                readonly: True
                on_touch_down:
                    app.open_subject_menu(self) if self.collide_point(*args[1].pos) else None
                theme_text_color: "Custom"
                text_color: [0, 0, 0, 1]

            MDTextField:
                id: question_field
                hint_text: "Type or paste your question here."
                multiline: True
                size_hint_y: None
                height: "110dp"
                theme_text_color: "Custom"
                text_color: [0, 0, 0, 1]

            MDBoxLayout:
                size_hint_y: None
                height: "50dp"
                spacing: "10dp"

                MDIconButton:
                    icon: "camera"
                    user_font_size: "32sp"
                    on_release: app.get_from_camera()

                MDIconButton:
                    icon: "image"
                    user_font_size: "32sp"
                    on_release: app.get_from_gallery()

                MDIconButton:
                    icon: "microphone"
                    user_font_size: "32sp"
                    on_release: app.get_from_mic()

            MDRaisedButton:
                text: "Get Solution"
                size_hint_y: None
                on_release: app.get_solution()

            MDLabel:
                id: status_label
                text: ""
                theme_text_color: "Custom"
                halign: "center"
                size_hint_y: None
                height: self.texture_size[1] + dp(8)
                text_color: [0, 0, 0, 1]

            ScrollView:
                MDLabel:
                    id: answer_label
                    text: "Your answer will appear here..."
                    size_hint_y: None
                    height: self.texture_size[1]
                    padding: 10, 10
                    halign: "left"
                    theme_text_color: "Custom"
                    text_color: [0, 0, 0, 1]
                    
<ProfileScreen@MDScreen>:
    name: "profile"

    MDBoxLayout:
        orientation: "vertical"
        spacing: dp(10)
        padding: dp(20)

        MDTopAppBar:
            title: "Profile"
            left_action_items: [["arrow-left", lambda x: app.go_back_home()]]
            right_action_items: [["pencil", lambda x: app.go_edit_profile()]]  # ✅ Edit button

        MDBoxLayout:
            orientation: "vertical"
            spacing: dp(10)
            padding: dp(10)
            adaptive_height: True
            halign: "center"

            MDCard:
                size_hint: None, None
                size: dp(120), dp(120)
                radius: [60,]
                elevation: 2
                pos_hint: {"center_x": 0.5}
                md_bg_color: 1, 1, 1, 1

                FitImage:
                    id: profile_img
                    source: "default_user.png"
                    size_hint: None, None
                    size: dp(120), dp(120)
                    radius: [60,]

        MDLabel:
            id: name_lbl
            text: "Name: —"
            halign: "left"

        MDLabel:
            id: phone_lbl
            text: "Phone: —"
            halign: "left"

        MDLabel:
            id: email_lbl
            text: "Email: —"
            halign: "left"

        MDLabel:
            id: class_lbl
            text: "Class: —"
            halign: "left"

        MDLabel:
            id: exam_lbl
            text: "Exam: —"
            halign: "left"
            
<EditProfileScreen@MDScreen>:
    name: "edit_profile"

    MDBoxLayout:
        orientation: "vertical"
        spacing: dp(10)
        padding: dp(20)

        MDTopAppBar:
            title: "Edit Profile"
            left_action_items: [["arrow-left", lambda x: app.go_back_profile()]]

        ScrollView:
            MDBoxLayout:
                orientation: "vertical"
                spacing: dp(20)
                size_hint_y: None
                height: self.minimum_height

                MDRaisedButton:
                    text: "Change Photo"
                    pos_hint: {"center_x": 0.5}
                    on_release: app.pick_photo()   # ✅ Camera/Gallery se photo

                MDTextField:
                    id: name_input
                    hint_text: "Enter Name"

                MDTextField:
                    id: phone_input
                    hint_text: "Enter Phone"

                MDTextField:
                    id: email_input
                    hint_text: "Enter Email"

                MDTextField:
                    id: class_input
                    hint_text: "Enter Class"

                MDTextField:
                    id: exam_input
                    hint_text: "Enter Exam"

                MDRaisedButton:
                    text: "Save"
                    pos_hint: {"center_x": 0.5}
                    on_release: app.save_profile()

<HistoryScreen@MDScreen>:
    name: "history"

    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "History"
            elevation: 10
            md_bg_color: app.theme_cls.primary_color
            title_color: 1, 1, 1, 1
            left_action_items: [["arrow-left", lambda x: app.go_home()]]
            right_action_items: [["delete", lambda x: app.confirm_clear_history()]]

        Widget:
            size_hint_y: None
            height: dp(20)

        MDBoxLayout:
            orientation: "horizontal"
            padding: dp(10)
            spacing: dp(10)
            size_hint_y: None
            height: dp(56)

            MDTextField:
                id: search_field
                hint_text: "Search"
                on_text: app.refresh_history()
                mode: "rectangle"
                size_hint_x: 0.7
                text_color: 1, 1, 1, 1
                hint_text_color: 0.7, 0.7, 0.7, 1
                line_color_normal: 0.6, 0.6, 0.6, 1
                line_color_focus: app.theme_cls.primary_color
                fill_color: 0.15, 0.15, 0.15, 1

            MDDropDownItem:
                id: subject_filter
                text: "All"
                on_release: app.open_subject_filter(self)
                size_hint_x: 0.3
                text_color: 1, 1, 1, 1

        ScrollView:
            MDList:
                id: history_list

<AboutHelpScreen@MDScreen>:
    name: "about"
    MDBoxLayout:
        orientation: "vertical"
        padding: "12dp"
        spacing: "12dp"

        MDLabel:
            text: "About DoubtCure"
            font_style: "H5"
            halign: "center"

        MDLabel:
            text: "This app helps students ask doubts, get answers via AI (Gemini placeholder), use OCR and voice input. OTP is simulated in this free demo."
            halign: "left"
            theme_text_color: "Secondary"

        MDTextButton:
            text: "Back"
            pos_hint: {"center_x": 0.5}
            on_release: root.manager.current = "main"
"""

class HistoryDB:
    def __init__(self, path="history.db"):
        self.path = path
        self._ensure()

    def _ensure(self):
        conn = sqlite3.connect(self.path)
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            subject TEXT,
            question TEXT,
            answer TEXT,
            ts TEXT
        )
        """)
        conn.commit()
        conn.close()

    def add(self, user_id, subject, question, answer):
        conn = sqlite3.connect(self.path)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO history (user_id, subject, question, answer, ts) VALUES (?,?,?,?,?)",
            (str(user_id), subject, question, answer, datetime.now().isoformat(timespec="seconds"))
        )
        conn.commit()
        conn.close()

    def query(self, user_id, q="", subject="All"):
        conn = sqlite3.connect(self.path)
        cur = conn.cursor()
        like = f"%{(q or '').strip()}%"
        if subject and subject != "All":
            cur.execute("""SELECT subject, question, answer, ts FROM history
                           WHERE user_id=? AND question LIKE ? AND subject=?
                           ORDER BY id DESC""", (str(user_id), like, subject))
        else:
            cur.execute("""SELECT subject, question, answer, ts FROM history
                           WHERE user_id=? AND question LIKE ?
                           ORDER BY id DESC""", (str(user_id), like))
        rows = cur.fetchall()
        conn.close()
        return rows

    def clear(self, user_id):
        conn = sqlite3.connect(self.path)
        cur = conn.cursor()
        cur.execute("DELETE FROM history WHERE user_id=?", (str(user_id),))
        conn.commit()
        conn.close()

def is_hinglish(text: str) -> bool:
    if re.search(r"[\u0900-\u097F]", text):
        return True
    common = ["hai", "kya", "kaise", "kyu", "kyon", "krdo", "mujhe", "batao", "matlab", "thoda", "hona", "mein", "se"]
    t = (text or "").lower()
    return any(w in t for w in common)

def make_prompt(subject: str, question: str) -> str:
    if is_hinglish(question):
        style = ("Answer strictly in **Hinglish** (English letters). "
                 "Pehele short steps bullets, phir final answer. "
                 "Agar koi mushkil Hindi shabd aaye, to uska English meaning (brackets) me likho.")
    else:
        style = "Answer in clear English, show steps first, then a final concise answer."
    return f"You are an expert in {subject}. {style}\n\nQuestion:\n{question}"

def gemini_answer(prompt: str) -> str:
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        r = requests.post(BASE_URL, json=payload, timeout=60)
        if r.status_code != 200:
            return f"Error {r.status_code}: {r.text}"
        data = r.json()
        # safe guard in case structure is different
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            return str(data)
    except Exception as e:
        return f"Error: {e}"

from kivy.properties import StringProperty, BooleanProperty, ListProperty
from kivymd.app import MDApp
from datetime import datetime

class DoubtCureApp(MDApp):
    # ---------------- Properties ----------------
    user_id = StringProperty("")       # string id used by history, etc.
    user_name = StringProperty("")
    user_phone = StringProperty("")
    user_email = StringProperty("")
    user_class = StringProperty("")
    user_exam = StringProperty("")
    is_logged_in = BooleanProperty(False)
    generated_otp = StringProperty("")
    otp = StringProperty("")
    subjects = ListProperty(["Maths", "Science", "English", "History", "Geography","Computer"])

    # ---------------- Init ----------------
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # ✅ History DB initialize here
        self.db = HistoryDB()
        # ✅ for testing (you can set these after login/signup)
        self.is_logged_in = True
        self.user_id = "1"

    def build(self):
        self.title = "DoubtCure"
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "BlueGray"
        self.conn = sqlite3.connect("doubtcure.db")
        self.cursor = self.conn.cursor()
        # users table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                phone TEXT UNIQUE,
                email TEXT,
                class TEXT,
                exam TEXT,
                password TEXT
            )
        """)
        
        self.conn.commit()

        # OTP and pending vars
        self.signup_otp = None
        self.signup_pending = None
        self.forgot_otp = None
        self.forgot_phone = None

        return Builder.load_string(KV)

    def skip_login(self):
        # allow guest use (no DB user); limit features
        self.user_id = ""
        self.user_name = ""
        self.user_email = ""
        self.user_phone = ""
        self.is_logged_in = False
        Snackbar(text="Guest mode: limited features.").open()
        # go to home screen
        self.root.current = "home"

    # ----------------- Auth: Signup OTP -----------------
    def send_signup_otp(self, name, phone, email, user_class, exam, password):
        if not phone or not password:
            Snackbar(text="Phone and password required").open()
            return
        # check if phone exists
        try:
            self.cursor.execute("SELECT id FROM users WHERE phone=?", (phone,))
            if self.cursor.fetchone():
                Snackbar(text="Phone already registered. Login or use forgot password.").open()
                return
        except Exception as e:
            Snackbar(text=f"DB error: {e}").open()
            return

        self.signup_pending = (name, phone, email, user_class, exam, password)
        self.signup_otp = str(random.randint(1000, 9999))
        Snackbar(text=f"OTP sent: {self.signup_otp} (demo)").open()
        self.root.current = "signup_verify"

    def resend_signup_otp(self):
		    if not getattr(self, "signup_performed", False):
		        # do something here
		        self.signup_performed = True
        # ----------------- Auth: Signup OTP -----------------
    def send_signup_otp(self, name, phone, email, user_class, exam, password):
        if not phone or not password:
            Snackbar(text="Phone and password required").open()
            return
        # check if phone exists
        try:
            self.cursor.execute("SELECT id FROM users WHERE phone=?", (phone,))
            if self.cursor.fetchone():
                Snackbar(text="Phone already registered. Login or use forgot password.").open()
                return
        except Exception as e:
            Snackbar(text=f"DB error: {e}").open()
            return

        self.signup_pending = (name, phone, email, user_class, exam, password)
        self.signup_otp = str(random.randint(1000, 9999))
        Snackbar(text=f"OTP sent: {self.signup_otp} (demo)").open()
        self.root.current = "signup_verify"

    def resend_signup_otp(self):
        if not getattr(self, "signup_pending", None):
            Snackbar(text="No signup pending").open()
            return
        self.signup_otp = str(random.randint(1000, 9999))
        Snackbar(text=f"Resent OTP: {self.signup_otp} (demo)").open()

    def verify_signup_otp(self, otp_text):
        if not getattr(self, "signup_otp", None):
            Snackbar(text="No OTP sent").open()
            return

        if otp_text == self.signup_otp:
            try:
                self.cursor.execute(
                    "INSERT INTO users (name, phone, email, class, exam, password) VALUES (?, ?, ?, ?, ?, ?)",
                    self.signup_pending
                )
                self.conn.commit()
                Snackbar(text="Signup successful! Please login.").open()
                self.signup_pending = None
                self.signup_otp = None
                self.root.current = "login"
            except Exception as e:
                Snackbar(text="Signup error: " + str(e)).open()
                print("Signup DB error:", e)
        else:
            Snackbar(text="Invalid OTP").open()

    # ----------------- Login -----------------
    def login(self, phone, password):
        if not phone or not password:
            toast("Phone & password required")
            return
        try:
            self.cursor.execute("SELECT id, name, email, class, exam FROM users WHERE phone=? AND password=?", (phone, password))
            row = self.cursor.fetchone()
        except Exception as e:
            toast("DB error: " + str(e))
            return

        if row:
            # set session vars used by other functions
            self.current_user_id = row[0]
            self.user_id = str(row[0])
            self.user_name = row[1] or ""
            self.user_phone = phone
            self.user_email = row[2] or ""
            self.user_class = row[3] or ""
            self.user_exam = row[4] or ""
            self.is_logged_in = True
            toast(f"Welcome {self.user_name or 'User'}")
            self.root.current = "home"
            self.load_profile()
        else:
            toast("Invalid credentials")

    # ----------------- Forgot Password -----------------
    def send_forgot_otp(self, phone):
	    if not phone:
	        Snackbar(text="Enter phone number").open()
	        return
	    try:
	        self.cursor.execute("SELECT id FROM users WHERE phone=?", (phone,))
	        r = self.cursor.fetchone()
	    except Exception as e:
	        Snackbar(text="DB error: " + str(e)).open()
	        return
	
	    if not r:
	        Snackbar(text="Phone not found").open()
	        return
	
	    # OTP generate
	    self.forgot_phone = phone
	    self.forgot_otp = str(random.randint(1000, 9999))
	
	    # Console pe bhi show hoga (debug ke liye)
	    print("Forgot OTP (simulated):", self.forgot_otp)
	
	    # Snackbar me actual OTP show karenge
	    Snackbar(text=f"Your OTP is: {self.forgot_otp}").open()

    def verify_forgot_otp(self, otp_text):
        if not getattr(self, "forgot_otp", None):
            toast("No OTP sent")
            return
        if otp_text == self.forgot_otp:
            toast("OTP verified. Enter new password.")
            self.root.current = "reset"
        else:
            toast("Invalid OTP")

    def reset_password(self, new_password):
        if not getattr(self, "forgot_phone", None):
            toast("No phone to reset")
            return
        if not new_password:
            toast("Enter a new password")
            return
        try:
            self.cursor.execute("UPDATE users SET password=? WHERE phone=?", (new_password, self.forgot_phone))
            self.conn.commit()
            toast("Password updated. Login with new password.")
            self.forgot_otp = None
            self.forgot_phone = None
            self.root.current = "login"
        except Exception as e:
            toast("Reset error: " + str(e))
            
    def open_subject_menu(self, caller_widget):
        menu_items = [{
            "viewclass": "OneLineListItem",
            "text": s,
            "on_release": lambda x=s: self._set_subject(x)
        } for s in self.subjects]
        self.subj_menu = MDDropdownMenu(caller=caller_widget, items=menu_items, width_mult=4)
        self.subj_menu.open()

    def _set_subject(self, s):
        self.root.get_screen("home").ids.subject_field.text = s
        if hasattr(self, "subj_menu"):
            self.subj_menu.dismiss()

    def open_subject_filter(self, caller_widget):
        menu_items = [{
            "viewclass": "OneLineListItem",
            "text": opt,
            "on_release": lambda x=opt: self._set_subject_filter(x)
        } for opt in (["All"] + self.subjects)]
        self.filter_menu = MDDropdownMenu(caller=caller_widget, items=menu_items, width_mult=3)
        self.filter_menu.open()

    def _set_subject_filter(self, s):
        self.root.get_screen("history").ids.subject_filter.text = s
        if hasattr(self, "filter_menu"):
            self.filter_menu.dismiss()
        self.refresh_history()

    def open_more_menu(self, button_widget):
        items = [
            {"viewclass": "OneLineListItem", "text": "History", "on_release": lambda: self._menu_action("history")},
            {"viewclass": "OneLineListItem", "text": "Profile", "on_release": lambda: self._menu_action("profile")},
            {"viewclass": "OneLineListItem", "text": "Theme: Light/Dark", "on_release": lambda: self._menu_action("theme")},
            {"viewclass": "OneLineListItem", "text": "About / Help", "on_release": lambda: self._menu_action("about")},
            {"viewclass": "OneLineListItem", "text": "Logout", "on_release": lambda: self._menu_action("logout")},
        ]
        self.more_menu = MDDropdownMenu(caller=button_widget, items=items, width_mult=4)
        self.more_menu.open()

    def _menu_action(self, key):
        if hasattr(self, "more_menu"):
            self.more_menu.dismiss()
        if key == "history":
            self.go_history()
        elif key == "theme":
            self.theme_toggle()
        elif key == "about":
            self.open_abouthelp()
        elif key == "logout":
            self.current_user_id = None
            self.user_id = ""
            self.is_logged_in = False
            Snackbar(text="Logged out").open()
            self.root.current = "login"
        elif key == "profile":
            self.open_profile()

    def theme_toggle(self):
        if self.theme_cls.theme_style == "Light":
            self.theme_cls.theme_style = "Dark"
            self.set_text_colors(white=True)
        else:
            self.theme_cls.theme_style = "Light"
            self.set_text_colors(white=False)

    def set_text_colors(self, white=True):
        c = [1, 1, 1, 1] if white else [0, 0, 0, 1]
        try:
            home = self.root.get_screen("home")
            home.ids.subject_field.text_color = c
            home.ids.question_field.text_color = c
            home.ids.status_label.text_color = c
            home.ids.answer_label.text_color = c
        except Exception:
            pass

        try:
            history = self.root.get_screen("history")
            history.ids.search_field.text_color = c
            history.ids.subject_filter.text_color = c
        except Exception:
            pass

    def get_solution(self):
        home = self.root.get_screen("home")
        subject = home.ids.subject_field.text
        question = home.ids.question_field.text

        if subject == "Select Subject" or not question.strip():
            home.ids.status_label.text = "Please select subject and enter a question."
            return

        home.ids.status_label.text = "Thinking..."
        home.ids.answer_label.text = ""

        prompt = make_prompt(subject, question)
        answer = gemini_answer(prompt)

        home.ids.answer_label.text = answer
        home.ids.status_label.text = ""

        if self.is_logged_in and self.user_id:
            self.db.add(self.user_id, subject, question, answer)

    def refresh_history(self, *_):
        if not self.is_logged_in or not self.user_id:
            return
        try:
            screen = self.root.get_screen("history")
            q = screen.ids.search_field.text
            subj = screen.ids.subject_filter.text
            data = self.db.query(self.user_id, q=q, subject=subj)
            lst = screen.ids.history_list
            lst.clear_widgets()
            for subject, question, answer, ts in data:
                item = ThreeLineListItem(
                    text=f"[{subject}] {question[:60]}",
                    secondary_text=(answer[:80] + ("..." if len(answer) > 80 else "")),
                    tertiary_text=datetime.fromisoformat(ts).strftime("%d %b %Y, %I:%M %p")
                )
                lst.add_widget(item)
        except Exception as e:
            print("Refresh history error:", e)

    def confirm_clear_history(self):
        if not self.is_logged_in:
            Snackbar(text="Login required").open()
            return
        def _clear(_):
            self.db.clear(self.user_id)
            self.refresh_history()
            dlg.dismiss()
            Snackbar(text="History cleared").open()
        dlg = MDDialog(
            title="Clear History?",
            text="This will remove all saved Q&A for your account on this device.",
            buttons=[
                MDFlatButton(text="Cancel", on_release=lambda x: dlg.dismiss()),
                MDRaisedButton(text="Clear", on_release=_clear),
            ]
        )
        dlg.open()

    def _need_login_guard(self, feature_name="this"):
        if not self.is_logged_in:
            Snackbar(text=f"Login required to use {feature_name}").open()
            self.root.current = "login"
            return True
        return False

    def get_from_camera(self):
        if self._need_login_guard("Camera"):
            return
        try:
            # TODO: Replace with actual camera capture path
            image_path = "captured.jpg"
            if not os.path.exists(image_path):
                Snackbar(text="Camera capture file not found (demo).").open()
                return
            self.extract_text_from_image(image_path)
        except Exception as e:
            Snackbar(text=f"Camera error: {e}").open()

    def get_from_gallery(self):
        if self._need_login_guard("Gallery"):
            return
        try:
            sel = filechooser.open_file(title="Pick an Image",
                                        filters=[("Image files", "*.png;*.jpg;*.jpeg")])
            if sel and len(sel) > 0:
                path = sel[0]
                Snackbar(text=f"Selected: {path}").open()
                self.extract_text_from_image(path)
            else:
                Snackbar(text="No image selected").open()
        except Exception as e:
            Snackbar(text=f"Gallery error: {e}").open()

    def get_from_mic(self):
        if self._need_login_guard("Voice"):
            return
        Snackbar(text="Mic feature coming soon (add recorder + STT).").open()

    def go_home(self):
        self.root.current = "home"

    def go_history(self):
        if not self.is_logged_in:
            Snackbar(text="Login required to view History").open()
            self.root.current = "login"
            return
        self.root.current = "history"
        Clock.schedule_once(lambda *_: self.refresh_history(), 0.1)

    def open_abouthelp(self):
        txt = ("DoubtCure\n\n"
               "• Solve doubts via AI (Gemini)\n"
               "• Subject-aware, Hinglish/English auto reply\n"
               "• Offline local History (search + subject filter)\n"
               "• Login required for History & media features\n"
               "• Light/Dark theme")

        self.about_dialog = MDDialog(
            title="About / Help",
            text=txt,
            buttons=[
                MDFlatButton(
                    text="OK",
                    on_release=lambda x: self.about_dialog.dismiss()
                )
            ],
        )
        self.about_dialog.open()

    # ----------------- Profile -----------------
    def load_profile(self):
        if not getattr(self, "current_user_id", None):
            return
        try:
            self.cursor.execute("SELECT name, phone, email, class, exam FROM users WHERE id=?", (self.current_user_id,))
            row = self.cursor.fetchone()
            if row:
                # update the profile screen labels (ids used in KV)
                prof_screen = self.root.get_screen("profile")
                prof_screen.ids.name_lbl.text = "Name: " + str(row[0] or "")
                prof_screen.ids.phone_lbl.text = "Phone: " + str(row[1] or "")
                prof_screen.ids.email_lbl.text = "Email: " + str(row[2] or "")
                prof_screen.ids.class_lbl.text = "Class: " + str(row[3] or "")
                prof_screen.ids.exam_lbl.text = "Exam: " + str(row[4] or "")
        except Exception as e:
            print("Load profile error:", e)

    def open_profile(self):
        if not getattr(self, "current_user_id", None):
            toast("Please login first")
            self.root.current = "login"
            return
        self.load_profile()
        self.root.current = "profile"
        
    def go_back_home(self):
        self.root.current = "home"

    def go_edit_profile(self):
        edit_screen = self.root.get_screen("edit_profile")
        edit_screen.ids.name_input.text = self.user_name or ""
        edit_screen.ids.phone_input.text = self.user_phone or ""
        edit_screen.ids.email_input.text = self.user_email or ""
        edit_screen.ids.class_input.text = self.user_class or ""
        edit_screen.ids.exam_input.text = self.user_exam or ""
        self.root.current = "edit_profile"

    def save_profile(self):
        edit_screen = self.root.get_screen("edit_profile")
        self.user_name = edit_screen.ids.name_input.text.strip()
        self.user_phone = edit_screen.ids.phone_input.text.strip()
        self.user_email = edit_screen.ids.email_input.text.strip()
        self.user_class = edit_screen.ids.class_input.text.strip()
        self.user_exam = edit_screen.ids.exam_input.text.strip()

        # optionally persist to DB for logged-in user
        if getattr(self, "current_user_id", None):
            try:
                self.cursor.execute("UPDATE users SET name=?, phone=?, email=?, class=?, exam=? WHERE id=?",
                                    (self.user_name, self.user_phone, self.user_email, self.user_class, self.user_exam, self.current_user_id))
                self.conn.commit()
            except Exception as e:
                print("Save profile DB error:", e)

        Snackbar(text="Profile Updated!").open()
        self.load_profile()
        self.root.current = "profile"

    def go_back_profile(self):
        self.root.current = "profile"

    # ----------------- Image OCR -----------------
    def extract_text_from_image(self, image_path):
	    try:
	        import pytesseract
	        from PIL import Image
	
	        # Open image
	        img = Image.open(image_path)
	
	        # Extract text using pytesseract
	        text = pytesseract.image_to_string(img)
	
	        if text.strip():
	            self.root.get_screen("home").ids.question_field.text = text
	            Snackbar(text="Text extracted from image!").open()
	        else:
	            Snackbar(text="No readable text found in image.").open()
	
	    except Exception as e:
	        Snackbar(text=f"Error extracting text: {e}").open()

if __name__ == "__main__":
    try:
        Window.size = (420, 800)
    except Exception:
        pass
    DoubtCureApp().run()