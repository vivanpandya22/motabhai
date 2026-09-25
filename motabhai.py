import tkinter as tk
import threading
import time
import webbrowser
import keyboard
import speech_recognition as sr
import pyttsx3
import queue

# ============================================================
# MOTABHAI V10 — MINIMAL CYAN + CLICKABLE MODES
# ============================================================

WAKE_COMMANDS = {
    "gpt": "https://chatgpt.com",
    "desmos": "https://www.desmos.com/calculator",
    "pw": "https://www.pw.live/study-v2/study",
    "youtube": "https://www.youtube.com",
    "clock": "https://pomofocus.io/",
}

PW_PREPARATION = "https://www.pw.live/study-v2/sahayak/goals?cameFrom=study"
MHTCET_EXAM = "https://cetcell.mahacet.org/"

pause_event = threading.Event()
silent_event = threading.Event()
shutdown_event = threading.Event()
voice_queue = queue.Queue()

recognizer = sr.Recognizer()
recognizer.pause_threshold = 0.45
recognizer.non_speaking_duration = 0.2
recognizer.phrase_threshold = 0.2
recognizer.dynamic_energy_threshold = True

BG = "#05090D"
CYAN = "#00E5FF"
CYAN_DIM = "#087A89"
WHITE = "#EAFBFF"
TEXT = "#B5CBD1"
GREEN = "#00E59B"
ORANGE = "#FFB347"
RED = "#FF5870"
BUTTON_BG = "#07151B"

# ============================================================
# GUI
# ============================================================

root = tk.Tk()
root.title("Motabhai")
root.geometry("760x610")
root.resizable(False, False)
root.configure(bg=BG)

header = tk.Frame(root, bg=BG)
header.pack(fill="x", padx=34, pady=(25, 0))

tk.Label(header, text="MOTABHAI", bg=BG, fg=WHITE,
         font=("Segoe UI", 25, "bold")).pack(side="left")

tk.Label(header, text="V10", bg=BG, fg=CYAN,
         font=("Segoe UI", 10, "bold")).pack(side="left", padx=(10, 0), pady=(10, 0))

tk.Label(header, text="STUDY ASSISTANT", bg=BG, fg=CYAN_DIM,
         font=("Segoe UI", 9, "bold")).pack(side="right", pady=(10, 0))

tk.Frame(root, bg=CYAN_DIM, height=1).pack(fill="x", padx=34, pady=(14, 0))

status_frame = tk.Frame(root, bg=BG)
status_frame.pack(pady=(20, 4))

status_dot = tk.Label(status_frame, text="●", bg=BG, fg=CYAN,
                      font=("Segoe UI", 22))
status_dot.pack(side="left", padx=(0, 9))

status_label = tk.Label(status_frame, text="LISTENING", bg=BG, fg=CYAN,
                        font=("Segoe UI", 16, "bold"))
status_label.pack(side="left")

tk.Label(root, text="HEARD", bg=BG, fg=CYAN_DIM,
         font=("Segoe UI", 9, "bold")).pack(pady=(16, 3))

heard_label = tk.Label(root, text="Waiting for speech...", bg=BG, fg=WHITE,
                       font=("Segoe UI", 16), wraplength=650)
heard_label.pack()

tk.Label(root, text="LAST ACTION", bg=BG, fg=CYAN_DIM,
         font=("Segoe UI", 9, "bold")).pack(pady=(15, 3))

action_label = tk.Label(root, text="None", bg=BG, fg=TEXT,
                        font=("Segoe UI", 11), wraplength=650)
action_label.pack()

# ============================================================
# CLICKABLE MODES
# ============================================================

tk.Label(root, text="MODES", bg=BG, fg=CYAN_DIM,
         font=("Segoe UI", 9, "bold")).pack(pady=(18, 8))

mode_frame = tk.Frame(root, bg=BG)
mode_frame.pack()

def make_mode_button(parent, text, command):
    button = tk.Button(
        parent,
        text=text,
        command=command,
        bg=BUTTON_BG,
        fg=CYAN,
        activebackground=CYAN,
        activeforeground=BG,
        relief="flat",
        bd=0,
        highlightthickness=1,
        highlightbackground=CYAN_DIM,
        highlightcolor=CYAN,
        font=("Segoe UI", 10, "bold"),
        padx=18,
        pady=9,
        cursor="hand2",
    )
    button.pack(side="left", padx=5)
    return button

# ============================================================
# STATUS LINE
# ============================================================

status_line = tk.Frame(root, bg=BG)
status_line.pack(pady=(18, 0))

voice_state = tk.Label(status_line, text="● VOICE ON", bg=BG, fg=GREEN,
                       font=("Segoe UI", 9, "bold"))
voice_state.pack(side="left", padx=16)

mic_state = tk.Label(status_line, text="● MIC STARTING", bg=BG, fg=ORANGE,
                     font=("Segoe UI", 9, "bold"))
mic_state.pack(side="left", padx=16)

# ============================================================
# SHORTCUTS
# ============================================================

tk.Frame(root, bg=CYAN_DIM, height=1).pack(fill="x", padx=34, pady=(18, 10))

tk.Label(
    root,
    text="CTRL + SHIFT + P   PAUSE / PLAY       •       CTRL + SHIFT + S   SILENT MODE",
    bg=BG, fg=CYAN_DIM, font=("Segoe UI", 9, "bold")
).pack()

tk.Label(
    root,
    text="Voice: GPT • Desmos • PW • YouTube • Clock",
    bg=BG, fg="#46636B", font=("Segoe UI", 8)
).pack(pady=(7, 0))

# ============================================================
# GUI HELPERS
# ============================================================

def update_heard(text):
    heard_label.config(text=f'"{text}"')

def update_action(text):
    action_label.config(text=text)

def set_mic_state(text, color):
    mic_state.config(text=text, fg=color)

def update_status():
    if pause_event.is_set():
        status_dot.config(fg=ORANGE)
        status_label.config(text="PAUSED", fg=ORANGE)
        voice_state.config(text="● VOICE OFF", fg=ORANGE)
        mic_state.config(text="● MIC PAUSED", fg=ORANGE)
    elif silent_event.is_set():
        status_dot.config(fg=CYAN_DIM)
        status_label.config(text="SILENT", fg=CYAN_DIM)
        voice_state.config(text="● VOICE OFF", fg=CYAN_DIM)
        mic_state.config(text="● MIC ACTIVE", fg=GREEN)
    else:
        status_dot.config(fg=CYAN)
        status_label.config(text="LISTENING", fg=CYAN)
        voice_state.config(text="● VOICE ON", fg=GREEN)
        mic_state.config(text="● MIC ACTIVE", fg=GREEN)

# ============================================================
# VOICE OUTPUT
# ============================================================

def voice_worker():
    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", 175)
        engine.setProperty("volume", 1.0)

        while not shutdown_event.is_set():
            try:
                text = voice_queue.get(timeout=0.2)
            except queue.Empty:
                continue

            if not text or silent_event.is_set():
                continue

            try:
                engine.say(text)
                engine.runAndWait()
            except Exception as error:
                print("TTS error:", error)

    except Exception as error:
        print("Could not start voice engine:", error)

def speak(text):
    if not silent_event.is_set():
        voice_queue.put(text)

# ============================================================
# BROWSER
# ============================================================

def open_urls(urls):
    for url in urls:
        if shutdown_event.is_set():
            return
        try:
            webbrowser.open_new_tab(url)
        except Exception as error:
            print("Browser error:", error)
        time.sleep(0.3)

def launch_urls(urls):
    threading.Thread(target=open_urls, args=(urls,), daemon=True).start()

# ============================================================
# MODES / COMMANDS
# ============================================================

def lecture_mode():
    speak("Lecture mode activated.")
    root.after(0, lambda: update_action("LECTURE MODE  →  PW"))
    launch_urls([WAKE_COMMANDS["pw"]])

def jee_solving():
    speak("JEE solving activated.")
    root.after(0, lambda: update_action("JEE SOLVING  →  PW + GPT + CLOCK"))
    launch_urls([
        PW_PREPARATION,
        WAKE_COMMANDS["gpt"],
        WAKE_COMMANDS["clock"]
    ])

def mhtcet_solving():
    speak("MHT CET solving activated.")
    root.after(0, lambda: update_action("MHT-CET SOLVING  →  EXAM + CLOCK"))
    launch_urls([
        MHTCET_EXAM,
        WAKE_COMMANDS["clock"]
    ])

def clock_mode():
    speak("Clock opened.")
    root.after(0, lambda: update_action("CLOCK  →  POMOFOCUS"))
    launch_urls([WAKE_COMMANDS["clock"]])

make_mode_button(mode_frame, "LECTURE MODE", lecture_mode)
make_mode_button(mode_frame, "JEE SOLVING", jee_solving)
make_mode_button(mode_frame, "MHT-CET SOLVING", mhtcet_solving)
make_mode_button(mode_frame, "CLOCK", clock_mode)

def normal_command(command, url):
    speak(command + " activated.")
    root.after(0, lambda c=command: update_action(c.upper() + "  →  OPENED"))
    launch_urls([url])

# ============================================================
# HOTKEYS
# ============================================================

def toggle_pause():
    if pause_event.is_set():
        pause_event.clear()
    else:
        pause_event.set()
    root.after(0, update_status)

def toggle_silent():
    if silent_event.is_set():
        silent_event.clear()
    else:
        silent_event.set()
    root.after(0, update_status)

keyboard.add_hotkey("ctrl+shift+p", toggle_pause)
keyboard.add_hotkey("ctrl+shift+s", toggle_silent)

# ============================================================
# MICROPHONE SELECTION
# ============================================================

def get_input_devices():
    """
    Find usable input devices. Prefer the Windows/PyAudio default,
    then fall back to the first device with input channels.
    """
    devices = []

    try:
        import pyaudio

        audio = pyaudio.PyAudio()

        try:
            default_info = audio.get_default_input_device_info()
            default_index = int(default_info["index"])
            devices.append(default_index)
            print(
                "Default microphone:",
                default_info.get("name", "Unknown"),
                "| index:", default_index
            )
        except Exception as error:
            print("Could not get default microphone:", error)

        for index in range(audio.get_device_count()):
            try:
                info = audio.get_device_info_by_index(index)
                if int(info.get("maxInputChannels", 0)) > 0:
                    if index not in devices:
                        devices.append(index)
                    print(
                        "Input device:",
                        index,
                        "|",
                        info.get("name", "Unknown")
                    )
            except Exception:
                continue

        audio.terminate()

    except Exception as error:
        print("PyAudio device scan failed:", error)

    return devices

# ============================================================
# VOICE LISTENER
# ============================================================

def voice_listener(device_index):
    print("Voice listener started on device:", device_index)

    try:
        with sr.Microphone(device_index=device_index) as source:

            # Calibrate ONCE while keeping the same microphone stream.
            print("Calibrating microphone...")
            recognizer.adjust_for_ambient_noise(source, duration=0.8)
            print("Energy threshold:", recognizer.energy_threshold)

            root.after(
                0,
                lambda: set_mic_state("● MIC ACTIVE", GREEN)
            )

            while not shutdown_event.is_set():

                if pause_event.is_set():
                    time.sleep(0.1)
                    continue

                try:
                    audio = recognizer.listen(
                        source,
                        timeout=0.35,
                        phrase_time_limit=3
                    )

                    if shutdown_event.is_set() or pause_event.is_set():
                        continue

                    try:
                        text = recognizer.recognize_google(audio).lower().strip()

                        if not text:
                            continue

                        print("Heard:", text)

                        root.after(
                            0,
                            lambda t=text: update_heard(t)
                        )

                        if (
                            "mht cet solving" in text
                            or "mhtcet solving" in text
                            or "mht cet solve" in text
                        ):
                            mhtcet_solving()
                            continue

                        if "jee solving" in text or "jee solve" in text:
                            jee_solving()
                            continue

                        if "lecture mode" in text:
                            lecture_mode()
                            continue

                        for command, url in WAKE_COMMANDS.items():
                            if command in text:
                                normal_command(command, url)
                                break

                    except sr.UnknownValueError:
                        continue

                    except sr.RequestError as error:
                        print("Speech recognition service error:", error)
                        root.after(
                            0,
                            lambda: update_action(
                                "Speech recognition service error"
                            )
                        )
                        time.sleep(0.5)

                except sr.WaitTimeoutError:
                    continue

                except OSError as error:
                    print("Microphone stream error:", error)
                    root.after(
                        0,
                        lambda: set_mic_state("● MIC RETRYING", ORANGE)
                    )
                    time.sleep(0.5)

    except Exception as error:
        print("Listener failed on device", device_index, ":", repr(error))
        return False

    return True

# ============================================================
# MICROPHONE STARTUP + FALLBACK
# ============================================================

def start_microphone():
    print("=================================")
    print("       MOTABHAI - VERSION 10")
    print("=================================")
    print("Scanning microphones...")

    devices = get_input_devices()

    if not devices:
        root.after(
            0,
            lambda: set_mic_state("● NO MIC FOUND", RED)
        )
        root.after(
            0,
            lambda: update_action(
                "No usable input microphone found — see CMD"
            )
        )
        return

    # Try the default first, then every other input device if needed.
    for device_index in devices:
        if shutdown_event.is_set():
            return

        root.after(
            0,
            lambda i=device_index: set_mic_state(
                f"● MIC TRYING #{i}",
                ORANGE
            )
        )

        print("Trying microphone device:", device_index)

        if voice_listener(device_index):
            return

        time.sleep(0.4)

    print("All microphone devices failed.")

    root.after(
        0,
        lambda: set_mic_state("● MIC ERROR", RED)
    )
    root.after(
        0,
        lambda: update_action(
            "All microphone devices failed — see CMD"
        )
    )

# ============================================================
# START WORKERS
# ============================================================

threading.Thread(
    target=voice_worker,
    daemon=True
).start()

threading.Thread(
    target=start_microphone,
    daemon=True
).start()

# ============================================================
# CLOSE
# ============================================================

def close_program():
    shutdown_event.set()

    try:
        keyboard.unhook_all()
    except Exception:
        pass

    try:
        voice_queue.put_nowait("")
    except Exception:
        pass

    root.destroy()

root.protocol("WM_DELETE_WINDOW", close_program)

# ============================================================
# RUN
# ============================================================

try:
    root.mainloop()
finally:
    shutdown_event.set()

    try:
        keyboard.unhook_all()
    except Exception:
        pass

    print("Motabhai closed.")