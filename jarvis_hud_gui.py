import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import speech_recognition as sr
import pyttsx3
import datetime
import wikipedia
import webbrowser
import pywhatkit
import smtplib
import os
import subprocess
import threading
import platform
import shutil
import psutil
import requests
import feedparser





# Initialize TTS and recognizer
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id) 
listener = sr.Recognizer()

EMAIL_ADDRESS = os.getenv('JARVIS_EMAIL')
EMAIL_PASSWORD = os.getenv('JARVIS_PASSWORD')

exit_event = threading.Event()
root = None  # will be assigned in main

def talk(text):
    engine.say(text)
    engine.runAndWait()

def greet_user():
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12:
        greeting = "Good morning!"
    elif 12 <= hour < 17:
        greeting = "Good afternoon!"
    elif 17 <= hour < 22:
        greeting = "Good evening!"
    else:
        greeting = "Hello!"
    talk(f"{greeting} I am Jarvis. How can I assist you?")

def take_command():
    try:
        with sr.Microphone() as source:
            listener.adjust_for_ambient_noise(source)
            print("Listening...")
            audio = listener.listen(source, timeout=5, phrase_time_limit=10)
            command = listener.recognize_google(audio).lower()
            if 'jarvis' in command:
                return command.replace('jarvis', '').strip()
    except:
        return ""
    return ""

def send_email(to_address, subject, message):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        email_text = f"Subject: {subject}\n\n{message}"
        server.sendmail(EMAIL_ADDRESS, to_address, email_text)
        server.quit()
        talk('Email has been sent!')
    except Exception as e:
        talk('Sorry, I was unable to send the email.')
        print(e)

def get_news_headlines():
    talk("Fetching the latest news headlines.")
    feed_url = "https://news.google.com/rss"
    news_feed = feedparser.parse(feed_url)

    if not news_feed.entries:
        talk("Sorry, I couldn't find any news right now.")
        return

    top_articles = news_feed.entries[:5]
    for i, article in enumerate(top_articles, start=1):
        talk(f"Headline {i}: {article.title}")

def open_app(app_name):
    apps = {
        'brave': {
            'Windows': r"C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe",
            'Darwin': "Brave Browser",
            'Linux': "brave-browser"
        },
        'vs code': {
            'Windows': r"S:\\Microsoft VS Code\\Code.exe",
            'Darwin': "Visual Studio Code",
            'Linux': "code"
        },
        'notepad': {
            'Windows': "notepad.exe"
        },
        'calculator': {
            'Windows': "calc.exe",
            'Darwin': "Calculator",
            'Linux': "gnome-calculator"
        },
        'Whatsapp': {
            'Windows': r"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\pwahelper.exe",
            'Darwin': "WhatsApp",
            'Linux': "whatsapp"
        },
        'Instagram': {
            'Windows': r"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge_proxy.exe",
            'Darwin': "Spotify",
            'Linux': "spotify"
        },
        'word': {
            'Windows': r"C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE"
        },
        'excel': {
            'Windows': r"C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE"
        },
        'powerpoint': {
            'Windows': r"C:\\Program Files\\Microsoft Office\\root\\Office16\\POWERPNT.EXE"
        }
    }

    system = platform.system()
    app_key = app_name.lower()

    if app_key not in apps or system not in apps[app_key]:
        talk(f"I don't know how to open {app_name} on {system}.")
        return

    path = apps[app_key][system]

    try:
        if system == 'Windows':
            os.startfile(path)
        elif system == 'Darwin':
            subprocess.Popen(['open', '-a', path])
        elif system == 'Linux':
            if shutil.which(path):
                subprocess.Popen([path])
            else:
                talk(f"{app_name} is not installed.")
                return
        talk(f"Opening {app_name}.")
    except Exception as e:
        talk(f"Failed to open {app_name}.")
        print(e)

def close_app(app_name):
    found = False
    app_name = app_name.lower()
    process_names = {
        'brave': 'brave.exe',
        'vs code': 'Code.exe',
        'notepad': 'notepad.exe',
        'calculator': 'Calculator.exe',
        'word': 'WINWORD.EXE',
        'excel': 'EXCEL.EXE',
        'powerpoint': 'POWERPNT.EXE'
    }
    target_process = process_names.get(app_name)
    if not target_process:
        talk(f"I don't know how to close {app_name}.")
        return

    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'].lower() == target_process.lower():
                proc.terminate()
                found = True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if found:
        talk(f"{app_name} has been closed.")
    else:
        talk(f"{app_name} is not running.")

def open_browser(url):
    try:
        system = platform.system()
        if system == 'Windows':
            brave_path = r"C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
            webbrowser.register('brave', None, webbrowser.BackgroundBrowser(brave_path))
            webbrowser.get('brave').open(url)
        elif system == 'Darwin':
            subprocess.Popen(['open', '-a', 'Brave Browser', url])
        elif system == 'Linux':
            subprocess.Popen(['brave-browser', url])
        talk(f'Opening {url}')
    except Exception as e:
        talk('Sorry, I could not open the browser.')
        print(e)
from huggingface_hub import InferenceClient

# Replace with your token
HUGGINGFACE_API_TOKEN = os.getenv("HF_API_TOKEN")

client = InferenceClient(
    "mistralai/Mistral-7B-Instruct-v0.1", 
    token=HUGGINGFACE_API_TOKEN
)

def chat_with_hf(prompt):
    try:
        response = client.text_generation(prompt, max_new_tokens=100)
        talk(response.strip())
    except Exception as e:
        talk("I couldn't generate a response.")
        print(e)

def run_jarvis():
    while not exit_event.is_set():
        command = take_command()
        if not command:
            continue

        if 'play' in command:
            song = command.replace('play', '').strip()
            talk(f'Playing {song}')
            pywhatkit.playonyt(song)
              
        elif 'time' in command:
            now = datetime.datetime.now().strftime('%I:%M %p')
            talk(f'Current time is {now}')

        elif 'who is' in command or 'what is' in command:
            topic = command.replace('who is', '').replace('what is', '').strip()
            try:
                summary = wikipedia.summary(topic, sentences=2)
                talk(summary)
            except wikipedia.DisambiguationError:
                talk('There are multiple entries. Please be more specific.')
            except Exception:
                talk('Sorry, I could not find that information.')

        elif 'open' in command:
            site_or_app = command.replace('open', '').strip()
            websites = {
                'youtube': 'https://www.youtube.com',
                'google': 'https://www.google.com',
                'wikipedia': 'https://www.wikipedia.org',
                'instagram': 'https://www.instagram.com',
                'facebook': 'https://www.facebook.com',
                'twitter': 'https://www.twitter.com',
                'linkedin': 'https://www.linkedin.com',
                'github': 'https://www.github.com',
                'gmail': 'https://mail.google.com',
                'reddit': 'https://www.reddit.com',
                'amazon': 'https://www.amazon.com',
                'netflix': 'https://www.netflix.com',
                'stackoverflow': 'https://stackoverflow.com',
                'spotify': 'https://www.spotify.com',
                'hotstar': 'https://www.hotstar.com/in/home',
                'digiicampus': 'https://ubs.digiicampus.com/home'
            }
            if site_or_app in websites:
                open_browser(websites[site_or_app])
            elif '.' in site_or_app:
                open_browser(f"https://{site_or_app}")
            else:
                open_app(site_or_app)

        elif 'close' in command:
            app = command.replace('close', '').strip()
            close_app(app)

        elif 'tell me the news' in command or 'news' in command:
          get_news_headlines()
          open_browser("https://news.google.com")

        elif 'email to' in command:
            try:
                talk('To whom should I send it?')
                to = take_command()
                talk('What is the subject?')
                subject = take_command()
                talk('What should I say?')
                message = take_command()
                send_email(to, subject, message)
            except:
                talk('I could not complete your email request.')

        elif 'exit' in command or 'quit' in command or 'stop' in command:
            talk('Goodbye!')
            exit_event.set()
            root.quit()
            break

        else:
            talk("I'm not sure how to help with that.")

class JarvisUI:
    def __init__(self, master):
        self.master = master
        master.title("Jarvis Assistant")
        master.geometry("1000x800")
        master.configure(bg='black')

        self.canvas = tk.Canvas(master, width=600, height=600, bg='black', highlightthickness=0)
        self.canvas.pack()

        self.gif = Image.open("jarvis.gif")
        self.frames = [ImageTk.PhotoImage(frame.copy().resize((400, 400))) for frame in ImageSequence.Iterator(self.gif)]
        self.frame_index = 0
        self.image_on_canvas = self.canvas.create_image(300, 300, image=self.frames[0])
        self.animate()

        self.label = tk.Label(master, text="Jarvis is Listening...", fg="cyan", bg="black", font=("Helvetica", 16))
        self.label.pack(pady=10)

        threading.Thread(target=run_jarvis, daemon=True).start()

    def animate(self):
        self.frame_index = (self.frame_index + 1) % len(self.frames)
        self.canvas.itemconfig(self.image_on_canvas, image=self.frames[self.frame_index])
        self.master.after(50, self.animate)

if __name__ == "__main__":
    greet_user()
    root = tk.Tk()
    app = JarvisUI(root)
    root.mainloop()
    os._exit(0)
