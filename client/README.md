# Banking App - React Native

Bu proje, Figma tasarımına dayalı modüler bir bankacılık uygulamasıdır. Expo Router kullanılarak geliştirilmiştir.

## 🎯 Özellikler

- **Modüler Tasarım**: Yeniden kullanılabilir bileşenler
- **Tema Desteği**: Açık/koyu tema
- **Responsive Tasarım**: Farklı ekran boyutlarına uyumlu
- **TypeScript**: Tip güvenliği
- **Expo Router**: Dosya tabanlı navigasyon

## 📱 Ekranlar

### Ana Sayfa (`app/(tabs)/index.tsx`)
- Kullanıcı profil başlığı
- Hoş geldin mesajı
- Hızlı işlemler grid'i

### Kampanyalar (`app/(tabs)/campaigns.tsx`)
- Profil başlığı
- Dairesel ilerleme göstergesi (%75)
- Kampanya kartları
- Popover/tooltip bileşeni
- Alt navigasyon

### Keşfet (`app/(tabs)/explore.tsx`)
- Mevcut örnek ekran

## 🧩 Modüler Bileşenler

### `ProfileHeader.tsx`
Kullanıcı profil bilgilerini gösterir:
- Avatar
- Selamlama mesajı
- Kullanıcı adı

```tsx
<ProfileHeader 
  userName="Alican" 
  greeting="İyi günler 👋" 
  avatarUrl="https://example.com/avatar.jpg" 
/>
```

### `CircularProgress.tsx`
Dairesel ilerleme göstergesi:
- Özelleştirilebilir boyut
- Yüzde gösterimi
- Renk teması desteği

```tsx
<CircularProgress 
  progress={75} 
  size={200} 
  strokeWidth={8} 
  showPercentage={true} 
/>
```

### `CampaignCard.tsx`
Kampanya kartı bileşeni:
- Resim
- Başlık ve açıklama
- Dokunma olayları
- Özelleştirilebilir boyutlar

```tsx
<CampaignCard
  title="Kart Kampanyaları"
  description="Özel kampanya fırsatlarını kaçırma!"
  imageUrl="https://example.com/campaign.jpg"
  onPress={() => handlePress()}
/>
```

### `TopBar.tsx`
Üst navigasyon çubuğu:
- Başlık
- Geri butonu (opsiyonel)
- Sağ bileşen (opsiyonel)

```tsx
<TopBar 
  title="Kampanyalar" 
  showBackButton={true}
  onBackPress={() => navigation.goBack()}
/>
```

### `BottomNavigation.tsx`
Alt navigasyon:
- Tab listesi
- Aktif tab gösterimi
- Tema renkleri

```tsx
<BottomNavigation 
  tabs={tabs} 
  onTabPress={(tabId) => setActiveTab(tabId)} 
/>
```

### `Popover.tsx`
Tooltip/popover bileşeni:
- Mesaj
- Geri/İleri butonları
- Ok işareti
- Pozisyon seçenekleri

```tsx
<Popover
  message="Bu bir bilgi mesajıdır."
  showBackButton={true}
  showNextButton={true}
  onBackPress={() => handleBack()}
  onNextPress={() => handleNext()}
/>
```

## 🎨 Tema Sistemi

### Renkler (`constants/Colors.ts`)
- **Primary**: `#0057B8` (Ana mavi)
- **Secondary**: `#84BD00` (Yeşil)
- **Text**: `#0C0C0D` (Metin rengi)
- **Background**: `#FFFFFF` (Arka plan)
- **Border**: `#EDEDED` (Kenarlık)

### Kullanım
```tsx
import { useThemeColor } from '@/hooks/useThemeColor';

const primaryColor = useThemeColor({}, 'primary');
const backgroundColor = useThemeColor({}, 'background');
```

## 🚀 Kurulum

1. Bağımlılıkları yükleyin:
```bash
npm install
```

2. Uygulamayı başlatın:
```bash
npm start
```

3. Platform seçin:
- iOS: `i`
- Android: `a`
- Web: `w`

## 📦 Bağımlılıklar

- **Expo Router**: Navigasyon
- **React Native SVG**: SVG desteği
- **Expo Image**: Görsel optimizasyonu
- **React Native Safe Area Context**: Güvenli alan yönetimi

## 🏗️ Proje Yapısı

```
app/
├── (tabs)/
│   ├── index.tsx          # Ana sayfa
│   ├── campaigns.tsx      # Kampanyalar
│   ├── explore.tsx        # Keşfet
│   └── _layout.tsx        # Tab düzeni
components/
├── ProfileHeader.tsx      # Profil başlığı
├── CircularProgress.tsx   # Dairesel ilerleme
├── CampaignCard.tsx       # Kampanya kartı
├── TopBar.tsx            # Üst çubuk
├── BottomNavigation.tsx  # Alt navigasyon
└── Popover.tsx           # Tooltip
constants/
└── Colors.ts             # Renk tanımları
```

## 🎨 Figma Tasarımı

Bu uygulama, aşağıdaki Figma tasarım öğelerini içerir:
- Profil bölümü (avatar + selamlama)
- Dairesel ilerleme göstergesi
- Kampanya kartları
- Popover/tooltip bileşeni
- Üst navigasyon çubuğu
- Alt navigasyon

## 📝 Notlar

- Tüm bileşenler TypeScript ile yazılmıştır
- Tema desteği açık/koyu mod için hazırdır
- Bileşenler yeniden kullanılabilir ve modülerdir
- Figma tasarımına sadık kalınmıştır
