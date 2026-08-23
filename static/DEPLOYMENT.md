# Panduan Deploy KasFlow (Single-File PWA)

Panduan lengkap deploy aplikasi KasFlow versi **single HTML** ke **GitHub Pages** dengan database **Firebase** (Firestore + Storage + Anonymous Auth). Semua **gratis**.

> Total waktu setup: **± 20–30 menit** (baru pertama kali)

---

## DAFTAR ISI

1. [Prasyarat](#step-0--prasyarat)
2. [Setup Firebase Project](#step-1--setup-firebase)
3. [Push Kode ke GitHub](#step-2--push-kode-ke-github)
4. [Aktifkan GitHub Pages](#step-3--aktifkan-github-pages)
5. [Setup Aplikasi Pertama Kali](#step-4--setup-aplikasi-di-browser)
6. [Install sebagai PWA di Android](#step-5--install-sebagai-pwa-di-android)
7. [Troubleshooting](#troubleshooting)
8. [Update Aplikasi](#update-aplikasi)

---

## STEP 0 — Prasyarat

Siapkan hal berikut sebelum mulai:

- [ ] Akun **GitHub** → https://github.com/signup (gratis)
- [ ] Akun **Google** (untuk Firebase) → gunakan Gmail yang sudah ada
- [ ] **Git** terinstal di komputer → https://git-scm.com/downloads
- [ ] Editor teks apa saja (VS Code, Notepad, dll)
- [ ] **Hp Android** dengan **Chrome** (untuk install PWA)
- [ ] Folder proyek: **`/app/static/`** — sudah berisi semua file yang dibutuhkan:
  ```
  /app/static/
  ├── index.html            ← aplikasi utama (1 file berisi semua)
  ├── manifest.webmanifest  ← metadata PWA
  ├── sw.js                 ← service worker (offline)
  ├── icon.svg
  ├── icon-192.png
  ├── icon-512.png
  ├── icon-maskable.png
  └── README.md
  ```

---

## STEP 1 — Setup Firebase

### 1.1. Buat Firebase Project

1. Buka https://console.firebase.google.com
2. Login dengan akun Google
3. Klik **Add project** (atau **Tambah proyek**)
4. Nama project: `kasflow` (atau nama lain terserah) → **Continue**
5. Google Analytics: **Disable** (tidak diperlukan) → **Create project**
6. Tunggu ± 30 detik → klik **Continue**

### 1.2. Aktifkan Anonymous Authentication

1. Di sidebar kiri: **Build → Authentication**
2. Klik **Get started**
3. Tab **Sign-in method** → cari **Anonymous** di daftar
4. Klik **Anonymous** → toggle **Enable** ON → **Save**
5. ✅ Anonymous auth aktif

### 1.3. Buat Firestore Database

1. Sidebar: **Build → Firestore Database**
2. Klik **Create database**
3. Pilih lokasi: **`asia-southeast2 (Jakarta)`** (atau region terdekat) → **Next**
4. Pilih **Start in production mode** → **Create**
5. Tunggu ± 30 detik sampai database siap
6. Klik tab **Rules**, hapus isi default, paste ini:

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{uid}/transactions/{doc} {
      allow read, write: if request.auth != null && request.auth.uid == uid;
    }
  }
}
```

7. Klik **Publish** → confirm

### 1.4. Aktifkan Firebase Storage

1. Sidebar: **Build → Storage**
2. Klik **Get started**
3. **Start in production mode** → **Next**
4. Pilih lokasi (sama dengan Firestore) → **Done**
5. Klik tab **Rules**, hapus isi default, paste ini:

```
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    match /users/{uid}/evidence/{file=**} {
      allow read, write: if request.auth != null && request.auth.uid == uid;
    }
  }
}
```

6. Klik **Publish**

### 1.5. Daftarkan Web App & Copy Config

1. Klik ikon **⚙️ Project settings** (pojok kiri atas dekat "Project Overview")
2. Scroll ke bawah **Your apps** → klik ikon **`</>` (Web)**
3. App nickname: `KasFlow Web` → **Register app** (skip "Firebase Hosting")
4. Anda akan melihat kode seperti ini:

```js
const firebaseConfig = {
  apiKey: "AIzaSyABC123XYZ...",
  authDomain: "kasflow-abc123.firebaseapp.com",
  projectId: "kasflow-abc123",
  storageBucket: "kasflow-abc123.appspot.com",
  messagingSenderId: "1234567890",
  appId: "1:1234567890:web:abcdef123456"
};
```

5. **Copy** seluruh object `firebaseConfig` di atas (dari `{` sampai `}`)
6. Simpan sementara di notepad → akan di-paste ke aplikasi nanti (Step 4)
7. Klik **Continue to console**

### 1.6. Tambahkan Domain GitHub Pages ke Authorized Domains

> Anda akan tahu domain GitHub setelah Step 3, tapi bisa juga tambahkan sekarang jika sudah tahu username GitHub.

1. Sidebar: **Build → Authentication → Settings** (tab)
2. Scroll ke **Authorized domains** → klik **Add domain**
3. Ketik: `USERNAME.github.io` (ganti `USERNAME` dengan username GitHub Anda, contoh: `budi123.github.io`)
4. **Add**

✅ **Setup Firebase selesai!**

---

## STEP 2 — Push Kode ke GitHub

### 2.1. Buat Repository Baru di GitHub

1. Login https://github.com
2. Klik tombol **+** kanan atas → **New repository**
3. Repository name: `kasflow` (atau nama lain)
4. **Public** (wajib untuk GitHub Pages gratis)
5. **Jangan** centang "Add README" (kita sudah punya file sendiri)
6. Klik **Create repository**
7. Catat URL repo, misal: `https://github.com/budi123/kasflow.git`

### 2.2. Push Folder `/app/static/` ke Repo

Buka terminal / command prompt di komputer, jalankan:

```bash
cd /app/static

git init
git add .
git commit -m "Initial commit: KasFlow single-file PWA"
git branch -M main
git remote add origin https://github.com/USERNAME/kasflow.git
git push -u origin main
```

> Ganti `USERNAME` dengan username GitHub Anda.

Kalau diminta login, gunakan **Personal Access Token** (bukan password):
- Buat token di: https://github.com/settings/tokens → Generate new token (classic) → centang `repo` scope → Generate
- Copy token → paste sebagai password saat prompt

Setelah `git push` berhasil, refresh halaman repo di GitHub — file sudah muncul.

---

## STEP 3 — Aktifkan GitHub Pages

1. Buka repo di GitHub → tab **Settings**
2. Di sidebar kiri: **Pages**
3. Bagian **Source**:
   - Pilih **Deploy from a branch**
4. Bagian **Branch**:
   - Pilih **`main`** + folder **`/ (root)`** → **Save**
5. Tunggu **1–3 menit**. Refresh halaman.
6. Kalau sudah aktif, muncul kotak hijau dengan URL:
   ```
   ✓ Your site is live at https://USERNAME.github.io/kasflow/
   ```
7. Buka URL tersebut → seharusnya muncul **layar Setup Firebase**

> ⚠️ Kalau muncul 404: tunggu 1 menit lagi, GitHub kadang butuh waktu. Kalau > 5 menit tetap 404, cek **Actions** tab di repo untuk error.

---

## STEP 4 — Setup Aplikasi di Browser

Sekali saja, di device pertama:

1. Buka URL GitHub Pages (contoh: `https://budi123.github.io/kasflow/`)
2. **Layar "Setup Firebase"** muncul
3. Di kotak textarea, **paste** object `firebaseConfig` yang tadi di-copy (Step 1.5):

```json
{
  "apiKey": "AIzaSyABC123XYZ...",
  "authDomain": "kasflow-abc123.firebaseapp.com",
  "projectId": "kasflow-abc123",
  "storageBucket": "kasflow-abc123.appspot.com",
  "messagingSenderId": "1234567890",
  "appId": "1:1234567890:web:abcdef123456"
}
```

> Format bebas — bisa JSON asli atau langsung paste JS object dengan `const firebaseConfig = { ... };`

4. Klik **Simpan & Mulai**
5. Halaman refresh otomatis → **Dashboard KasFlow** muncul dengan saldo Rp 0
6. Config Firebase tersimpan di localStorage device Anda (tidak perlu setup ulang)

✅ Kalau ada error toast merah "Firebase gagal: auth/api-key-not-valid...", lihat [Troubleshooting](#troubleshooting).

---

## STEP 5 — Install sebagai PWA di Android

### 5.1. Buka di Chrome Android

1. Buka Chrome di Android
2. Ketik URL GitHub Pages Anda: `https://USERNAME.github.io/kasflow/`
3. Setup Firebase (kalau belum) — sama seperti Step 4
4. Setelah dashboard muncul, ketuk menu **⋮** (3 titik) di kanan atas Chrome
5. Pilih **Add to Home screen** atau **Install app**
6. Confirm → icon KasFlow muncul di home screen Android
7. Buka dari home screen → aplikasi berjalan **fullscreen** tanpa address bar

### 5.2. Verifikasi Fitur

Cek satu per satu:

- [ ] **+ Tambah transaksi** → Cash in Rp 1.000.000 → tersimpan → saldo update
- [ ] Tambah Cash out dengan **upload bukti** (foto/PDF) → cek link "Bukti" muncul
- [ ] **Filter tabs** (Semua / Cash in / Cash out) berfungsi
- [ ] Menu **⋮** → **Export ke Excel** → file `.xlsx` terunduh
- [ ] Menu **⋮** → **Backup ke JSON** → file `.json` terunduh
- [ ] **Monthly Recap** card muncul (kalau ada transaksi bulan ini)
- [ ] Setelah 7 hari, banner **Backup mingguan siap** muncul otomatis

---

## TROUBLESHOOTING

### Error: `auth/api-key-not-valid`
- Config Firebase salah copy. Kembali ke Firebase console → Project settings → Your apps → copy ulang seluruh `firebaseConfig`
- Menu **⋮ → Ganti Firebase config** → paste ulang

### Error: `Firestore permission denied` / `Missing or insufficient permissions`
- Firestore Rules belum di-publish. Ulangi **Step 1.3** poin 6-7
- Pastikan match path `/users/{uid}/transactions/{doc}` (bukan path lain)

### Error: `Storage/unauthorized` saat upload bukti
- Storage Rules belum di-publish. Ulangi **Step 1.4** poin 5-6

### Error: `auth/unauthorized-domain`
- Domain GitHub Pages belum ditambahkan ke Authorized domains. Ulangi **Step 1.6**

### PWA install option tidak muncul di Chrome Android
- Pastikan URL HTTPS (GitHub Pages auto-HTTPS ✓)
- Refresh halaman 2-3 kali sampai service worker terdaftar
- Buka **chrome://flags** → cari "Desktop PWAs" → pastikan enabled
- Buka Chrome DevTools (via komputer) → Application tab → Manifest → cek tidak ada error

### Aplikasi tidak update setelah push kode baru
- Bump versi cache di `sw.js` (misal `kasflow-v2` → `kasflow-v3`) sebelum push
- Di Android: buka **Settings → Apps → KasFlow → Storage → Clear cache**
- Atau tunggu 24 jam — service worker auto-update

### Data hilang setelah clear browser
- Anonymous auth = UID disimpan di localStorage. Kalau di-clear → UID baru → **data lama masih ada di Firebase tapi tidak bisa diakses**
- Solusi: rajin **Backup ke JSON** (auto-banner tiap 7 hari)
- Untuk multi-device / recovery permanent, upgrade ke Email auth (butuh sedikit modifikasi kode — bisa diminta ke developer)

---

## UPDATE APLIKASI

Setiap kali ada perubahan kode:

```bash
cd /app/static

# 1. Edit file (index.html, sw.js, dll)

# 2. Naikkan versi cache supaya user dapat update
#    Edit sw.js: const CACHE = 'kasflow-v3';  ← naikkan angka

# 3. Commit & push
git add .
git commit -m "Update: [deskripsi perubahan]"
git push
```

GitHub Pages auto-deploy dalam **1–2 menit**. User akan otomatis dapat versi baru saat buka aplikasi (atau setelah service worker refresh).

---

## LOCAL TESTING (Opsional, Sebelum Deploy)

Untuk test di komputer sebelum push ke GitHub:

```bash
cd /app/static
python3 -m http.server 8080
# Buka http://localhost:8080 di browser
```

> ⚠️ Firebase Anonymous Auth **butuh HTTPS atau `localhost`** (tidak jalan di file:// atau IP).

---

## BATAS FIREBASE FREE (Spark Plan)

| Layanan | Batas Gratis | Estimasi Muat |
|---|---|---|
| **Firestore Reads** | 50.000 / hari | ± 5.000× buka aplikasi/hari |
| **Firestore Writes** | 20.000 / hari | ± 20.000 transaksi baru/hari |
| **Firestore Storage** | 1 GiB | Puluhan ribu transaksi |
| **Cloud Storage** | 5 GB total | ± 5.000 foto bukti (@1MB) |
| **Storage Download** | 1 GB / hari | Cukup untuk pemakaian pribadi |
| **Auth Anonymous** | Unlimited | ✓ |

Untuk **pemakaian pribadi 1 device**, batas ini **tidak akan pernah tercapai**.

---

## STRUKTUR FILE FINAL

```
kasflow/                        ← repo GitHub Anda
├── index.html                  (aplikasi utama, 30+ KB)
├── manifest.webmanifest        (metadata PWA)
├── sw.js                       (service worker offline)
├── icon.svg                    (icon vektor)
├── icon-192.png                (icon PWA kecil)
├── icon-512.png                (icon PWA besar)
├── icon-maskable.png           (icon Android bulat)
├── README.md                   (dokumentasi ringkas)
└── DEPLOYMENT.md               (file ini)
```

---

## RINGKASAN URL PENTING

| Layanan | URL |
|---|---|
| Firebase Console | https://console.firebase.google.com |
| GitHub | https://github.com |
| GitHub Pages settings | `https://github.com/USERNAME/kasflow/settings/pages` |
| Aplikasi live | `https://USERNAME.github.io/kasflow/` |

---

Selamat mencatat! 💰

Kalau ada pertanyaan atau menemui error, cek section [Troubleshooting](#troubleshooting) dulu, atau baca log error di Chrome DevTools (F12 di desktop) → tab Console.
