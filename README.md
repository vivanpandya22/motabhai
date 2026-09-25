# Motabhai — Voice-Controlled Study Assistant

Motabhai is a desktop voice assistant built with Tkinter. It listens for
spoken commands and opens the right study tool — ChatGPT, Desmos, PW,
YouTube, or a Pomodoro timer — in your browser. It also has a minimal
always-on-top style GUI showing live status, and global hotkeys for
pausing or silencing voice output.

## Features

- **Voice commands** — say a keyword ("gpt", "desmos", "pw", "youtube",
  "clock") to open the matching site.
- **Study modes**
  - `lecture mode` → opens PW
  - `jee solving` → opens PW prep, ChatGPT, and a Pomodoro clock
  - `mht cet solving` → opens the MHT-CET exam portal and a Pomodoro clock
  - Clickable buttons in the GUI for each mode
- **Text-to-speech feedback** for every action (can be silenced).
- **Global hotkeys**
  - `Ctrl+Shift+P` — pause / resume listening
  - `Ctrl+Shift+S` — toggle silent mode (mutes voice output)
- **Automatic microphone fallback** — scans available input devices and
  tries each one until it finds a working microphone.

## Requirements

- Python 3.9+
- Windows, macOS, or Linux with a working microphone
- [PortAudio](http://www.portaudio.com/) installed at the system level
  (required by `PyAudio`):
  - **Windows**: usually installs fine via pip.
  - **macOS**: `brew install portaudio`
  - **Linux (Debian/Ubuntu)**: `sudo apt-get install portaudio19-dev`

## Installation

```bash
git clone https://github.com/<your-username>/motabhai.git
cd motabhai
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

```bash
python motabhai.py
```

Speak a keyword or study-mode phrase, or click one of the mode buttons in
the GUI. Use the hotkeys to pause listening or mute voice feedback.

> **Note:** On some platforms, global hotkeys via the `keyboard` library
> require running the script with administrator/root privileges.

## Configuration

Wake words and destination URLs are defined near the top of `motabhai.py`
in the `WAKE_COMMANDS` dictionary — edit this to add or change shortcuts:

```python
WAKE_COMMANDS = {
    "gpt": "https://chatgpt.com",
    "desmos": "https://www.desmos.com/calculator",
    "pw": "https://www.pw.live/study-v2/study",
    "youtube": "https://www.youtube.com",
    "clock": "https://pomofocus.io/",
}
```

## License

All rights reserved — see [LICENSE](LICENSE). This repository is shared
publicly for portfolio purposes; copying, modifying, or reusing the code
is not permitted without permission.
