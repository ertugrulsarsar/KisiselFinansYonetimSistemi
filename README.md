# Kişisel Finans Yönetim Sistemi

Bu proje, kullanıcıların gelir ve giderlerini takip ederek aylık bütçe yönetimi yapabilmelerini sağlayan bir web uygulamasıdır.

## Özellikler

- Kullanıcı yönetimi (kayıt, giriş, profil)
- Gelir ve gider kayıtları
- Kategori bazlı harcama takibi
- Aylık/yıllık raporlama
- En çok harcama yapılan kategorilerin analizi
- Veri yedekleme ve geri yükleme

## Teknolojiler

- Backend: Flask (Python)
- Frontend: HTML, CSS, JavaScript, Bootstrap
- Veritabanı: SQLite (geliştirme), PostgreSQL (production)
- ORM: SQLAlchemy
- Kimlik Doğrulama: Flask-Login
- Form Yönetimi: Flask-WTF
- Veritabanı Migrasyonları: Flask-Migrate

## Kurulum

1. Python 3.8+ yükleyin
2. Projeyi klonlayın:
   ```bash
   git clone https://github.com/kullaniciadi/kisisel-finans-yonetim-sistemi.git
   cd kisisel-finans-yonetim-sistemi
   ```
3. Sanal ortam oluşturun ve aktif edin:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```
4. Gerekli paketleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```
5. Veritabanını oluşturun:
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```
6. Uygulamayı çalıştırın:
   ```bash
   flask run
   ```

## Geliştirme Roadmap

### Faz 1: Temel Yapı (MVP)
- [x] Proje yapısının oluşturulması
- [x] Temel veritabanı modelleri
- [x] Kullanıcı kimlik doğrulama sistemi
- [x] Gelir/gider ekleme ve listeleme
- [x] Basit dashboard

### Faz 2: Temel Özellikler
- [ ] Kategori yönetimi
- [ ] Aylık raporlama
- [ ] Basit analizler
- [ ] Veri dışa aktarma (CSV)
- [ ] Kullanıcı profil yönetimi

### Faz 3: Gelişmiş Özellikler
- [ ] Detaylı analiz ve raporlama
- [ ] Grafik gösterimleri
- [ ] Bütçe hedefleri
- [ ] Hatırlatıcılar
- [ ] Çoklu para birimi desteği

### Faz 4: Optimizasyon ve Güvenlik
- [ ] Performans optimizasyonu
- [ ] Güvenlik testleri
- [ ] Hata yönetimi
- [ ] Loglama sistemi
- [ ] Yedekleme sistemi

## API Endpoints

### Kullanıcı İşlemleri
- `POST /auth/register` - Yeni kullanıcı kaydı
- `POST /auth/login` - Kullanıcı girişi
- `GET /auth/logout` - Çıkış yapma

### İşlem Yönetimi
- `GET /transactions/list` - İşlemleri listele
- `POST /transactions/add` - Yeni işlem ekle
- `GET /transactions/api/summary` - Son 30 günlük özet

## Güvenlik Özellikleri
- Şifre hash'leme
- CSRF koruması
- Session güvenliği
- Input validasyonu
- Güvenli cookie ayarları

## Sonraki Adımlar
1. Templates ve statik dosyaların oluşturulması
2. Dashboard arayüzünün tasarlanması
3. Kategori yönetimi özelliklerinin eklenmesi
4. Raporlama sisteminin geliştirilmesi

## Katkıda Bulunma

1. Fork'layın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## İletişim

Proje Sahibi: Ertuğrul Sarsar 

Proje Linki: [https://github.com/ertugrulsarsar/KisiselFinansYonetimSistemi](https://github.com/ertugrulsarsar/KisiselFinansYonetimSistemi)
