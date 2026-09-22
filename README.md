# FotoSecim v1.1

Windows için yerel çalışan düğün fotoğrafı seçim uygulaması.

## Akış
1. Fotoğrafların bulunduğu klasörü seçin.
2. Albüm adını ve normal fotoğraf sayısını girin.
3. İsterseniz albüm kapağı ve tablo fotoğrafı seçimlerini açın/kapatın.
4. **BAŞLA** ile seçim ekranına geçin.
5. Fotoğraflara tıklayarak seçin; çift tıklayarak büyük önizleme açın.
6. Normal seçim tamamlanınca kapak ve tablo fotoğrafı seçilir.
7. **İLERİ** ile tamamlandığında seçilen fotoğraflar albüm klasörüne kopyalanır.

## Çıktı
- Normal fotoğraflar: `001.jpg`, `002.jpg`, ...
- Albüm kapağı: `ALBUM_KAPAK.jpg` (kaynak uzantısı korunur)
- Tablo fotoğrafı: `TABLO.jpg` (kaynak uzantısı korunur)

Orijinal fotoğraflar silinmez veya taşınmaz; yalnızca kopyalanır.

## Not
Bu sürümde albüm kapağı tasarım seçimi kaldırılmıştır. Kapak olarak seçilen fotoğraf doğrudan kopyalanır.

## Kurulum
```bat
pip install -r requirements.txt
python foto_secim.py
```

Windows'ta EXE oluşturmak için `build_windows.bat` kullanılabilir.
