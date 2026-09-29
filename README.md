<div align="center">

# 📷 FotoSecim

### Profesyonel Düğün Fotoğraf Seçim Uygulaması

*Fotoğraf seçim sürecini hızlandırın, albüm hazırlamaya daha fazla zaman ayırın.*

<br>

FotoSecim; düğün, nişan, dış çekim ve benzeri profesyonel fotoğrafçılık işlerinde müşterilerin seçtiği fotoğrafları hızlı ve düzenli bir şekilde albüm klasörlerine aktarmak için geliştirilmiş, Windows tabanlı masaüstü uygulamasıdır.

<br>

![Platform](https://img.shields.io/badge/Platform-Windows_10%2F11-0078D6?style=for-the-badge&logo=windows&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pillow](https://img.shields.io/badge/Pillow-Image_Processing-EC8115?style=for-the-badge&logo=python&logoColor=white)
![Status](https://img.shields.io/badge/Status-Private_Distribution-8A6D3B?style=for-the-badge&logo=lock&logoColor=white)

</div>

---

## ✨ FotoSecim Nedir?

FotoSecim, özellikle düğün fotoğrafçıları ve fotoğraf stüdyoları için tasarlanmış bir fotoğraf seçim ve albüm hazırlama yardımcısıdır.

Geleneksel yöntemde müşterinin seçtiği fotoğraf numaralarını bir kağıda yazması, fotoğrafçının daha sonra bu numaraları tek tek bulması ve ayrı bir klasöre kopyalaması zaman kaybına ve hatalara neden olabilir.

FotoSecim bu süreci tek bir arayüz altında toplar:

> **Klasörü seç** → **Albümü oluştur** → **Fotoğrafları seç** → **Kapak/Tabloyu belirle** → **Başlat** → **Albüm hazır**

---

## 🎯 Temel Amaç

FotoSecim'in amacı yalnızca fotoğraf seçtirmek değil, seçim sonrasındaki dosya düzenleme işlemini de mümkün olduğunca otomatikleştirmektir.

#### Geleneksel Yöntem
```
Müşteri fotoğraf numaralarını yazar
              ↓
Fotoğrafçı numaraları kontrol eder
              ↓
Fotoğraflar tek tek bulunur
              ↓
Dosyalar kopyalanır
              ↓
Kapak ve tablo ayrıca düzenlenir
              ↓
Albüm klasörü hazırlanır
```
FotoSecim ile
```
Klasörü seç
    ↓
Albüm bilgilerini gir
    ↓
Fotoğrafları seç
    ↓
Kapak / tabloyu belirle
    ↓
BAŞLAT
    ↓
Albüm klasörü hazır
```
🌟 Öne Çıkan Özellikler
| Özellik | Açıklama |
|---|---|
| 📁 Klasör Bazlı Çalışma | Fotoğrafların bulunduğu mevcut klasör üzerinden çalışır. |
| 🖼️ Hızlı Fotoğraf Seçimi | Fotoğraflar arayüz üzerinden tek tıklamayla seçilebilir. |
| 🔍 Büyük Önizleme | Fotoğrafı daha detaylı incelemek için tam ekran önizleme kullanılabilir. |
| 💍 Albüm Yönetimi | Her çalışma için ayrı bir albüm klasörü oluşturulur. |
| 💛 Albüm Kapağı | Kapak fotoğrafı ayrı olarak belirlenebilir. |
| 🖼️ Tablo Fotoğrafı | Tablo için kullanılacak fotoğraf ayrı olarak seçilebilir. |
| 🔢 Otomatik Sıralama | Seçilen fotoğraflar düzenli ve sıralı şekilde kopyalanır. |
| 🛡️️ Güvenli Kopyalama | Orijinal fotoğraflar değiştirilmez, taşınmaz veya silinmez. |
| 💻 Windows Desteği | Windows 10 ve Windows 11 üzerinde çalışmak üzere tasarlanmıştır. |
| 🚀 Kurulumsuz EXE | Build edilmiş sürüm tek bir .exe dosyası olarak kullanılabilir. |
| 🔒 Yerel Çalışma | Fotoğrafların internet üzerinden herhangi bir sunucuya yüklenmesine gerek yoktur. |
🖥️ Kullanım
1. 📁 Fotoğraf Klasörünü Seç
Fotoğrafların bulunduğu ana klasörü seçin. Uygulama bu klasörde bulunan fotoğraflar üzerinden seçim ekranını oluşturur.
2. ✏️ Albüm Bilgilerini Gir
Albüm için gerekli bilgileri belirleyin:
 * Albüm adı
 * Seçilecek normal fotoğraf sayısı
 * Kapak kullanılacak mı?
 * Tablo fotoğrafı kullanılacak mı?
3. 🖼 Fotoğrafları Seç
Fotoğraflar seçim ekranında görüntülenir. Fotoğraflara tıklayarak seçim yapabilirsiniz.
Seçim sırasında:
 * Tek tıklama: Fotoğrafı seç / seçimden çıkar
 * Çift tıklama: Büyük önizleme
 * Klavye yön tuşları: Fotoğraflar arasında gezinme
 * <Space>: Seç / seçimden çıkar
 * <F>: Tam ekran önizleme
 * <Esc>: Önizlemeyi kapat / geri dön
4. 💛 Kapak ve Tabloyu Belirle
Albüm kapağı ve tablo için kullanılacak fotoğraflar, normal albüm fotoğraflarından ayrı olarak belirlenebilir. Bu sayede albüm içerisindeki özel dosyaların düzenlenmesiyle ayrıca uğraşmanız gerekmez.
5. ▶️ Albümü Oluştur
Seçim tamamlandığında Başla butonuna basın. FotoSecim otomatik olarak albüm klasörünü oluşturur ve seçilen dosyaları bu klasöre kopyalar.
📂 Oluşturulan Klasör Yapısı
Kaynak klasörünüz:
```
Düğün_2026/
├── IMG_0001.jpg
├── IMG_0002.jpg
├── IMG_0003.jpg
├── IMG_0004.jpg
├── IMG_0005.jpg
└── ...
```
Seçim tamamlandıktan sonra:
```
Düğün_2026/
├── IMG_0001.jpg
├── IMG_0002.jpg
├── IMG_0003.jpg
├── IMG_0004.jpg
├── IMG_0005.jpg
│
└── Albüm/
    ├── 001.jpg
    ├── 002.jpg
    ├── 003.jpg
    ├── 004.jpg
    ├── ...
    ├── ALBUM_KAPAK.jpg
    └── TABLO.jpg
```
> Not: Dosya adlandırma ve çıktı yapısı uygulamanın mevcut sürümündeki yapılandırmaya göre değişebilir.
> 
🛡️ Veri Güvenliği
FotoSecim'in temel çalışma prensiplerinden biri yerel dosya işlemleridir. Fotoğraflarınızı seçmek veya albüm oluşturmak için herhangi bir bulut depolama sistemine yükleme yapılması gerekmez.
Uygulama:
 * ❌ Fotoğrafları internete yüklemez
 * ❌ Fotoğrafları sunucuya göndermez
 * ❌ Orijinal dosyaları silmez
 * ❌ Orijinal dosyaları taşımaz
 * ✅ Seçilen fotoğrafların kopyalarını oluşturur
 * ✅ İşlemleri bilgisayar üzerinde gerçekleştirir
Bu yapı özellikle müşterilerinin fotoğraflarıyla çalışan profesyonel fotoğrafçılar için tasarlanmıştır.
⌨️️ Klavye Kısayolları
| Kısayol | İşlev |
|---|---|
| <kbd>←</kbd> <kbd>→</kbd> | Önceki / sonraki fotoğraf |
| <kbd>↑</kbd> <kbd>↓</kbd> | Fotoğraflar arasında gezinme |
| <kbd>Space</kbd> | Fotoğrafı seç / seçimden çıkar |
| <kbd>F</kbd> | Tam ekran önizleme |
| <kbd>Esc</kbd> | Önizlemeyi kapat / geri dön |
> Not: Kısayollar kullanılan uygulama sürümüne göre değişebilir.
> 
🧰 Teknik Yapı
FotoSecim Python tabanlı olarak geliştirilmiştir.
Kullanılan Teknolojiler:
 * Python 3.10+
 * Pillow
 * Windows Masaüstü Arayüz Teknolojileri
 * Dosya Sistemi ve Klasör Yönetimi
 * Görsel Önizleme ve İşleme
Pillow; fotoğrafların okunması, boyutlandırılması, önizleme için işlenmesi ve desteklenen görsel formatlarının yönetilmesinde kullanılmaktadır.
📋 Sistem Gereksinimleri
| Gereksinim | Minimum | Önerilen |
|---|---|---|
| İşletim Sistemi | Windows 10 64-bit | Windows 10 / 11 64-bit |
| Bellek (RAM) | 4 GB RAM | 8 GB+ RAM |
| Depolama | Standart HDD | SSD (Hızlı okuma/yazma) |
| Ortam | Python 3.10+ (Kaynak kod için) | Kurulumsuz .exe |
🔄 İş Akışı
flowchart LR
    A[📁 Klasör Seç] --> B[✏️ Albüm Bilgileri]
    B --> C[🖼 Fotoğraf Seçimi]
    C --> D{Özel Fotoğraflar?}
    D -->|Evet| E[💛 Kapak / Tablo]
    D -->|Hayır| F[▶️ Başlat]
    E --> F
    F --> G[📂 Albüm Klasörü]
    G --> H[✅ Seçilen Fotoğraflar Kopyalandı]

🎨 Tasarım
FotoSecim'in arayüzü, uzun süre bilgisayar başında çalışan fotoğrafçılar düşünülerek tasarlanmıştır.
Tasarım Yaklaşımı:
 * 🌑 Koyu arayüz
 * 🟡 Gold vurgu renkleri
 * 🧭 Sade navigasyon
 * 🖱️ Minimum tıklama
 * 🖼️ Fotoğraf odaklı çalışma alanı
 * ⚡ Gereksiz ekranlardan kaçınan hızlı iş akışı
👤 Kimler İçin?
 * 📸 Düğün fotoğrafçıları
 * 💍 Nişan ve söz fotoğrafçıları
 * 🎞️ Fotoğraf stüdyoları
 * 🖼️️ Albüm tasarımı yapan işletmeler
 * 👰 Dış çekim hizmeti veren fotoğrafçılar
 * 🏢 Profesyonel fotoğrafçılık ekipleri
🚀 Kullanım Senaryosu
Örneğin bir düğün çekiminde müşterinizden 50 fotoğraf seçmesi gerekiyor.
 * Çekimin bulunduğu klasörü açın.
 * FotoSecim'i çalıştırın.
 * Albüm adını girin.
 * 50 fotoğraf seçileceğini belirtin.
 * Müşterinin seçtiği fotoğrafları işaretleyin.
 * Kapak ve tablo fotoğrafını belirleyin.
 * Başla butonuna basın.
Uygulama seçilen fotoğrafları otomatik olarak yeni albüm klasörüne kopyalar. Böylece yüzlerce fotoğraf arasından seçilen dosyaları manuel olarak bulup kopyalama ihtiyacı ortadan kalkar.
🔐 Dağıtım & Lisans
FotoSecim şu anda özel dağıtım amacıyla geliştirilmektedir. Proje kaynak kodu GitHub üzerinde bulunsa dahi herkese açık hazır EXE dağıtımı yapılmayabilir.
Bu proje özel kullanım ve dağıtım amacıyla geliştirilmektedir. Kaynak kodunun, uygulamanın veya oluşturulan derlenmiş dosyaların izinsiz olarak yeniden dağıtılması, değiştirilmesi veya ticari amaçla kullanılması proje sahibinin iznine tabidir.
🗺️ Gelecek Planları
 * [ ] Daha gelişmiş fotoğraf filtreleme
 * [ ] Gelişmiş benzer fotoğraf karşılaştırma
 * [ ] Daha fazla görsel format desteği
 * [ ] Özelleştirilebilir klavye kısayolları
 * [ ] Gelişmiş albüm şablonları
 * [ ] Seçim istatistikleri
 * [ ] Çoklu albüm işlemleri
 * [ ] Performans iyileştirmeleri
<div align="center">
📷 FotoSecim
Fotoğraf seçimini kolaylaştırın. Albüm hazırlamaya odaklanın.
Fotoğraf, en güzel hikâyedir. ✨
Made with ❤️ for photographers
</div>
