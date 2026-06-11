# ══════════════════════════════════════════════════════════════
# MOON Fitness - Premium Workout & Progress Tracker
# نسخه: 1.0
# ══════════════════════════════════════════════════════════════

import json
import math
import os
import sqlite3
import sys
import time
from datetime import datetime, timedelta

from kivy.utils import platform
if platform != "android":
    from kivy.config import Config
    Config.set("graphics", "width", "430")
    Config.set("graphics", "height", "860")

from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Line, Rectangle, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.properties import (
    BooleanProperty, ListProperty, NumericProperty,
    ObjectProperty, StringProperty,
)
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDIconButton, MDRaisedButton
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.textfield import MDTextField

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    HAS_BIDI = True
except ImportError:
    arabic_reshaper = None
    get_display = None
    HAS_BIDI = False

try:
    from plyer import notification as plyer_notification
    HAS_NOTIFICATION = True
except Exception:
    plyer_notification = None
    HAS_NOTIFICATION = False

try:
    from plyer import vibrator as plyer_vibrator
    HAS_VIBRATOR = True
except Exception:
    plyer_vibrator = None
    HAS_VIBRATOR = False


def get_db_path():
    if platform == "android":
        try:
            from android.storage import primary_external_storage_path
            base = primary_external_storage_path()
            folder = os.path.join(base, "MOON")
            os.makedirs(folder, exist_ok=True)
            return os.path.join(folder, "moon.db")
        except Exception:
            pass
        try:
            app = MDApp.get_running_app()
            if app:
                return os.path.join(app.user_data_dir, "moon.db")
        except Exception:
            pass
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "moon.db")


DB_PATH = get_db_path()


class MoonColors:
    DARK_BG = "#0D0B1A"
    DARK_SURFACE = "#161330"
    DARK_CARD = "#1E1A3A"
    DARK_CARD_ALT = "#241F42"
    DARK_ACCENT = "#A78BFA"
    DARK_ACCENT2 = "#F9A8D4"
    DARK_GOLD = "#F5D07A"
    DARK_TEXT = "#EDE9FE"
    DARK_TEXT2 = "#A5A0C8"
    DARK_SUCCESS = "#6EE7B7"
    DARK_ERROR = "#FCA5A5"
    DARK_DIVIDER = "#2E2854"
    DARK_NAV = "#120F26"
    DARK_NAV_ACTIVE = "#A78BFA"
    DARK_NAV_INACTIVE = "#5B5580"
    DARK_BUTTON = "#7C3AED"
    DARK_BUTTON_TEXT = "#FFFFFF"
    DARK_INPUT_BG = "#1E1A3A"
    DARK_INPUT_BORDER = "#3B3570"
    DARK_HEADER = "#161330"

    LIGHT_BG = "#F8F6FF"
    LIGHT_SURFACE = "#FFFFFF"
    LIGHT_CARD = "#FFFFFF"
    LIGHT_CARD_ALT = "#F3EEFF"
    LIGHT_ACCENT = "#7C3AED"
    LIGHT_ACCENT2 = "#EC4899"
    LIGHT_GOLD = "#D4A843"
    LIGHT_TEXT = "#1E1B3A"
    LIGHT_TEXT2 = "#6B6490"
    LIGHT_SUCCESS = "#10B981"
    LIGHT_ERROR = "#EF4444"
    LIGHT_DIVIDER = "#E5E0F5"
    LIGHT_NAV = "#FFFFFF"
    LIGHT_NAV_ACTIVE = "#7C3AED"
    LIGHT_NAV_INACTIVE = "#9B95B0"
    LIGHT_BUTTON = "#7C3AED"
    LIGHT_BUTTON_TEXT = "#FFFFFF"
    LIGHT_INPUT_BG = "#F3EEFF"
    LIGHT_INPUT_BORDER = "#C8BEE5"
    LIGHT_HEADER = "#FFFFFF"

    @staticmethod
    def get(name, dark=True):
        prefix = "DARK_" if dark else "LIGHT_"
        return get_color_from_hex(getattr(MoonColors, prefix + name, "#FFFFFF"))


def rtl_text(text):
    if not text:
        return ""
    text = str(text)
    if HAS_BIDI:
        try:
            reshaped = arabic_reshaper.reshape(text)
            return get_display(reshaped)
        except Exception:
            return text
    return text


RTL_FONT_NAME = "Vazirmatn"
RTL_FONT_LOADED = False

def load_rtl_font():
    global RTL_FONT_LOADED
    candidates = [
        os.path.join("assets", "fonts", "Vazirmatn-Regular.ttf"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "fonts", "Vazirmatn-Regular.ttf"),
    ]
    if platform == "android":
        try:
            app = MDApp.get_running_app()
            if app:
                candidates.insert(0, os.path.join(app.user_data_dir, "assets", "fonts", "Vazirmatn-Regular.ttf"))
        except Exception:
            pass
        candidates.append("/system/fonts/NotoNaskhArabic-Regular.ttf")
        candidates.append("/system/fonts/NotoSansArabic-Regular.ttf")

    for path in candidates:
        if os.path.exists(path):
            try:
                LabelBase.register(name=RTL_FONT_NAME, fn_regular=path)
                RTL_FONT_LOADED = True
                return True
            except Exception:
                continue
    return False


TRANSLATIONS = {
    "en": {
        "app_title": "MOON Fitness",
        "app_subtitle": "Your Elegant Fitness Companion",
        "app_slogan": "Glow. Move. Transform.",
        "welcome": "Welcome to MOON",
        "skip": "Skip",
        "next": "Next",
        "get_started": "Get Started",
        "save": "Save",
        "done": "Done",
        "ok": "OK",
        "yes": "Yes",
        "no": "No",
        "back": "Back",
        "cancel": "Cancel",
        "confirm": "Confirm",
        "close": "Close",
        "home": "Home",
        "plans": "Plans",
        "progress": "Progress",
        "settings": "Settings",
        "about": "About",
        "reminders": "Reminders",
        "profile_setup": "Profile Setup",
        "save_profile": "Save Profile",
        "edit_profile": "Edit Profile",
        "name": "Name",
        "age": "Age",
        "height": "Height (cm)",
        "weight": "Weight (kg)",
        "goal": "Goal",
        "activity_level": "Activity Level",
        "fitness_level": "Fitness Level",
        "training_days": "Training Days / Week",
        "preferred_workout": "Preferred Workout Style",
        "equipment": "Available Equipment",
        "limitations": "Injuries / Limitations",
        "preferred_time": "Preferred Workout Time",
        "note": "Note",
        "greeting": "Hello, {name} ✨",
        "active_plan": "Active Plan",
        "todays_workout": "Today's Workout",
        "quick_start": "Quick Start",
        "progress_log": "Log Progress",
        "completed_workouts": "Completed",
        "streak": "Streak",
        "total_minutes": "Minutes",
        "latest_progress": "Latest Progress",
        "quote_of_day": "Quote of the Day",
        "details": "Details",
        "activate": "Activate",
        "active": "✓ Active",
        "difficulty": "Difficulty",
        "weeks": "Weeks",
        "days_per_week": "Days/Week",
        "session_minutes": "Session",
        "goal_label": "Goal",
        "exercises": "Exercises",
        "exercise_list": "Exercise List",
        "start_workout": "Start Workout",
        "workout_session": "Workout Session",
        "current_exercise": "Current Exercise",
        "sets": "Sets",
        "reps": "Reps / Time",
        "rest": "Rest",
        "target_muscles": "Target Muscles",
        "previous": "Previous",
        "pause": "Pause",
        "resume": "Resume",
        "finish": "Finish",
        "theme": "Theme",
        "language": "Language",
        "light": "Light",
        "dark": "Dark",
        "vibration": "Vibration",
        "sound": "Sound",
        "reset_data": "Reset All Data",
        "version": "Version",
        "workout_reminder": "Workout Reminder",
        "hydration_reminder": "Hydration Reminder",
        "progress_reminder": "Progress Log Reminder",
        "time": "Time",
        "save_preferences": "Save Preferences",
        "onboarding_1_title": "Personalized Workouts",
        "onboarding_1_body": "Set your profile and let MOON suggest the best plan for your goals.",
        "onboarding_2_title": "Track Your Progress",
        "onboarding_2_body": "Log weight and body measurements, then watch your consistency grow.",
        "onboarding_3_title": "Stay Motivated",
        "onboarding_3_body": "Enjoy elegant design, daily quotes, and a calm premium fitness experience.",
        "onboarding_4_title": "Beautiful & Bilingual",
        "onboarding_4_body": "MOON speaks your language — switch between Persian and English anytime.",
        "field_required": "Please fill all required fields.",
        "invalid_number": "Please enter valid numeric values.",
        "profile_saved": "Profile saved successfully! ✨",
        "plan_activated": "Plan activated! 🌙",
        "progress_saved": "Progress saved! 📊",
        "reminders_saved": "Reminder settings saved.",
        "settings_saved": "Settings saved.",
        "theme_saved": "Theme updated.",
        "language_saved": "Language updated.",
        "workout_completed": "Workout completed! 🎉",
        "no_profile": "Please complete your profile first.",
        "no_active_plan": "No active plan yet. Choose a plan first.",
        "recommendation": "Recommended For You",
        "stats": "Your Stats",
        "start_now": "Start Now",
        "reset_warning": "This will remove profile, progress, sessions, and reminders. Seed plans will remain.",
        "reset_done": "App data reset completed.",
        "profile_hint_goal": "e.g. fat loss / tone / glutes / stronger",
        "profile_hint_activity": "e.g. low / medium / active",
        "profile_hint_fitness": "Beginner / Intermediate / Advanced",
        "profile_hint_workout": "e.g. home / lower body / full body / stretching",
        "profile_hint_equipment": "e.g. none / bands / dumbbells",
        "profile_hint_limitations": "e.g. knee pain / lower back sensitive",
        "profile_hint_time": "e.g. morning / evening / 18:00",
        "today_focus": "Today's Focus",
        "session_progress": "Session Progress",
        "completed": "Completed",
        "no_progress_yet": "No progress logs yet.",
        "save_first_log": "Save your first progress record! 📝",
        "about_text": "MOON is a beautiful offline fitness companion designed to help you train, stay consistent, and track your progress — all in a calm, premium, moonlit space.",
        "features_title": "Main Features",
        "feature_1": "🌙 Bilingual Persian / English support",
        "feature_2": "🏋️ Offline workout plans and daily training",
        "feature_3": "📊 Progress logs, streaks, reminders, and themes",
        "feature_4": "✨ Elegant premium UI inspired by moonlight",
        "feature_5": "🔔 Smart reminders and personalized plans",
        "beginner": "Beginner",
        "intermediate": "Intermediate",
        "advanced": "Advanced",
        "all_levels": "All Levels",
        "minutes_short": "min",
        "days_short": "days",
        "weight_unit": "kg",
        "cm_unit": "cm",
        "workout_day": "Workout Day",
        "selected_plan": "Selected Plan",
        "general_info": "General Information",
        "body_metrics": "Body Metrics",
        "save_log": "Save Log",
        "plan_overview": "Plan Overview",
        "target_areas": "Target Areas",
        "history": "History",
        "recommend_plan_btn": "Auto Recommend",
        "use_recommended": "Recommended plan activated! ✨",
        "profile_missing_for_recommend": "Complete profile to use recommendation.",
        "today_label": "Today",
        "rest_timer": "Rest Timer",
        "congratulations": "Congratulations! 🌟",
        "workout_done_msg": "You just finished your workout! Keep going, you're amazing.",
        "chart_title": "Progress Chart",
        "weight_chart": "Weight Trend",
        "no_chart_data": "Not enough data for chart. Keep logging!",
        "notify_workout_title": "MOON Workout Reminder",
        "notify_workout_msg": "Time to shine! Your workout is waiting. 🌙",
        "notify_hydration_title": "MOON Hydration Reminder",
        "notify_hydration_msg": "Stay hydrated! Drink some water. 💧",
        "made_with_love": "Made with 🤍 for you",
        "send_notification": "Send Test Notification",
        "notification_sent": "Notification sent!",
        "notification_unavailable": "Notifications unavailable on this device.",
        "vibrate_test": "Vibrate",
        "vibrated": "Vibrated!",
        "vibrate_unavailable": "Vibration unavailable.",
    },
    "fa": {
        "app_title": "MOON Fitness",
        "app_subtitle": "همراه ظریف تناسب اندام شما",
        "app_slogan": "بدرخش. حرکت کن. تغییر کن.",
        "welcome": "به MOON خوش آمدی",
        "skip": "رد کردن",
        "next": "بعدی",
        "get_started": "شروع",
        "save": "ذخیره",
        "done": "انجام شد",
        "ok": "باشه",
        "yes": "بله",
        "no": "خیر",
        "back": "بازگشت",
        "cancel": "لغو",
        "confirm": "تأیید",
        "close": "بستن",
        "home": "خانه",
        "plans": "برنامه‌ها",
        "progress": "پیشرفت",
        "settings": "تنظیمات",
        "about": "درباره",
        "reminders": "یادآورها",
        "profile_setup": "تنظیم پروفایل",
        "save_profile": "ذخیره پروفایل",
        "edit_profile": "ویرایش پروفایل",
        "name": "نام",
        "age": "سن",
        "height": "قد (سانتی‌متر)",
        "weight": "وزن (کیلوگرم)",
        "goal": "هدف",
        "activity_level": "سطح فعالیت",
        "fitness_level": "سطح آمادگی",
        "training_days": "روزهای تمرین در هفته",
        "preferred_workout": "نوع تمرین دلخواه",
        "equipment": "تجهیزات در دسترس",
        "limitations": "آسیب‌دیدگی / محدودیت بدنی",
        "preferred_time": "زمان دلخواه تمرین",
        "note": "یادداشت",
        "greeting": "سلام {name} ✨",
        "active_plan": "برنامه فعال",
        "todays_workout": "تمرین امروز",
        "quick_start": "شروع سریع",
        "progress_log": "ثبت پیشرفت",
        "completed_workouts": "تکمیل‌شده",
        "streak": "تداوم",
        "total_minutes": "دقیقه",
        "latest_progress": "آخرین پیشرفت",
        "quote_of_day": "نقل‌قول روز",
        "details": "جزئیات",
        "activate": "فعال‌سازی",
        "active": "✓ فعال",
        "difficulty": "سطح سختی",
        "weeks": "هفته",
        "days_per_week": "روز/هفته",
        "session_minutes": "مدت جلسه",
        "goal_label": "هدف",
        "exercises": "حرکت‌ها",
        "exercise_list": "فهرست حرکت‌ها",
        "start_workout": "شروع تمرین",
        "workout_session": "جلسه تمرین",
        "current_exercise": "حرکت فعلی",
        "sets": "ست",
        "reps": "تکرار / زمان",
        "rest": "استراحت",
        "target_muscles": "عضلات هدف",
        "previous": "قبلی",
        "pause": "توقف",
        "resume": "ادامه",
        "finish": "پایان",
        "theme": "تم",
        "language": "زبان",
        "light": "روشن",
        "dark": "تاریک",
        "vibration": "لرزش",
        "sound": "صدا",
        "reset_data": "ریست کامل داده‌ها",
        "version": "نسخه",
        "workout_reminder": "یادآور تمرین",
        "hydration_reminder": "یادآور آب",
        "progress_reminder": "یادآور ثبت پیشرفت",
        "time": "زمان",
        "save_preferences": "ذخیره تنظیمات",
        "onboarding_1_title": "تمرین‌های شخصی‌سازی‌شده",
        "onboarding_1_body": "پروفایلت را کامل کن تا MOON مناسب‌ترین برنامه را برای هدفت پیشنهاد دهد.",
        "onboarding_2_title": "پیگیری پیشرفت",
        "onboarding_2_body": "وزن و اندازه‌ها را ثبت کن و روند پیشرفت و استمرار خودت را ببین.",
        "onboarding_3_title": "باانگیزه بمان",
        "onboarding_3_body": "از طراحی ظریف، نقل‌قول‌های روزانه و تجربه‌ای آرام و حرفه‌ای لذت ببر.",
        "onboarding_4_title": "زیبا و دوزبانه",
        "onboarding_4_body": "MOON زبان تو را می‌فهمد — هر زمان بین فارسی و انگلیسی جابه‌جا شو.",
        "field_required": "لطفاً فیلدهای ضروری را کامل کن.",
        "invalid_number": "لطفاً مقادیر عددی معتبر وارد کن.",
        "profile_saved": "پروفایل با موفقیت ذخیره شد! ✨",
        "plan_activated": "برنامه فعال شد! 🌙",
        "progress_saved": "پیشرفت ذخیره شد! 📊",
        "reminders_saved": "تنظیمات یادآوری ذخیره شد.",
        "settings_saved": "تنظیمات ذخیره شد.",
        "theme_saved": "تم به‌روزرسانی شد.",
        "language_saved": "زبان به‌روزرسانی شد.",
        "workout_completed": "تمرین با موفقیت کامل شد! 🎉",
        "no_profile": "لطفاً ابتدا پروفایل را کامل کن.",
        "no_active_plan": "هنوز برنامه فعالی انتخاب نشده.",
        "recommendation": "پیشنهاد ویژه برای تو",
        "stats": "آمار تو",
        "start_now": "شروع کن",
        "reset_warning": "با این کار پروفایل، پیشرفت‌ها، جلسات و یادآورها حذف می‌شوند. برنامه‌های آماده باقی می‌مانند.",
        "reset_done": "ریست داده‌های برنامه انجام شد.",
        "profile_hint_goal": "مثال: چربی‌سوزی / فرم‌دهی / باسن / قوی‌تر شدن",
        "profile_hint_activity": "مثال: کم / متوسط / فعال",
        "profile_hint_fitness": "مبتدی / متوسط / پیشرفته",
        "profile_hint_workout": "مثال: خانگی / پایین‌تنه / فول‌بادی / کششی",
        "profile_hint_equipment": "مثال: بدون وسیله / کش / دمبل",
        "profile_hint_limitations": "مثال: درد زانو / کمر حساس",
        "profile_hint_time": "مثال: صبح / عصر / ۱۸:۰۰",
        "today_focus": "تمرکز امروز",
        "session_progress": "پیشرفت جلسه",
        "completed": "تکمیل‌شده",
        "no_progress_yet": "هنوز رکوردی ثبت نشده.",
        "save_first_log": "اولین رکورد پیشرفتت را ثبت کن! 📝",
        "about_text": "MOON یک همراه آفلاین و زیبا برای تناسب اندام است که کمک می‌کند تمرین کنی، استمرار داشته باشی و در فضایی آرام و لاکچری پیشرفتت را ثبت کنی.",
        "features_title": "ویژگی‌های اصلی",
        "feature_1": "🌙 پشتیبانی دو زبانه فارسی و انگلیسی",
        "feature_2": "🏋️ برنامه‌های تمرینی آفلاین و تمرین روزانه",
        "feature_3": "📊 ثبت پیشرفت، تداوم، یادآورها و تم‌ها",
        "feature_4": "✨ رابط ظاهری ظریف و الهام‌گرفته از ماه",
        "feature_5": "🔔 یادآورهای هوشمند و برنامه‌های شخصی‌سازی‌شده",
        "beginner": "مبتدی",
        "intermediate": "متوسط",
        "advanced": "پیشرفته",
        "all_levels": "همه سطوح",
        "minutes_short": "دقیقه",
        "days_short": "روز",
        "weight_unit": "کیلوگرم",
        "cm_unit": "سانتی‌متر",
        "workout_day": "روز تمرین",
        "selected_plan": "برنامه انتخاب‌شده",
        "general_info": "اطلاعات عمومی",
        "body_metrics": "شاخص‌های بدنی",
        "save_log": "ذخیره رکورد",
        "plan_overview": "نمای کلی برنامه",
        "target_areas": "ناحیه‌های هدف",
        "history": "تاریخچه",
        "recommend_plan_btn": "پیشنهاد خودکار",
        "use_recommended": "برنامه پیشنهادی فعال شد! ✨",
        "profile_missing_for_recommend": "برای پیشنهاد خودکار، ابتدا پروفایل را کامل کن.",
        "today_label": "امروز",
        "rest_timer": "تایمر استراحت",
        "congratulations": "تبریک! 🌟",
        "workout_done_msg": "تمرینت تمام شد! ادامه بده، عالی هستی.",
        "chart_title": "نمودار پیشرفت",
        "weight_chart": "روند وزن",
        "no_chart_data": "داده‌ی کافی برای نمودار نیست. به ثبت پیشرفت ادامه بده!",
        "notify_workout_title": "یادآور تمرین MOON",
        "notify_workout_msg": "وقت درخشیدنه! تمرینت منتظرته. 🌙",
        "notify_hydration_title": "یادآور آب MOON",
        "notify_hydration_msg": "آب بنوش! سلامتیت مهمه. 💧",
        "made_with_love": "با 🤍 برای تو ساخته شده",
        "send_notification": "ارسال نوتیفیکیشن تست",
        "notification_sent": "نوتیفیکیشن ارسال شد!",
        "notification_unavailable": "نوتیفیکیشن روی این دستگاه در دسترس نیست.",
        "vibrate_test": "ویبره",
        "vibrated": "ویبره شد!",
        "vibrate_unavailable": "ویبره در دسترس نیست.",
    },
}


EXERCISES = {
    "march_in_place": {
        "name_en": "March in Place", "name_fa": "راه رفتن درجا",
        "desc_en": "A gentle warm-up movement to raise body temperature and prepare for training.",
        "desc_fa": "یک حرکت گرم‌کردنی ملایم برای بالا بردن دمای بدن و آماده شدن برای تمرین.",
        "muscles_en": "Full body, cardio", "muscles_fa": "کل بدن، هوازی",
        "category": "warmup", "difficulty": "Beginner",
    },
    "jumping_jacks": {
        "name_en": "Jumping Jacks", "name_fa": "جامپینگ جک",
        "desc_en": "A classic cardio move that boosts heart rate and activates the whole body.",
        "desc_fa": "یک حرکت هوازی کلاسیک که ضربان قلب را بالا می‌برد و کل بدن را فعال می‌کند.",
        "muscles_en": "Full body, cardio", "muscles_fa": "کل بدن، هوازی",
        "category": "cardio", "difficulty": "Beginner",
    },
    "bodyweight_squat": {
        "name_en": "Bodyweight Squat", "name_fa": "اسکوات بدون وزنه",
        "desc_en": "Lower your hips back and down, then stand strong through your heels.",
        "desc_fa": "باسن را به عقب و پایین ببر و با فشار پاشنه‌ها دوباره بالا بیا.",
        "muscles_en": "Quads, glutes", "muscles_fa": "چهارسر، باسن",
        "category": "lower body", "difficulty": "Beginner",
    },
    "reverse_lunge": {
        "name_en": "Reverse Lunge", "name_fa": "لانج معکوس",
        "desc_en": "Step one leg back and bend both knees with control before returning up.",
        "desc_fa": "یک پا را به عقب ببر و هر دو زانو را کنترل‌شده خم کن، سپس بالا برگرد.",
        "muscles_en": "Glutes, quads, balance", "muscles_fa": "باسن، چهارسر، تعادل",
        "category": "lower body", "difficulty": "Intermediate",
    },
    "glute_bridge": {
        "name_en": "Glute Bridge", "name_fa": "پل باسن",
        "desc_en": "Drive hips upward while squeezing the glutes at the top.",
        "desc_fa": "باسن را به سمت بالا ببر و در بالا عضلات باسن را منقبض کن.",
        "muscles_en": "Glutes, hamstrings", "muscles_fa": "باسن، همسترینگ",
        "category": "glutes", "difficulty": "Beginner",
    },
    "wall_sit": {
        "name_en": "Wall Sit", "name_fa": "وال سیت",
        "desc_en": "Sit against a wall with thighs engaged and core tight.",
        "desc_fa": "به دیوار تکیه بده و در حالت نشسته با درگیری ران و میان‌تنه بمان.",
        "muscles_en": "Quads, glutes, core", "muscles_fa": "چهارسر، باسن، میان‌تنه",
        "category": "lower body", "difficulty": "Beginner",
    },
    "high_knees": {
        "name_en": "High Knees", "name_fa": "زانو بلند",
        "desc_en": "Lift knees quickly with light feet to raise cardio intensity.",
        "desc_fa": "زانوها را سریع بالا بیاور تا شدت هوازی بیشتر شود.",
        "muscles_en": "Cardio, core, legs", "muscles_fa": "هوازی، میان‌تنه، پاها",
        "category": "cardio", "difficulty": "Intermediate",
    },
    "knee_push_up": {
        "name_en": "Knee Push-Up", "name_fa": "شنا روی زانو",
        "desc_en": "A modified push-up that builds upper body strength with control.",
        "desc_fa": "نسخه ساده‌تر شنا برای تقویت کنترل‌شده بالاتنه.",
        "muscles_en": "Chest, shoulders, triceps", "muscles_fa": "سینه، سرشانه، پشت بازو",
        "category": "upper body", "difficulty": "Beginner",
    },
    "push_up": {
        "name_en": "Push-Up", "name_fa": "شنا",
        "desc_en": "Lower chest toward the floor and push back while keeping the body aligned.",
        "desc_fa": "سینه را به زمین نزدیک کن و با حفظ راستای بدن دوباره بالا برو.",
        "muscles_en": "Chest, shoulders, triceps, core", "muscles_fa": "سینه، سرشانه، پشت بازو، میان‌تنه",
        "category": "upper body", "difficulty": "Intermediate",
    },
    "plank": {
        "name_en": "Plank", "name_fa": "پلنک",
        "desc_en": "Hold a straight-body position while bracing the core deeply.",
        "desc_fa": "بدن را صاف نگه دار و میان‌تنه را عمیق درگیر کن.",
        "muscles_en": "Core, shoulders", "muscles_fa": "شکم، سرشانه",
        "category": "core", "difficulty": "Beginner",
    },
    "mountain_climber": {
        "name_en": "Mountain Climber", "name_fa": "مانتین کلایمر",
        "desc_en": "Drive alternating knees forward in a plank position at a steady pace.",
        "desc_fa": "در حالت پلنک، زانوها را یکی‌درمیان با ریتم مناسب به جلو بیاور.",
        "muscles_en": "Core, cardio, shoulders", "muscles_fa": "شکم، هوازی، سرشانه",
        "category": "cardio", "difficulty": "Intermediate",
    },
    "bird_dog": {
        "name_en": "Bird Dog", "name_fa": "برد داگ",
        "desc_en": "Extend opposite arm and leg while keeping hips and spine stable.",
        "desc_fa": "دست و پای مخالف را دراز کن و لگن و ستون فقرات را ثابت نگه دار.",
        "muscles_en": "Core, lower back, balance", "muscles_fa": "میان‌تنه، کمر، تعادل",
        "category": "core", "difficulty": "Beginner",
    },
    "donkey_kick": {
        "name_en": "Donkey Kick", "name_fa": "دانکی کیک",
        "desc_en": "Press the heel upward from all-fours to target the glutes.",
        "desc_fa": "در حالت چهار دست‌وپا پاشنه را به سمت بالا فشار بده تا باسن درگیر شود.",
        "muscles_en": "Glutes", "muscles_fa": "باسن",
        "category": "glutes", "difficulty": "Beginner",
    },
    "side_leg_raise": {
        "name_en": "Side Leg Raise", "name_fa": "بالا بردن پا از بغل",
        "desc_en": "Lift the top leg out to the side with slow, controlled motion.",
        "desc_fa": "پا را با کنترل و آرامش از پهلو بالا ببر.",
        "muscles_en": "Glutes, outer thighs", "muscles_fa": "باسن، کناره ران",
        "category": "glutes", "difficulty": "Beginner",
    },
    "crunch": {
        "name_en": "Crunch", "name_fa": "کرانچ",
        "desc_en": "Lift shoulders slightly while contracting the abdominal muscles.",
        "desc_fa": "شانه‌ها را کمی بالا بیاور و عضلات شکم را منقبض کن.",
        "muscles_en": "Abs", "muscles_fa": "شکم",
        "category": "core", "difficulty": "Beginner",
    },
    "russian_twist": {
        "name_en": "Russian Twist", "name_fa": "روشن توئیست",
        "desc_en": "Rotate the torso side to side while keeping the core engaged.",
        "desc_fa": "بالاتنه را به طرفین بچرخان و میان‌تنه را درگیر نگه دار.",
        "muscles_en": "Obliques, core", "muscles_fa": "پهلو، میان‌تنه",
        "category": "core", "difficulty": "Intermediate",
    },
    "dead_bug": {
        "name_en": "Dead Bug", "name_fa": "ددباگ",
        "desc_en": "Move opposite arm and leg slowly while maintaining core stability.",
        "desc_fa": "دست و پای مخالف را آرام حرکت بده و ثبات میان‌تنه را حفظ کن.",
        "muscles_en": "Core, coordination", "muscles_fa": "میان‌تنه، هماهنگی",
        "category": "core", "difficulty": "Beginner",
    },
    "superman": {
        "name_en": "Superman", "name_fa": "سوپرمن",
        "desc_en": "Lift arms and legs gently off the floor to strengthen the back line.",
        "desc_fa": "دست‌ها و پاها را آرام از زمین جدا کن تا پشت بدن تقویت شود.",
        "muscles_en": "Lower back, glutes", "muscles_fa": "کمر، باسن",
        "category": "recovery", "difficulty": "Beginner",
    },
    "inchworm": {
        "name_en": "Inchworm", "name_fa": "ایچ‌ورم",
        "desc_en": "Walk hands forward to plank and back up for mobility and core work.",
        "desc_fa": "دست‌ها را تا پلنک جلو ببر و برگرد تا تحرک و میان‌تنه فعال شوند.",
        "muscles_en": "Core, shoulders, hamstrings", "muscles_fa": "میان‌تنه، سرشانه، همسترینگ",
        "category": "full body", "difficulty": "Intermediate",
    },
    "calf_raise": {
        "name_en": "Calf Raise", "name_fa": "ساق پا",
        "desc_en": "Lift heels slowly to activate the calves and ankle control.",
        "desc_fa": "پاشنه‌ها را آرام بالا بیاور تا عضلات ساق و کنترل مچ فعال شوند.",
        "muscles_en": "Calves", "muscles_fa": "ساق پا",
        "category": "lower body", "difficulty": "Beginner",
    },
    "step_touch": {
        "name_en": "Step Touch", "name_fa": "استپ تاچ",
        "desc_en": "Step side to side with a light rhythm for low-impact cardio.",
        "desc_fa": "با ریتمی سبک به طرفین قدم بردار تا هوازی کم‌فشار انجام شود.",
        "muscles_en": "Cardio, legs", "muscles_fa": "هوازی، پاها",
        "category": "cardio", "difficulty": "Beginner",
    },
}


WORKOUT_PLANS = [
    {
        "key": "beginner_home",
        "name_en": "Beginner Home Plan", "name_fa": "برنامه خانگی مبتدی",
        "description_en": "A soft and confidence-building plan to create consistency and basic fitness at home.",
        "description_fa": "یک برنامه ملایم و اعتمادساز برای ایجاد عادت تمرین و آمادگی پایه در خانه.",
        "difficulty": "Beginner", "weeks": 4, "days_per_week": 3, "session_minutes": 25,
        "goal_en": "Consistency and basic strength", "goal_fa": "ایجاد استمرار و قدرت پایه",
        "target_en": "Full body, core, mobility", "target_fa": "کل بدن، میان‌تنه، تحرک",
        "days": [
            {"title_en": "Day 1 — Gentle Full Body", "title_fa": "روز ۱ — فول بادی ملایم",
             "exercises": [
                {"key": "march_in_place", "sets": "2", "reps": "60 sec", "rest": "20 sec"},
                {"key": "bodyweight_squat", "sets": "3", "reps": "12", "rest": "30 sec"},
                {"key": "knee_push_up", "sets": "3", "reps": "10", "rest": "30 sec"},
                {"key": "glute_bridge", "sets": "3", "reps": "15", "rest": "30 sec"},
                {"key": "plank", "sets": "3", "reps": "25 sec", "rest": "30 sec"},
             ]},
            {"title_en": "Day 2 — Core & Stability", "title_fa": "روز ۲ — شکم و ثبات",
             "exercises": [
                {"key": "step_touch", "sets": "2", "reps": "60 sec", "rest": "20 sec"},
                {"key": "bird_dog", "sets": "3", "reps": "10/side", "rest": "25 sec"},
                {"key": "dead_bug", "sets": "3", "reps": "10/side", "rest": "25 sec"},
                {"key": "crunch", "sets": "3", "reps": "15", "rest": "25 sec"},
                {"key": "superman", "sets": "3", "reps": "12", "rest": "25 sec"},
             ]},
            {"title_en": "Day 3 — Lower Body Basics", "title_fa": "روز ۳ — پایه پایین‌تنه",
             "exercises": [
                {"key": "march_in_place", "sets": "2", "reps": "45 sec", "rest": "20 sec"},
                {"key": "reverse_lunge", "sets": "3", "reps": "10/side", "rest": "30 sec"},
                {"key": "wall_sit", "sets": "3", "reps": "30 sec", "rest": "30 sec"},
                {"key": "calf_raise", "sets": "3", "reps": "20", "rest": "20 sec"},
                {"key": "glute_bridge", "sets": "3", "reps": "15", "rest": "25 sec"},
             ]},
        ],
    },
    {
        "key": "fat_burn_tone",
        "name_en": "Fat Burn & Tone Plan", "name_fa": "برنامه چربی‌سوزی و فرم‌دهی",
        "description_en": "A more energetic plan designed to boost calorie burn and shape the body with home-friendly movements.",
        "description_fa": "یک برنامه پرانرژی‌تر برای افزایش چربی‌سوزی و فرم‌دهی بدن با حرکات مناسب خانه.",
        "difficulty": "Intermediate", "weeks": 6, "days_per_week": 4, "session_minutes": 30,
        "goal_en": "Fat loss and toning", "goal_fa": "چربی‌سوزی و فرم‌دهی",
        "target_en": "Cardio, lower body, core", "target_fa": "هوازی، پایین‌تنه، شکم",
        "days": [
            {"title_en": "Day 1 — Cardio Burn", "title_fa": "روز ۱ — هوازی چربی‌سوز",
             "exercises": [
                {"key": "jumping_jacks", "sets": "3", "reps": "40 sec", "rest": "20 sec"},
                {"key": "high_knees", "sets": "3", "reps": "30 sec", "rest": "25 sec"},
                {"key": "mountain_climber", "sets": "3", "reps": "30 sec", "rest": "30 sec"},
                {"key": "bodyweight_squat", "sets": "3", "reps": "15", "rest": "25 sec"},
                {"key": "plank", "sets": "3", "reps": "30 sec", "rest": "30 sec"},
             ]},
            {"title_en": "Day 2 — Tone Lower Body", "title_fa": "روز ۲ — فرم‌دهی پایین‌تنه",
             "exercises": [
                {"key": "reverse_lunge", "sets": "3", "reps": "12/side", "rest": "30 sec"},
                {"key": "glute_bridge", "sets": "4", "reps": "18", "rest": "25 sec"},
                {"key": "wall_sit", "sets": "3", "reps": "40 sec", "rest": "30 sec"},
                {"key": "side_leg_raise", "sets": "3", "reps": "15/side", "rest": "20 sec"},
                {"key": "calf_raise", "sets": "3", "reps": "20", "rest": "20 sec"},
             ]},
            {"title_en": "Day 3 — Core Tone", "title_fa": "روز ۳ — فرم‌دهی شکم",
             "exercises": [
                {"key": "dead_bug", "sets": "3", "reps": "12/side", "rest": "25 sec"},
                {"key": "crunch", "sets": "3", "reps": "18", "rest": "25 sec"},
                {"key": "russian_twist", "sets": "3", "reps": "20", "rest": "25 sec"},
                {"key": "plank", "sets": "3", "reps": "35 sec", "rest": "30 sec"},
                {"key": "superman", "sets": "3", "reps": "15", "rest": "25 sec"},
             ]},
            {"title_en": "Day 4 — Full Body Sweep", "title_fa": "روز ۴ — فول بادی کامل",
             "exercises": [
                {"key": "inchworm", "sets": "3", "reps": "8", "rest": "30 sec"},
                {"key": "jumping_jacks", "sets": "3", "reps": "45 sec", "rest": "20 sec"},
                {"key": "knee_push_up", "sets": "3", "reps": "12", "rest": "30 sec"},
                {"key": "bodyweight_squat", "sets": "3", "reps": "15", "rest": "25 sec"},
                {"key": "mountain_climber", "sets": "3", "reps": "30 sec", "rest": "25 sec"},
             ]},
        ],
    },
    {
        "key": "glutes_core",
        "name_en": "Glutes & Core Plan", "name_fa": "برنامه باسن و میان‌تنه",
        "description_en": "A shape-focused plan built to target glutes, waistline, and core control.",
        "description_fa": "برنامه‌ای هدفمند برای تقویت و فرم‌دهی باسن، کمر و میان‌تنه.",
        "difficulty": "Intermediate", "weeks": 5, "days_per_week": 4, "session_minutes": 28,
        "goal_en": "Glute shape and stronger core", "goal_fa": "فرم‌دهی باسن و تقویت میان‌تنه",
        "target_en": "Glutes, abs, obliques", "target_fa": "باسن، شکم، پهلو",
        "days": [
            {"title_en": "Day 1 — Glute Activation", "title_fa": "روز ۱ — فعال‌سازی باسن",
             "exercises": [
                {"key": "glute_bridge", "sets": "4", "reps": "20", "rest": "25 sec"},
                {"key": "donkey_kick", "sets": "3", "reps": "15/side", "rest": "20 sec"},
                {"key": "side_leg_raise", "sets": "3", "reps": "15/side", "rest": "20 sec"},
                {"key": "wall_sit", "sets": "3", "reps": "35 sec", "rest": "30 sec"},
                {"key": "calf_raise", "sets": "3", "reps": "20", "rest": "20 sec"},
             ]},
            {"title_en": "Day 2 — Core Control", "title_fa": "روز ۲ — کنترل میان‌تنه",
             "exercises": [
                {"key": "plank", "sets": "4", "reps": "30 sec", "rest": "30 sec"},
                {"key": "dead_bug", "sets": "3", "reps": "12/side", "rest": "25 sec"},
                {"key": "crunch", "sets": "3", "reps": "18", "rest": "25 sec"},
                {"key": "russian_twist", "sets": "3", "reps": "20", "rest": "25 sec"},
                {"key": "bird_dog", "sets": "3", "reps": "12/side", "rest": "25 sec"},
             ]},
            {"title_en": "Day 3 — Lower Sculpt", "title_fa": "روز ۳ — فرم‌دهی پایین‌تنه",
             "exercises": [
                {"key": "bodyweight_squat", "sets": "4", "reps": "15", "rest": "25 sec"},
                {"key": "reverse_lunge", "sets": "3", "reps": "12/side", "rest": "30 sec"},
                {"key": "glute_bridge", "sets": "3", "reps": "18", "rest": "25 sec"},
                {"key": "donkey_kick", "sets": "3", "reps": "15/side", "rest": "20 sec"},
                {"key": "side_leg_raise", "sets": "3", "reps": "15/side", "rest": "20 sec"},
             ]},
            {"title_en": "Day 4 — Waist & Flow", "title_fa": "روز ۴ — کمر و جریان حرکتی",
             "exercises": [
                {"key": "step_touch", "sets": "2", "reps": "60 sec", "rest": "20 sec"},
                {"key": "russian_twist", "sets": "3", "reps": "22", "rest": "25 sec"},
                {"key": "plank", "sets": "3", "reps": "35 sec", "rest": "30 sec"},
                {"key": "superman", "sets": "3", "reps": "15", "rest": "25 sec"},
                {"key": "dead_bug", "sets": "3", "reps": "12/side", "rest": "25 sec"},
             ]},
        ],
    },
    {
        "key": "full_body_fit",
        "name_en": "Full Body Fit Plan", "name_fa": "برنامه فول بادی فیت",
        "description_en": "A balanced and stylish plan for total-body fitness, stamina, and strength.",
        "description_fa": "یک برنامه متعادل و حرفه‌ای برای آمادگی کلی بدن، استقامت و قدرت.",
        "difficulty": "All Levels", "weeks": 6, "days_per_week": 4, "session_minutes": 32,
        "goal_en": "Balanced full-body fitness", "goal_fa": "آمادگی متعادل کل بدن",
        "target_en": "Full body, stamina, strength", "target_fa": "کل بدن، استقامت، قدرت",
        "days": [
            {"title_en": "Day 1 — Full Body Flow", "title_fa": "روز ۱ — جریان فول بادی",
             "exercises": [
                {"key": "jumping_jacks", "sets": "3", "reps": "35 sec", "rest": "20 sec"},
                {"key": "bodyweight_squat", "sets": "3", "reps": "15", "rest": "25 sec"},
                {"key": "knee_push_up", "sets": "3", "reps": "12", "rest": "30 sec"},
                {"key": "plank", "sets": "3", "reps": "30 sec", "rest": "30 sec"},
                {"key": "glute_bridge", "sets": "3", "reps": "18", "rest": "25 sec"},
             ]},
            {"title_en": "Day 2 — Cardio & Core", "title_fa": "روز ۲ — هوازی و شکم",
             "exercises": [
                {"key": "high_knees", "sets": "3", "reps": "30 sec", "rest": "20 sec"},
                {"key": "mountain_climber", "sets": "3", "reps": "30 sec", "rest": "25 sec"},
                {"key": "crunch", "sets": "3", "reps": "18", "rest": "25 sec"},
                {"key": "russian_twist", "sets": "3", "reps": "20", "rest": "25 sec"},
                {"key": "dead_bug", "sets": "3", "reps": "12/side", "rest": "25 sec"},
             ]},
            {"title_en": "Day 3 — Strength Balance", "title_fa": "روز ۳ — تعادل قدرت",
             "exercises": [
                {"key": "inchworm", "sets": "3", "reps": "8", "rest": "30 sec"},
                {"key": "push_up", "sets": "3", "reps": "8", "rest": "35 sec"},
                {"key": "reverse_lunge", "sets": "3", "reps": "12/side", "rest": "30 sec"},
                {"key": "bird_dog", "sets": "3", "reps": "10/side", "rest": "25 sec"},
                {"key": "superman", "sets": "3", "reps": "15", "rest": "25 sec"},
             ]},
            {"title_en": "Day 4 — Fit Finish", "title_fa": "روز ۴ — پایان قدرتمند",
             "exercises": [
                {"key": "step_touch", "sets": "2", "reps": "60 sec", "rest": "20 sec"},
                {"key": "jumping_jacks", "sets": "3", "reps": "40 sec", "rest": "20 sec"},
                {"key": "bodyweight_squat", "sets": "3", "reps": "15", "rest": "25 sec"},
                {"key": "glute_bridge", "sets": "3", "reps": "18", "rest": "25 sec"},
                {"key": "plank", "sets": "3", "reps": "35 sec", "rest": "30 sec"},
             ]},
        ],
    },
]


QUOTES = [
    {"en": "Glow gently. Grow steadily.", "fa": "آرام بدرخش، پیوسته رشد کن."},
    {"en": "Consistency is a quiet kind of power.", "fa": "استمرار، نوعی قدرت آرام است."},
    {"en": "Every small session shapes a stronger you.", "fa": "هر جلسه کوچک، نسخه قوی‌تری از تو می‌سازد."},
    {"en": "Move with grace. Progress with purpose.", "fa": "با ظرافت حرکت کن، با هدف پیشرفت کن."},
    {"en": "Your body listens to what you repeat.", "fa": "بدنت به چیزهایی پاسخ می‌دهد که تکرار می‌کنی."},
    {"en": "Strong can be soft and beautiful too.", "fa": "قدرت می‌تواند نرم و زیبا هم باشد."},
    {"en": "One workout at a time, one brighter day at a time.", "fa": "هر بار یک تمرین، هر بار یک روز روشن‌تر."},
    {"en": "Grace, discipline, and tiny steps change everything.", "fa": "ظرافت، نظم و قدم‌های کوچک همه‌چیز را تغییر می‌دهند."},
    {"en": "Be patient with your body. It's learning.", "fa": "با بدنت صبور باش. در حال یادگیری است."},
    {"en": "The moon doesn't rush to be full. Neither should you.", "fa": "ماه عجله نمی‌کند تا کامل شود. تو هم نباید."},
]


class AppDB:
    def __init__(self):
        self.db_path = get_db_path()
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()
        self.seed_data()

    def execute(self, query, params=()):
        cur = self.conn.cursor()
        cur.execute(query, params)
        self.conn.commit()
        return cur

    def fetchone(self, query, params=()):
        cur = self.conn.cursor()
        cur.execute(query, params)
        return cur.fetchone()

    def fetchall(self, query, params=()):
        cur = self.conn.cursor()
        cur.execute(query, params)
        return cur.fetchall()

    def create_tables(self):
        self.execute("""CREATE TABLE IF NOT EXISTS app_settings (
            key TEXT PRIMARY KEY, value TEXT)""")
        self.execute("""CREATE TABLE IF NOT EXISTS user_profile (
            id INTEGER PRIMARY KEY CHECK(id = 1),
            name TEXT, age INTEGER, height REAL, weight REAL,
            goal TEXT, activity_level TEXT, fitness_level TEXT,
            training_days INTEGER, preferred_workout TEXT,
            equipment TEXT, limitations TEXT,
            preferred_time TEXT, note TEXT)""")
        self.execute("""CREATE TABLE IF NOT EXISTS workout_plans (
            plan_key TEXT PRIMARY KEY,
            name_en TEXT, name_fa TEXT,
            description_en TEXT, description_fa TEXT,
            difficulty TEXT, weeks INTEGER,
            days_per_week INTEGER, session_minutes INTEGER,
            goal_en TEXT, goal_fa TEXT,
            target_en TEXT, target_fa TEXT,
            data_json TEXT)""")
        self.execute("""CREATE TABLE IF NOT EXISTS workout_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_date TEXT, plan_key TEXT,
            day_title TEXT, duration_minutes INTEGER,
            completed INTEGER)""")
        self.execute("""CREATE TABLE IF NOT EXISTS progress_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            log_date TEXT, weight REAL, waist REAL,
            hips REAL, arm REAL, chest REAL, note TEXT)""")
        self.execute("""CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY CHECK(id = 1),
            workout_enabled INTEGER, workout_time TEXT,
            hydration_enabled INTEGER, hydration_time TEXT,
            progress_enabled INTEGER, progress_time TEXT)""")
        self.execute("""CREATE TABLE IF NOT EXISTS motivational_quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quote_en TEXT, quote_fa TEXT)""")

    def seed_data(self):
        defaults = {
            "language": "en", "theme_style": "Dark",
            "active_plan_key": "", "onboarding_completed": "0",
            "vibration": "1", "sound": "1",
        }
        for key, value in defaults.items():
            if self.get_setting(key) is None:
                self.set_setting(key, value)

        if not self.fetchone("SELECT id FROM reminders WHERE id = 1"):
            self.execute("""INSERT INTO reminders (
                id, workout_enabled, workout_time,
                hydration_enabled, hydration_time,
                progress_enabled, progress_time
                ) VALUES (1, 1, '18:00', 0, '12:00', 0, '20:00')""")

        count = self.fetchone("SELECT COUNT(*) AS c FROM workout_plans")["c"]
        if count == 0:
            for plan in WORKOUT_PLANS:
                self.execute("""INSERT INTO workout_plans (
                    plan_key, name_en, name_fa, description_en, description_fa,
                    difficulty, weeks, days_per_week, session_minutes,
                    goal_en, goal_fa, target_en, target_fa, data_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (
                    plan["key"], plan["name_en"], plan["name_fa"],
                    plan["description_en"], plan["description_fa"],
                    plan["difficulty"], plan["weeks"], plan["days_per_week"],
                    plan["session_minutes"], plan["goal_en"], plan["goal_fa"],
                    plan["target_en"], plan["target_fa"],
                    json.dumps(plan["days"], ensure_ascii=False),
                ))

        qcount = self.fetchone("SELECT COUNT(*) AS c FROM motivational_quotes")["c"]
        if qcount == 0:
            for q in QUOTES:
                self.execute("INSERT INTO motivational_quotes (quote_en, quote_fa) VALUES (?, ?)",
                             (q["en"], q["fa"]))

    def get_setting(self, key, default=None):
        row = self.fetchone("SELECT value FROM app_settings WHERE key = ?", (key,))
        return row["value"] if row else default

    def set_setting(self, key, value):
        self.execute("""INSERT INTO app_settings (key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value""", (key, str(value)))

    def save_profile(self, d):
        self.execute("""INSERT INTO user_profile (
            id, name, age, height, weight, goal, activity_level,
            fitness_level, training_days, preferred_workout,
            equipment, limitations, preferred_time, note
            ) VALUES (1,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(id) DO UPDATE SET
                name=excluded.name, age=excluded.age,
                height=excluded.height, weight=excluded.weight,
                goal=excluded.goal, activity_level=excluded.activity_level,
                fitness_level=excluded.fitness_level,
                training_days=excluded.training_days,
                preferred_workout=excluded.preferred_workout,
                equipment=excluded.equipment,
                limitations=excluded.limitations,
                preferred_time=excluded.preferred_time,
                note=excluded.note""",
            (d["name"], d["age"], d["height"], d["weight"],
             d["goal"], d["activity_level"], d["fitness_level"],
             d["training_days"], d["preferred_workout"],
             d["equipment"], d["limitations"],
             d["preferred_time"], d["note"]))

    def get_profile(self):
        row = self.fetchone("SELECT * FROM user_profile WHERE id = 1")
        return dict(row) if row else None

    def get_plans(self):
        rows = self.fetchall("SELECT * FROM workout_plans ORDER BY name_en")
        result = []
        for r in rows:
            item = dict(r)
            item["days"] = json.loads(item["data_json"])
            result.append(item)
        return result

    def get_plan(self, key):
        row = self.fetchone("SELECT * FROM workout_plans WHERE plan_key = ?", (key,))
        if not row:
            return None
        item = dict(row)
        item["days"] = json.loads(item["data_json"])
        return item

    def set_active_plan(self, key):
        self.set_setting("active_plan_key", key)

    def get_active_plan(self):
        key = self.get_setting("active_plan_key", "")
        return self.get_plan(key) if key 


class MoonGlowLabel(BoxLayout):
    def __init__(self, text="", font_size=sp(16), color=None,
                 bold=False, center=False, fa=False, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(40)
        self.padding = [dp(4), dp(2)]

        app = MDApp.get_running_app()
        is_dark = app.is_dark if app else True
        default_color = MoonColors.get("TEXT", is_dark)
        text_color = color or default_color

        rendered = rtl_text(text) if fa else text
        font = RTL_FONT_NAME if (fa and RTL_FONT_LOADED) else "Roboto"

        self.lbl = MDLabel(
            text=rendered, font_size=font_size,
            halign="center" if center else ("right" if fa else "left"),
            valign="middle",
            theme_text_color="Custom",
            text_color=text_color, bold=bold, font_name=font,
        )
        self.lbl.bind(
            width=lambda inst, val: setattr(inst, "text_size", (val, None)),
            texture_size=lambda inst, val: setattr(inst, "height", val[1] + dp(6)),
        )
        self.add_widget(self.lbl)

    def set_text(self, text, fa=False):
        self.lbl.text = rtl_text(text) if fa else text


class MoonCard(MDCard):
    def __init__(self, dark=True, alt=False, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.radius = [dp(20), dp(20), dp(20), dp(20)]
        self.elevation = 3
        self.padding = [dp(18), dp(16), dp(18), dp(16)]
        self.spacing = dp(10)
        self.size_hint_y = None

        if alt:
            col = MoonColors.get("CARD_ALT", dark)
        else:
            col = MoonColors.get("CARD", dark)
        self.md_bg_color = col
        self.bind(minimum_height=self.setter("height"))


class MoonStatCard(BoxLayout):
    def __init__(self, title="", value="", icon="star",
                 dark=True, accent_color=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint_y = None
        self.height = dp(120)
        self.padding = [dp(10), dp(10)]
        self.spacing = dp(4)

        card = MDCard(
            orientation="vertical",
            radius=[dp(22), dp(22), dp(22), dp(22)],
            elevation=4,
            padding=[dp(12), dp(10)],
            spacing=dp(6),
            md_bg_color=MoonColors.get("CARD_ALT", dark),
            size_hint=(1, 1),
        )

        icon_color = accent_color or MoonColors.get("ACCENT", dark)
        icon_label = MDIcon(
            icon=icon, theme_text_color="Custom",
            text_color=icon_color, halign="center", font_size=sp(24),
        )
        value_label = MDLabel(
            text=str(value), halign="center",
            font_style="H6", bold=True,
            theme_text_color="Custom",
            text_color=MoonColors.get("TEXT", dark),
        )
        title_label = MDLabel(
            text=title, halign="center",
            font_style="Caption",
            theme_text_color="Custom",
            text_color=MoonColors.get("TEXT2", dark),
        )

        card.add_widget(icon_label)
        card.add_widget(value_label)
        card.add_widget(title_label)
        self.add_widget(card)


class MoonProgressChart(BoxLayout):
    def __init__(self, data=None, dark=True, lang="en", **kwargs):
        super().__init__(**kwargs)
        self.data = data or []
        self.dark = dark
        self.lang = lang
        self.size_hint_y = None
        self.height = dp(200)
        self.bind(pos=self._draw, size=self._draw)

    def _draw(self, *args):
        self.canvas.before.clear()
        if len(self.data) < 2:
            return

        values = [d["weight"] for d in self.data if d.get("weight") is not None]
        if len(values) < 2:
            return

        w = self.width
        h = self.height
        x0 = self.x
        y0 = self.y

        min_v = min(values)
        max_v = max(values)
        diff = max_v - min_v if max_v != min_v else 1.0

        pad_x = dp(24)
        pad_y = dp(24)
        chart_w = w - pad_x * 2
        chart_h = h - pad_y * 2

        accent = MoonColors.get("ACCENT", self.dark)
        accent2 = MoonColors.get("ACCENT2", self.dark)
        text2 = MoonColors.get("TEXT2", self.dark)
        divider = MoonColors.get("DIVIDER", self.dark)

        with self.canvas.before:
            Color(*MoonColors.get("CARD", self.dark))
            RoundedRectangle(pos=(x0, y0), size=(w, h), radius=[dp(20)])

            Color(*divider, 0.4)
            for i in range(4):
                gy = y0 + pad_y + (chart_h / 3) * i
                Line(points=[x0 + pad_x, gy, x0 + w - pad_x, gy], width=dp(0.5))

            n = len(values)
            pts = []
            for i, v in enumerate(values):
                px = x0 + pad_x + (i / (n - 1)) * chart_w
                py = y0 + pad_y + ((v - min_v) / diff) * chart_h
                pts.extend([px, py])

            Color(*accent)
            Line(points=pts, width=dp(2.2))

            for i, v in enumerate(values):
                px = x0 + pad_x + (i / (n - 1)) * chart_w
                py = y0 + pad_y + ((v - min_v) / diff) * chart_h
                Color(*accent2)
                Ellipse(pos=(px - dp(5), py - dp(5)), size=(dp(10), dp(10)))

            Color(*MoonColors.get("GOLD", self.dark))
            first_px = x0 + pad_x
            first_py = y0 + pad_y + ((values[0] - min_v) / diff) * chart_h
            last_px = x0 + pad_x + chart_w
            last_py = y0 + pad_y + ((values[-1] - min_v) / diff) * chart_h
            Ellipse(pos=(first_px - dp(7), first_py - dp(7)), size=(dp(14), dp(14)))
            Ellipse(pos=(last_px - dp(7), last_py - dp(7)), size=(dp(14), dp(14)))


class MoonButton(BoxLayout):
    def __init__(self, text="", on_press=None, flat=False,
                 dark=True, fa=False, icon=None, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(50)

        btn_color = (MoonColors.get("CARD_ALT", dark) if flat
                     else MoonColors.get("BUTTON", dark))
        text_color = (MoonColors.get("ACCENT", dark) if flat
                      else MoonColors.get("BUTTON_TEXT", dark))

        rendered = rtl_text(text) if fa else text
        font = RTL_FONT_NAME if (fa and RTL_FONT_LOADED) else "Roboto"

        if flat:
            btn = MDFlatButton(
                text=rendered, theme_text_color="Custom",
                text_color=text_color, font_name=font, size_hint=(1, 1),
            )
        else:
            btn = MDRaisedButton(
                text=rendered, md_bg_color=btn_color,
                theme_text_color="Custom", text_color=text_color,
                font_name=font, size_hint=(1, 1), elevation=3,
            )

        if on_press:
            btn.bind(on_release=on_press)
        self.add_widget(btn)
        self.btn = btn

    def update_text(self, text, fa=False):
        self.btn.text = rtl_text(text) if fa else text


class MoonTextField(MDTextField):
    def __init__(self, hint="", value="", fa=False, dark=True, **kwargs):
        super().__init__(**kwargs)
        font = RTL_FONT_NAME if (fa and RTL_FONT_LOADED) else "Roboto"
        self.hint_text = rtl_text(hint) if fa else hint
        self.text = "" if value is None else str(value)
        self.font_name = font
        self.mode = "rectangle"
        self.size_hint_y = None
        self.height = dp(56)
        self.size_hint_x = 1
        self.line_color_normal = MoonColors.get("INPUT_BORDER", dark)
        self.line_color_focus = MoonColors.get("ACCENT", dark)


class MoonDivider(Widget):
    def __init__(self, dark=True, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(1)
        with self.canvas:
            Color(*MoonColors.get("DIVIDER", dark))
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update, size=self._update)

    def _update(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class MoonHeader(BoxLayout):
    def __init__(self, title="", back_cb=None, dark=True, fa=False, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(64)
        self.padding = [dp(8), dp(8), dp(8), dp(8)]
        self.spacing = dp(4)

        with self.canvas.before:
            Color(*MoonColors.get("HEADER", dark))
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        if back_cb:
            icon_name = "arrow-right" if fa else "arrow-left"
            back_btn = MDIconButton(
                icon=icon_name, theme_text_color="Custom",
                text_color=MoonColors.get("ACCENT", dark),
            )
            back_btn.bind(on_release=back_cb)
            if fa:
                self.add_widget(Widget())
                self.add_widget(back_btn)
            else:
                self.add_widget(back_btn)
        else:
            self.add_widget(Widget(size_hint_x=None, width=dp(48)))

        font = RTL_FONT_NAME if (fa and RTL_FONT_LOADED) else "Roboto"
        rendered = rtl_text(title) if fa else title
        title_lbl = MDLabel(
            text=rendered, font_style="H6", halign="center",
            theme_text_color="Custom",
            text_color=MoonColors.get("TEXT", dark),
            bold=True, font_name=font,
        )
        self.add_widget(title_lbl)

        if back_cb and fa:
            self.add_widget(Widget(size_hint_x=None, width=dp(48)))
        else:
            self.add_widget(Widget(size_hint_x=None, width=dp(48)))

    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size


class MoonBottomNav(BoxLayout):
    def __init__(self, current="home", on_tab=None, dark=True, fa=False, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(68)
        self.padding = [dp(0), dp(0), dp(0), dp(0)]
        self.spacing = dp(0)
        self.on_tab_cb = on_tab
        self.current = current
        self.dark = dark
        self.fa = fa
        self.tab_widgets = {}

        with self.canvas.before:
            Color(*MoonColors.get("NAV", dark))
            self.bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._upd, size=self._upd)

        tabs = [
            ("home", "home-variant", "home", "خانه"),
            ("plans", "dumbbell", "plans", "برنامه‌ها"),
            ("progress", "chart-line", "progress", "پیشرفت"),
            ("settings", "cog", "settings", "تنظیمات"),
        ]

        for tab_name, icon, en_label, fa_label in tabs:
            label = fa_label if fa else en_label
            is_active = (current == tab_name)
            tab = self._make_tab(tab_name, icon, label, is_active)
            self.tab_widgets[tab_name] = tab
            self.add_widget(tab)

    def _upd(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size

    def _make_tab(self, name, icon, label, active):
        col = MoonColors.get("NAV_ACTIVE" if active else "NAV_INACTIVE", self.dark)
        font = RTL_FONT_NAME if (self.fa and RTL_FONT_LOADED) else "Roboto"
        rendered = rtl_text(label) if self.fa else label

        box = BoxLayout(orientation="vertical", spacing=dp(2),
                        padding=[dp(4), dp(6), dp(4), dp(6)])

        icon_btn = MDIconButton(
            icon=icon, theme_text_color="Custom",
            text_color=col, halign="center",
        )
        icon_btn.bind(on_release=lambda x, n=name: self._on_press(n))

        lbl = MDLabel(
            text=rendered, halign="center",
            font_size=sp(10), theme_text_color="Custom",
            text_color=col, font_name=font,
            size_hint_y=None, height=dp(16),
        )

        box.add_widget(icon_btn)
        box.add_widget(lbl)
        return box

    def _on_press(self, name):
        if self.on_tab_cb:
            self.on_tab_cb(name)

    def set_active(self, name):
        self.current = name
        tabs_info = [
            ("home", "home-variant", "home", "خانه"),
            ("plans", "dumbbell", "plans", "برنامه‌ها"),
            ("progress", "chart-line", "progress", "پیشرفت"),
            ("settings", "cog", "settings", "تنظیمات"),
        ]
        self.clear_widgets()
        self.tab_widgets = {}
        for tab_name, icon, en_label, fa_label in tabs_info:
            label = fa_label if self.fa else en_label
            is_active = (name == tab_name)
            tab = self._make_tab(tab_name, icon, label, is_active)
            self.tab_widgets[tab_name] = tab
            self.add_widget(tab)


class BaseScreen(MDScreen):
    def app(self):
        return MDApp.get_running_app()

    def is_fa(self):
        return self.app().language == "fa"

    def is_dark(self):
        return self.app().is_dark

    def t(self, key, **kwargs):
        return self.app().t(key, **kwargs)

    def render(self, text):
        return self.app().render(text)

    def show_msg(self, text):
        self.app().show_message(text)

    def vibrate(self, duration=0.05):
        try:
            if HAS_VIBRATOR and self.app().db.get_setting("vibration", "1") == "1":
                plyer_vibrator.vibrate(duration)
        except Exception:
            pass

    def send_notification(self, title, message):
        try:
            if HAS_NOTIFICATION:
                plyer_notification.notify(
                    title=title, message=message,
                    app_name="MOON Fitness", timeout=5,
                )
                return True
        except Exception:
            pass
        return False

    def lv(self, en, fa):
        return fa if self.is_fa() else en

    def make_scroll_body(self):
        sc = ScrollView(do_scroll_x=False)
        body = MDBoxLayout(
            orientation="vertical",
            padding=[dp(14), dp(10), dp(14), dp(20)],
            spacing=dp(14), size_hint_y=None,
        )
        body.bind(minimum_height=body.setter("height"))
        sc.add_widget(body)
        return sc, body

    def make_card(self, alt=False):
        return MoonCard(dark=self.is_dark(), alt=alt)

    def make_label(self, text, style="Body1", secondary=False,
                   center=False, bold=False, color=None):
        is_dark = self.is_dark()
        fa = self.is_fa()
        rendered = rtl_text(str(text)) if fa else str(text)
        font = RTL_FONT_NAME if (fa and RTL_FONT_LOADED) else "Roboto"

        if color:
            text_color = color
        elif secondary:
            text_color = MoonColors.get("TEXT2", is_dark)
        else:
            text_color = MoonColors.get("TEXT", is_dark)

        lbl = MDLabel(
            text=rendered, font_style=style,
            halign="center" if center else ("right" if fa else "left"),
            theme_text_color="Custom", text_color=text_color,
            bold=bold, font_name=font, size_hint_y=None,
        )
        lbl.bind(
            width=lambda inst, val: setattr(inst, "text_size", (val, None)),
            texture_size=lambda inst, val: setattr(inst, "height", val[1] + dp(8)),
        )
        return lbl

    def make_field(self, hint, value=""):
        return MoonTextField(
            hint=hint, value=value,
            fa=self.is_fa(), dark=self.is_dark()
        )

    def make_btn(self, text, cb, flat=False, icon=None):
        return MoonButton(
            text=text, on_press=cb, flat=flat,
            dark=self.is_dark(), fa=self.is_fa(), icon=icon
        )

    def make_divider(self):
        return MoonDivider(dark=self.is_dark())

    def make_header(self, title, back_to=None, back_cb=None):
        def _back(x):
            if back_cb:
                back_cb()
            elif back_to:
                self.app().go_to(back_to)
        cb = _back if (back_to or back_cb) else None
        return MoonHeader(
            title=title, back_cb=cb,
            dark=self.is_dark(), fa=self.is_fa()
        )

    def make_bottom_nav(self, current="home"):
        return MoonBottomNav(
            current=current,
            on_tab=self.app().go_to,
            dark=self.is_dark(), fa=self.is_fa(),
        )

    def scaffold(self, title, back_to=None, back_cb=None,
                 bottom_nav=None, scroll=True):
        self.clear_widgets()
        is_dark = self.is_dark()

        root = MDBoxLayout(orientation="vertical")
        with root.canvas.before:
            Color(*MoonColors.get("BG", is_dark))
            self._bg_rect = Rectangle(pos=root.pos, size=root.size)
        root.bind(
            pos=lambda inst, val: setattr(self._bg_rect, "pos", val),
            size=lambda inst, val: setattr(self._bg_rect, "size", val),
        )

        header = self.make_header(title, back_to=back_to, back_cb=back_cb)
        root.add_widget(header)
        root.add_widget(MoonDivider(dark=is_dark))

        if scroll:
            sc, body = self.make_scroll_body()
            root.add_widget(sc)
        else:
            body = MDBoxLayout(
                orientation="vertical",
                padding=[dp(14), dp(10), dp(14), dp(14)],
                spacing=dp(12),
            )
            root.add_widget(body)

        if bottom_nav:
            nav = self.make_bottom_nav(current=bottom_nav)
            root.add_widget(MoonDivider(dark=is_dark))
            root.add_widget(nav)

        self.add_widget(root)
        return body


class SplashScreen(BaseScreen):
    def on_enter(self, *args):
        self._build()
        Clock.schedule_once(self._decide, 1.8)

    def _build(self):
        self.clear_widgets()
        is_dark = self.is_dark()

        root = FloatLayout()
        with root.canvas.before:
            Color(*MoonColors.get("BG", is_dark))
            self._bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(
            pos=lambda i, v: setattr(self._bg, "pos", v),
            size=lambda i, v: setattr(self._bg, "size", v),
        )

        center_box = MDBoxLayout(
            orientation="vertical", spacing=dp(16),
            padding=[dp(40), dp(0)],
            size_hint=(1, None),
            pos_hint={"center_x": 0.5, "center_y": 0.52},
        )
        center_box.bind(minimum_height=center_box.setter("height"))

        moon_icon = MDLabel(
            text="◐", font_size=sp(90), halign="center",
            theme_text_color="Custom",
            text_color=MoonColors.get("ACCENT", is_dark),
            size_hint_y=None, height=dp(110),
        )

        title_lbl = MDLabel(
            text="MOON", font_style="H3", halign="center", bold=True,
            theme_text_color="Custom",
            text_color=MoonColors.get("TEXT", is_dark),
            size_hint_y=None, height=dp(56),
        )

        subtitle_lbl = MDLabel(
            text=self.t("app_subtitle"), font_style="Subtitle1", halign="center",
            theme_text_color="Custom",
            text_color=MoonColors.get("TEXT2", is_dark),
            size_hint_y=None, height=dp(36),
        )

        slogan_lbl = MDLabel(
            text=self.t("app_slogan"), font_style="Caption", halign="center",
            theme_text_color="Custom",
            text_color=MoonColors.get("ACCENT2", is_dark),
            size_hint_y=None, height=dp(28),
        )

        center_box.add_widget(moon_icon)
        center_box.add_widget(title_lbl)
        center_box.add_widget(subtitle_lbl)
        center_box.add_widget(slogan_lbl)

        root.add_widget(center_box)
        self.add_widget(root)

    def _decide(self, *args):
        app = self.app()
        try:
            onboarding = app.db.get_setting("onboarding_completed", "0") == "1"
            profile = app.db.get_profile()
            if not onboarding:
                app.go_to("onboarding")
            elif not profile:
                app.go_to("profile")
            else:
                app.ensure_recommended_plan()
                app.go_to("home")
        except Exception as e:
            print(f"[MOON] Splash error: {e}")
            app.go_to("onboarding")


class OnboardingScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.index = 0
        self.slides = [
            ("onboarding_1_title", "onboarding_1_body", "◐", "ACCENT"),
            ("onboarding_2_title", "onboarding_2_body", "📊", "ACCENT2"),
            ("onboarding_3_title", "onboarding_3_body", "✨", "GOLD"),
            ("onboarding_4_title", "onboarding_4_body", "🌙", "ACCENT"),
        ]

    def on_pre_enter(self, *args):
        self._build()

    def _build(self):
        self.clear_widgets()
        is_dark = self.is_dark()
        n = len(self.slides)
        title_key, body_key, icon_ch, color_key = self.slides[self.index]

        root = MDBoxLayout(orientation="vertical")
        with root.canvas.before:
            Color(*MoonColors.get("BG", is_dark))
            self._bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(
            pos=lambda i, v: setattr(self._bg, "pos", v),
            size=lambda i, v: setattr(self._bg, "size", v),
        )

        top_row = MDBoxLayout(size_hint_y=None, height=dp(52),
                              padding=[dp(8), dp(8)])
        top_row.add_widget(Widget())
        skip_btn = MDFlatButton(
            text=self.render(self.t("skip")),
            theme_text_color="Custom",
            text_color=MoonColors.get("TEXT2", is_dark),
        )
        skip_btn.bind(on_release=lambda x: self._finish())
        top_row.add_widget(skip_btn)
        root.add_widget(top_row)

        root.add_widget(Widget(size_hint_y=0.06))

        icon_lbl = MDLabel(
            text=icon_ch, font_size=sp(80), halign="center",
            size_hint_y=None, height=dp(100),
        )
        root.add_widget(icon_lbl)

        root.add_widget(Widget(size_hint_y=0.03))

        title_lbl = self.make_label(self.t(title_key), style="H5",
                                    center=True, bold=True,
                                    color=MoonColors.get(color_key, is_dark))
        root.add_widget(title_lbl)

        root.add_widget(Widget(size_hint_y=None, height=dp(14)))

        body_lbl = self.make_label(self.t(body_key), style="Body1",
                                   center=True, secondary=True)
        body_lbl.size_hint_x = 0.82
        body_lbl.pos_hint = {"center_x": 0.5}
        root.add_widget(body_lbl)

        root.add_widget(Widget())

        dot_row = MDBoxLayout(
            size_hint_y=None, height=dp(28),
            spacing=dp(8), padding=[0, dp(4)],
        )
        dot_row.add_widget(Widget())
        for i in range(n):
            ch = "●" if i == self.index else "○"
            col = (MoonColors.get("ACCENT", is_dark)
                   if i == self.index else MoonColors.get("TEXT2", is_dark))
            dot = MDLabel(
                text=ch, halign="center", font_size=sp(14),
                size_hint=(None, None), size=(dp(22), dp(22)),
                theme_text_color="Custom", text_color=col,
            )
            dot_row.add_widget(dot)
        dot_row.add_widget(Widget())
        root.add_widget(dot_row)

        root.add_widget(Widget(size_hint_y=None, height=dp(20)))

        btn_row = MDBoxLayout(
            size_hint_y=None, height=dp(60),
            spacing=dp(12), padding=[dp(24), dp(4)],
        )
        is_last = self.index == n - 1
        btn_text = self.t("get_started") if is_last else self.t("next")
        next_btn = MDRaisedButton(
            text=self.render(btn_text),
            md_bg_color=MoonColors.get("BUTTON", is_dark),
            theme_text_color="Custom",
            text_color=MoonColors.get("BUTTON_TEXT", is_dark),
            size_hint_x=1, elevation=4,
        )
        next_btn.bind(on_release=self._next)
        btn_row.add_widget(next_btn)
        root.add_widget(btn_row)
        root.add_widget(Widget(size_hint_y=None, height=dp(16)))

        self.add_widget(root)

    def _next(self, *args):
        if self.index < len(self.slides) - 1:
            self.index += 1
            self._build()
        else:
            self._finish()

    def _finish(self):
        self.app().db.set_setting("onboarding_completed", "1")
        if self.app().db.get_profile():
            self.app().go_to("home")
        else:
            self.app().go_to("profile")


class ProfileSetupScreen(BaseScreen):
    def on_pre_enter(self, *args):
        self._build()

    def _build(self):
        body = self.scaffold(
            self.t("profile_setup"),
            back_to=None, scroll=True
        )
        fa = self.is_fa()
        profile = self.app().db.get_profile() or {}

        body.add_widget(self.make_label(
            self.t("general_info"), style="Subtitle1", bold=True,
            color=MoonColors.get("ACCENT", self.is_dark())
        ))

        self.name_f = self.make_field(self.t("name"), profile.get("name", ""))
        self.age_f = self.make_field(self.t("age"), profile.get("age", ""))
        self.height_f = self.make_field(self.t("height"), profile.get("height", ""))
        self.weight_f = self.make_field(self.t("weight"), profile.get("weight", ""))

        for f in [self.name_f, self.age_f, self.height_f, self.weight_f]:
            body.add_widget(f)

        body.add_widget(Widget(size_hint_y=None, height=dp(8)))
        body.add_widget(self.make_divider())
        body.add_widget(Widget(size_hint_y=None, height=dp(8)))
        body.add_widget(self.make_label(
            self.lv("Workout Preferences", "ترجیحات تمرینی"),
            style="Subtitle1", bold=True,
            color=MoonColors.get("ACCENT", self.is_dark())
        ))

        self.goal_f = self.make_field(self.t("goal"), profile.get("goal", ""))
        self.goal_f.helper_text = self.render(self.t("profile_hint_goal"))
        self.goal_f.helper_text_mode = "on_focus"

        self.activity_f = self.make_field(self.t("activity_level"), profile.get("activity_level", ""))
        self.activity_f.helper_text = self.render(self.t("profile_hint_activity"))
        self.activity_f.helper_text_mode = "on_focus"

        self.fitness_f = self.make_field(self.t("fitness_level"), profile.get("fitness_level", ""))
        self.fitness_f.helper_text = self.render(self.t("profile_hint_fitness"))
        self.fitness_f.helper_text_mode = "on_focus"

        self.days_f = self.make_field(self.t("training_days"), profile.get("training_days", ""))
        self.workout_f = self.make_field(self.t("preferred_workout"), profile.get("preferred_workout", ""))
        self.workout_f.helper_text = self.render(self.t("profile_hint_workout"))
        self.workout_f.helper_text_mode = "on_focus"

        self.equipment_f = self.make_field(self.t("equipment"), profile.get("equipment", ""))
        self.equipment_f.helper_text = self.render(self.t("profile_hint_equipment"))
        self.equipment_f.helper_text_mode = "on_focus"

        self.limits_f = self.make_field(self.t("limitations"), profile.get("limitations", ""))
        self.limits_f.helper_text = self.render(self.t("profile_hint_limitations"))
        self.limits_f.helper_text_mode = "on_focus"

        self.time_f = self.make_field(self.t("preferred_time"), profile.get("preferred_time", ""))
        self.time_f.helper_text = self.render(self.t("profile_hint_time"))
        self.time_f.helper_text_mode = "on_focus"

        self.note_f = MoonTextField(
            hint=self.t("note"), value=profile.get("note", ""),
            fa=fa, dark=self.is_dark(),
            multiline=True, height=dp(80),
        )
        self.note_f.size_hint_y = None
        self.note_f.height = dp(80)

        for f in [self.goal_f, self.activity_f, self.fitness_f,
                  self.days_f, self.workout_f, self.equipment_f,
                  self.limits_f, self.time_f, self.note_f]:
            body.add_widget(f)

        body.add_widget(Widget(size_hint_y=None, height=dp(12)))
        save_btn = self.make_btn(self.t("save_profile"), self._save)
        body.add_widget(save_btn)
        body.add_widget(Widget(size_hint_y=None, height=dp(20)))

    def _save(self, *args):
        name = self.name_f.text.strip()
        age = self.age_f.text.strip()
        height = self.height_f.text.strip()
        weight = self.weight_f.text.strip()
        days = self.days_f.text.strip()

        if not name or not age or not height or not weight or not days:
            self.show_msg(self.t("field_required"))
            return
        try:
            age_v = int(age)
            height_v = float(height)
            weight_v = float(weight)
            days_v = int(days)
        except ValueError:
            self.show_msg(self.t("invalid_number"))
            return

        data = {
            "name": name, "age": age_v, "height": height_v,
            "weight": weight_v, "goal": self.goal_f.text.strip(),
            "activity_level": self.activity_f.text.strip(),
            "fitness_level": self.fitness_f.text.strip(),
            "training_days": days_v,
            "preferred_workout": self.workout_f.text.strip(),
            "equipment": self.equipment_f.text.strip(),
            "limitations": self.limits_f.text.strip(),
            "preferred_time": self.time_f.text.strip(),
            "note": self.note_f.text.strip(),
        }
        try:
            self.app().db.save_profile(data)
            self.app().ensure_recommended_plan()
            self.vibrate()
            self.show_msg(self.t("profile_saved"))
            self.app().refresh_screen("home")
            self.app().go_to("home")
        except Exception as e:
            print(f"[MOON] Profile save error: {e}")
            self.show_msg(str(e))


class HomeScreen(BaseScreen):
    def on_pre_enter(self, *args):
        self._build()

    def _build(self):
        body = self.scaffold("MOON Fitness", bottom_nav="home", scroll=True)
        app = self.app()
        is_dark = self.is_dark()

        profile = app.db.get_profile()
        if not profile:
            card = self.make_card()
            card.add_widget(self.make_label(
                "◐  MOON Fitness", style="H5", center=True, bold=True,
                color=MoonColors.get("ACCENT", is_dark)
            ))
            card.add_widget(self.make_label(
                self.t("no_profile"), center=True, secondary=True
            ))
            body.add_widget(card)
            body.add_widget(self.make_btn(
                self.t("profile_setup"),
                lambda x: app.go_to("profile")
            ))
            return

        app.ensure_recommended_plan()
        stats = app.db.get_session_stats()
        active_plan = app.db.get_active_plan()
        quote = app.db.get_quote_of_day(app.language)

        greet_card = self.make_card()
        greet_row = MDBoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        moon_lbl = MDLabel(
            text="◐", font_size=sp(28),
            size_hint=(None, None), size=(dp(40), dp(40)),
            halign="center", theme_text_color="Custom",
            text_color=MoonColors.get("ACCENT", is_dark),
        )
        greet_row.add_widget(moon_lbl)
        greet_row.add_widget(self.make_label(
            self.t("greeting", name=profile["name"]),
            style="H6", bold=True
        ))
        greet_card.add_widget(greet_row)
        greet_card.add_widget(self.make_divider())
        greet_card.add_widget(self.make_label(
            self.t("quote_of_day"), style="Caption", secondary=True
        ))
        greet_card.add_widget(self.make_label(
            quote, style="Body1",
            color=MoonColors.get("GOLD", is_dark)
        ))
        body.add_widget(greet_card)

        stats_row = GridLayout(
            cols=3, size_hint_y=None, height=dp(130),
            spacing=dp(8), padding=[dp(0), dp(0)],
        )
        stats_row.add_widget(MoonStatCard(
            title=self.t("completed_workouts"),
            value=stats["total_sessions"],
            icon="check-circle-outline", dark=is_dark,
            accent_color=MoonColors.get("ACCENT", is_dark),
        ))
        stats_row.add_widget(MoonStatCard(
            title=self.t("streak"),
            value=f"{stats['streak']}🔥",
            icon="fire", dark=is_dark,
            accent_color=MoonColors.get("ACCENT2", is_dark),
        ))
        stats_row.add_widget(MoonStatCard(
            title=self.t("total_minutes"),
            value=stats["total_minutes"],
            icon="timer-outline", dark=is_dark,
            accent_color=MoonColors.get("GOLD", is_dark),
        ))
        body.add_widget(stats_row)

        plan_card = self.make_card()
        plan_card.add_widget(self.make_label(
            self.t("active_plan"), style="Caption", secondary=True
        ))
        plan_name = app.plan_name(active_plan) if active_plan else "—"
        plan_card.add_widget(self.make_label(
            plan_name, style="H6", bold=True,
            color=MoonColors.get("ACCENT", is_dark)
        ))

        if active_plan:
            today = app.get_today_day(active_plan)
            plan_card.add_widget(self.make_divider())
            plan_card.add_widget(self.make_label(
                self.t("todays_workout"), style="Caption", secondary=True
            ))
            plan_card.add_widget(self.make_label(
                app.day_title(today), style="Subtitle1", bold=True
            ))
            exs = today.get("exercises", [])
            if exs:
                first_ex = EXERCISES.get(exs[0]["key"], {})
                ex_name = app.exercise_name(first_ex)
                plan_card.add_widget(self.make_label(
                    f"• {ex_name} " + self.lv(f"+ {len(exs)-1} more", f"+ {len(exs)-1} حرکت دیگر"),
                    style="Body2", secondary=True
                ))
            btn_row = MDBoxLayout(size_hint_y=None, height=dp(50), spacing=dp(8))
            btn_row.add_widget(self.make_btn(
                self.t("start_now"), lambda x: app.start_workout()
            ))
            btn_row.add_widget(self.make_btn(
                self.t("plans"),
                lambda x: app.go_to("plans"), flat=True
            ))
            plan_card.add_widget(btn_row)
        else:
            plan_card.add_widget(self.make_label(
                self.t("no_active_plan"), secondary=True
            ))
            plan_card.add_widget(self.make_btn(
                self.t("plans"), lambda x: app.go_to("plans")
            ))

        body.add_widget(plan_card)

        latest = stats.get("latest_progress")
        prog_card = self.make_card(alt=True)
        prog_card.add_widget(self.make_label(
            self.t("latest_progress"), style="Subtitle1", bold=True
        ))
        if latest:
            parts = []
            if latest.get("weight"):
                parts.append(f"{self.t('weight')}: {latest['weight']} {self.t('weight_unit')}")
            if latest.get("waist"):
                parts.append(self.lv(f"Waist: {latest['waist']}cm", f"کمر: {latest['waist']}سانت"))
            if latest.get("hips"):
                parts.append(self.lv(f"Hips: {latest['hips']}cm", f"باسن: {latest['hips']}سانت"))
            prog_card.add_widget(self.make_label(
                " | ".join(parts) if parts else "—",
                color=MoonColors.get("SUCCESS", is_dark)
            ))
        else:
            prog_card.add_widget(self.make_label(
                self.t("save_first_log"), secondary=True
            ))
        prog_card.add_widget(self.make_btn(
            self.t("progress_log"),
            lambda x: app.go_to("progress"), flat=True
        ))
        body.add_widget(prog_card)

        quick_row = MDBoxLayout(size_hint_y=None, height=dp(50), spacing=dp(8))
        quick_row.add_widget(self.make_btn(
            self.t("vibrate_test"),
            lambda x: self._test_vibrate(), flat=True
        ))
        quick_row.add_widget(self.make_btn(
            self.t("send_notification"),
            lambda x: self._test_notification(), flat=True
        ))
        body.add_widget(quick_row)

    def _test_vibrate(self):
        try:
            if HAS_VIBRATOR:
                plyer_vibrator.vibrate(0.1)
                self.show_msg(self.t("vibrated"))
            else:
                self.show_msg(self.t("vibrate_unavailable"))
        except Exception:
            self.show_msg(self.t("vibrate_unavailable"))

    def _test_notification(self):
        success = self.send_notification(
            self.t("notify_workout_title"),
            self.t("notify_workout_msg"),
        )
        if success:
            self.show_msg(self.t("notification_sent"))
        else:
            self.show_msg(self.t("notification_unavailable"))


class PlansScreen(BaseScreen):
    def on_pre_enter(self, *args):
        self._build()

    def _build(self):
        body = self.scaffold(self.t("plans"), bottom_nav="plans", scroll=True)
        app = self.app()
        is_dark = self.is_dark()
        profile = app.db.get_profile()
        active_key = app.db.get_setting("active_plan_key", "")

        rec_card = self.make_card(alt=True)
        rec_card.add_widget(self.make_label(
            self.t("recommendation"), style="Subtitle1", bold=True,
            color=MoonColors.get("GOLD", is_dark)
        ))
        if profile:
            rec_key = app.recommend_plan_key(profile)
            rec_plan = app.db.get_plan(rec_key)
            rec_name = app.plan_name(rec_plan) if rec_plan else "—"
            rec_row = MDBoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
            rec_row.add_widget(self.make_label(
                rec_name, style="H6",
                color=MoonColors.get("ACCENT", is_dark)
            ))
            rec_card.add_widget(rec_row)
            rec_card.add_widget(self.make_btn(
                self.t("recommend_plan_btn"),
                lambda x: self._activate_rec()
            ))
        else:
            rec_card.add_widget(self.make_label(
                self.t("profile_missing_for_recommend"), secondary=True
            ))
        body.add_widget(rec_card)

        for plan in app.db.get_plans():
            self._plan_card(body, plan, active_key, is_dark)

    def _plan_card(self, body, plan, active_key, is_dark):
        app = self.app()
        is_active = active_key == plan["plan_key"]

        card = self.make_card()

        top_row = MDBoxLayout(size_hint_y=None, height=dp(40), spacing=dp(8))
        top_row.add_widget(self.make_label(
            app.plan_name(plan), style="H6", bold=True,
            color=MoonColors.get("ACCENT" if not is_active else "GOLD", is_dark)
        ))
        if is_active:
            badge = MDLabel(
                text="✓", font_size=sp(18),
                size_hint=(None, None), size=(dp(32), dp(32)),
                halign="center", theme_text_color="Custom",
                text_color=MoonColors.get("SUCCESS", is_dark),
            )
            top_row.add_widget(badge)
        card.add_widget(top_row)

        card.add_widget(self.make_label(
            app.plan_desc(plan), style="Body2", secondary=True
        ))

        diff_text = app.diff_label(plan["difficulty"])
        meta = self.lv(
            f"⭐ {diff_text}   •   {plan['weeks']} weeks   •   {plan['days_per_week']} days/week   •   ~{plan['session_minutes']} min",
            f"⭐ {diff_text}   •   {plan['weeks']} هفته   •   {plan['days_per_week']} روز   •   ~{plan['session_minutes']} دقیقه",
        )
        card.add_widget(self.make_label(meta, style="Caption",
                                        color=MoonColors.get("ACCENT2", is_dark)))

        goal = f"🎯 {app.plan_goal(plan)}"
        card.add_widget(self.make_label(goal, style="Body2"))

        btn_row = MDBoxLayout(size_hint_y=None, height=dp(50), spacing=dp(8))
        detail_btn = self.make_btn(
            self.t("details"),
            lambda x, k=plan["plan_key"]: app.open_plan_details(k),
            flat=True,
        )
        btn_row.add_widget(detail_btn)

        if is_active:
            active_btn = MDRaisedButton(
                text=self.render(self.t("active")),
                md_bg_color=MoonColors.get("SUCCESS", is_dark),
                theme_text_color="Custom",
                text_color=MoonColors.get("BG", is_dark),
                size_hint_x=1, elevation=2,
            )
            btn_row.add_widget(active_btn)
        else:
            act_btn = self.make_btn(
                self.t("activate"),
                lambda x, k=plan["plan_key"]: self._activate(k),
            )
            btn_row.add_widget(act_btn)

        card.add_widget(btn_row)
        body.add_widget(card)

    def _activate(self, key):
        self.app().db.set_active_plan(key)
        self.vibrate()
        self.show_msg(self.t("plan_activated"))
        self.app().refresh_screen("home")
        self._build()

    def _activate_rec(self):
        profile = self.app().db.get_profile()
        if not profile:
            self.show_msg(self.t("profile_missing_for_recommend"))
            return
        key = self.app().recommend_plan_key(profile)
        self.app().db.set_active_plan(key)
        self.vibrate()
        self.show_msg(self.t("use_recommended"))
        self.app().refresh_screen("home")
        self._build()


class PlanDetailScreen(BaseScreen):
    def on_pre_enter(self, *args):
        self._build()

    def _build(self):
        body = self.scaffold(self.t("details"), back_to="plans", scroll=True)
        app = self.app()
        is_dark = self.is_dark()

        if not app.selected_plan_key:
            body.add_widget(self.make_label("—", secondary=True))
            return

        plan = app.db.get_plan(app.selected_plan_key)
        if not plan:
            body.add_widget(self.make_label("—", secondary=True))
            return

        hero = self.make_card()
        hero.add_widget(self.make_label(
            app.plan_name(plan), style="H5", bold=True,
            color=MoonColors.get("ACCENT", is_dark)
        ))
        hero.add_widget(self.make_label(
            app.plan_desc(plan), style="Body1", secondary=True
        ))

        info_grid = GridLayout(
            cols=2, size_hint_y=None, height=dp(90), spacing=dp(8)
        )
        pairs = [
            (self.t("difficulty"), app.diff_label(plan["difficulty"])),
            (self.t("goal_label"), app.plan_goal(plan)),
            (self.t("weeks"), f"{plan['weeks']} {self.t('weeks')}"),
            (self.t("target_areas"), app.plan_target(plan)),
        ]
        for k, v in pairs:
            box = MDBoxLayout(orientation="vertical", spacing=dp(2))
            box.add_widget(self.make_label(k, style="Caption", secondary=True))
            box.add_widget(self.make_label(v, style="Body2", bold=True))
            info_grid.add_widget(box)
        hero.add_widget(info_grid)

        btn_row = MDBoxLayout(size_hint_y=None, height=dp(50), spacing=dp(8))
        btn_row.add_widget(self.make_btn(
            self.t("activate"),
            lambda x: self._activate(plan["plan_key"])
        ))
        btn_row.add_widget(self.make_btn(
            self.t("start_workout"),
            lambda x: self._start(plan["plan_key"]),
            flat=True
        ))
        hero.add_widget(btn_row)
        body.add_widget(hero)

        for day in plan["days"]:
            day_card = self.make_card(alt=True)
            day_card.add_widget(self.make_label(
                app.day_title(day), style="Subtitle1", bold=True,
                color=MoonColors.get("ACCENT2", is_dark)
            ))
            for item in day["exercises"]:
                ex = EXERCISES.get(item["key"], {})
                ex_name = app.exercise_name(ex)
                line = self.lv(
                    f"• {ex_name}  |  {self.t('sets')}: {item['sets']}  |  {self.t('reps')}: {item['reps']}  |  {self.t('rest')}: {item['rest']}",
                    f"• {ex_name}  |  ست: {item['sets']}  |  تکرار: {item['reps']}  |  استراحت: {item['rest']}"
                )
                day_card.add_widget(self.make_label(line, style="Body2"))
            body.add_widget(day_card)

    def _activate(self, key):
        self.app().db.set_active_plan(key)
        self.vibrate()
        self.show_msg(self.t("plan_activated"))
        self.app().refresh_screen("home")

    def _start(self, key):
        self.app().db.set_active_plan(key)
        self.app().current_workout_plan_key = key
        self.app().current_day_index = 0
        self.app().go_to("workout")


class SplashScreen(BaseScreen):
    def on_enter(self, *args):
        self._build()
        Clock.schedule_once(self._decide, 1.8)

    def _build(self):
        self.clear_widgets()
        is_dark = self.is_dark()

        root = FloatLayout()
        with root.canvas.before:
            Color(*MoonColors.get("BG", is_dark))
            self._bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(
            pos=lambda i, v: setattr(self._bg, "pos", v),
            size=lambda i, v: setattr(self._bg, "size", v),
        )

        center_box = MDBoxLayout(
            orientation="vertical", spacing=dp(16),
            padding=[dp(40), dp(0)],
            size_hint=(1, None),
            pos_hint={"center_x": 0.5, "center_y": 0.52},
        )
        center_box.bind(minimum_height=center_box.setter("height"))

        moon_icon = MDLabel(
            text="◐", font_size=sp(90), halign="center",
            theme_text_color="Custom",
            text_color=MoonColors.get("ACCENT", is_dark),
            size_hint_y=None, height=dp(110),
        )

        title_lbl = MDLabel(
            text="MOON", font_style="H3", halign="center", bold=True,
            theme_text_color="Custom",
            text_color=MoonColors.get("TEXT", is_dark),
            size_hint_y=None, height=dp(56),
        )

        subtitle_lbl = MDLabel(
            text=self.t("app_subtitle"), font_style="Subtitle1", halign="center",
            theme_text_color="Custom",
            text_color=MoonColors.get("TEXT2", is_dark),
            size_hint_y=None, height=dp(36),
        )

        slogan_lbl = MDLabel(
            text=self.t("app_slogan"), font_style="Caption", halign="center",
            theme_text_color="Custom",
            text_color=MoonColors.get("ACCENT2", is_dark),
            size_hint_y=None, height=dp(28),
        )

        center_box.add_widget(moon_icon)
        center_box.add_widget(title_lbl)
        center_box.add_widget(subtitle_lbl)
        center_box.add_widget(slogan_lbl)

        root.add_widget(center_box)
        self.add_widget(root)

    def _decide(self, *args):
        app = self.app()
        try:
            onboarding = app.db.get_setting("onboarding_completed", "0") == "1"
            profile = app.db.get_profile()
            if not onboarding:
                app.go_to("onboarding")
            elif not profile:
                app.go_to("profile")
            else:
                app.ensure_recommended_plan()
                app.go_to("home")
        except Exception as e:
            print(f"[MOON] Splash error: {e}")
            app.go_to("onboarding")


class OnboardingScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.index = 0
        self.slides = [
            ("onboarding_1_title", "onboarding_1_body", "◐", "ACCENT"),
            ("onboarding_2_title", "onboarding_2_body", "📊", "ACCENT2"),
            ("onboarding_3_title", "onboarding_3_body", "✨", "GOLD"),
            ("onboarding_4_title", "onboarding_4_body", "🌙", "ACCENT"),
        ]

    def on_pre_enter(self, *args):
        self._build()

    def _build(self):
        self.clear_widgets()
        is_dark = self.is_dark()
        n = len(self.slides)
        title_key, body_key, icon_ch, color_key = self.slides[self.index]

        root = MDBoxLayout(orientation="vertical")
        with root.canvas.before:
            Color(*MoonColors.get("BG", is_dark))
            self._bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(
            pos=lambda i, v: setattr(self._bg, "pos", v),
            size=lambda i, v: setattr(self._bg, "size", v),
        )

        top_row = MDBoxLayout(size_hint_y=None, height=dp(52),
                              padding=[dp(8), dp(8)])
        top_row.add_widget(Widget())
        skip_btn = MDFlatButton(
            text=self.render(self.t("skip")),
            theme_text_color="Custom",
            text_color=MoonColors.get("TEXT2", is_dark),
        )
        skip_btn.bind(on_release=lambda x: self._finish())
        top_row.add_widget(skip_btn)
        root.add_widget(top_row)

        root.add_widget(Widget(size_hint_y=0.06))

        icon_lbl = MDLabel(
            text=icon_ch, font_size=sp(80), halign="center",
            size_hint_y=None, height=dp(100),
        )
        root.add_widget(icon_lbl)

        root.add_widget(Widget(size_hint_y=0.03))

        title_lbl = self.make_label(self.t(title_key), style="H5",
                                    center=True, bold=True,
                                    color=MoonColors.get(color_key, is_dark))
        root.add_widget(title_lbl)

        root.add_widget(Widget(size_hint_y=None, height=dp(14)))

        body_lbl = self.make_label(self.t(body_key), style="Body1",
                                   center=True, secondary=True)
        body_lbl.size_hint_x = 0.82
        body_lbl.pos_hint = {"center_x": 0.5}
        root.add_widget(body_lbl)

        root.add_widget(Widget())

        dot_row = MDBoxLayout(
            size_hint_y=None, height=dp(28),
            spacing=dp(8), padding=[0, dp(4)],
        )
        dot_row.add_widget(Widget())
        for i in range(n):
            ch = "●" if i == self.index else "○"
            col = (MoonColors.get("ACCENT", is_dark)
                   if i == self.index else MoonColors.get("TEXT2", is_dark))
            dot = MDLabel(
                text=ch, halign="center", font_size=sp(14),
                size_hint=(None, None), size=(dp(22), dp(22)),
                theme_text_color="Custom", text_color=col,
            )
            dot_row.add_widget(dot)
        dot_row.add_widget(Widget())
        root.add_widget(dot_row)

        root.add_widget(Widget(size_hint_y=None, height=dp(20)))

        btn_row = MDBoxLayout(
            size_hint_y=None, height=dp(60),
            spacing=dp(12), padding=[dp(24), dp(4)],
        )
        is_last = self.index == n - 1
        btn_text = self.t("get_started") if is_last else self.t("next")
        next_btn = MDRaisedButton(
            text=self.render(btn_text),
            md_bg_color=MoonColors.get("BUTTON", is_dark),
            theme_text_color="Custom",
            text_color=MoonColors.get("BUTTON_TEXT", is_dark),
            size_hint_x=1, elevation=4,
        )
        next_btn.bind(on_release=self._next)
        btn_row.add_widget(next_btn)
        root.add_widget(btn_row)
        root.add_widget(Widget(size_hint_y=None, height=dp(16)))

        self.add_widget(root)

    def _next(self, *args):
        if self.index < len(self.slides) - 1:
            self.index += 1
            self._build()
        else:
            self._finish()

    def _finish(self):
        self.app().db.set_setting("onboarding_completed", "1")
        if self.app().db.get_profile():
            self.app().go_to("home")
        else:
            self.app().go_to("profile")


class ProfileSetupScreen(BaseScreen):
    def on_pre_enter(self, *args):
        self._build()

    def _build(self):
        body = self.scaffold(
            self.t("profile_setup"),
            back_to=None, scroll=True
        )
        fa = self.is_fa()
        profile = self.app().db.get_profile() or {}

        body.add_widget(self.make_label(
            self.t("general_info"), style="Subtitle1", bold=True,
            color=MoonColors.get("ACCENT", self.is_dark())
        ))

        self.name_f = self.make_field(self.t("name"), profile.get("name", ""))
        self.age_f = self.make_field(self.t("age"), profile.get("age", ""))
        self.height_f = self.make_field(self.t("height"), profile.get("height", ""))
        self.weight_f = self.make_field(self.t("weight"), profile.get("weight", ""))

        for f in [self.name_f, self.age_f, self.height_f, self.weight_f]:
            body.add_widget(f)

        body.add_widget(Widget(size_hint_y=None, height=dp(8)))
        body.add_widget(self.make_divider())
        body.add_widget(Widget(size_hint_y=None, height=dp(8)))
        body.add_widget(self.make_label(
            self.lv("Workout Preferences", "ترجیحات تمرینی"),
            style="Subtitle1", bold=True,
            color=MoonColors.get("ACCENT", self.is_dark())
        ))

        self.goal_f = self.make_field(self.t("goal"), profile.get("goal", ""))
        self.goal_f.helper_text = self.render(self.t("profile_hint_goal"))
        self.goal_f.helper_text_mode = "on_focus"

        self.activity_f = self.make_field(self.t("activity_level"), profile.get("activity_level", ""))
        self.activity_f.helper_text = self.render(self.t("profile_hint_activity"))
        self.activity_f.helper_text_mode = "on_focus"

        self.fitness_f = self.make_field(self.t("fitness_level"), profile.get("fitness_level", ""))
        self.fitness_f.helper_text = self.render(self.t("profile_hint_fitness"))
        self.fitness_f.helper_text_mode = "on_focus"

        self.days_f = self.make_field(self.t("training_days"), profile.get("training_days", ""))
        self.workout_f = self.make_field(self.t("preferred_workout"), profile.get("preferred_workout", ""))
        self.workout_f.helper_text = self.render(self.t("profile_hint_workout"))
        self.workout_f.helper_text_mode = "on_focus"

        self.equipment_f = self.make_field(self.t("equipment"), profile.get("equipment", ""))
        self.equipment_f.helper_text = self.render(self.t("profile_hint_equipment"))
        self.equipment_f.helper_text_mode = "on_focus"

        self.limits_f = self.make_field(self.t("limitations"), profile.get("limitations", ""))
        self.limits_f.helper_text = self.render(self.t("profile_hint_limitations"))
        self.limits_f.helper_text_mode = "on_focus"

        self.time_f = self.make_field(self.t("preferred_time"), profile.get("preferred_time", ""))
        self.time_f.helper_text = self.render(self.t("profile_hint_time"))
        self.time_f.helper_text_mode = "on_focus"

        self.note_f = MoonTextField(
            hint=self.t("note"), value=profile.get("note", ""),
            fa=fa, dark=self.is_dark(),
            multiline=True, height=dp(80),
        )
        self.note_f.size_hint_y = None
        self.note_f.height = dp(80)

        for f in [self.goal_f, self.activity_f, self.fitness_f,
                  self.days_f, self.workout_f, self.equipment_f,
                  self.limits_f, self.time_f, self.note_f]:
            body.add_widget(f)

        body.add_widget(Widget(size_hint_y=None, height=dp(12)))
        save_btn = self.make_btn(self.t("save_profile"), self._save)
        body.add_widget(save_btn)
        body.add_widget(Widget(size_hint_y=None, height=dp(20)))

    def _save(self, *args):
        name = self.name_f.text.strip()
        age = self.age_f.text.strip()
        height = self.height_f.text.strip()
        weight = self.weight_f.text.strip()
        days = self.days_f.text.strip()

        if not name or not age or not height or not weight or not days:
            self.show_msg(self.t("field_required"))
            return
        try:
            age_v = int(age)
            height_v = float(height)
            weight_v = float(weight)
            days_v = int(days)
        except ValueError:
            self.show_msg(self.t("invalid_number"))
            return

        data = {
            "name": name, "age": age_v, "height": height_v,
            "weight": weight_v, "goal": self.goal_f.text.strip(),
            "activity_level": self.activity_f.text.strip(),
            "fitness_level": self.fitness_f.text.strip(),
            "training_days": days_v,
            "preferred_workout": self.workout_f.text.strip(),
            "equipment": self.equipment_f.text.strip(),
            "limitations": self.limits_f.text.strip(),
            "preferred_time": self.time_f.text.strip(),
            "note": self.note_f.text.strip(),
        }
        try:
            self.app().db.save_profile(data)
            self.app().ensure_recommended_plan()
            self.vibrate()
            self.show_msg(self.t("profile_saved"))
            self.app().refresh_screen("home")
            self.app().go_to("home")
        except Exception as e:
            print(f"[MOON] Profile save error: {e}")
            self.show_msg(str(e))


class HomeScreen(BaseScreen):
    def on_pre_enter(self, *args):
        self._build()

    def _build(self):
        body = self.scaffold("MOON Fitness", bottom_nav="home", scroll=True)
        app = self.app()
        is_dark = self.is_dark()

        profile = app.db.get_profile()
        if not profile:
            card = self.make_card()
            card.add_widget(self.make_label(
                "◐  MOON Fitness", style="H5", center=True, bold=True,
                color=MoonColors.get("ACCENT", is_dark)
            ))
            card.add_widget(self.make_label(
                self.t("no_profile"), center=True, secondary=True
            ))
            body.add_widget(card)
            body.add_widget(self.make_btn(
                self.t("profile_setup"),
                lambda x: app.go_to("profile")
            ))
            return

        app.ensure_recommended_plan()
        stats = app.db.get_session_stats()
        active_plan = app.db.get_active_plan()
        quote = app.db.get_quote_of_day(app.language)

        greet_card = self.make_card()
        greet_row = MDBoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        moon_lbl = MDLabel(
            text="◐", font_size=sp(28),
            size_hint=(None, None), size=(dp(40), dp(40)),
            halign="center", theme_text_color="Custom",
            text_color=MoonColors.get("ACCENT", is_dark),
        )
        greet_row.add_widget(moon_lbl)
        greet_row.add_widget(self.make_label(
            self.t("greeting", name=profile["name"]),
            style="H6", bold=True
        ))
        greet_card.add_widget(greet_row)
        greet_card.add_widget(self.make_divider())
        greet_card.add_widget(self.make_label(
            self.t("quote_of_day"), style="Caption", secondary=True
        ))
        greet_card.add_widget(self.make_label(
            quote, style="Body1",
            color=MoonColors.get("GOLD", is_dark)
        ))
        body.add_widget(greet_card)

        stats_row = GridLayout(
            cols=3, size_hint_y=None, height=dp(130),
            spacing=dp(8), padding=[dp(0), dp(0)],
        )
        stats_row.add_widget(MoonStatCard(
            title=self.t("completed_workouts"),
            value=stats["total_sessions"],
            icon="check-circle-outline", dark=is_dark,
            accent_color=MoonColors.get("ACCENT", is_dark),
        ))
        stats_row.add_widget(MoonStatCard(
            title=self.t("streak"),
            value=f"{stats['streak']}🔥",
            icon="fire", dark=is_dark,
            accent_color=MoonColors.get("ACCENT2", is_dark),
        ))
        stats_row.add_widget(MoonStatCard(
            title=self.t("total_minutes"),
            value=stats["total_minutes"],
            icon="timer-outline", dark=is_dark,
            accent_color=MoonColors.get("GOLD", is_dark),
        ))
        body.add_widget(stats_row)

        plan_card = self.make_card()
        plan_card.add_widget(self.make_label(
            self.t("active_plan"), style="Caption", secondary=True
        ))
        plan_name = app.plan_name(active_plan) if active_plan else "—"
        plan_card.add_widget(self.make_label(
            plan_name, style="H6", bold=True,
            color=MoonColors.get("ACCENT", is_dark)
        ))

        if active_plan:
            today = app.get_today_day(active_plan)
            plan_card.add_widget(self.make_divider())
            plan_card.add_widget(self.make_label(
                self.t("todays_workout"), style="Caption", secondary=True
            ))
            plan_card.add_widget(self.make_label(
                app.day_title(today), style="Subtitle1", bold=True
            ))
            exs = today.get("exercises", [])
            if exs:
                first_ex = EXERCISES.get(exs[0]["key"], {})
                ex_name = app.exercise_name(first_ex)
                plan_card.add_widget(self.make_label(
                    f"• {ex_name} " + self.lv(f"+ {len(exs)-1} more", f"+ {len(exs)-1} حرکت دیگر"),
                    style="Body2", secondary=True
                ))
            btn_row = MDBoxLayout(size_hint_y=None, height=dp(50), spacing=dp(8))
            btn_row.add_widget(self.make_btn(
                self.t("start_now"), lambda x: app.start_workout()
            ))
            btn_row.add_widget(self.make_btn(
                self.t("plans"),
                lambda x: app.go_to("plans"), flat=True
            ))
            plan_card.add_widget(btn_row)
        else:
            plan_card.add_widget(self.make_label(
                self.t("no_active_plan"), secondary=True
            ))
            plan_card.add_widget(self.make_btn(
                self.t("plans"), lambda x: app.go_to("plans")
            ))

        body.add_widget(plan_card)

        latest = stats.get("latest_progress")
        prog_card = self.make_card(alt=True)
        prog_card.add_widget(self.make_label(
            self.t("latest_progress"), style="Subtitle1", bold=True
        ))
        if latest:
            parts = []
            if latest.get("weight"):
                parts.append(f"{self.t('weight')}: {latest['weight']} {self.t('weight_unit')}")
            if latest.get("waist"):
                parts.append(self.lv(f"Waist: {latest['waist']}cm", f"کمر: {latest['waist']}سانت"))
            if latest.get("hips"):
                parts.append(self.lv(f"Hips: {latest['hips']}cm", f"باسن: {latest['hips']}سانت"))
            prog_card.add_widget(self.make_label(
                " | ".join(parts) if parts else "—",
                color=MoonColors.get("SUCCESS", is_dark)
            ))
        else:
            prog_card.add_widget(self.make_label(
                self.t("save_first_log"), secondary=True
            ))
        prog_card.add_widget(self.make_btn(
            self.t("progress_log"),
            lambda x: app.go_to("progress"), flat=True
        ))
        body.add_widget(prog_card)

        quick_row = MDBoxLayout(size_hint_y=None, height=dp(50), spacing=dp(8))
        quick_row.add_widget(self.make_btn(
            self.t("vibrate_test"),
            lambda x: self._test_vibrate(), flat=True
        ))
        quick_row.add_widget(self.make_btn(
            self.t("send_notification"),
            lambda x: self._test_notification(), flat=True
        ))
        body.add_widget(quick_row)

    def _test_vibrate(self):
        try:
            if HAS_VIBRATOR:
                plyer_vibrator.vibrate(0.1)
                self.show_msg(self.t("vibrated"))
            else:
                self.show_msg(self.t("vibrate_unavailable"))
        except Exception:
            self.show_msg(self.t("vibrate_unavailable"))

    def _test_notification(self):
        success = self.send_notification(
            self.t("notify_workout_title"),
            self.t("notify_workout_msg"),
        )
        if success:
            self.show_msg(self.t("notification_sent"))
        else:
            self.show_msg(self.t("notification_unavailable"))


class PlansScreen(BaseScreen):
    def on_pre_enter(self, *args):
        self._build()

    def _build(self):
        body = self.scaffold(self.t("plans"), bottom_nav="plans", scroll=True)
        app = self.app()
        is_dark = self.is_dark()
        profile = app.db.get_profile()
        active_key = app.db.get_setting("active_plan_key", "")

        rec_card = self.make_card(alt=True)
        rec_card.add_widget(self.make_label(
            self.t("recommendation"), style="Subtitle1", bold=True,
            color=MoonColors.get("GOLD", is_dark)
        ))
        if profile:
            rec_key = app.recommend_plan_key(profile)
            rec_plan = app.db.get_plan(rec_key)
            rec_name = app.plan_name(rec_plan) if rec_plan else "—"
            rec_row = MDBoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
            rec_row.add_widget(self.make_label(
                rec_name, style="H6",
                color=MoonColors.get("ACCENT", is_dark)
            ))
            rec_card.add_widget(rec_row)
            rec_card.add_widget(self.make_btn(
                self.t("recommend_plan_btn"),
                lambda x: self._activate_rec()
            ))
        else:
            rec_card.add_widget(self.make_label(
                self.t("profile_missing_for_recommend"), secondary=True
            ))
        body.add_widget(rec_card)

        for plan in app.db.get_plans():
            self._plan_card(body, plan, active_key, is_dark)

    def _plan_card(self, body, plan, active_key, is_dark):
        app = self.app()
        is_active = active_key == plan["plan_key"]

        card = self.make_card()

        top_row = MDBoxLayout(size_hint_y=None, height=dp(40), spacing=dp(8))
        top_row.add_widget(self.make_label(
            app.plan_name(plan), style="H6", bold=True,
            color=MoonColors.get("ACCENT" if not is_active else "GOLD", is_dark)
        ))
        if is_active:
            badge = MDLabel(
                text="✓", font_size=sp(18),
                size_hint=(None, None), size=(dp(32), dp(32)),
                halign="center", theme_text_color="Custom",
                text_color=MoonColors.get("SUCCESS", is_dark),
            )
            top_row.add_widget(badge)
        card.add_widget(top_row)

        card.add_widget(self.make_label(
            app.plan_desc(plan), style="Body2", secondary=True
        ))

        diff_text = app.diff_label(plan["difficulty"])
        meta = self.lv(
            f"⭐ {diff_text}   •   {plan['weeks']} weeks   •   {plan['days_per_week']} days/week   •   ~{plan['session_minutes']} min",
            f"⭐ {diff_text}   •   {plan['weeks']} هفته   •   {plan['days_per_week']} روز   •   ~{plan['session_minutes']} دقیقه",
        )
        card.add_widget(self.make_label(meta, style="Caption",
                                        color=MoonColors.get("ACCENT2", is_dark)))

        goal = f"🎯 {app.plan_goal(plan)}"
        card.add_widget(self.make_label(goal, style="Body2"))

        btn_row = MDBoxLayout(size_hint_y=None, height=dp(50), spacing=dp(8))
        detail_btn = self.make_btn(
            self.t("details"),
            lambda x, k=plan["plan_key"]: app.open_plan_details(k),
            flat=True,
        )
        btn_row.add_widget(detail_btn)

        if is_active:
            active_btn = MDRaisedButton(
                text=self.render(self.t("active")),
                md_bg_color=MoonColors.get("SUCCESS", is_dark),
                theme_text_color="Custom",
                text_color=MoonColors.get("BG", is_dark),
                size_hint_x=1, elevation=2,
            )
            btn_row.add_widget(active_btn)
        else:
            act_btn = self.make_btn(
                self.t("activate"),
                lambda x, k=plan["plan_key"]: self._activate(k),
            )
            btn_row.add_widget(act_btn)

        card.add_widget(btn_row)
        body.add_widget(card)

    def _activate(self, key):
        self.app().db.set_active_plan(key)
        self.vibrate()
        self.show_msg(self.t("plan_activated"))
        self.app().refresh_screen("home")
        self._build()

    def _activate_rec(self):
        profile = self.app().db.get_profile()
        if not profile:
            self.show_msg(self.t("profile_missing_for_recommend"))
            return
        key = self.app().recommend_plan_key(profile)
        self.app().db.set_active_plan(key)
        self.vibrate()
        self.show_msg(self.t("use_recommended"))
        self.app().refresh_screen("home")
        self._build()


class PlanDetailScreen(BaseScreen):
    def on_pre_enter(self, *args):
        self._build()

    def _build(self):
        body = self.scaffold(self.t("details"), back_to="plans", scroll=True)
        app = self.app()
        is_dark = self.is_dark()

        if not app.selected_plan_key:
            body.add_widget(self.make_label("—", secondary=True))
            return

        plan = app.db.get_plan(app.selected_plan_key)
        if not plan:
            body.add_widget(self.make_label("—", secondary=True))
            return

        hero = self.make_card()
        hero.add_widget(self.make_label(
            app.plan_name(plan), style="H5", bold=True,
            color=MoonColors.get("ACCENT", is_dark)
        ))
        hero.add_widget(self.make_label(
            app.plan_desc(plan), style="Body1", secondary=True
        ))

        info_grid = GridLayout(
            cols=2, size_hint_y=None, height=dp(90), spacing=dp(8)
        )
        pairs = [
            (self.t("difficulty"), app.diff_label(plan["difficulty"])),
            (self.t("goal_label"), app.plan_goal(plan)),
            (self.t("weeks"), f"{plan['weeks']} {self.t('weeks')}"),
            (self.t("target_areas"), app.plan_target(plan)),
        ]
        for k, v in pairs:
            box = MDBoxLayout(orientation="vertical", spacing=dp(2))
            box.add_widget(self.make_label(k, style="Caption", secondary=True))
            box.add_widget(self.make_label(v, style="Body2", bold=True))
            info_grid.add_widget(box)
        hero.add_widget(info_grid)

        btn_row = MDBoxLayout(size_hint_y=None, height=dp(50), spacing=dp(8))
        btn_row.add_widget(self.make_btn(
            self.t("activate"),
            lambda x: self._activate(plan["plan_key"])
        ))
        btn_row.add_widget(self.make_btn(
            self.t("start_workout"),
            lambda x: self._start(plan["plan_key"]),
            flat=True
        ))
        hero.add_widget(btn_row)
        body.add_widget(hero)

        for day in plan["days"]:
            day_card = self.make_card(alt=True)
            day_card.add_widget(self.make_label(
                app.day_title(day), style="Subtitle1", bold=True,
                color=MoonColors.get("ACCENT2", is_dark)
            ))
            for item in day["exercises"]:
                ex = EXERCISES.get(item["key"], {})
                ex_name = app.exercise_name(ex)
                line = self.lv(
                    f"• {ex_name}  |  {self.t('sets')}: {item['sets']}  |  {self.t('reps')}: {item['reps']}  |  {self.t('rest')}: {item['rest']}",
                    f"• {ex_name}  |  ست: {item['sets']}  |  تکرار: {item['reps']}  |  استراحت: {item['rest']}"
                )
                day_card.add_widget(self.make_label(line, style="Body2"))
            body.add_widget(day_card)

    def _activate(self, key):
        self.app().db.set_active_plan(key)
        self.vibrate()
        self.show_msg(self.t("plan_activated"))
        self.app().refresh_screen("home")

    def _start(self, key):
        self.app().db.set_active_plan(key)
        self.app().current_workout_plan_key = key
        self.app().current_day_index = 0
        self.app().go_to("workout")


class WorkoutScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.elapsed = 0
        self.rest_elapsed = 0
        self.timer_ev = None
        self.rest_ev = None
        self.running = False
        self.resting = False
        self.ex_index = 0
        self.plan = None
        self.day = None

    def on_pre_enter(self, *args):
        self.elapsed = 0
        self.rest_elapsed = 0
        self.ex_index = 0
        self.running = False
        self.resting = False
        self._cancel_all()
        self._build()

    def on_leave(self, *args):
        self._cancel_all()

    def _cancel_all(self):
        if self.timer_ev:
            self.timer_ev.cancel()
            self.timer_ev = None
        if self.rest_ev:
            self.rest_ev.cancel()
            self.rest_ev = None

    def _build(self):
        body = self.scaffold(self.t("workout_session"), back_to="home", scroll=False)
        app = self.app()
        is_dark = self.is_dark()

        self.plan = (
            app.db.get_plan(app.current_workout_plan_key)
            if app.current_workout_plan_key
            else app.db.get_active_plan()
        )

        if not self.plan:
            body.add_widget(self.make_label(self.t("no_active_plan"), secondary=True))
            body.add_widget(self.make_btn(self.t("plans"), lambda x: app.go_to("plans")))
            return

        if app.current_day_index is None:
            app.current_day_index = app.get_today_day_index(self.plan)

        days = self.plan["days"]
        if not days:
            body.add_widget(self.make_label("—", secondary=True))
            return
        self.day = days[app.current_day_index % len(days)]

        sc, scroll_body = self.make_scroll_body()

        info_card = self.make_card()
        info_card.add_widget(self.make_label(
            app.plan_name(self.plan), style="H6", bold=True,
            color=MoonColors.get("ACCENT", is_dark)
        ))
        info_card.add_widget(self.make_label(
            app.day_title(self.day), style="Subtitle1"
        ))
        scroll_body.add_widget(info_card)

        timer_card = self.make_card(alt=True)
        self.timer_lbl = MDLabel(
            text="00:00", font_style="H4", halign="center", bold=True,
            theme_text_color="Custom",
            text_color=MoonColors.get("ACCENT", is_dark),
            size_hint_y=None, height=dp(60),
        )
        self.rest_lbl = MDLabel(
            text="", font_style="Caption", halign="center",
            theme_text_color="Custom",
            text_color=MoonColors.get("ACCENT2", is_dark),
            size_hint_y=None, height=dp(22),
        )
        self.prog_lbl = MDLabel(
            text="", font_style="Caption", halign="center",
            theme_text_color="Custom",
            text_color=MoonColors.get("TEXT2", is_dark),
            size_hint_y=None, height=dp(22),
        )
        timer_card.add_widget(self.make_label(
            self.t("session_progress"), style="Caption", secondary=True, center=True
        ))
        timer_card.add_widget(self.timer_lbl)
        timer_card.add_widget(self.rest_lbl)
        timer_card.add_widget(self.prog_lbl)

        n = max(1, len(self.day["exercises"]))
        self.pb = MDProgressBar(
            value=0, max=n,
            color=MoonColors.get("ACCENT", is_dark),
            size_hint_y=None, height=dp(8),
        )
        timer_card.add_widget(self.pb)
        scroll_body.add_widget(timer_card)

        self.current_card = self.make_card()
        self.current_name_lbl = self.make_label("", style="H6", bold=True,
                                                 color=MoonColors.get("ACCENT", is_dark))
        self.current_desc_lbl = self.make_label("", style="Body1", secondary=True)
        self.current_meta_lbl = self.make_label("", style="Caption",
                                                 color=MoonColors.get("ACCENT2", is_dark))
        self.current_muscles_lbl = self.make_label("", style="Caption", secondary=True)
        self.current_card.add_widget(self.make_label(
            self.t("current_exercise"), style="Caption", secondary=True
        ))
        self.current_card.add_widget(self.current_name_lbl)
        self.current_card.add_widget(self.current_desc_lbl)
        self.current_card.add_widget(self.current_meta_lbl)
        self.current_card.add_widget(self.current_muscles_lbl)
        scroll_body.add_widget(self.current_card)

        self.list_card = self.make_card(alt=True)
        self.list_card.add_widget(self.make_label(
            self.t("exercise_list"), style="Subtitle1", bold=True
        ))
        self.ex_list_box = MDBoxLayout(
            orientation="vertical", spacing=dp(6), size_hint_y=None
        )
        self.ex_list_box.bind(minimum_height=self.ex_list_box.setter("height"))
        self.list_card.add_widget(self.ex_list_box)
        scroll_body.add_widget(self.list_card)

        body.add_widget(sc)

        ctrl1 = MDBoxLayout(size_hint_y=None, height=dp(52),
                             spacing=dp(8), padding=[dp(14), dp(4)])
        start_btn = self.make_btn(self.t("start_workout"), self._start)
        pause_btn = self.make_btn(self.t("pause"), self._pause, flat=True)
        resume_btn = self.make_btn(self.t("resume"), self._resume, flat=True)
        ctrl1.add_widget(start_btn)
        ctrl1.add_widget(pause_btn)
        ctrl1.add_widget(resume_btn)
        body.add_widget(ctrl1)

        ctrl2 = MDBoxLayout(size_hint_y=None, height=dp(52),
                             spacing=dp(8), padding=[dp(14), dp(4)])
        prev_btn = self.make_btn(self.t("previous"), self._prev, flat=True)
        next_btn = self.make_btn(self.t("next"), self._next)
        finish_btn = self.make_btn(self.t("finish"), self._finish, flat=True)
        ctrl2.add_widget(prev_btn)
        ctrl2.add_widget(next_btn)
        ctrl2.add_widget(finish_btn)
        body.add_widget(ctrl2)

        self._refresh_ex_ui()

    def _start(self, *args):
        if not self.running:
            self.running = True
            self._cancel_all()
            self.timer_ev = Clock.schedule_interval(self._tick, 1)

    def _pause(self, *args):
        self.running = False
        self._cancel_all()

    def _resume(self, *args):
        self._start()

    def _tick(self, dt):
        self.elapsed += 1
        m = self.elapsed // 60
        s = self.elapsed % 60
        self.timer_lbl.text = f"{m:02d}:{s:02d}"

    def _refresh_ex_ui(self):
        exercises = self.day["exercises"]
        if not exercises:
            return
        item = exercises[self.ex_index]
        ex = EXERCISES.get(item["key"], {})
        app = self.app()

        self.current_name_lbl.text = self.render(app.exercise_name(ex))
        self.current_desc_lbl.text = self.render(app.exercise_desc(ex))

        meta = self.lv(
            f"{self.t('sets')}: {item['sets']}  |  {self.t('reps')}: {item['reps']}  |  {self.t('rest')}: {item['rest']}",
            f"ست: {item['sets']}  |  تکرار: {item['reps']}  |  استراحت: {item['rest']}"
        )
        self.current_meta_lbl.text = self.render(meta)
        self.current_muscles_lbl.text = self.render(
            f"{self.t('target_muscles')}: {app.exercise_muscles(ex)}"
        )

        self.pb.value = self.ex_index + 1
        self.prog_lbl.text = self.render(
            f"{self.ex_index + 1} / {len(exercises)}"
        )

        self.ex_list_box.clear_widgets()
        for i, it in enumerate(exercises):
            ex_i = EXERCISES.get(it["key"], {})
            prefix = "✓ " if i < self.ex_index else ("➜ " if i == self.ex_index else "• ")
            col = (
                MoonColors.get("SUCCESS", self.is_dark()) if i < self.ex_index
                else (MoonColors.get("ACCENT", self.is_dark()) if i == self.ex_index
                      else MoonColors.get("TEXT2", self.is_dark()))
            )
            lbl = self.make_label(
                f"{prefix}{app.exercise_name(ex_i)}",
                style="Body2", color=col
            )
            self.ex_list_box.add_widget(lbl)

    def _next(self, *args):
        exs = self.day["exercises"]
        if self.ex_index < len(exs) - 1:
            self.ex_index += 1
            self.vibrate(0.04)
            self._refresh_ex_ui()

    def _prev(self, *args):
        if self.ex_index > 0:
            self.ex_index -= 1
            self._refresh_ex_ui()

    def _finish(self, *args):
        self._cancel_all()
        self.running = False
        duration = max(1, round(self.elapsed / 60))
        try:
            self.app().db.save_session(
                self.plan["plan_key"],
                self.app().day_title(self.day),
                duration, completed=1,
            )
        except Exception as e:
            print(f"[MOON] Session save error: {e}")

        self.vibrate(0.15)
        self._show_completion_dialog(duration)

    def _show_completion_dialog(self, duration):
        is_dark = self.is_dark()
        app = self.app()

        try:
            if app.dialog:
                app.dialog.dismiss()
        except Exception:
            pass

        dialog = MDDialog(
            title=self.render(self.t("congratulations")),
            text=self.render(
                self.t("workout_done_msg") + f"\n⏱ {duration} {self.t('minutes_short')}"
            ),
            buttons=[
                MDRaisedButton(
                    text=self.render(self.t("done")),
                    md_bg_color=MoonColors.get("BUTTON", is_dark),
                    theme_text_color="Custom",
                    text_color=MoonColors.get("BUTTON_TEXT", is_dark),
                    on_release=lambda x: self._close_dialog(dialog),
                ),
            ],
        )
        app.dialog = dialog
        dialog.open()

    def _close_dialog(self, dialog):
        try:
            dialog.dismiss()
        except Exception:
            pass
        self.show_msg(self.t("workout_completed"))
        self.app().refresh_screen("home")
        self.app().refresh_screen("progress")
        self.app().go_to("home")


class ProgressScreen(BaseScreen):
    def on_pre_enter(self, *args):
        self._build()

    def _build(self):
        body = self.scaffold(self.t("progress"), bottom_nav="progress", scroll=True)
        app = self.app()
        is_dark = self.is_dark()
        stats = app.db.get_session_stats()
        logs = app.db.get_progress_logs()
        weight_history = app.db.get_weight_history()

        summary = self.make_card()
        summary.add_widget(self.make_label(
            self.t("stats"), style="Subtitle1", bold=True,
            color=MoonColors.get("ACCENT", is_dark)
        ))
        row = MDBoxLayout(size_hint_y=None, height=dp(60), spacing=dp(12))
        row.add_widget(MoonStatCard(
            title=self.t("completed_workouts"),
            value=stats["total_sessions"],
            icon="check-circle-outline", dark=is_dark,
            accent_color=MoonColors.get("ACCENT", is_dark),
        ))
        row.add_widget(MoonStatCard(
            title=self.t("total_minutes"),
            value=stats["total_minutes"],
            icon="timer-outline", dark=is_dark,
            accent_color=MoonColors.get("GOLD", is_dark),
        ))
        summary.add_widget(row)
        body.add_widget(summary)

        chart_card = self.make_card(alt=True)
        chart_card.add_widget(self.make_label(
            self.t("weight_chart"), style="Subtitle1", bold=True,
            color=MoonColors.get("ACCENT2", is_dark)
        ))
        if len(weight_history) >= 2:
            chart = MoonProgressChart(
                data=weight_history, dark=is_dark, lang=app.language
            )
            chart_card.add_widget(chart)
            if weight_history:
                first_w = weight_history[0].get("weight", "—")
                last_w = weight_history[-1].get("weight", "—")
                diff = None
                try:
                    diff = round(float(last_w) - float(first_w), 1)
                except Exception:
                    pass
                if diff is not None:
                    diff_text = (f"▲ {diff} kg" if diff > 0 else f"▼ {abs(diff)} kg") if diff != 0 else "↔ 0 kg"
                    diff_color = (
                        MoonColors.get("ACCENT2", is_dark) if diff > 0
                        else MoonColors.get("SUCCESS", is_dark)
                    )
                    chart_card.add_widget(self.make_label(
                        self.lv(f"Change: {diff_text}", f"تغییر: {diff_text}"),
                        style="Caption", color=diff_color
                    ))
        else:
            chart_card.add_widget(self.make_label(
                self.t("no_chart_data"), secondary=True, center=True
            ))
        body.add_widget(chart_card)

        form = self.make_card()
        form.add_widget(self.make_label(
            self.t("body_metrics"), style="Subtitle1", bold=True,
            color=MoonColors.get("ACCENT", is_dark)
        ))
        self.w_f = self.make_field(self.t("weight"))
        self.waist_f = self.make_field(self.lv("Waist (cm)", "دور کمر (سانتی‌متر)"))
        self.hips_f = self.make_field(self.lv("Hips (cm)", "دور باسن (سانتی‌متر)"))
        self.arm_f = self.make_field(self.lv("Arm (cm)", "دور بازو (سانتی‌متر)"))
        self.chest_f = self.make_field(self.lv("Chest (cm)", "دور سینه (سانتی‌متر)"))
        self.note_f = MoonTextField(
            hint=self.t("note"), fa=self.is_fa(),
            dark=is_dark, multiline=True, height=dp(70),
        )
        self.note_f.size_hint_y = None
        self.note_f.height = dp(70)

        for f in [self.w_f, self.waist_f, self.hips_f,
                  self.arm_f, self.chest_f, self.note_f]:
            form.add_widget(f)

        form.add_widget(self.make_btn(self.t("save_log"), self._save))
        body.add_widget(form)

        hist_card = self.make_card(alt=True)
        hist_card.add_widget(self.make_label(
            self.t("history"), style="Subtitle1", bold=True,
            color=MoonColors.get("ACCENT", is_dark)
        ))
        if not logs:
            hist_card.add_widget(self.make_label(
                self.t("no_progress_yet"), secondary=True, center=True
            ))
        else:
            for item in logs[:15]:
                row_card = MDCard(
                    orientation="vertical",
                    padding=[dp(12), dp(10)], spacing=dp(4),
                    radius=[dp(14), dp(14), dp(14), dp(14)],
                    elevation=1,
                    md_bg_color=MoonColors.get("SURFACE", is_dark),
                    size_hint_y=None,
                )
                row_card.bind(minimum_height=row_card.setter("height"))
                row_card.add_widget(self.make_label(
                    item["log_date"], style="Caption", secondary=True
                ))
                parts = []
                if item.get("weight"):
                    parts.append(f"⚖ {item['weight']} kg")
                if item.get("waist"):
                    parts.append(self.lv(f"Waist {item['waist']}", f"کمر {item['waist']}"))
                if item.get("hips"):
                    parts.append(self.lv(f"Hips {item['hips']}", f"باسن {item['hips']}"))
                if item.get("arm"):
                    parts.append(self.lv(f"Arm {item['arm']}", f"بازو {item['arm']}"))
                if item.get("chest"):
                    parts.append(self.lv(f"Chest {item['chest']}", f"سینه {item['chest']}"))
                if parts:
                    row_card.add_widget(self.make_label(
                        "  |  ".join(parts), style="Body2",
                        color=MoonColors.get("SUCCESS", is_dark)
                    ))
                if item.get("note"):
                    row_card.add_widget(self.make_label(
                        item["note"], style="Body2", secondary=True
                    ))
                hist_card.add_widget(row_card)
        body.add_widget(hist_card)

    def _parse_float(self, val):
        val = val.strip()
        if not val:
            return None
        return float(val)

    def _save(self, *args):
        try:
            weight = self._parse_float(self.w_f.text)
            waist = self._parse_float(self.waist_f.text)
            hips = self._parse_float(self.hips_f.text)
            arm = self._parse_float(self.arm_f.text)
            chest = self._parse_float(self.chest_f.text)
        except ValueError:
            self.show_msg(self.t("invalid_number"))
            return

        note = self.note_f.text.strip()
        if all(v is None for v in [weight, waist, hips, arm, chest]) and not note:
            self.show_msg(self.t("field_required"))
            return

        try:
            self.app().db.save_progress(weight, waist, hips, arm, chest, note)
            self.vibrate()
            self.show_msg(self.t("progress_saved"))
            self.app().refresh_screen("home")
            self._build()
        except Exception as e:
            print(f"[MOON] Progress save error: {e}")
            self.show_msg(str(e))


class RemindersScreen(BaseScreen):
    def on_pre_enter(self, *args):
        self._build()

    def _build(self):
        body = self.scaffold(self.t("reminders"), back_to="settings", scroll=True)
        is_dark = self.is_dark()
        r = self.app().db.get_reminders()

        def switch_row(label_text, switch_widget):
            row = MDBoxLayout(size_hint_y=None, height=dp(50), spacing=dp(8))
            lbl = self.make_label(label_text, style="Body1")
            if self.is_fa():
                row.add_widget(switch_widget)
                row.add_widget(lbl)
            else:
                row.add_widget(lbl)
                row.add_widget(switch_widget)
            return row

        workout_card = self.make_card()
        workout_card.add_widget(self.make_label(
            self.t("workout_reminder"), style="Subtitle1", bold=True,
            color=MoonColors.get("ACCENT", is_dark)
        ))
        self.w_switch = MDSwitch(active=bool(r["workout_enabled"]))
        self.w_time = self.make_field(self.t("time"), r["workout_time"])
        workout_card.add_widget(switch_row(self.t("workout_reminder"), self.w_switch))
        workout_card.add_widget(self.w_time)

        notif_btn = self.make_btn(
            self.t("send_notification"),
            lambda x: self._send_workout_notif(), flat=True
        )
        workout_card.add_widget(notif_btn)
        body.add_widget(workout_card)

        hydration_card = self.make_card(alt=True)
        hydration_card.add_widget(self.make_label(
            self.t("hydration_reminder"), style="Subtitle1", bold=True,
            color=MoonColors.get("ACCENT2", is_dark)
        ))
        self.h_switch = MDSwitch(active=bool(r["hydration_enabled"]))
        self.h_time = self.make_field(self.t("time"), r["hydration_time"])
        hydration_card.add_widget(switch_row(self.t("hydration_reminder"), self.h_switch))
        hydration_card.add_widget(self.h_time)
        body.add_widget(hydration_card)

        prog_card = self.make_card()
        prog_card.add_widget(self.make_label(
            self.t("progress_reminder"), style="Subtitle1", bold=True,
            color=MoonColors.get("GOLD", is_dark)
        ))
        self.p_switch = MDSwitch(active=bool(r["progress_enabled"]))
        self.p_time = self.make_field(self.t("time"), r["progress_time"])
        prog_card.add_widget(switch_row(self.t("progress_reminder"), self.p_switch))
        prog_card.add_widget(self.p_time)
        body.add_widget(prog_card)

        body.add_widget(Widget(size_hint_y=None, height=dp(8)))
        body.add_widget(self.make_btn(self.t("save_preferences"), self._save))

    def _send_workout_notif(self):
        success = self.send_notification(
            self.t("notify_workout_title"),
            self.t("notify_workout_msg"),
        )
        self.show_msg(
            self.t("notification_sent") if success
            else self.t("notification_unavailable")
        )

    def _save(self, *args):
        try:
            self.app().db.save_reminders({
                "workout_enabled": self.w_switch.active,
                "workout_time": self.w_time.text.strip() or "18:00",
                "hydration_enabled": self.h_switch.active,
                "hydration_time": self.h_time.text.strip() or "12:00",
                "progress_enabled": self.p_switch.active,
                "progress_time": self.p_time.text.strip() or "20:00",
            })
            self.vibrate()
            self.show_msg(self.t("reminders_saved"))
        except Exception as e:
            print(f"[MOON] Reminder save error: {e}")


class SettingsScreen(BaseScreen):
    def on_pre_enter(self, *args):
        self._build()

    def _build(self):
        body = self.scaffold(self.t("settings"), bottom_nav="settings", scroll=True)
        app = self.app()
        is_dark = self.is_dark()

        lang_card = self.make_card()
        lang_card.add_widget(self.make_label(
            self.t("language"), style="Subtitle1", bold=True,
            color=MoonColors.get("ACCENT", is_dark)
        ))
        lang_row = MDBoxLayout(size_hint_y=None, height=dp(50), spacing=dp(8))
        en_btn = MDRaisedButton(
            text="🇬🇧  English",
            md_bg_color=(MoonColors.get("BUTTON", is_dark) if app.language == "en"
                         else MoonColors.get("CARD_ALT", is_dark)),
            theme_text_color="Custom",
            text_color=MoonColors.get("BUTTON_TEXT", is_dark),
            size_hint_x=1, elevation=3 if app.language == "en" else 1,
        )
        en_btn.bind(on_release=lambda x: self._set_lang("en"))

        fa_btn = MDRaisedButton(
            text="🇮🇷  فارسی",
            md_bg_color=(MoonColors.get("BUTTON", is_dark) if app.language == "fa"
                         else MoonColors.get("CARD_ALT", is_dark)),
            theme_text_color="Custom",
            text_color=MoonColors.get("BUTTON_TEXT", is_dark),
            size_hint_x=1, elevation=3 if app.language == "fa" else 1,
        )
        fa_btn.bind(on_release=lambda x: self._set_lang("fa"))
        lang_row.add_widget(en_btn)
        lang_row.add_widget(fa_btn)
        lang_card.add_widget(lang_row)
        body.add_widget(lang_card)

        theme_card = self.make_card(alt=True)
        theme_card.add_widget(self.make_label(
            self.t("theme"), style="Subtitle1", bold=True,
            color=MoonColors.get("GOLD", is_dark)
        ))
        theme_row = MDBoxLayout(size_hint_y=None, height=dp(50), spacing=dp(8))
        dark_btn = MDRaisedButton(
            text=f"🌙  {self.t('dark')}",
            md_bg_color=(MoonColors.get("BUTTON", is_dark) if is_dark
                         else MoonColors.get("CARD_ALT", is_dark)),
            theme_text_color="Custom",
            text_color=MoonColors.get("BUTTON_TEXT", is_dark),
            size_hint_x=1, elevation=3 if is_dark else 1,
        )
        dark_btn.bind(on_release=lambda x: self._set_theme("Dark"))

        light_btn = MDRaisedButton(
            text=f"☀️  {self.t('light')}",
            md_bg_color=(MoonColors.get("BUTTON", is_dark) if not is_dark
                         else MoonColors.get("CARD_ALT", is_dark)),
            theme_text_color="Custom",
            text_color=MoonColors.get("BUTTON_TEXT", is_dark),
            size_hint_x=1, elevation=3 if not is_dark else 1,
        )
        light_btn.bind(on_release=lambda x: self._set_theme("Light"))
        theme_row.add_widget(dark_btn)
        theme_row.add_widget(light_btn)
        theme_card.add_widget(theme_row)
        body.add_widget(theme_card)

        pref_card = self.make_card()
        pref_card.add_widget(self.make_label(
            self.lv("Preferences", "ترجیحات"), style="Subtitle1", bold=True,
            color=MoonColors.get("ACCENT2", is_dark)
        ))

        def sw_row(label_text, sw):
            row = MDBoxLayout(size_hint_y=None, height=dp(50), spacing=dp(8))
            lbl = self.make_label(label_text, style="Body1")
            if self.is_fa():
                row.add_widget(sw)
                row.add_widget(lbl)
            else:
                row.add_widget(lbl)
                row.add_widget(sw)
            return row

        self.vib_sw = MDSwitch(active=app.db.get_setting("vibration", "1") == "1")
        self.snd_sw = MDSwitch(active=app.db.get_setting("sound", "1") == "1")
        pref_card.add_widget(sw_row(self.t("vibration"), self.vib_sw))
        pref_card.add_widget(sw_row(self.t("sound"), self.snd_sw))
        pref_card.add_widget(self.make_btn(self.t("save"), self._save_prefs))
        body.add_widget(pref_card)

        links_card = self.make_card(alt=True)
        links_card.add_widget(self.make_label(
            self.lv("More", "بیشتر"), style="Subtitle1", bold=True
        ))
        links_row = MDBoxLayout(size_hint_y=None, height=dp(50), spacing=dp(8))
        links_row.add_widget(self.make_btn(
            self.t("reminders"),
            lambda x: app.go_to("reminders"), flat=True
        ))
        links_row.add_widget(self.make_btn(
            self.t("about"),
            lambda x: app.go_to("about"), flat=True
        ))
        links_card.add_widget(links_row)
        links_card.add_widget(self.make_btn(
            self.t("edit_profile"),
            lambda x: app.go_to("profile"), flat=True
        ))
        body.add_widget(links_card)

        reset_card = self.make_card()
        reset_card.add_widget(self.make_label(
            self.t("reset_data"), style="Subtitle1", bold=True,
            color=MoonColors.get("ERROR", is_dark)
        ))
        reset_card.add_widget(self.make_label(
            self.t("reset_warning"), style="Body2", secondary=True
        ))
        reset_card.add_widget(self.make_btn(
            self.t("reset_data"), self._show_reset_dialog
        ))
        body.add_widget(reset_card)

        ver_card = self.make_card(alt=True)
        ver_card.add_widget(self.make_label(
            f"MOON Fitness  •  {self.t('version')} 1.0",
            style="Caption", secondary=True, center=True
        ))
        ver_card.add_widget(self.make_label(
            self.t("made_with_love"), style="Caption",
            secondary=True, center=True
        ))
        body.add_widget(ver_card)

    def _set_lang(self, lang):
        self.app().set_language(lang)
        self.show_msg(self.t("language_saved"))

    def _set_theme(self, style):
        self.app().set_theme(style)
        self.show_msg(self.t("theme_saved"))

    def _save_prefs(self, *args):
        self.app().db.set_setting("vibration", "1" if self.vib_sw.active else "0")
        self.app().db.set_setting("sound", "1" if self.snd_sw.active else "0")
        self.vibrate()
        self.show_msg(self.t("settings_saved"))

    def _show_reset_dialog(self, *args):
        app = self.app()
        is_dark = self.is_dark()
        try:
            if app.dialog:
                app.dialog.dismiss()
        except Exception:
            pass

        dialog = MDDialog(
            title=self.render(self.t("reset_data")),
            text=self.render(self.t("reset_warning")),
            buttons=[
                MDFlatButton(
                    text=self.render(self.t("cancel")),
                    theme_text_color="Custom",
                    text_color=MoonColors.get("TEXT2", is_dark),
                    on_release=lambda x: dialog.dismiss()
                ),
                MDRaisedButton(
                    text=self.render(self.t("confirm")),
                    md_bg_color=MoonColors.get("ERROR", is_dark),
                    theme_text_color="Custom",
                    text_color="#FFFFFF",
                    on_release=lambda x: self._confirm_reset(dialog)
                ),
            ],
        )
        app.dialog = dialog
        dialog.open()

    def _confirm_reset(self, dialog):
        try:
            dialog.dismiss()
        except Exception:
            pass
        try:
            self.app().db.reset_user_data()
            self.app().language = "en"
            self.app().is_dark = True
            self.app().theme_cls.theme_style = "Dark"
            self.app().selected_plan_key = None
            self.app().current_workout_plan_key = None
            self.app().current_day_index = None
        except Exception as e:
            print(f"[MOON] Reset error: {e}")
        self.show_msg(self.t("reset_done"))
        self.app().go_to("onboarding")


class AboutScreen(BaseScreen):
    def on_pre_enter(self, *args):
        self._build()

    def _build(self):
        body = self.scaffold(self.t("about"), back_to="settings", scroll=True)
        is_dark = self.is_dark()

        hero = self.make_card()
        hero.add_widget(MDLabel(
            text="◐", font_size=sp(70), halign="center",
            size_hint_y=None, height=dp(90),
        ))
        hero.add_widget(self.make_label(
            "MOON Fitness", style="H4", bold=True, center=True,
            color=MoonColors.get("ACCENT", is_dark)
        ))
        hero.add_widget(self.make_label(
            self.t("app_subtitle"), style="Subtitle1", center=True, secondary=True
        ))
        hero.add_widget(self.make_label(
            self.t("app_slogan"), style="Body1", center=True,
            color=MoonColors.get("GOLD", is_dark)
        ))
        body.add_widget(hero)

        about_card = self.make_card(alt=True)
        about_card.add_widget(self.make_label(
            self.t("about_text"), style="Body1", secondary=True
        ))
        body.add_widget(about_card)

        feat_card = self.make_card()
        feat_card.add_widget(self.make_label(
            self.t("features_title"), style="Subtitle1", bold=True,
            color=MoonColors.get("ACCENT2", is_dark)
        ))
        for k in ["feature_1", "feature_2", "feature_3", "feature_4", "feature_5"]:
            feat_card.add_widget(self.make_label(
                self.t(k), style="Body2"
            ))
        body.add_widget(feat_card)

        ver_card = self.make_card(alt=True)
        ver_card.add_widget(self.make_label(
            f"{self.t('version')} 1.0  •  MOON Fitness",
            style="Caption", secondary=True, center=True
        ))
        ver_card.add_widget(self.make_label(
            self.t("made_with_love"),
            style="Caption", secondary=True, center=True,
            color=MoonColors.get("ACCENT2", is_dark)
        ))
        body.add_widget(ver_card)


class MoonFitnessApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = AppDB()
        self.language = self.db.get_setting("language", "en")
        theme_style = self.db.get_setting("theme_style", "Dark")
        self.is_dark = (theme_style == "Dark")
        self.selected_plan_key = None
        self.current_workout_plan_key = None
        self.current_day_index = None
        self.dialog = None
        self.sm = None

    def build(self):
        self.title = "MOON Fitness"
        self.theme_cls.primary_palette = "DeepPurple"
        self.theme_cls.accent_palette = "Pink"
        self.theme_cls.theme_style = "Dark" if self.is_dark else "Light"

        load_rtl_font()

        self.sm = MDScreenManager()
        screens = [
            SplashScreen(name="splash"),
            OnboardingScreen(name="onboarding"),
            ProfileSetupScreen(name="profile"),
            HomeScreen(name="home"),
            PlansScreen(name="plans"),
            PlanDetailScreen(name="plan_details"),
            WorkoutScreen(name="workout"),
            ProgressScreen(name="progress"),
            RemindersScreen(name="reminders"),
            SettingsScreen(name="settings"),
            AboutScreen(name="about"),
        ]
        for s in screens:
            self.sm.add_widget(s)
        self.sm.current = "splash"
        return self.sm

    def t(self, key, **kwargs):
        lang_map = TRANSLATIONS.get(self.language, TRANSLATIONS["en"])
        text = lang_map.get(key, TRANSLATIONS["en"].get(key, key))
        try:
            return text.format(**kwargs)
        except Exception:
            return text

    def render(self, text):
        if not text:
            return ""
        text = str(text)
        if self.language == "fa":
            return rtl_text(text)
        return text

    def show_message(self, text):
        try:
            rendered = self.render(str(text))
            Snackbar(
                text=rendered,
                snackbar_x=dp(8), snackbar_y=dp(8),
                size_hint_x=0.96,
                bg_color=MoonColors.get("CARD", self.is_dark),
            ).open()
        except Exception as e:
            print(f"[MOON] Snackbar error: {e} | msg: {text}")

    def go_to(self, screen_name):
        try:
            if self.sm and screen_name in [s.name for s in self.sm.screens]:
                self.sm.current = screen_name
        except Exception as e:
            print(f"[MOON] Navigation error to {screen_name}: {e}")

    def refresh_screen(self, screen_name):
        try:
            for s in self.sm.screens:
                if s.name == screen_name and hasattr(s, "_build"):
                    if self.sm.current == screen_name:
                        s._build()
        except Exception as e:
            print(f"[MOON] Refresh error for {screen_name}: {e}")

    def refresh_all(self):
        try:
            current = self.sm.current if self.sm else None
            for s in self.sm.screens:
                if hasattr(s, "_build") and s.name == current:
                    try:
                        s._build()
                    except Exception:
                        pass
        except Exception as e:
            print(f"[MOON] Refresh all error: {e}")

    def set_language(self, lang):
        self.language = lang
        self.db.set_setting("language", lang)
        self.refresh_all()

    def set_theme(self, style):
        self.is_dark = (style == "Dark")
        self.theme_cls.theme_style = style
        self.db.set_setting("theme_style", style)
        self.refresh_all()

    def diff_label(self, difficulty):
        mapping = {
            "Beginner": self.t("beginner"),
            "Intermediate": self.t("intermediate"),
            "Advanced": self.t("advanced"),
            "All Levels": self.t("all_levels"),
        }
        return mapping.get(difficulty, difficulty)

    def _local(self, item, en_key, fa_key):
        return item[fa_key] if self.language == "fa" else item[en_key]

    def plan_name(self, plan):
        return self._local(plan, "name_en", "name_fa") if plan else "—"

    def plan_desc(self, plan):
        return self._local(plan, "description_en", "description_fa") if plan else "—"

    def plan_goal(self, plan):
        return self._local(plan, "goal_en", "goal_fa") if plan else "—"

    def plan_target(self, plan):
        return self._local(plan, "target_en", "target_fa") if plan else "—"

    def day_title(self, day):
        return self._local(day, "title_en", "title_fa") if day else "—"

    def exercise_name(self, ex):
        return self._local(ex, "name_en", "name_fa") if ex else "—"

    def exercise_desc(self, ex):
        return self._local(ex, "desc_en", "desc_fa") if ex else "—"

    def exercise_muscles(self, ex):
        return self._local(ex, "muscles_en", "muscles_fa") if ex else "—"

    def recommend_plan_key(self, profile):
        goal = (profile.get("goal") or "").lower()
        fitness = (profile.get("fitness_level") or "").lower()
        workout = (profile.get("preferred_workout") or "").lower()
        equipment = (profile.get("equipment") or "").lower()
        limitations = (profile.get("limitations") or "").lower()
        try:
            days = int(profile.get("training_days") or 3)
        except Exception:
            days = 3

        injury_words = ["knee", "back", "injury", "pain", "زانو", "کمر", "درد", "آسیب"]
        fat_words = ["fat", "weight", "burn", "tone", "lose", "slim", "چربی", "لاغر", "فرم", "تناسب"]
        glute_words = ["glute", "booty", "core", "waist", "hip", "باسن", "شکم", "پهلو", "میان"]
        beginner_words = ["begin", "basic", "new", "start", "home", "مبتدی", "خانگی", "شروع", "ابتدا"]

        if any(w in limitations for w in injury_words):
            return "beginner_home"
        if any(w in goal for w in glute_words) or any(w in workout for w in glute_words):
            return "glutes_core"
        if any(w in goal for w in fat_words):
            return "fat_burn_tone"
        if (any(w in fitness for w in beginner_words)
                or days <= 3
                or "none" in equipment
                or "بدون" in equipment):
            return "beginner_home"
        return "full_body_fit"

    def ensure_recommended_plan(self):
        try:
            if self.db.get_active_plan():
                return
            profile = self.db.get_profile()
            if profile:
                self.db.set_active_plan(self.recommend_plan_key(profile))
        except Exception as e:
            print(f"[MOON] Recommend error: {e}")

    def open_plan_details(self, plan_key):
        self.selected_plan_key = plan_key
        self.go_to("plan_details")

    def get_today_day_index(self, plan):
        if not plan or not plan.get("days"):
            return 0
        return datetime.now().weekday() % len(plan["days"])

    def get_today_day(self, plan):
        idx = self.get_today_day_index(plan)
        return plan["days"][idx]

    def start_workout(self):
        try:
            if not self.db.get_profile():
                self.show_message(self.t("no_profile"))
                self.go_to("profile")
                return
            plan = self.db.get_active_plan()
            if not plan:
                self.show_message(self.t("no_active_plan"))
                self.go_to("plans")
                return
            self.current_workout_plan_key = plan["plan_key"]
            self.current_day_index = self.get_today_day_index(plan)
            self.go_to("workout")
        except Exception as e:
            print(f"[MOON] Start workout error: {e}")


if __name__ == "__main__":
    try:
        MoonFitnessApp().run()
    except Exception as e:
        print(f"[MOON] Critical error: {e}")
        import traceback
        traceback.print_exc()