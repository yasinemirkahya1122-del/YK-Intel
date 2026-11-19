<div align="center">

# YK-Intel
### AI-Powered OSINT & Open-Source Web Intelligence Tool

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-Web_UI-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![Gemini AI](https://img.shields.io/badge/Gemini_AI-Google-4285F4?style=for-the-badge&logo=googlegemini&logoColor=white)](https://ai.google.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-FFD700?style=for-the-badge)](LICENSE)

<p align="center">
  <b>İnternette açık kaynak araştırması yapan, sonuçları doğrulayıp kaynaklarıyla özetleyen ve yedek arama motoru desteği sunan tek dosyalık OSINT aracı.</b>
</p>

</div>

---

## 💡 YK-Intel Nedir?

**YK-Intel**, kamuya açık kaynaklardan bilgi toplayan ve bunu düzenli bir rapor haline getiren **Flask** tabanlı yerel bir araştırma arayüzüdür. Öncelikli olarak **Gemini**'nin yerleşik Google Arama yeteneğini kullanır; erişim veya kota durumlarında **DuckDuckGo (`ddgs`)** yedek hattına geçer.

---

## ✨ Öne Çıkan Özellikler

- 🌐 **Gemini Google Search Grounding:** Güncel web sonuçlarını doğrudan arayarak kaynak bağlantılarıyla birlikte özetleme.
- 🔄 **Otomatik Yedek Arama (`ddgs` Fallback):** Gemini araması başarısız olursa DuckDuckGo (`tr-tr`, `wt-wt`, `us-en`) üzerinden sonuç toplayıp özetleme veya ham veri sunma.
- 🛡️ **Hassas Veri Koruması:** Sistem kuralları gereği T.C. kimlik numarası, açık ev adresi veya sızdırılmış özel verileri rapora dahil etmeme.
- ⚡ **Tek Dosya (`YK-Intel.py`) Mimarisi:** Ekstra karmaşık klasör yapısı olmadan doğrudan çalıştırılabilir yapı.
- 🎨 **Karanlık Tema Web Arayüzü:** Tailwind CSS, `marked.js` ve `DOMPurify` (XSS koruması) destekli sade yerel arayüz.

---

## 🛠️ Kurulum ve Çalıştırma

### 1. Repoyu Klonlayın
    git clone [https://github.com/yasinemirkahya1122-del/YK-Intel.git](https://github.com/yasinemirkahya1122-del/YK-Intel.git)
    cd YK-Intel

### 2. Bağımlılıkları Yükleyin
    pip install flask google-genai ddgs

### 3. Aracı Başlatın
    python YK-Intel.py

> **Not:** Uygulama açıldığında `[http://127.0.0.1:5000](http://127.0.0.1:5000)` adresi otomatik olarak başlatılır. Arayüz üzerinden kendi Gemini API anahtarını girmen gerekir.

---

## ⚠️ Sorumluluk Reddi (Disclaimer)

Bu yazılım yalnızca **eğitim, araştırma, siber güvenlik farkındalığı ve kamuya açık verilerle yapılan yasal OSINT çalışmaları** amacıyla sunulmaktadır.

Aracın kullanımından, üçüncü taraf servislerin (Google, DuckDuckGo vb.) sunduğu verilerin doğruluğundan/eksikliğinden veya kullanıcıların bu aracı **hukuka aykırı, izinsiz, taciz, ifşa veya zarar verici** amaçlarla kullanmasından doğabilecek hiçbir doğrudan veya dolaylı zarardan, veri kaybından ya da hukuki/cezai sorumluluktan **yazılım geliştiricisi sorumlu tutulamaz**. Tüm sorumluluk tamamen aracı çalıştıran kişiye aittir.

---

## 📜 Lisans

Bu proje **MIT Lisansı** ile lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına göz atabilirsin.

<div align="center">
  <sub>Developed with ❤️ by <b>Yasin Emir KAHYA</b></sub>
</div>
