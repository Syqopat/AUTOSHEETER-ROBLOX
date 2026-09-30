# 🎹 AUTOSHEETER-ROBLOX (Roblox Piano Sheet Player)

![Status](https://img.shields.io/badge/Durum-%C3%87al%C4%B1%C5%9F%C4%B1yor%20%2F%20Working-brightgreen?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge)
![CI](https://img.shields.io/badge/CI%2FCD-Active-success?style=for-the-badge)

**AUTOSHEETER-ROBLOX**, Roblox oyun içi piyanoları için geliştirilmiş otomatik nota çalma ve makro kontrol yazılımıdır. Tkinter grafik arayüzü ve düşük seviye tuş giriş simülasyonu sunar.

---

## 📌 Proje Durumu (Project Status)

- **Durum:** 🟢 **Çalışıyor (Working / Stable)**
- **Test & CI/CD:** GitHub Actions syntax denetimi aktif.
- **Konfigürasyon:** `config.json` ile varsayılan gecikme süreleri ve kısayol tuşları özelleştirilebilir.

---

## 🚀 Özellikler

- **Nota Ayrıştırma:** Parantezli akorları ve tekil notaları otomatik ayrıştırır.
- **Canlı Vurgu Paneli:** O an çalınan notayı ekranda vurgular.
- **Otomatik / Adımlı Çalma:** F1 ve Ok tuşları veya otomatik mod ile ritim kontrolü sağlar.

---

## 🛠️ Kurulum ve Kullanım

```bash
pip install -r requirements.txt
python sheeter.py
```

---

## ⚙️ Yapılandırma (`config.json`)

```json
{
  "default_speed_delay": 0.15,
  "key1": "F1",
  "key2": "RIGHT",
  "window_title": "Piano Controller"
}
```

---

## 📄 Lisans

MIT License
