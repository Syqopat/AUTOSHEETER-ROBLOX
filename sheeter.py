import ctypes
import time
import re
import tkinter as tk
import threading
import random
from pynput import keyboard

# --- DONANIM SEVİYESİ GİRİŞ SİSTEMİ (STABİLİZE EDİLDİ) ---
SendInput = ctypes.windll.user32.SendInput

# Tuş Kodları (ScanCodes)
SCAN_CODES = {
    '1': 0x02, '2': 0x03, '3': 0x04, '4': 0x05, '5': 0x06, '6': 0x07, '7': 0x08, '8': 0x09, '9': 0x0A, '0': 0x0B,
    'q': 0x10, 'w': 0x11, 'e': 0x12, 'r': 0x13, 't': 0x14, 'y': 0x15, 'u': 0x16, 'i': 0x17, 'o': 0x18, 'p': 0x19,
    'a': 0x1E, 's': 0x1F, 'd': 0x20, 'f': 0x21, 'g': 0x22, 'h': 0x23, 'j': 0x24, 'k': 0x25, 'l': 0x26,
    'z': 0x2C, 'x': 0x2D, 'c': 0x2E, 'v': 0x2F, 'b': 0x30, 'n': 0x31, 'm': 0x32, 'shift': 0x2A, 'space': 0x39
}

PUL = ctypes.POINTER(ctypes.c_ulong)
class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort), ("wScan", ctypes.c_ushort), ("dwFlags", ctypes.c_ulong), ("time", ctypes.c_ulong), ("dwExtraInfo", PUL)]
class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput)]
class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong), ("ii", Input_I)]

def send_key(code, is_press):
    # KEYEVENTF_SCANCODE = 0x0008 | KEYEVENTF_KEYUP = 0x0002
    flags = 0x0008 
    if not is_press:
        flags |= 0x0002
    
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, code, flags, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

class PianoBot:
    def __init__(self, root):
        self.root = root
        self.root.title("Piano Controller")
        self.root.geometry("650x780")
        self.root.configure(bg="#121212")
        self.root.attributes("-topmost", True)

        self.tokens = []
        self.index = 0
        self.running = False
        self.key1 = keyboard.Key.f1
        self.key2 = keyboard.Key.right
        self.binding_target = None 

        self.create_widgets()
        self.listener = keyboard.Listener(on_press=self.handle_global_keys)
        self.listener.start()

    def create_widgets(self):
        # Header
        tk.Label(self.root, text="ROBLOX PIANO CONTROLLER", bg="#121212", fg="#BB86FC", font=("Segoe UI", 12, "bold")).pack(pady=10)

        # Input
        main_frame = tk.Frame(self.root, bg="#121212", padx=20)
        main_frame.pack(fill="both", expand=True)

        tk.Label(main_frame, text="SHEET INPUT", bg="#121212", fg="#888").pack(anchor="w")
        self.input_area = tk.Text(main_frame, height=8, bg="#1E1E1E", fg="#FFF", relief="flat", font=("Consolas", 10))
        self.input_area.pack(fill="x", pady=5)

        # Display (Vurgu Paneli)
        tk.Label(main_frame, text="PLAYBACK VIEW", bg="#121212", fg="#888").pack(anchor="w", pady=(10, 0))
        self.display = tk.Text(main_frame, height=10, bg="#000", fg="#0F0", state='disabled', relief="flat", font=("Consolas", 11))
        self.display.pack(fill="x", pady=5)
        self.display.tag_config("active", background="#BB86FC", foreground="#000")

        # Controls
        btn_frame = tk.Frame(main_frame, bg="#121212")
        btn_frame.pack(fill="x", pady=10)

        self.load_btn = tk.Button(btn_frame, text="LOAD", command=self.load_sheet, bg="#03DAC6", width=12, relief="flat")
        self.load_btn.pack(side="left", padx=5)

        self.auto_btn = tk.Button(btn_frame, text="START AUTO", command=self.toggle_auto, bg="#3700B3", fg="white", width=12, relief="flat")
        self.auto_btn.pack(side="left", padx=5)

        self.speed_slider = tk.Scale(main_frame, from_=0.01, to=1.0, resolution=0.01, orient="horizontal", label="Speed Delay", bg="#121212", fg="#FFF", highlightthickness=0)
        self.speed_slider.set(0.15)
        self.speed_slider.pack(fill="x", pady=10)

        # Keybinds
        kb_frame = tk.Frame(main_frame, bg="#1E1E1E", pady=10, padx=10)
        kb_frame.pack(fill="x", pady=10)

        self.btn_k1 = tk.Button(kb_frame, text=f"Key 1: {self.format_key(self.key1)}", command=lambda: self.wait_for_key(1), bg="#333", fg="#FFF", width=20)
        self.btn_k1.grid(row=0, column=0, padx=5)

        self.btn_k2 = tk.Button(kb_frame, text=f"Key 2: {self.format_key(self.key2)}", command=lambda: self.wait_for_key(2), bg="#333", fg="#FFF", width=20)
        self.btn_k2.grid(row=0, column=1, padx=5)

    def format_key(self, k):
        if hasattr(k, 'name'): return k.name.upper()
        if hasattr(k, 'char'): return k.char.upper()
        return str(k).upper()

    def wait_for_key(self, target):
        self.binding_target = target
        btn = self.btn_k1 if target == 1 else self.btn_k2
        btn.config(text="WAITING...", bg="#BB86FC")

    def handle_global_keys(self, key):
        if self.binding_target:
            if self.binding_target == 1: self.key1 = key
            else: self.key2 = key
            self.binding_target = None
            self.root.after(0, lambda: self.btn_k1.config(text=f"Key 1: {self.format_key(self.key1)}", bg="#333"))
            self.root.after(0, lambda: self.btn_k2.config(text=f"Key 2: {self.format_key(self.key2)}", bg="#333"))
            return
        if key in [self.key1, self.key2]:
            self.play_step()

    def load_sheet(self):
        content = self.input_area.get("1.0", tk.END)
        # TOKEN AYRIŞTIRMA (Görsel hata çözümü için boşlukları da token yapıyoruz)
        self.all_elements = re.findall(r'\[.*?\]|.|\s', content)
        self.tokens = [t for t in self.all_elements if t.strip() != ""] # Sadece notalar
        self.index = 0
        
        self.display.config(state='normal')
        self.display.delete("1.0", tk.END)
        self.display.insert("1.0", content)
        self.display.config(state='disabled')
        self.update_highlight()

    def update_highlight(self):
        self.display.config(state='normal')
        self.display.tag_remove("active", "1.0", tk.END)
        
        if self.index < len(self.tokens):
            target = self.tokens[self.index]
            
            # Görsel Hatayı Çözen Yeni Arama Algoritması:
            # Baştan itibaren kaçıncı notada olduğumuzu sayarak bulur
            search_index = 0
            found_count = 0
            
            start_pos = "1.0"
            while found_count <= self.index:
                # regex=True kullanarak köşeli parantez gibi özel karakterleri tam eşleştiriyoruz
                found_pos = self.display.search(target, start_pos, stopindex=tk.END, exact=True)
                if not found_pos: break
                
                if found_count == self.index:
                    end_pos = f"{found_pos} + {len(target)}c"
                    self.display.tag_add("active", found_pos, end_pos)
                    self.display.see(found_pos)
                    break
                
                start_pos = f"{found_pos} + {len(target)}c"
                # Bu token'ın gerçekten bir nota olup olmadığını kontrol et (regex ile değil)
                # Basit bir sayaç kullanıyoruz
                found_count += 1 
                
        self.display.config(state='disabled')

    def play_token(self, token):
        if not token or token == "|": return
        
        if token.startswith("["):
            chars = token.strip("[]")
            has_upper = any(c.isupper() for c in chars)
            if has_upper: send_key(SCAN_CODES['shift'], True)
            
            for c in chars:
                code = SCAN_CODES.get(c.lower())
                if code: send_key(code, True)
            
            time.sleep(0.07) # Roblox için güvenli basılı tutma süresi
            
            for c in chars:
                code = SCAN_CODES.get(c.lower())
                if code: send_key(code, False)
            if has_upper: send_key(SCAN_CODES['shift'], False)
        else:
            is_up = token.isupper()
            code = SCAN_CODES.get(token.lower())
            if code:
                if is_up: send_key(SCAN_CODES['shift'], True)
                send_key(code, True)
                time.sleep(0.06) 
                send_key(code, False)
                if is_up: send_key(SCAN_CODES['shift'], False)

    def play_step(self):
        if self.index < len(self.tokens):
            t = self.tokens[self.index]
            threading.Thread(target=self.play_token, args=(t,), daemon=True).start()
            self.index += 1
            self.root.after(0, self.update_highlight)

    def auto_loop(self):
        while self.running and self.index < len(self.tokens):
            self.play_token(self.tokens[self.index])
            self.index += 1
            self.root.after(0, self.update_highlight)
            time.sleep(self.speed_slider.get() + random.uniform(0.001, 0.01))
        
        self.running = False
        self.root.after(0, lambda: self.auto_btn.config(text="START AUTO", bg="#3700B3"))

    def toggle_auto(self):
        if not self.running:
            if not self.tokens: return
            self.running = True
            self.auto_btn.config(text="STOP AUTO", bg="#CF6679")
            threading.Thread(target=self.auto_loop, daemon=True).start()
        else:
            self.running = False
            self.auto_btn.config(text="START AUTO", bg="#3700B3")

if __name__ == "__main__":
    root = tk.Tk()
    app = PianoBot(root)
    root.mainloop()