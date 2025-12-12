import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
from tkcalendar import DateEntry
import tkinter.font as tkFont

import sounddevice as sd
from scipy.io.wavfile import write
import tempfile

import numpy as np
import re
import speech_recognition as sr
import json
import csv
from datetime import datetime, date, timedelta
import os
# JSON file path: keep JSON in same folder as this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATAFILE = os.path.join(BASE_DIR, "hostel_expenses.json")
print("USING JSON FILE:", DATAFILE)

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.patches as patches

# OCR imports
import pytesseract
import cv2
from PIL import Image, ImageTk

# Set Tesseract path (change if your install path is different)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ================== LANGUAGE & CATEGORY DEFINITIONS ==================
LANG = {
    'en': {
        'title': '🧾 Hostel Expense Tracker',
        'subtitle': '💰 with Roommate Split',
        'monthlylimit': '💳 Monthly Limit:',
        'savingsgoal': '🎯 Savings Goal:',
        'date': '📅 Date',
        'note': '📝 Note',
        'category': '🏷️ Category',
        'amount': '💰 Amount',
        'splittype': '👥 Split Type',
        'onlyme': '👤 Only Me',
        'shared': '🤝 Shared with Roommate (You paid half)',
        'thismonth': '📊 This Month Overview',
        'totalspent': '💸 Total Spent',
        'remaining': '💵 Remaining',
        'nolimit': '❌ No limit set',
        'withinlimit': '✅ Within limit',
        'overlimit': '⚠️ Over limit',
        'roommatetitle': '🤝 Roommate Balance',
        'roommatenone': '📭 No shared expenses yet',
        'roommateyouget': '💰 Roommate should pay you ₹{amt}',
        'roommateyoupay': '💸 You should pay roommate ₹{amt}',
        'roommatesettled': '🤝 You and roommate are settled!',
        'flowbtn': '📈 Limit Flowchart',
        'savingstitle': '💰 Savings Target',
        'savingsnotset': '⚠️ Savings Goal Not set',
        'savingstrack': '🎯 Savings Goal ₹{goal:.2f} - set a monthly limit to track better!',
        'savingsprogress': '💰 Saved ₹{saved:.2f} / ₹{goal:.2f}',
        'topcategorieslabel': '🏆 Top Categories',
        'nodata': '📭 No data',
        'avgperdaylabel': '📅 Average per day',
        'avgnone': '📅 Average per day -',
        'motivationtitle': '🧠 Spending Motivation',
        'motivationtext': '💡 Save more, smart!',
        'expensestitle': '📋 Expenses List',
        'btnsave': '💾 Save',
        'btnchart': '📊 Show Chart',
        'btnexport': '📤 Export CSV',
        'btndues': '📅 Dues',
        'btndelete': '🗑️ Delete',
        'btnnewmonth': '🆕 New Month',
        'btnvoice': '🎤 Voice Add'
    },
    'ta': {
        'title': '🧾 ஹாஸ்டல் செலவு டிராக்கர்',
        'subtitle': '💰 ரூம்மேட்டுடன் பகிர்வு',
        'monthlylimit': '💳 மாத வரம்பு:',
        'savingsgoal': '🎯 சேமிப்பு இலக்கு:',
        'date': '📅 தேதி',
        'note': '📝 குறிப்பு',
        'category': '🏷️ வகை',
        'amount': '💰 தொகை',
        'splittype': '👥 பகிர்வு வகை',
        'onlyme': '👤 எனக்கு மட்டும்',
        'shared': '🤝 ரூம்மேட்டுடன் பகிர் (நீயே அரை செலுத்தினாய்)',
        'thismonth': '📊 இந்த மாத சுருக்கம்',
        'totalspent': '💸 மொத்த செலவு',
        'remaining': '💵 மீதமுள்ளது',
        'nolimit': '❌ வரம்பு அமைக்கப்படவில்லை',
        'withinlimit': '✅ வரம்புக்குள்',
        'overlimit': '⚠️ வரம்பு மீறப்பட்டது',
        'roommatetitle': '🤝 ரூம்மேட் இருப்பு',
        'roommatenone': '📭 இதுவரை பகிர்ந்த செலவுகள் இல்லை',
        'roommateyouget': '💰 ரூம்மேட் உனக்கு ₹{amt} செலுத்த வேண்டும்',
        'roommateyoupay': '💸 நீ ரூம்மேட்டுக்கு ₹{amt} செலுத்த வேண்டும்',
        'roommatesettled': '🤝 நீயும் ரூம்மேட்டும் சமமாக உள்ளீர்கள்!',
        'flowbtn': '📈 வரம்பு ஃப்ளோசார்ட்',
        'savingstitle': '💰 சேமிப்பு இலக்கு',
        'savingsnotset': '⚠️ சேமிப்பு இலக்கு அமைக்கப்படவில்லை',
        'savingstrack': '🎯 சேமிப்பு இலக்கு ₹{goal:.2f} - மாத வரம்பு அமைக்கவும்!',
        'savingsprogress': '💰 சேமித்த ₹{saved:.2f} / ₹{goal:.2f}',
        'topcategorieslabel': '🏆 மேல் வகைகள்',
        'nodata': '📭 தரவு இல்லை',
        'avgperdaylabel': '📅 நாள் சராசரி',
        'avgnone': '📅 நாள் சராசரி -',
        'motivationtitle': '🧠 செலவு உந்துதல்',
        'motivationtext': '💡 அதிகம் சேமி, ஞானி!',
        'expensestitle': '📋 செலவுகள் பட்டியல்',
        'btnsave': '💾 சேமி',
        'btnchart': '📊 சார்ட் காட்டு',
        'btnexport': '📤 CSV ஏற்றுமதி',
        'btndues': '📅 கட்டணங்கள்',
        'btndelete': '🗑️ அழி',
        'btnnewmonth': '🆕 புதிய மாதம்',
        'btnvoice': '🎤 குரல் சேர்'
    }
}

CATEGORYDISPLAY = {
    'en': {
        'food': '🍚 Food',
        'mess': '🍲 Mess',
        'snacks': '🥪 Snacks',
        'transport': '🚌 Transport',
        'recharge': '📱 Recharge',
        'stationery': '📚 Stationery',
        'rent': '🏠 Rent',
        'utilities': '⚡ Utilities',
        'health': '💊 Health',
        'entertainment': '🎬 Entertainment',
        'clothes': '👕 Clothes',
        'personal_care': '🧴 Personal care',
        'others': '❓ Others'
    },
    'ta': {
        'food': '🍚 உணவு',
        'mess': '🍲 மெஸ்',
        'snacks': '🥪 ஸ்னாக்ஸ்',
        'transport': '🚌 போக்குவரத்து',
        'recharge': '📱 ரீசார்ஜ்',
        'stationery': '📚 ஸ்டேஷனரி',
        'rent': '🏠 வாடகை',
        'utilities': '⚡ பயன்பாடுகள்',
        'health': '💊 உடல்நலம்',
        'entertainment': '🎬 பொழுதுபோக்கு',
        'clothes': '👕 ஆடைகள்',
        'personal_care': '🧴 தனிப்பட்ட பராமரிப்பு',
        'others': '❓ மற்றவை'
    }
}

TAMILCATKEYWORDS = {
    'food': [
        # English
        'food', 'meal', 'meals', 'lunch', 'dinner', 'breakfast', 'brunch',
        'tiffin', 'canteen', 'mess food', 'hostel food',
        'biriyani', 'biryani', 'fried rice', 'noodles', 'idli', 'dosa',
        'parotta', 'poori', 'chapati', 'pulao', 'rice', 'sambar',
        'curry', 'veg', 'non veg', 'non-veg',
        'hotel', 'restaurant', 'dhaba', 'takeaway', 'take away',
        'parcel', 'swiggy', 'zomato', 'eat out', 'eating out',
        'combo', 'thali', 'meals combo', 'set meal',

        # Tamil
        'உணவு', 'சாப்பாடு', 'சாதம்', 'அரிசி', 'கறி',
        'மதிய உணவு', 'இரவு உணவு', 'காலை உணவு',
        'ஹோட்டல்', 'டைனிங்', 'டிபன்', 'டிஃபின்',
        'சாமான்', 'கேட்டரிங்', 'பிரியாணி', 'இட்லி', 'தோசை'
    ],

    'mess': [
        # English
        'mess', 'mess bill', 'mess fee', 'mess fees', 'mess charge',
        'mess charges', 'hostel mess', 'college mess', 'canteen mess',

        # Tamil
        'மெஸ்', 'மெஸ் பில்', 'மெஸ் கட்டணம்', 'ஹாஸ்டல் மெஸ்',
        'மெஸ் ஃபீஸ்', 'மெஸ் விலை', 'மெஸ் கட்டணங்கள்'
    ],

    'snacks': [
        # English
        'snack', 'snacks', 'evening snacks', 'tea time',
        'chips', 'lays', 'kurkure', 'puffs', 'puff',
        'biscuit', 'biscuits', 'cookie', 'cookies',
        'chocolate', 'chocolates', 'candy', 'toffee',
        'cake', 'cupcake', 'pastry', 'brownie',
        'ice cream', 'icecream', 'kulfi',
        'juice', 'cool drink', 'cold drink', 'soft drink', 'soda',
        'lassi', 'shake', 'milkshake',
        'chaat', 'samosa', 'pani puri', 'vada pav',
        'momos', 'fries', 'french fries',

        # Tamil
        'ஸ்நாக்ஸ்', 'ச்னாக்ஸ்', 'பஃப்ஸ்', 'பிஸ்கட்', 'சாக்லேட்',
        'கேக்', 'குக்கீ', 'சமோசா', 'பானி பூரி', 'வடை'
    ],

    'transport': [
        # English
        'bus', 'train', 'metro', 'tram',
        'auto', 'autorickshaw', 'cab', 'taxi', 'car', 'bike', 'scooter',
        'share auto', 'tempo', 'van',
        'ola', 'uber', 'rapido', 'ola bike', 'uber moto',
        'ticket', 'bus ticket', 'train ticket', 'platform ticket',
        'pass', 'bus pass', 'metro pass', 'monthly pass',
        'petrol', 'diesel', 'fuel', 'fuel bill', 'gas station',
        'parking', 'toll', 'highway toll', 'transport',

        # Tamil
        'போக்குவரத்து', 'பஸ்', 'ட்ரெயின்', 'ரயில்', 'ஆட்டோ',
        'கேப்', 'கார்', 'பைக்', 'ஸ்கூட்டர்', 'டிக்கெட்',
        'பஸ் பாஸ்', 'மெட்ரோ பாஸ்', 'பெட்ரோல்', 'டீசல்'
    ],

    'recharge': [
        # English
        'recharge', 'mobile recharge', 'phone recharge',
        'data', 'data pack', 'data add on', 'internet pack',
        'net pack', 'topup', 'top up', 'booster pack',
        'prepaid', 'postpaid', 'mobile bill', 'phone bill',
        'sim recharge', 'calling pack', 'unlimited pack',
        'jio', 'airtel', 'vi', 'vodafone idea', 'bsnl',

        # Tamil
        'ரீசார்ஜ்', 'மொபைல் ரீசார்ஜ்', 'டேட்டா', 'இன்டர்நெட்',
        'நெட் பேக்', 'ரீசார்ஜ் பேக்', 'ஜியோ', 'எயர்டெல்', 'வி', 'பிஎஸ்என்எல்'
    ],

    'stationery': [
        # English
        'pen', 'pens', 'pencil', 'pencils',
        'note', 'notes', 'notebook', 'note book',
        'rough book', 'class notes', 'register', 'long book',
        'diary', 'journal',
        'stationery', 'stationary',
        'scale', 'ruler', 'eraser', 'sharpener',
        'marker', 'highlighter', 'sketch', 'sketch pen',
        'file', 'folder', 'pouch', 'pocket file',
        'a4 paper', 'paper', 'sheets', 'graph sheet',
        'printout', 'xerox', 'photocopy',

        # Tamil
        'பென்', 'பென்சில்', 'நோட்', 'நோட்புக்', 'ரெஜிஸ்டர்',
        'ஸ்கேல்', 'ரப்பர்', 'மார்க்கர்', 'ஹைலைட்டர்'
    ],

    'rent': [
        # English
        'rent', 'room rent', 'house rent', 'hostel rent',
        'pg rent', 'pg room', 'sharing room',
        'accommodation', 'stay', 'lodging',
        'advance', 'deposit', 'security deposit',
        'maintenance charge', 'room maintenance',

        # Tamil
        'வாடகை', 'ரூம் வாடகை', 'ஹாஸ்டல் கட்டணம்',
        'ஹாஸ்டல் ஃபீஸ்', 'முன்பணம்', 'டெபாசிட்'
    ],

    'utilities': [
        # English
        'current', 'electricity', 'power', 'electric bill', 'eb bill',
        'electricity bill', 'light bill',
        'water', 'water bill', 'borewell', 'tank water',
        'wifi', 'wi-fi', 'broadband', 'internet bill',
        'fiber', 'jiofiber', 'airtel fiber',
        'gas', 'gas bill', 'cylinder', 'lpg',
        'dth', 'tv recharge', 'cable tv',
        'utilities', 'utility bill',

        # Tamil
        'மின்சாரம்', 'மின்பில்', 'ஈபி பில்', 'நீர்', 'ஜல கட்டணம்',
        'வைஃபை', 'பிராட்பேண்ட்', 'கேஸ்', 'சிலிண்டர்', 'கரண்ட்'
    ],

    'health': [
        # English
        'medicine', 'medicines', 'tablet', 'tablets', 'capsule',
        'syrup', 'tonic', 'drops',
        'doctor', 'dr', 'consultation', 'consulting fees',
        'hospital', 'clinic', 'nursing home',
        'pharmacy', 'medical shop', 'chemist',
        'test', 'lab test', 'blood test', 'scan', 'xray', 'x-ray',
        'checkup', 'health check', 'dentist', 'eye checkup',
        'first aid', 'bandage', 'ointment',

        # Tamil
        'மருந்து', 'டேப்லட்', 'சிரப்', 'டாக்டர்', 'கிளினிக்',
        'ஹாஸ்பிடல்', 'மெடிக்கல்', 'பாராசிட்டமால்', 'காய்ச்சல்', 'வலி'
    ],

    'entertainment': [
        # English
        'movie', 'movies', 'cinema', 'theatre', 'theater',
        'movie ticket', 'cinema ticket',
        'ott', 'ott app',
        'netflix', 'prime', 'amazon prime', 'hotstar',
        'disney', 'disney+', 'sony liv', 'zee5', 'aha',
        'spotify', 'wynk', 'gaana', 'music app',
        'game', 'games', 'gaming', 'steam', 'epic games',
        'pubg', 'bgmi', 'free fire',
        'concert', 'event', 'show', 'party',

        # Tamil
        'படம்', 'மூவி', 'தியேட்டர்', 'நெட்ஃப்ளிக்ஸ்', 'பிரைம்',
        'ஹாட்ஸ்டார்', 'ஓடிடி', 'கேம்', 'புப்ஜி', 'பிஜிஎம்ஐ'
    ],

    'clothes': [
        # English
        'shirt', 'tshirt', 't-shirt', 'formal shirt',
        'pant', 'pants', 'trouser', 'jeans', 'track pant',
        'dress', 'frock', 'kurta', 'kurti', 'salwar',
        'churidhar', 'churidar', 'saree', 'lehenga',
        'shoe', 'shoes', 'sneakers', 'sports shoes',
        'slipper', 'flipflop', 'flip-flop', 'sandal', 'chappal',
        'hoodie', 'jacket', 'sweater', 'coat',
        'cap', 'hat', 'socks', 'gloves',

        # Tamil
        'ஷர்ட்', 'டி ஷர்ட்', 'பேண்ட்', 'ஜீன்ஸ்', 'டிரஸ்',
        'சேர்ட்', 'சல்வார்', 'சால்வார்', 'ஷூ', 'சாண்டல்', 'சப்பல்'
    ],

    'personal_care': [
        # English
        'soap', 'body wash', 'face wash', 'facewash',
        'shampoo', 'conditioner', 'hair oil',
        'paste', 'toothpaste', 'brush', 'toothbrush',
        'cream', 'face cream', 'moisturizer',
        'lotion', 'body lotion', 'sunscreen',
        'sanitary', 'pads', 'napkin', 'tampon',
        'razor', 'blade', 'trimmer', 'shaving cream',
        'deodorant', 'deo', 'perfume', 'body spray',
        'tissue', 'wet wipes', 'wipes',
        'salon', 'parlour', 'parlor', 'haircut',

        # Tamil
        'சோப்பு', 'பாடி வாஷ்', 'ஷாம்பு', 'ஹேர் ஆயில்',
        'பேஸ்ட்', 'பல் தூரிகை', 'பிரஷ்',
        'க்ரீம்', 'லோஷன்', 'எண்ணெய்', 'ஃபேஸ்வாஷ்', 'ரேஸர்'
    ],

    'subscription': [
        # English
        'subscription', 'subs', 'sub',
        'netflix', 'prime video', 'amazon prime', 'hotstar',
        'disney+', 'sony liv', 'zee5', 'aha',
        'spotify', 'youtube premium', 'yt premium',
        'discord nitro', 'nitro',
        'google one', 'icloud', 'onedrive', 'office 365',
        'domain renewal', 'hosting renewal', 'app subscription',
        'membership', 'monthly plan', 'annual plan',

        # Tamil
        'சப்ஸ்க்ரிப்ஷன்', 'மேம்பாடு கட்டணம்'
    ],

    'rewards': [
        # English
        'reward', 'rewards', 'cashback', 'cash back',
        'offer', 'offers', 'discount', 'discounts',
        'coupon', 'coupons', 'promo', 'promo code',
        'voucher', 'gift card', 'gift voucher',
        'loyalty points', 'reward points',

        # Tamil
        'ரிவார்ட்', 'கேஷ்பேக்', 'கூப்பன்', 'டிஸ்கவுண்ட்'
    ],

    'others': [
        # English
        'other', 'others', 'misc', 'miscellaneous',
        'general', 'random', 'uncategorized', 'unknown',
        'etc', 'various', 'extra',

        # Tamil
        'மற்றவை', 'பிற செலவு', 'அன்னியம்'
    ]
}


class ExpenseApp:
    def __init__(self, root):
        self.root = root
        self.currentlanguage = 'en'  # default language
        
        # LOGIN SYSTEM VARIABLES
        self.current_user = None
        self.username = "admin"
        self.password = "1234"
        
        self.root.title('🧾 Hostel Expense Tracker')
        #self.root.withdraw()  # Hide main window initially

        # App data
        self.expenses = []
        self.monthlimit = 0.0
        self.savingsgoal = 0.0
        self.usedsavingswarningshown = False
        self.lastopened = None
        self.subscriptions = []
        self.loggingstreak = 0
        self.lastexpensedate = None
        self.lastsummarymonth = None
        
        # Show login first
        

    # ==================== LOGIN SYSTEM ====================
    def show_login(self):
        """Shows login window on app startup."""
        self.login_window = tk.Toplevel(self.root)
        self.login_window.title("🔐 Login - Hostel Expense Tracker")
        self.login_window.geometry("400x350")
        self.login_window.configure(bg='#020617')
        self.login_window.resizable(False, False)
        
        # Center the window
        self.login_window.transient(self.root)
        self.login_window.grab_set()
        self.login_window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Title
        title_frame = tk.Frame(self.login_window, bg='#15192b', pady=20)
        title_frame.pack(fill='x')
        tk.Label(title_frame, text="🧾 Hostel Expense Tracker", 
                 font=('Bahnschrift', 22, 'bold'), fg='#ffdd57', bg='#15192b').pack(pady=10)
        tk.Label(title_frame, text="💰 with Roommate Split", 
                 font=('Calibri', 12), fg='#e5e7eb', bg='#15192b').pack()
        
        # Login form
        form_frame = tk.Frame(self.login_window, bg='#111827', bd=2, relief='groove', padx=40, pady=30)
        form_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        tk.Label(form_frame, text="👤 Username", font=('Calibri', 12), fg='#ffd966', bg='#111827').pack(anchor='w', pady=(0,5))
        self.login_username = tk.Entry(form_frame, font=('Calibri', 12), width=20, justify='center', fg="black", bg="#020617")
        self.login_username.pack(pady=5)
       
        self.login_username.focus()
        # Password label
        tk.Label(
            form_frame,
            text="🔑 Password",
            font=('Calibri', 12),
            fg='#ffd966',
            bg='#111827'
        ).pack(anchor='w', pady=(20, 5))

        # Frame to hold password entry + eye button
        pass_frame = tk.Frame(form_frame, bg='#111827')
        pass_frame.pack(pady=5)

        self.login_password = tk.Entry(
            pass_frame,
            font=('Calibri', 12),
            width=17,          # slightly smaller to make space for eye
            show='*',
            justify='center',
            fg="black",
            bg="#020617"
        )
        self.login_password.pack(side='left')

        # eye toggle state
        self.pw_visible = False

        def toggle_password():
            if self.pw_visible:
                self.login_password.config(show='*')
                eye_btn.config(text="👁")
                self.pw_visible = False
            else:
                self.login_password.config(show='')
                eye_btn.config(text="🙈")
                self.pw_visible = True

        eye_btn = tk.Button(
            pass_frame,
            text="👁",
            font=('Segoe UI', 10, 'bold'),
            bg='#111827',
            fg='white',
            bd=0,
            activebackground='#111827',
            command=toggle_password
        )
        eye_btn.pack(side='left', padx=6)
        
                # ----- placeholders -----
        def set_user_ph(e=None):
            if not self.login_username.get():
                self.login_username.insert(0, "Username")
                self.login_username.config(fg="grey")

        def clear_user_ph(e=None):
            if self.login_username.get() == "Username":
                self.login_username.delete(0, tk.END)
            self.login_username.config(fg="white")

        def set_pass_ph(e=None):
            if not self.login_password.get():
                self.login_password.config(show="")  # show text while placeholder
                self.login_password.insert(0, "Password")
                self.login_password.config(fg="grey")

        def clear_pass_ph(e=None):
            if self.login_password.get() == "Password":
                self.login_password.delete(0, tk.END)
            self.login_password.config(fg="white", show="*")

        # bind focus events
        self.login_username.bind("<FocusIn>", clear_user_ph)
        self.login_username.bind("<FocusOut>", set_user_ph)

        self.login_password.bind("<FocusIn>", clear_pass_ph)
        self.login_password.bind("<FocusOut>", set_pass_ph)

        # initialize placeholders
        set_user_ph()
        set_pass_ph()
        
        
        # Buttons
        btn_frame = tk.Frame(form_frame, bg='#111827')
        btn_frame.pack(pady=25)
        
        tk.Button(btn_frame, text="✅ Login", font=('Segoe UI', 12, 'bold'), width=12,
                  bg='#00b894', fg='white', bd=0, pady=10, relief='flat',
                  command=self.login).pack(side='left', padx=8)
        
        tk.Button(btn_frame, text="🔄 Reset", font=('Segoe UI', 12, 'bold'), width=12,
                  bg='#f59e0b', fg='white', bd=0, pady=10, relief='flat',
                  command=self.reset_login).pack(side='right', padx=8)
        
        # Bind Enter key
        self.login_window.bind('<Return>', lambda e: self.login())
        self.login_username.bind('<Return>', lambda e: self.login_password.focus_set())
        self.login_password.bind('<Return>', lambda e: self.login())

    def login(self):
        """Validate login and show main app."""
        entered_user = self.login_username.get().strip()
        entered_pass = self.login_password.get().strip()
        if entered_user == "Username":
            entered_user = ""
        if entered_pass == "Password":
            entered_pass = ""        

        if entered_user == self.username and entered_pass == self.password:
            self.current_user = entered_user
            self.login_window.destroy()
            self.start_main_app()
        else:
            messagebox.showerror("❌ Login Failed", "Invalid username or password!\n\nDefault: admin / 1234")
            self.login_username.focus()

    def reset_login(self):
        """Reset login fields."""
        self.login_username.delete(0, tk.END)
        self.login_password.delete(0, tk.END)
        self.login_username.insert(0, "admin")
        self.login_password.insert(0, "1234")
        self.login_username.focus()
    def show_settings(self):
        """Settings window to change username/password."""
        settings_win = tk.Toplevel(self.root)
        settings_win.title("⚙️ User Settings")
        settings_win.geometry("450x420")  # slightly taller
        settings_win.configure(bg="#020617")
        settings_win.resizable(False, False)

        # Scrollable container
        canvas = tk.Canvas(settings_win, bg="#020617", highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(settings_win, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)

        inner = tk.Frame(canvas, bg="#111827", bd=2, relief="groove", padx=30, pady=30)
        canvas.create_window((0, 0), window=inner, anchor="nw")

        def _on_config(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        inner.bind("<Configure>", _on_config)

        tk.Label(
            inner,
            text="🔐 Account Settings",
            font=("Segoe UI Semibold", 16),
            fg="#ffdd57",
            bg="#111827",
        ).pack(pady=(0, 25))

        tk.Label(
            inner,
            text=f"👤 Current Username: {self.current_user}",
            font=("Calibri", 12),
            fg="#e5e7eb",
            bg="#111827",
        ).pack(anchor="w", pady=5)

        tk.Label(
            inner,
            text="👤 New Username:",
            font=("Calibri", 12),
            fg="#ffd966",
            bg="#111827",
        ).pack(anchor="w", pady=(25, 5))
        new_user_entry = tk.Entry(inner, font=("Calibri", 12), width=25)
        new_user_entry.pack(pady=5)
        new_user_entry.insert(0, self.username)

        tk.Label(
            inner,
            text="🔑 New Password:",
            font=("Calibri", 12),
            fg="#ffd966",
            bg="#111827",
        ).pack(anchor="w", pady=(20, 5))
        new_pass_entry = tk.Entry(inner, font=("Calibri", 12), width=25, show="*")
        new_pass_entry.pack(pady=5)

        tk.Label(
            inner,
            text="🔑 Confirm Password:",
            font=("Calibri", 12),
            fg="#ffd966",
            bg="#111827",
        ).pack(anchor="w", pady=(15, 5))
        confirm_pass_entry = tk.Entry(inner, font=("Calibri", 12), width=25, show="*")
        confirm_pass_entry.pack(pady=5)

        def save_settings():
            new_user = new_user_entry.get().strip()
            new_pass = new_pass_entry.get().strip()
            confirm_pass = confirm_pass_entry.get().strip()

            if not new_user or len(new_user) < 3:
                messagebox.showerror("❌ Error", "Username must be 3+ characters!")
                return
            if new_pass != confirm_pass:
                messagebox.showerror("❌ Error", "Passwords don't match!")
                return
            if len(new_pass) < 4:
                messagebox.showerror("❌ Error", "Password must be 4+ characters!")
                return

            self.username = new_user
            self.password = new_pass
            self.current_user = new_user
            self.savetofile()
            messagebox.showinfo(
                "✅ Saved",
                "Credentials updated successfully!\n\nLogin again to use new credentials.",
            )
            settings_win.destroy()

        tk.Button(
            inner,
            text="💾 Update Credentials",
            command=save_settings,
            font=("Segoe UI", 12, "bold"),
            bg="#00b894",
            fg="white",
            width=22,
            bd=0,
            pady=12,
            relief="flat",
        ).pack(pady=25)

    
    def start_main_app(self):
        """Create the actual main app window after login."""
        self.root.deiconify()  # Show main window
        self.root.geometry("1200x800")
        self.root.configure(bg="#020617")
        self.root.title(f"🧾 Hostel Expense Tracker - Welcome {self.current_user}")
        
        # Initialize UI
        self.init_ui()
        
        # Load data and refresh
        self.applylanguage()
        self.loadfromfile()
        self.refreshlist()
        self.updatesummary()
        self.refreshsubscriptionslist()
        self.checkdailyreminder()
        self.checksubscriptionreminders()
        self.showmonthsummaryifneeded()

    def init_ui(self):
        """Initialize main UI after login."""
        # -------- ttk Styles --------
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Limit.Horizontal.TProgressbar',
                       troughcolor='#020617', background='#22c55e',
                       bordercolor='#1f2937', lightcolor='#22c55e', darkcolor='#16a34a')
        style.configure('OverLimit.Horizontal.TProgressbar',
                       troughcolor='#020617', background='#ef4444',
                       bordercolor='#1f2937', lightcolor='#ef4444', darkcolor='#dc2626')
        style.configure('Savings.Horizontal.TProgressbar',
                       troughcolor='#020617', background='#22c55e',
                       bordercolor='#1f2937', lightcolor='#22c55e', darkcolor='#16a34a')

        # -------- Fonts --------
        self.titlefont = tkFont.Font(family='Bahnschrift', size=26, weight='bold')
        self.sectionfont = tkFont.Font(family='Segoe UI Semibold', size=14)
        self.labelfont = tkFont.Font(family='Calibri', size=12)
        self.buttonfont = tkFont.Font(family='Segoe UI', size=12, weight='bold')
        self.listfont = tkFont.Font(family='Cascadia Mono', size=12)

        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # -------- Left accent bar --------
        accent = tk.Frame(self.root, bg='#22c55e', width=4)
        accent.pack(side='left', fill='y')

        # -------- Main container --------
        self.container = tk.Frame(self.root, bg='#020617')
        self.container.pack(side='left', fill='both', expand=True)

        # -------- Menu bar --------
        menubar = tk.Menu(self.root, tearoff=0, font=self.labelfont)
        
        # Help menu
        helpmenu = tk.Menu(menubar, tearoff=0, font=self.labelfont)
        helpmenu.add_command(label='❓ How to use', command=self.showhelp)
        menubar.add_cascade(label='❓ Help', menu=helpmenu)
        
        # Settings menu
        settingsmenu = tk.Menu(menubar, tearoff=0, font=self.labelfont)
        settingsmenu.add_command(label='⚙️ Change Password', command=self.show_settings)
        settingsmenu.add_separator()
        settingsmenu.add_command(label='🚪 Logout', command=self.logout)
        menubar.add_cascade(label='⚙️ Settings', menu=settingsmenu)
        
        self.root.config(menu=menubar)

        # -------- Title frame --------
        titleframe = tk.Frame(self.container, bg='#15192b')
        titleframe.pack(side='top', fill='x', pady=5)

        self.titlelabel = tk.Label(titleframe, text='', font=self.titlefont,
                                   fg='#ffdd57', bg='#15192b')
        self.titlelabel.pack(side='left', padx=15, pady=5)

        self.subtitlelabel = tk.Label(titleframe, text='', font=self.labelfont,
                                      fg='#e5e7eb', bg='#15192b')
        self.subtitlelabel.pack(side='left', padx=10, pady=5)

        # User info
        userlabel = tk.Label(titleframe, text=f"👤 {self.current_user}", 
                            font=('Segoe UI', 11), fg='#10b981', bg='#15192b')
        userlabel.pack(side='right', padx=15, pady=5)

        # Language toggle button
        self.langbutton = tk.Button(
            titleframe, text='🇮🇳 EN | TA',
            font=('Segoe UI', 10, 'bold'),
            bg='#00b894', fg='white',
            activebackground='#019874', activeforeground='white',
            bd=0, padx=10, pady=4, relief='flat',
            command=self.togglelanguage
        )
        self.langbutton.pack(side='right', padx=10)

        # Continue with rest of UI creation
        self.create_main_ui()

    def create_main_ui(self):
        """Create the main UI components."""
        # -------- Limit and goal frame --------
        limitframe = tk.Frame(self.container, bg='#020617')
        limitframe.pack(side='top', fill='x', padx=15, pady=(4, 6))

        self.limitlabel = tk.Label(limitframe, text='', fg='#ffd966',
                                   bg='#020617', font=self.sectionfont)
        self.limitlabel.grid(row=0, column=0, sticky='w')

        self.limitentry = tk.Entry(limitframe, font=self.labelfont, width=14)
        self.limitentry.grid(row=0, column=1, padx=5)

        self.limitbtn = tk.Button(
            limitframe, text='✅ OK', font=self.buttonfont,
            bg='#0984e3', fg='white',
            activebackground='#0766b5', activeforeground='white',
            bd=0, padx=10, pady=6, relief='flat',
            command=self.setlimit
        )
        self.limitbtn.grid(row=0, column=2, padx=5)

        self.goallabel = tk.Label(limitframe, text='', fg='#ffd966',
                                  bg='#020617', font=self.sectionfont)
        self.goallabel.grid(row=0, column=3, sticky='w', padx=(25, 0))

        self.goalentry = tk.Entry(limitframe, font=self.labelfont, width=14)
        self.goalentry.grid(row=0, column=4, padx=5)
        self.goalbtn = tk.Button(
            limitframe, text='✅ OK', font=self.buttonfont,
            bg='#00b894', fg='white',
            activebackground='#019874', activeforeground='white',
            bd=0, padx=10, pady=6, relief='flat',
            command=self.setsavingsgoal
        )
        self.goalbtn.grid(row=0, column=5, padx=5)

        # -------- Dashboard --------
        dashboard = tk.Frame(self.container, bg='#020617')
        dashboard.pack(side='top', fill='x', padx=15, pady=(0, 6))
        dashboard.columnconfigure(0, weight=1)
        dashboard.columnconfigure(1, weight=1)
        dashboard.rowconfigure(0, weight=1)
        dashboard.rowconfigure(1, weight=1)

        cardbg = '#111827'

        # INPUT CARD
        inputframe = tk.Frame(dashboard, bg=cardbg, bd=2, relief='groove',
                              padx=18, pady=18)
        inputframe.grid(row=0, column=0, padx=6, pady=6, sticky='nsew')

        self.scanbtn = tk.Button(
            inputframe, text="📷 Scan Receipt",
            font=self.buttonfont, bg='#ff6b35', fg='#ffffff',
            activebackground='#e55a2b', activeforeground='#ffffff',
            bd=0, padx=12, pady=8, relief='flat',
            command=self.scanreceipt
        )
        self.scanbtn.grid(row=0, column=0, columnspan=2, pady=(0, 8), sticky='ew')

        pad = (10, 0)
        self.datelabel = tk.Label(inputframe, text='', fg='#ffd966',
                                  bg=cardbg, font=self.sectionfont)
        self.datelabel.grid(row=1, column=0, sticky='w', padx=pad, pady=4)

        self.notelabel = tk.Label(inputframe, text='', fg='#ffd966',
                                  bg=cardbg, font=self.sectionfont)
        self.notelabel.grid(row=2, column=0, sticky='w', padx=pad, pady=4)

        self.catlabel = tk.Label(inputframe, text='', fg='#ffd966',
                                 bg=cardbg, font=self.sectionfont)
        self.catlabel.grid(row=3, column=0, sticky='w', padx=pad, pady=4)

        self.amountlabel = tk.Label(inputframe, text='', fg='#ffd966',
                                    bg=cardbg, font=self.sectionfont)
        self.amountlabel.grid(row=4, column=0, sticky='w', padx=pad, pady=4)

        self.splitlabel = tk.Label(inputframe, text='', fg='#ffd966',
                                   bg=cardbg, font=self.sectionfont)
        self.splitlabel.grid(row=5, column=0, sticky='w', padx=pad, pady=4)

        self.dateentry = DateEntry(inputframe, date_pattern='dd-mm-yyyy',
                                   font=self.labelfont, width=16)
        self.dateentry.grid(row=1, column=1, padx=10, pady=4, sticky='w', ipady=2)

        self.noteentry = tk.Entry(inputframe, font=self.labelfont, width=26)
        self.noteentry.grid(row=2, column=1, padx=10, pady=4, sticky='w', ipady=2)

        self.catentry = tk.Entry(inputframe, font=self.labelfont, width=26)
        self.catentry.grid(row=3, column=1, padx=10, pady=4, sticky='w', ipady=2)

        self.amountentry = tk.Entry(inputframe, font=self.labelfont, width=26)
        
        self.amountentry.grid(row=4, column=1, padx=10, pady=4, sticky='w', ipady=2)

        self.splitvar = tk.StringVar(value='Only Me')
        self.splitcombo = ttk.Combobox(
            inputframe, textvariable=self.splitvar,
            values=['Only Me', 'Shared with Roommate (You paid half)'],
            state='readonly', font=self.labelfont, width=28
        )
        self.splitcombo.grid(row=5, column=1, padx=10, pady=4, sticky='w')

        self.dateentry.bind('<Return>', lambda e: self.noteentry.focus_set())
        self.noteentry.bind('<Return>', lambda e: self.autofillcategoryfromnote())
        self.catentry.bind('<Return>', lambda e: self.amountentry.focus_set())
        self.amountentry.bind('<Return>', lambda e: self.addexpense())
        self.dateentry.focus_set()

        # SUMMARY CARD
        self.summaryframebgnormal = '#26293a'
        self.summaryframebgalert = '#3b1f1f'

        summarytop = tk.Frame(dashboard, bg=self.summaryframebgnormal,
                              bd=2, relief='groove', padx=26, pady=16)
        summarytop.grid(row=0, column=1, padx=6, pady=6, sticky='nsew')
        self.summaryframe = summarytop

        summarytop.columnconfigure(0, weight=1)
        summarytop.columnconfigure(1, weight=1)
        summarytop.rowconfigure(4, weight=1)

        self.monthoverviewlabel = tk.Label(
            summarytop, text='', bg=self.summaryframebgnormal,
            fg='#ffdd57', font=self.sectionfont,
            anchor='w', wraplength=420
        )
        self.monthoverviewlabel.grid(row=0, column=0, columnspan=2,
                                     sticky='we', pady=(2, 10))

        self.totalspentlabel = tk.Label(
            summarytop, text='', bg=self.summaryframebgnormal,
            fg='white', font=self.labelfont, anchor='w'
        )
        self.totalspentlabel.grid(row=1, column=0, sticky='w', padx=4, pady=2)

        self.summarytotal = tk.Label(
            summarytop, text='₹0.00', bg=self.summaryframebgnormal,
            fg='#a5ff7a', font=self.labelfont, anchor='w'
        )
        self.summarytotal.grid(row=1, column=1, sticky='w', padx=4, pady=2)

        self.remaininglabel = tk.Label(
            summarytop, text='', bg=self.summaryframebgnormal,
            fg='white', font=self.labelfont, anchor='w'
        )
        self.remaininglabel.grid(row=2, column=0, sticky='w', padx=4, pady=2)

        self.summaryleft = tk.Label(
            summarytop, text='-', bg=self.summaryframebgnormal,
            fg='#a5ff7a', font=self.labelfont, anchor='w'
        )
        self.summaryleft.grid(row=2, column=1, sticky='w', padx=4, pady=2)

        self.limitprogressvar = tk.DoubleVar(value=0.0)
        self.limitprogress = ttk.Progressbar(
            summarytop, orient='horizontal', mode='determinate',
            maximum=100, variable=self.limitprogressvar, length=200,
            style='Limit.Horizontal.TProgressbar'
        )
        self.limitprogress.grid(row=3, column=0, columnspan=2,
                                sticky='we', padx=4, pady=4)

        self.summarystatus = tk.Label(
            summarytop, text='', bg=self.summaryframebgnormal,
            fg='white', font=self.labelfont, anchor='w'
        )
        self.summarystatus.grid(row=4, column=0, columnspan=2,
                                sticky='w', padx=4, pady=2)

        self.roommatetitlelabel = tk.Label(
            summarytop, text='', bg=self.summaryframebgnormal,
            fg='white', font=self.labelfont, anchor='w'
        )
        self.roommatetitlelabel.grid(row=5, column=0, sticky='w',
                                     padx=4, pady=2)

        self.roommatebalancelabel = tk.Label(
            summarytop, text='', bg=self.summaryframebgnormal,
            fg='#fcd34d', font=self.labelfont,
            anchor='w', wraplength=280
        )
        self.roommatebalancelabel.grid(row=5, column=1, sticky='w',
                                       padx=4, pady=2)

        self.flowbtn = tk.Button(
            summarytop, text='', font=('Segoe UI', 10, 'bold'),
            bg='#0984e3', fg='white',
            activebackground='#0766b5', bd=0,
            padx=12, pady=4, relief='flat',
            command=self.show_limit_flowchart
        )
        self.flowbtn.grid(row=6, column=0, columnspan=2, pady=8)

        # SAVINGS CARD
        savingsframe = tk.Frame(dashboard, bg=cardbg, bd=2, relief='groove',
                                padx=18, pady=18)
        savingsframe.grid(row=1, column=0, padx=6, pady=6, sticky='nsew')
        self.savingsframe = savingsframe

        self.savingstitlelabel = tk.Label(
            savingsframe, text='', bg=cardbg,
            fg='#ffdd57', font=self.sectionfont
        )
        self.savingstitlelabel.grid(row=0, column=0, columnspan=2,
                                    pady=(2, 6), sticky='w')

        self.savingslabel = tk.Label(
            savingsframe, text='', bg=cardbg,
            fg='#cbd5e1', font=self.labelfont,
            anchor='w', wraplength=280
        )
        self.savingslabel.grid(row=1, column=0, columnspan=2,
                               pady=(0, 6), sticky='w')

        self.savingsvar = tk.DoubleVar(value=0.0)
        self.savingsbar = ttk.Progressbar(
            savingsframe, orient='horizontal', mode='determinate',
            maximum=100, variable=self.savingsvar,
            style='Savings.Horizontal.TProgressbar'
        )
        self.savingsbar.grid(row=2, column=0, columnspan=2,
                             pady=(0, 8), sticky='ew')

        self.summarytoplabel = tk.Label(
            savingsframe, text='', bg=cardbg,
            fg='#cbd5e1', font=self.labelfont,
            anchor='w', wraplength=280
        )
        self.summarytoplabel.grid(row=3, column=0, columnspan=2,
                                  pady=(2, 4), sticky='w')

        self.summaryavglabel = tk.Label(
            savingsframe, text='', bg=cardbg,
            fg='#cbd5e1', font=self.labelfont,
            anchor='w', wraplength=280
        )
        self.summaryavglabel.grid(row=4, column=0, columnspan=2,
                                  pady=(0, 4), sticky='w')

        # INSIGHTS CARD
        insightsframe = tk.Frame(dashboard, bg=cardbg, bd=2, relief='groove',
                                 padx=18, pady=18)
        insightsframe.grid(row=1, column=1, padx=6, pady=6, sticky='nsew')

        self.motivationtitlelabel = tk.Label(
            insightsframe, text='', bg=cardbg,
            fg='#ffdd57', font=self.sectionfont
        )
        self.motivationtitlelabel.grid(row=0, column=0, pady=(2, 8), sticky='w')

        self.motivationlabel = tk.Label(
            insightsframe, text='', bg=cardbg,
            fg='#a5ff7a', font=self.sectionfont,
            justify='center'
        )
        self.motivationlabel.grid(row=1, column=0, pady=(6, 6))

        tk.Label(
            insightsframe,
            text='💡 TIP: Track shared expenses to avoid confusion with roommate.',
            bg=cardbg, fg='#ffdd57',
            font=tkFont.Font(family='Bahnschrift', size=11,
                             weight='bold', slant='italic'),
            justify='center', wraplength=260
        ).grid(row=2, column=0, pady=(0, 4), sticky='we')

        # EXPENSES LIST
        listframe = tk.Frame(self.container, bg='#020617', bd=1, relief='ridge')
        listframe.pack(side='left', fill='both', expand=True,
                       padx=15, pady=(0, 6))

        self.expensestitlelabel = tk.Label(
            listframe, text='', fg='#ffdd57',
            bg='#020617', font=self.sectionfont
        )
        self.expensestitlelabel.pack(anchor='w', pady=6, padx=8)

        self.listbox = tk.Listbox(
            listframe, bg='#020617', fg='#e5e7eb', font=self.listfont,
            selectbackground='#0984e3', selectforeground='white',
            borderwidth=0, highlightthickness=0
        )
        self.listbox.pack(fill='both', expand=True, pady=6, padx=6)
# BOTTOM BUTTONS
        bottom = tk.Frame(self.container, bg='#020617')
        bottom.pack(side='bottom', fill='x', padx=15, pady=(0, 8))

        self.btnsave = tk.Button(
            bottom, text='', font=self.buttonfont,
            bg='#00b894', fg='white',
            activebackground='#019874', bd=0,
            padx=10, pady=6, relief='flat',
            command=self.savetofile
        )
        self.btnsave.pack(side='left', padx=(0, 6))

        self.btnchart = tk.Button(
            bottom, text='', font=self.buttonfont,
            bg='#0984e3', fg='white',
            activebackground='#0766b5', bd=0,
            padx=10, pady=6, relief='flat',
            command=self.showchart
        )
        self.btnchart.pack(side='left', padx=6)

        self.btnexport = tk.Button(
            bottom, text='', font=self.buttonfont,
            bg='#f59e0b', fg='white',
            activebackground='#d97706', bd=0,
            padx=10, pady=6, relief='flat',
            command=self.exportcsv
        )
        self.btnexport.pack(side='left', padx=6)

        self.btndues = tk.Button(
            bottom, text='', font=self.buttonfont,
            bg='#8b5cf6', fg='white',
            activebackground='#7c3aed', bd=0,
            padx=10, pady=6, relief='flat',
            command=self.showdueswindow
        )
        self.btndues.pack(side='left', padx=(18, 6))

        self.btndelete = tk.Button(
            bottom, text='', font=self.buttonfont,
            bg='#d63031', fg='white',
            activebackground='#b02a28', bd=0,
            padx=10, pady=6, relief='flat',
            command=self.deleteselected
        )
        self.btndelete.pack(side='left', padx=6)

        self.btnnewmonth = tk.Button(
            bottom, text='', font=self.buttonfont,
            bg='#10b981', fg='white',
            activebackground='#059669', bd=0,
            padx=10, pady=6, relief='flat',
            command=self.newmonth
        )
        self.btnnewmonth.pack(side='left', padx=(6, 18))

        self.btnvoice = tk.Button(
            bottom, text='', font=self.buttonfont,
            bg='#ef4444', fg='white',
            activebackground='#dc2626', bd=0,
            padx=10, pady=6, relief='flat',
            command=self.voiceaddexpense
        )
        self.btnvoice.pack(side='right', padx=0)
    def savetofile(self):
        print("savetofile CALLED")
        print("DATAFILE =", DATAFILE)

        data = {
            'expenses': self.expenses,
            'monthlimit': self.monthlimit,
            'savingsgoal': self.savingsgoal,
            'lastopened': date.today().strftime('%d-%m-%Y'),
            'subscriptions': self.subscriptions,
            'loggingstreak': self.loggingstreak,
            'lastexpensedate': self.lastexpensedate.strftime('%d-%m-%Y') if self.lastexpensedate else None,
            'lastsummarymonth': self.lastsummarymonth,
            'username': self.username,
            # Save credentials
            'password': self.password
        }
        try:
            os.makedirs(os.path.dirname(DATAFILE), exist_ok=True)
            with open(DATAFILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print("WRITE OK")
            messagebox.showinfo("💾 Save", "Data saved successfully.")
        except Exception as e:
            print("WRITE ERROR:", e)
            messagebox.showerror("💾 Save Error", f"Could not save data: {e}")

    def loadfromfile(self):
        if not os.path.exists(DATAFILE):
            return
        try:
            with open(DATAFILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.expenses = data.get('expenses', [])
            self.monthlimit = data.get('monthlimit', 0.0)
            self.savingsgoal = data.get('savingsgoal', 0.0)
            self.lastopened = data.get('lastopened')
            self.subscriptions = data.get('subscriptions', [])
            self.loggingstreak = data.get('loggingstreak', 0)
            lastexp = data.get('lastexpensedate')
            if lastexp:
                try:
                    self.lastexpensedate = datetime.strptime(lastexp, '%d-%m-%Y').date()
                except ValueError:
                    pass
            self.lastsummarymonth = data.get('lastsummarymonth')
            self.username = data.get("username", "admin")
            self.password = data.get('password', "1234")
        except Exception:
            pass

    def setlimit(self):
        t = self.limitentry.get().strip()
        if not t:
            self.monthlimit = 0.0
            self.updatesummary()
            return
        try:
            v = float(t)
            if v < 0:
                raise ValueError
            self.monthlimit = v
            self.usedsavingswarningshown = False
            self.updatesummary()
            messagebox.showinfo("💳 Limit", f"Monthly limit set to ₹{v:.2f}")
        except ValueError:
            messagebox.showerror("❌ Error", "Enter a valid positive number for limit.")

    def setsavingsgoal(self):
        t = self.goalentry.get().strip()
        if not t:
            self.savingsgoal = 0.0
            self.updatesummary()
            return
        try:
            v = float(t)
            if v <= 0:
                raise ValueError
            self.savingsgoal = v
            self.usedsavingswarningshown = False
            self.updatesummary()
            self.savetofile() 
            messagebox.showinfo("🎯 Goal", f"Savings goal set to ₹{v:.2f}")
        except ValueError:
            messagebox.showerror("❌ Error", "Enter a valid positive number for goal.")
    def updatesummary(self):
        print("DEBUG: savingsvar exists?", hasattr(self, 'savingsvar'))  # ADD THIS
        print("DEBUG: savingslabel exists?", hasattr(self, 'savingslabel'))  # ADD 
        """Update all summary displays including savings progress"""
        self.summaryframebgnormal = '#26293a'
        self.summaryframebgalert = '#3b1f1f'
        L = LANG[self.currentlanguage]
        total = sum(e['amount'] for e in self.expenses)
        self.summarytotal.config(text=f"₹{total:.2f}")
        
        # Update monthly limit progress
        if self.monthlimit > 0:
            remaining = self.monthlimit - total
            spentpct = min(total / self.monthlimit * 100, 100)
            self.limitprogressvar.set(spentpct)
            over = remaining < 0
            cardbg = self.summaryframebgalert if over else self.summaryframebgnormal
            status = L['overlimit'] if over else L['withinlimit']
            colorval = '#ff7675' if over else '#a5ff7a'
            self.summaryleft.config(text=f"₹{remaining:.2f}", fg=colorval)
            self.summarystatus.config(text=status, fg=colorval)
            self.summaryframe.config(bg=cardbg)
            stylename = 'OverLimit.Horizontal.TProgressbar' if over else 'Limit.Horizontal.TProgressbar'
            self.limitprogress.configure(style=stylename)
            # Update card backgrounds safely
            for child in self.summaryframe.winfo_children():
                # Only configure bg for tk.Label or tk.Frame widgets
                if isinstance(child, (tk.Label, tk.Frame)):
                    child.config(bg=cardbg)
            self.summarytotal.config(bg=cardbg)
            self.summaryleft.config(bg=cardbg)
            if hasattr(self, 'roommatebalancelabel'):
                self.roommatebalancelabel.config(bg=cardbg)
        else:
            self.summarystatus.config(text=L['nolimit'])
        
        # Update roommate balance
        roommatebalance = 0.0
        for e in self.expenses:
            amt = e['amount']
            st = e.get('splittype', 'Only Me')
            if 'Shared' in st:
                roommatebalance += amt / 2.0
        if roommatebalance > 0:
            self.roommatebalancelabel.config(text=L['roommateyouget'].format(amt=roommatebalance), fg='#22c55e')
        elif roommatebalance < 0:
            self.roommatebalancelabel.config(text=L['roommateyoupay'].format(amt=abs(roommatebalance)), fg='#f97373')
        else:
            self.roommatebalancelabel.config(text=L['roommatesettled'], fg='#fcd34d')
        
        # FIXED: Update savings goal progress bar and label
        if self.savingsgoal > 0 and self.monthlimit > 0:
            dangerline = max(self.monthlimit - self.savingsgoal, 0)
            if total > dangerline:
                usedfromsavings = total - dangerline
                saved = max(self.savingsgoal - usedfromsavings, 0)
            else:
                saved = self.savingsgoal
            savingspct = (saved / self.savingsgoal) * 100
            self.savingsvar.set(savingspct)
            self.savingslabel.config(text=L['savingsprogress'].format(saved=saved, goal=self.savingsgoal))
        else:
            self.savingslabel.config(text=L['savingsnotset'])
            self.savingsvar.set(0)
        
        # Update average per day
        if self.expenses:
            dates = set()
            for e in self.expenses:
                try:
                    d = datetime.strptime(e['date'], '%d-%m-%Y').date()
                    dates.add(d)
                except ValueError:
                    continue
            days = (max(dates) - min(dates)).days + 1 if dates else 0
            avgperday = total / days if days > 0 else 0
            self.summaryavglabel.config(text=f"{L['avgperdaylabel']} ₹{avgperday:.0f}")
        else:
            self.summaryavglabel.config(text=L['avgnone'])    
        # Update top categories
        if self.expenses:
            cattotal = {}
            for e in self.expenses:
                cat = e['category']
                cattotal[cat] = cattotal.get(cat, 0) + e['amount']
            
            # Get top 3 categories
            sortedcats = sorted(cattotal.items(), key=lambda x: x[1], reverse=True)[:3]
            cattext = ", ".join([f"{cat}: ₹{amt:.0f}" for cat, amt in sortedcats])
            self.summarytoplabel.config(text=f"{L['topcategorieslabel']}: {cattext}")
        else:
            self.summarytoplabel.config(text=f"{L['topcategorieslabel']} {L['nodata']}")
                                    

    def refreshlist(self):
        self.listbox.delete(0, tk.END)
        catmap = CATEGORYDISPLAY.get(self.currentlanguage, {})
        for e in self.expenses:
            splitshort = 'Me' if e.get('splittype', 'Only Me') == 'Only Me' else 'Shared'
            dispcat = catmap.get(e['category'], e['category'])
            line = f"{e['date']} {dispcat[:12]} ₹{e['amount']:.2f} {splitshort} {e['note']}"
            self.listbox.insert(tk.END, line)

    def refreshsubscriptionslist(self):
        """Refresh subscriptions list (currently handled in dues window)."""
        pass

    def addexpense(self):
        datestr = self.dateentry.get()
        note = self.noteentry.get().strip()
        cat = self.catentry.get().strip().lower()
        if not cat and note:
            suggested = self.categorizenote(note)
            if suggested:
                cat = suggested

        try:
            amt = float(self.amountentry.get().strip())
            if amt <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("❌ Error", "Invalid amount")
            return

        if not cat:
            cat = 'others'

        splittype = self.splitvar.get()
        if 'shared' in splittype.lower():
            splittype = 'Shared with Roommate (You paid half)'
        else:
            splittype = 'Only Me'

        self.expenses.append({
            'date': datestr,
            'category': cat,
            'amount': amt,
            'note': note,
            'splittype': splittype
        })
        total = sum(x['amount'] for x in self.expenses)
        if self.monthlimit > 0 and total > self.monthlimit:
            messagebox.showwarning("⚠️ Limit Exceeded", f"Your total ₹{total:.2f} is above the monthly limit ₹{self.monthlimit:.2f}!")

        self.refreshlist()
        self.updatesummary()

        try:
            today = datetime.strptime(datestr, '%d-%m-%Y').date()
        except ValueError:
            today = date.today()

        if self.lastexpensedate is None:
            self.loggingstreak = 1
        else:
            diff = (today - self.lastexpensedate).days
            if diff == 0:
                pass
            elif diff == 1:
                self.loggingstreak += 1
            else:
                self.loggingstreak = 1
        self.lastexpensedate = today

        if self.loggingstreak in [3, 7, 30]:
            badge = {3: "3-day starter streak!", 7: "First week consistent logger!", 30: "30-day champion!"}
            messagebox.showinfo("🏆 Streak Badge", f"Logging streak: {self.loggingstreak} days!\n{badge[self.loggingstreak]}")

        messagebox.showinfo("✅ OK", "Expense added successfully!")
        self.noteentry.delete(0, tk.END)
        self.catentry.delete(0, tk.END)
        self.amountentry.delete(0, tk.END)
        self.noteentry.focus_set()

    def categorizenote(self, text):
        text = text.lower()
        words = re.split(r'[,. -]', text)
        for cat, kwlist in TAMILCATKEYWORDS.items():
            for kw in kwlist:
                kw = kw.lower()
                if kw in text or any(kw in w for w in words):
                    return cat
        return 'others'

    def autofillcategoryfromnote(self):
        note = self.noteentry.get().strip().lower()
        suggested = self.categorizenote(note)
        if suggested:
            self.catentry.delete(0, tk.END)
            self.catentry.insert(0, suggested)
            self.catentry.focus_set()

    def deleteselected(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showinfo("🗑️ Delete", "Select an expense to delete.")
            return
        idx = sel[0]
        if not messagebox.askyesno("🗑️ Delete", "Delete this expense?"):
            return
        try:
            del self.expenses[idx]
        except IndexError:
            messagebox.showerror("🗑️ Delete", "Could not delete item.")
            return
        self.refreshlist()
        self.updatesummary()
        messagebox.showinfo("🗑️ Delete", "Expense deleted.")

    def newmonth(self):
        if not messagebox.askyesno("🆕 New Month", "This will clear current expenses list.\nData is still saved in JSON. Continue?"):
            return
        self.expenses.clear()
        self.refreshlist()
        self.updatesummary()

    def showchart(self):
        if not self.expenses:
            messagebox.showinfo("📊 Chart", "No expenses to show yet.")
            return

        # Aggregate
        cattot = {}
        for e in self.expenses:
            cat = e['category']
            cattot[cat] = cattot.get(cat, 0) + e['amount']

        cats = list(cattot.keys())
        amounts = list(cattot.values())

        win = tk.Toplevel(self.root)
        win.title("📊 Expenses by Category")
        win.geometry("650x420")
        win.configure(bg='#020617')

        fig = Figure(figsize=(8, 5), facecolor='#020617')
        ax = fig.add_subplot(111)
        ax.set_facecolor('#020617')

        wedges, texts, autotexts = ax.pie(
            amounts,
            labels=cats,
            autopct='%1.1f%%',
            startangle=90,
            colors=['#ff6b35', '#0984e3', '#00b894', '#f59e0b', '#8b5cf6', '#10b981'],
            textprops={'color': 'white', 'fontsize': 10}  # make labels readable
        )

        for t in autotexts:
            t.set_color('#020617')   # dark color for percentage text inside slices

        ax.set_title("Expenses by Category", color='#ffdd57', fontsize=16, pad=20)
        ax.axis('equal')  # keep pie circular so labels position correctly

        fig.tight_layout(pad=2.0)  # reduce cropping of labels

        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=20, pady=20)
    
    def exportcsv(self):
        if not self.expenses:
            messagebox.showinfo("📤 Export", "No expenses to export.")
            return
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Export expenses to CSV"
        )
        if filepath:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['date', 'category', 'amount', 'note', 'splittype'])
                writer.writeheader()
                writer.writerows(self.expenses)
            messagebox.showinfo("📤 Export", f"Exported {len(self.expenses)} expenses to {filepath}")

    def showdueswindow(self):
        win = tk.Toplevel(self.root)
        win.title("📅 Bills & Subscriptions Dues")
        win.configure(bg='#020617')
        win.geometry("420x420")

        card = tk.Frame(win, bg='#111827', bd=2, relief='groove', padx=12, pady=10)
        card.pack(fill='both', expand=True, padx=10, pady=10)

        tk.Label(card, text="📅 Bills & Subscriptions", bg='#111827', fg='#ffdd57', font=self.sectionfont
                ).grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 6))

        tk.Label(card, text="Name", bg='#111827', fg='#e5e7eb', font=self.labelfont
                ).grid(row=1, column=0, sticky='w', pady=2)
        nameentry = tk.Entry(card, font=self.labelfont, width=18)
        nameentry.grid(row=1, column=1, pady=2, sticky='w')

        tk.Label(card, text="Amount", bg='#111827', fg='#e5e7eb', font=self.labelfont
                ).grid(row=2, column=0, sticky='w', pady=2)
        amountentry = tk.Entry(card, font=self.labelfont, width=18)
        amountentry.grid(row=2, column=1, pady=2, sticky='w')

        tk.Label(card, text="Due Date", bg='#111827', fg='#e5e7eb', font=self.labelfont
                ).grid(row=3, column=0, sticky='w', pady=2)
        dueentry = DateEntry(card, date_pattern='dd-mm-yyyy', font=self.labelfont, width=16)
        dueentry.grid(row=3, column=1, pady=2, sticky='w')

        tk.Label(card, text="Repeat", bg='#111827', fg='#e5e7eb', font=self.labelfont
                ).grid(row=4, column=0, sticky='w', pady=2)
        repeatvar = tk.StringVar(value='One-time')
        repeatcombo = ttk.Combobox(card, textvariable=repeatvar,
                                   values=['One-time', 'Monthly'], state='readonly',
                                   font=self.labelfont, width=15)
        repeatcombo.grid(row=4, column=1, pady=2, sticky='w')

        def addlocalsubscription():
            name = nameentry.get().strip()
            amounttext = amountentry.get().strip()
            duestr = dueentry.get()
            repeat = repeatvar.get()
            if not name:
                messagebox.showerror("❌ Error", "Enter a name for the bill/subscription.")
                return
            try:
                amt = float(amounttext)
                if amt <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("❌ Error", "Enter a valid positive amount.")
                return
            self.subscriptions.append({
                'name': name,
                'amount': amt,
                'duedate': duestr,
                'repeat': repeat
            })
            refreshlocallist()
            messagebox.showinfo("✅ Added", f"Bill '{name}' added.")
            nameentry.delete(0, tk.END)
            amountentry.delete(0, tk.END)

        tk.Button(card, text="➕ Add Bill", command=addlocalsubscription,
                  font=self.buttonfont, bg='#00b894', fg='white',
                  activebackground='#019874', activeforeground='white', bd=0,
                  padx=10, pady=4, relief='flat'
                 ).grid(row=5, column=0, columnspan=2, pady=6)

        tk.Label(card, text="📋 Upcoming Bills", bg='#111827', fg='#ffdd57', font=self.sectionfont
                ).grid(row=6, column=0, columnspan=2, sticky='w', pady=(4, 2))

        sublistbox = tk.Listbox(card, bg='#020617', fg='#e5e7eb', font=('Cascadia Mono', 10),
                                height=10, width=44, selectbackground='#0984e3')
        sublistbox.grid(row=7, column=0, columnspan=2, sticky='nsew', pady=2)

        def refreshlocallist():
            sublistbox.delete(0, tk.END)
            for s in self.subscriptions:
                line = f"{s['duedate']} {s['name'][:12]} ₹{s['amount']:.0f} {s['repeat']}"
                sublistbox.insert(tk.END, line)

        def deletelocalsubscription():
            sel = sublistbox.curselection()
            if not sel:
                messagebox.showinfo("🗑️ Delete", "Select a subscription to delete.")
                return
            idx = sel[0]
            if not messagebox.askyesno("🗑️ Delete", "Delete this bill/subscription?"):
                return
            try:
                del self.subscriptions[idx]
            except IndexError:
                messagebox.showerror("🗑️ Delete", "Could not delete subscription.")
                return
            refreshlocallist()
            messagebox.showinfo("🗑️ Delete", "Subscription deleted.")

        tk.Button(card, text="🗑️ Delete Selected", command=deletelocalsubscription,
                  font=self.buttonfont, bg='#d63031', fg='white',
                  activebackground='#b02a28', activeforeground='white', bd=0,
                  padx=10, pady=4, relief='flat'
                 ).grid(row=8, column=0, columnspan=2, pady=(4, 2))

        refreshlocallist()
    def checkdailyreminder(self):
        """Show warning for bills due within 3 days."""
        if not self.subscriptions:
            return

        today = date.today()
        soon = today + timedelta(days=3)
        duesoon = []

        for s in self.subscriptions:
            duestr = s.get("duedate")  # safe access
            if not duestr:
                continue
            try:
                d = datetime.strptime(duestr, "%d-%m-%Y").date()
            except ValueError:
                continue
            if today <= d <= soon:
                duesoon.append((s.get("name", "Bill"), s.get("amount", 0), d))

        if duesoon:
            lines = "\n".join(
                f"{d.strftime('%d-%m-%Y')} - {name} ₹{amt:.0f}"
                for name, amt, d in duesoon
            )
            messagebox.showwarning(
                "⚠️ Upcoming Bills",
                f"These bills are due within 3 days:\n{lines}",
            )
    def checksubscriptionreminders(self):
        """Show reminders for bills due today/tomorrow."""
        if not self.subscriptions:
            return

        today = date.today()
        tomorrow = today + timedelta(days=1)
        duetoday = []
        duetomorrow = []

        for s in self.subscriptions:
            duestr = s.get("duedate")
            if not duestr:
                continue
            try:
                d = datetime.strptime(duestr, "%d-%m-%Y").date()
            except ValueError:
                continue

            if d == today:
                duetoday.append((s.get("name", "Bill"), s.get("amount", 0), d))
            elif d == tomorrow:
                duetomorrow.append((s.get("name", "Bill"), s.get("amount", 0), d))

        if duetoday:
            lines = "\n".join(f"{name} ₹{amt:.0f}" for name, amt, d in duetoday)
            messagebox.showwarning("🚨 Bills Due TODAY", lines)
        elif duetomorrow:
            lines = "\n".join(f"{name} ₹{amt:.0f}" for name, amt, d in duetomorrow)
            messagebox.showwarning("⚠️ Bills Due Tomorrow", lines)

        # check again after 30 minutes
        self.root.after(30 * 60 * 1000, self.checksubscriptionreminders)

    
    def showmonthsummaryifneeded(self):
        if not self.expenses:
            return
        currentmonth = datetime.now().strftime('%Y-%m')
        if self.lastsummarymonth != currentmonth:
            totalspent = sum(e['amount'] for e in self.expenses)
            dates = set()
            for e in self.expenses:
                try:
                    d = datetime.strptime(e['date'], '%d-%m-%Y').date()
                    dates.add(d)
                except ValueError:
                    continue
            days = (max(dates) - min(dates)).days + 1 if dates else 0
            avgperday = totalspent / days if days > 0 else 0
            messagebox.showinfo("📊 Monthly Summary",
                f"Total Spent: ₹{totalspent:.2f}\n"
                f"Days tracked: {days}\n"
                f"Average per day: ₹{avgperday:.2f}")
            self.lastsummarymonth = currentmonth

    def show_limit_flowchart(self):
        total = sum(e["amount"] for e in self.expenses)

        win = tk.Toplevel(self.root)
        win.title("📊 Monthly Limit Flowchart")
        win.geometry("700x500")
        win.configure(bg="#020617")

        fig = Figure(figsize=(8, 6), dpi=100, facecolor="#020617")
        ax = fig.add_subplot(111)
        ax.set_facecolor("#020617")

        limit_pct = (total / self.monthlimit * 100) if self.monthlimit > 0 else 0

        if limit_pct <= 75:
            status_color = "#22c55e"
            status_text = "✅ SAFE ZONE"
        elif limit_pct <= 100:
            status_color = "#f59e0b"
            status_text = "⚠️  CAUTION"
        else:
            status_color = "#ef4444"
            status_text = "❌ OVER LIMIT"

        y_pos = 0.8
        box_height = 0.12

        ax.add_patch(patches.FancyBboxPatch(
            (0.1, y_pos), 0.3, box_height,
            boxstyle="round,pad=0.02",
            facecolor="#3b82f6", edgecolor="white",
            linewidth=2, alpha=0.9
        ))
        ax.text(
            0.25, y_pos + box_height / 2, "Monthly Limit\nSet",
            ha="center", va="center",
            fontsize=12, fontweight="bold", color="white"
        )

        ax.add_patch(patches.FancyBboxPatch(
            (0.55, y_pos), 0.35, box_height,
            boxstyle="round,pad=0.02",
            facecolor="#10b981", edgecolor="white",
            linewidth=2, alpha=0.9
        ))
        ax.text(
            0.725, y_pos + box_height / 2, f"Spent\n₹{total:.0f}",
            ha="center", va="center",
            fontsize=12, fontweight="bold", color="white"
        )

        ax.annotate(
            '', xy=(0.4, y_pos + box_height / 2),
            xytext=(0.55, y_pos + box_height / 2),
            arrowprops=dict(arrowstyle='->', lw=3, color='white')
        )

        y_pos -= 0.2

        ax.add_patch(patches.FancyBboxPatch(
            (0.25, y_pos), 0.5, box_height,
            boxstyle="round,pad=0.02",
            facecolor=status_color, edgecolor="white",
            linewidth=3, alpha=0.95
        ))
        ax.text(
            0.5, y_pos + box_height / 2,
            f"{status_text}\n{limit_pct:.1f}% used",
            ha="center", va="center",
            fontsize=14, fontweight="bold", color="white"
        )

        ax.add_patch(patches.Rectangle(
            (0.1, y_pos - 0.05),
            min(limit_pct / 100 * 0.8, 0.8), 0.03,
            facecolor=status_color, alpha=0.8
        ))
        ax.text(
            0.5, y_pos - 0.08,
            f"Progress: {limit_pct:.1f}%",
            ha="center", va="center",
            fontsize=11, color="#e5e7eb"
        )

        remaining = self.monthlimit - total if self.monthlimit > 0 else 0
        ax.text(
            0.5, y_pos - 0.18,
            f"Remaining: ₹{remaining:.0f}",
            ha="center", va="center",
            fontsize=12, fontweight="bold",
            color="#10b981" if remaining >= 0 else "#ef4444"
        )

        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        ax.set_title(
            "Monthly Budget Flowchart",
            fontsize=20, color="#ffdd57", pad=20
        )

        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=20)


    def togglelanguage(self):
        self.currentlanguage = 'ta' if self.currentlanguage == 'en' else 'en'
        self.applylanguage()
        self.refreshlist()
        self.updatesummary()

    def applylanguage(self):
        L = LANG[self.currentlanguage]
        self.root.title(L['title'])
        self.titlelabel.config(text=L['title'])
        self.subtitlelabel.config(text=L['subtitle'])

        self.limitlabel.config(text=L['monthlylimit'])
        self.goallabel.config(text=L['savingsgoal'])
        self.limitbtn.config(text='✅ OK')
        self.goalbtn.config(text='✅ OK')

        self.datelabel.config(text=L['date'])
        self.notelabel.config(text=L['note'])
        self.catlabel.config(text=L['category'])
        self.amountlabel.config(text=L['amount'])
        self.splitlabel.config(text=L['splittype'])
        self.splitcombo['values'] = [L['onlyme'], L['shared']]
        if self.splitvar.get() not in [L['onlyme'], L['shared']]:
            self.splitvar.set(L['onlyme'])

        self.monthoverviewlabel.config(text=L['thismonth'])
        self.totalspentlabel.config(text=L['totalspent'])
        self.remaininglabel.config(text=L['remaining'])
        self.summarystatus.config(text=L['nolimit'])
        self.roommatetitlelabel.config(text=L['roommatetitle'])
        self.flowbtn.config(text=L['flowbtn'])

        self.savingstitlelabel.config(text=L['savingstitle'])
        if self.savingsgoal == 0:
            self.savingslabel.config(text=L['savingsnotset'])
        self.summarytoplabel.config(text=f"{L['topcategorieslabel']}: {L['nodata']}")
        self.summaryavglabel.config(text=L['avgnone'])

        self.motivationtitlelabel.config(text=L['motivationtitle'])
        self.motivationlabel.config(text=L['motivationtext'])
        self.expensestitlelabel.config(text=L['expensestitle'])

        self.btnsave.config(text=L['btnsave'])
        self.btnchart.config(text=L['btnchart'])
        self.btnexport.config(text=L['btnexport'])
        self.btndues.config(text=L['btndues'])
        self.btndelete.config(text=L['btndelete'])
        self.btnnewmonth.config(text=L['btnnewmonth'])
        self.btnvoice.config(text=L['btnvoice'])

    def detectamountfromtext(self, text):
        text = text.lower().strip()
        patterns = [
            r'(\d+(?:,\d{2,3})*(?:\.?\d{1,2})?)\s*(?:rs|rupees|ரூ|ரூபாய்|rupee)?',
            r'(?:₹|ரூ)\s*(\d+(?:,\d{2,3})*(?:\.?\d{1,2})?)',
            r'(\d+)\s*(?:rs|rupees|ரூ|ரூபாய்)',
        ]
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                s = re.sub(r'[^0-9.]', '', match)
                try:
                    v = float(s)
                    if 0 < v < 100000:
                        return v
                except ValueError:
                    continue

        number_words = {
            'twenty': 20, 'thirty': 30, 'forty': 40, 'fifty': 50,
            'sixty': 60, 'seventy': 70, 'eighty': 80, 'ninety': 90,
            'hundred': 100, 'thousand': 1000
        }
        words = text.split()
        for i, w in enumerate(words):
            if w in number_words:
                v = number_words[w]
                if i + 1 < len(words) and 'rupee' in words[i + 1]:
                    return v
        return None

    def detectcategoryfromtext(self, text):
        text = text.lower()
        words = re.split(r'[,. -]', text)
        for cat, kwlist in TAMILCATKEYWORDS.items():
            for kw in kwlist:
                kw = kw.lower()
                if kw in text or any(kw in w for w in words):
                    return cat
        return 'others'

    def voiceaddexpense(self):
        recognizer = sr.Recognizer()
        fs = 16000
        duration = 4
        try:
            messagebox.showinfo("🎤 Voice Input", "Speak your expense:\n\"120 rupees food\" or \"50 rs mess\" or \"25 auto\"")
            messagebox.showinfo("🔴 Recording", f"Recording for {duration} seconds...")
            audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
            sd.wait()
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tempwav:
                write(tempwav.name, fs, audio)
                temp_path = tempwav.name 
            texten = ''
            textta = ''
            try:
                with sr.AudioFile(tempwav.name) as source:
                    recorded = recognizer.record(source)
                    texten = recognizer.recognize_google(recorded, language='en-IN').strip()
            except sr.UnknownValueError:
                texten = ''
            try:
                with sr.AudioFile(tempwav.name) as source:
                    recorded = recognizer.record(source)
                    textta = recognizer.recognize_google(recorded, language='ta-IN').strip()
            except sr.UnknownValueError:
                textta = ''
            os.unlink(tempwav.name)
            text = texten or textta
            if not text:
                messagebox.showerror("❌ Error", "Could not understand speech.")
                return
            todaydate = date.today().strftime('%d-%m-%Y')
            self.dateentry.set_date(todaydate)
            amount = self.detectamountfromtext(text)
            if amount is None:
                messagebox.showerror("❌ Error", "Amount not found in your voice.\n\"120 rupees food\" or \"50 rs mess\"")
                return
            category = self.detectcategoryfromtext(text)
            self.expenses.append({
                'date': todaydate,
                'category': category,
                'amount': amount,
                'note': text,
                'splittype': 'Only Me'
            })
            self.refreshlist()
            self.updatesummary()
            catmap = CATEGORYDISPLAY.get(self.currentlanguage, {})
            disp = catmap.get(category, category)
            messagebox.showinfo("✅ Added", f"₹{amount:.2f} added in {disp}\nDate set to TODAY\n{text}")
        except Exception as e:
            messagebox.showerror("❌ Error", f"Voice input failed: {e}")

    def scanreceipt(self):
        filepath = filedialog.askopenfilename(
            title="Select Receipt Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff"), ("All files", "*.*")]
        )
        if not filepath:
            return

        progresswin = None
        try:
            progresswin = tk.Toplevel(self.root)
            progresswin.title("Scanning Receipt...")
            progresswin.geometry("300x100")
            progresswin.configure(bg='#020617')
            tk.Label(progresswin, text="Processing receipt with AI OCR...",
                     fg='#ffdd57', bg='#020617', font=('Segoe UI', 12)
                    ).pack(expand=True)
            self.root.update()

            extracted = self.processreceiptimage(filepath)
            if progresswin:
                progresswin.destroy()

            if extracted:
                self.populatefromocr(extracted)
                messagebox.showinfo("✅ Receipt Scanned!",
                    f"AI extracted:\n"
                    f"Date: {extracted['date']}\n"
                    f"Amount: ₹{extracted['amount']:.2f}\n"
                    f"Category: {extracted['category']}\n"
                    f"Note: {extracted['note'][:50]}...")
            else:
                messagebox.showwarning("⚠️ OCR Failed", "Could not extract data from receipt. Please enter manually.")
        except Exception as e:
            try:
                if progresswin:
                    progresswin.destroy()
            except:
                pass
            messagebox.showerror("❌ OCR Error", f"Failed to process image: {e}\n\nInstall: pip install pytesseract opencv-python pillow")

    def processreceiptimage(self, imagepath):
        img = cv2.imread(imagepath)
        if img is None:
            return None
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray1 = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        gray1 = cv2.GaussianBlur(gray1, (3, 3), 0)
        gray2 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        fulltext = pytesseract.image_to_string(gray1).lower().strip()
        if not re.search(r'[\d.,]', fulltext):
            numbersonly = pytesseract.image_to_string(gray2, config='--psm 8 -c tessedit_char_whitelist=0123456789.,Rs')
            fulltext = numbersonly.lower()

        extracted = {}
        extracted['date'] = self.extractdate(fulltext)
        extracted['amount'] = self.extractamount(fulltext)
        extracted['category'] = self.autocategorize(fulltext)
        extracted['note'] = self.extractnote(fulltext)

        if extracted['amount'] == 0 or not extracted['note']:
            return None
        return extracted

    def extractdate(self, text):
        patterns = [r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b', r'\b(\d{1,2}[-/][a-z]{3,})\b']
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).replace('/', '-')
        return date.today().strftime('%d-%m-%Y')

    def extractamount(self, text):
        lines = text.split('\n')
        best = 0.0

        def lastnumber(line):
            nums = re.findall(r'[\d,.?]+', line)
            if not nums:
                return None
            s = nums[-1].replace(',', '')
            try:
                v = float(s)
                return v
            except ValueError:
                return None

        for line in lines:
            l = line.lower()
            if 'total' in l and 'amount' in l and 'paid' in l:
                v = lastnumber(line)
                if v is not None:
                    return v
        for line in lines:
            l = line.lower()
            if 'recharge' in l or 'amount' in l and 'total' in l:
                v = lastnumber(line)
                if v is not None:
                    best = max(best, v)
        return best

    def extractnote(self, text):
        lines = text.split('\n')
        for line in lines[:5]:
            line = line.strip()
            if len(line) > 3 and re.search(r'[a-z]', line) and not re.match(r'^\d', line):
                return line[:100].title()
        return "Receipt"

    def autocategorize(self, text):
        text = text.lower()
        words = re.split(r'[,. -]', text)
        for cat, kwlist in TAMILCATKEYWORDS.items():
            for kw in kwlist:
                kw = kw.lower()
                if kw in text or any(kw in w for w in words):
                    return cat
        return 'others'

    def populatefromocr(self, extracted):
        if extracted['date']:
            self.dateentry.set_date(extracted['date'])
        self.noteentry.delete(0, tk.END)
        self.noteentry.insert(0, extracted['note'])
        self.catentry.delete(0, tk.END)
        self.catentry.insert(0, extracted['category'])
        self.amountentry.delete(0, tk.END)
        self.amountentry.insert(0, f"{extracted['amount']:.2f}")

    def showhelp(self):
        messagebox.showinfo("❓ How to use",
            "1. Set Monthly Limit and optional Savings Goal\n"
            "2. Add expenses manually or use Voice/Scan\n"
            "3. Track roommate shared expenses\n"
            "4. View charts, export CSV, manage dues\n"
            "5. Switch EN/TA languages\n\n"
            "Default login: admin / 1234")

    def logout(self):
        """Logout and return to login screen."""
        if messagebox.askyesno("🚪 Logout", "Logout and return to login?"):
            self.root.withdraw()
            self.show_login()

    def on_closing(self):
        """Handle app closing."""
        if messagebox.askokcancel("❌ Quit", "Do you want to quit?"):
            self.savetofile()
            self.root.destroy()

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseApp(root)
    app.loadfromfile()
    app.show_login()
    root.mainloop()