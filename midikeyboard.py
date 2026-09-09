import ctypes
from ctypes import wintypes
import time
import threading
import queue
import tkinter as tk
from datetime import datetime
import mido

# ==========================================
# 1. GERÇEK DONANIM GİRİŞİ (YAPI TAMİR EDİLDİ)
# ==========================================
user32 = ctypes.WinDLL('user32', use_last_error=True)
wintypes.ULONG_PTR = wintypes.WPARAM

# Eksiksiz yapı geri getirildi. Bunlar silinince Windows paketi reddediyor.
class MOUSEINPUT(ctypes.Structure):
    _fields_ = (("dx",          wintypes.LONG),
                ("dy",          wintypes.LONG),
                ("mouseData",   wintypes.DWORD),
                ("dwFlags",     wintypes.DWORD),
                ("time",        wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG_PTR))

class KEYBDINPUT(ctypes.Structure):
    _fields_ = (("wVk",         wintypes.WORD),
                ("wScan",       wintypes.WORD),
                ("dwFlags",     wintypes.DWORD),
                ("time",        wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG_PTR))

class HARDWAREINPUT(ctypes.Structure):
    _fields_ = (("uMsg",    wintypes.DWORD),
                ("wParamL", wintypes.WORD),
                ("wParamH", wintypes.WORD))

class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = (("ki", KEYBDINPUT),
                    ("mi", MOUSEINPUT),
                    ("hi", HARDWAREINPUT))
    _anonymous_ = ("_input",)
    _fields_ = (("type",   wintypes.DWORD),
                ("_input", _INPUT))

def send_scancode(scancode, is_press):
    x = INPUT()
    x.type = 1 # INPUT_KEYBOARD
    x.ki.wVk = 0 
    x.ki.wScan = scancode
    x.ki.dwFlags = 0x0008 # KEYEVENTF_SCANCODE
    if not is_press:
        x.ki.dwFlags |= 0x0002 # KEYEVENTF_KEYUP
    x.ki.time = 0
    x.ki.dwExtraInfo = 0
    return user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(INPUT)) == 1

# ==========================================
# 2. VIRTUAL PIANO HARİTASI
# ==========================================
SCAN_CODES = {
    '1': 0x02, '2': 0x03, '3': 0x04, '4': 0x05, '5': 0x06, '6': 0x07, '7': 0x08, '8': 0x09, '9': 0x0A, '0': 0x0B,
    'q': 0x10, 'w': 0x11, 'e': 0x12, 'r': 0x13, 't': 0x14, 'y': 0x15, 'u': 0x16, 'i': 0x17, 'o': 0x18, 'p': 0x19,
    'a': 0x1E, 's': 0x1F, 'd': 0x20, 'f': 0x21, 'g': 0x22, 'h': 0x23, 'j': 0x24, 'k': 0x25, 'l': 0x26,
    'z': 0x2C, 'x': 0x2D, 'c': 0x2E, 'v': 0x2F, 'b': 0x30, 'n': 0x31, 'm': 0x32, 'shift': 0x2A
}

SHIFT_MAP = {'!': '1', '@': '2', '#': '3', '$': '4', '%': '5', '^': '6', '&': '7', '*': '8', '(': '9', ')': '0'}

VP_NOTES = [
    "1", "!", "2", "@", "3", "4", "$", "5", "%", "6", "^", "7", 
    "8", "*", "9", "(", "0", "q", "Q", "w", "W", "e", "E", "r", 
    "t", "T", "y", "Y", "u", "i", "I", "o", "O", "p", "P", "a", 
    "s", "S", "d", "D", "f", "g", "G", "h", "H", "j", "J", "k", 
    "l", "L", "z", "Z", "x", "c", "C", "v", "V", "b", "B", "n", "m"
]

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
def get_note_name(midi_number):
    return f"{NOTE_NAMES[midi_number % 12]}{(midi_number // 12) - 1}"

# ==========================================
# 3. ARAYÜZ VE MOTOR
# ==========================================
class ProMidiBot:
    def __init__(self, root):
        self.root = root
        self.root.title("Roblox Piano - Sustain Engine")
        self.root.geometry("600x400")
        self.root.configure(bg="#1E1E1E")
        self.root.attributes("-topmost", True)
        
        self.note_queue = queue.Queue()

        tk.Label(root, text="🎹 SUSTAIN PİYANO MOTORU", bg="#1E1E1E", fg="#BB86FC", font=("Segoe UI", 14, "bold")).pack(pady=10)
        self.status_lbl = tk.Label(root, text="USB Klavye Bekleniyor...", bg="#1E1E1E", fg="#FFB300", font=("Segoe UI", 11))
        self.status_lbl.pack(pady=5)

        log_frame = tk.Frame(root, bg="#121212")
        log_frame.pack(fill="both", expand=True, padx=15, pady=10)
        tk.Label(log_frame, text="İŞLEM KAYDI", bg="#121212", fg="#888", font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=5, pady=2)
        
        self.log_text = tk.Text(log_frame, bg="#000000", fg="#FFFFFF", font=("Consolas", 10), relief="flat", state="disabled")
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.log_text.tag_config("time", foreground="#888888")
        self.log_text.tag_config("note", foreground="#03DAC6", font=("Consolas", 10, "bold"))
        self.log_text.tag_config("press", foreground="#00E676")   
        self.log_text.tag_config("release", foreground="#FF9800") 

        threading.Thread(target=self.midi_listener, daemon=True).start()
        threading.Thread(target=self.keystroke_worker, daemon=True).start()

    def add_log(self, midi_num, char, action_type):
        now = datetime.now().strftime("%H:%M:%S")
        note_name = get_note_name(midi_num)
        
        self.log_text.config(state="normal")
        self.log_text.insert("1.0", f"[{now}]  ", "time")
        
        if action_type == "press":
            self.log_text.insert("1.0 + 12c", f"👇 BASILDI  : {note_name:<4} (Tuş: {char})\n", "press")
        else:
            self.log_text.insert("1.0 + 12c", f"☝️ BIRAKILDI: {note_name:<4} (Tuş: {char})\n", "release")

        lines = self.log_text.get("1.0", "end-1c").split("\n")
        if len(lines) > 12:
            self.log_text.delete("13.0", "end")
        self.log_text.config(state="disabled")

    def keystroke_worker(self):
        while True:
            action, midi_num, char = self.note_queue.get()
            
            needs_shift = char.isupper() or char in SHIFT_MAP
            base_char = SHIFT_MAP.get(char, char.lower())
            code = SCAN_CODES.get(base_char)
            
            if code:
                if action == "press":
                    if needs_shift:
                        send_scancode(SCAN_CODES['shift'], True)
                        time.sleep(0.01) 
                        
                    send_scancode(code, True) 
                    
                    if needs_shift:
                        time.sleep(0.01)
                        send_scancode(SCAN_CODES['shift'], False) 
                        
                    self.root.after(0, lambda: self.add_log(midi_num, char, "press"))

                elif action == "release":
                    send_scancode(code, False) 
                    self.root.after(0, lambda: self.add_log(midi_num, char, "release"))

            self.note_queue.task_done()

    def midi_listener(self):
        while True:
            device = next((name for name in mido.get_input_names() if "Keystation" in name), None)
            
            if device:
                try:
                    with mido.open_input(device) as port:
                        self.root.after(0, lambda: self.status_lbl.config(text=f"🟢 BAĞLANDI: {device}", fg="#00E676"))
                        
                        for msg in port:
                            if 36 <= getattr(msg, 'note', -1) <= 96:
                                char = VP_NOTES[msg.note - 36]
                                
                                if msg.type == 'note_on' and msg.velocity > 0:
                                    self.note_queue.put(("press", msg.note, char))
                                    
                                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                                    self.note_queue.put(("release", msg.note, char))
                                    
                except Exception:
                    pass
            
            self.root.after(0, lambda: self.status_lbl.config(text="USB Klavye Bekleniyor...", fg="#FFB300"))
            time.sleep(2)

if __name__ == "__main__":
    root = tk.Tk()
    app = ProMidiBot(root)
    root.mainloop()