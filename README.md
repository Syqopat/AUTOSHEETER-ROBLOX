# 🎹 AUTOSHEETER-ROBLOX (Roblox Piano Sheet Player)

![Status](https://img.shields.io/badge/Status-Working%20%2F%20Stable-brightgreen?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge)
![CI](https://img.shields.io/badge/CI%2FCD-Active-success?style=for-the-badge)

**AUTOSHEETER-ROBLOX** is an automated sheet music macro playback utility designed for virtual piano games in Roblox. It features a Tkinter GUI and low-level keypress simulation.

---

## 📌 Project Status

- **Status:** 🟢 **Working / Stable**
- **CI/CD:** Automated GitHub Actions syntax verification enabled.
- **Configuration:** Customizable delay times and keybinds via `config.json`.

---

## 🚀 Key Features

- **Sheet Parser:** Automatically parses bracketed chords, delays, and individual notes.
- **Active Visual Highlight Panel:** Highlights the currently played note in real-time.
- **Auto / Step Playback:** Toggle automatic loop mode or trigger steps manually via bindable hotkeys.

---

## 🛠️ Installation & Usage

```bash
pip install -r requirements.txt
python sheeter.py
```

---

## ⚙️ Configuration (`config.json`)

```json
{
  "default_speed_delay": 0.15,
  "key1": "F1",
  "key2": "RIGHT",
  "window_title": "Piano Controller"
}
```

---

## 📄 License

Licensed under the MIT License.
