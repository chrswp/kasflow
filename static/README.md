# KasFlow — Single-File PWA Cash Tracker

Aplikasi cash tracker (cash in / cash out) berupa **1 file HTML** dengan MongoDB alternatif: **Firebase Firestore + Storage**. Host di **GitHub Pages** (gratis), install sebagai PWA di Android.

## Fitur

- ✅ Cash in / cash out / balance
- ✅ Purpose, tanggal, catatan, upload bukti (foto / PDF)
- ✅ Filter Semua / Cash in / Cash out
- ✅ Export **Petty Cash Report** ke Excel (format styled)
- ✅ Backup export & import JSON
- ✅ PWA installable di Android (add to home screen)
- ✅ Offline shell (data tetap perlu online untuk sync)
- ✅ Data aman: anonymous auth per-device, security rules Firestore

---

## STEP 1 — Setup Firebase (Gratis, ± 10 menit)

### 1.1. Buat Project
1. Login https://console.firebase.google.com
2. Klik **Add project** → beri nama (misal `kasflow`) → matikan Google Analytics (opsional) → Create

### 1.2. Aktifkan Anonymous Auth
1. Menu kiri: **Build → Authentication → Get started**
2. Tab **Sign-in method** → klik **Anonymous** → **Enable** → Save

### 1.3. Aktifkan Firestore
1. Menu kiri: **Build → Firestore Database → Create database**
2. Pilih **Production mode** → region terdekat (misal `asia-southeast2` untuk Jakarta) → Enable
3. Tab **Rules** → paste rules ini:

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
4. Klik **Publish**

### 1.4. Aktifkan Storage
1. Menu kiri: **Build → Storage → Get started**
2. Pilih **Production mode** → Next → region sama dengan Firestore → Done
3. Tab **Rules** → paste rules ini:

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
4. Klik **Publish**

### 1.5. Daftarkan Web App
1. Klik ⚙️ **Project settings** (kanan atas)
2. Scroll ke bawah **Your apps** → klik icon **</> (Web)**
3. Nickname: `KasFlow Web` → **Register app** (skip hosting)
4. **Copy** object `firebaseConfig`, contoh:

```
const firebaseConfig = {
  apiKey: "AIzaSyABC...",
  authDomain: "kasflow-xxxx.firebaseapp.com",
  projectId: "kasflow-xxxx",
  storageBucket: "kasflow-xxxx.appspot.com",
  messagingSenderId: "1234567890",
  appId: "1:1234567890:web:abc..."
};
```

### 1.6. Tambahkan domain GitHub Pages ke authorized domains
1. **Authentication → Settings → Authorized domains → Add domain**
2. Tambahkan `USERNAME.github.io` (ganti USERNAME dengan username GitHub Anda)

---

## STEP 2 — Deploy ke GitHub Pages

### 2.1. Push ke GitHub
1. Buat repo baru di GitHub, misal `kasflow`
2. Push isi folder `/app/static/`:
   ```bash
   cd /app/static
   git init
   git add .
   git commit -m "Initial KasFlow single-file PWA"
   git branch -M main
   git remote add origin https://github.com/USERNAME/kasflow.git
   git push -u origin main
   ```

### 2.2. Aktifkan GitHub Pages
1. Buka repo di GitHub → **Settings → Pages**
2. **Source**: Deploy from a branch
3. **Branch**: `main` + folder `/ (root)` → **Save**
4. Tunggu 1-2 menit. URL akan muncul:
   ```
   https://USERNAME.github.io/kasflow/
   ```

### 2.3. Setup Aplikasi (Pertama Kali)
1. Buka URL di atas di browser (**Chrome di Android** direkomendasikan)
2. Layar setup muncul → paste `firebaseConfig` yang Anda copy → **Simpan & Mulai**
3. Config tersimpan di localStorage device Anda

### 2.4. Install sebagai PWA di Android
1. Buka aplikasi di Chrome Android
2. Menu 3-titik → **Add to Home screen** (atau **Install app**)
3. Icon KasFlow akan muncul di home screen — bisa dibuka fullscreen seperti app native

---

## STEP 3 — Pakai Aplikasi

- **+ Tambah transaksi** → pilih Cash in / Cash out, isi form, upload bukti jika perlu
- **Filter tabs** → lihat semua / cash in only / cash out only
- **Menu 3-titik** kanan atas:
  - **Export ke Excel** → download `.xlsx` styled Petty Cash Report
  - **Backup ke JSON** → download semua data sebagai `.json`
  - **Import dari JSON** → restore data dari backup
  - **Ganti Firebase config** → reset & masukkan config lain

---

## Struktur File

| File | Fungsi |
|---|---|
| `index.html` | Aplikasi utama — semua HTML, CSS, JS dalam 1 file |
| `manifest.webmanifest` | Metadata PWA (nama, icon, warna) |
| `sw.js` | Service worker untuk offline shell |
| `icon.svg` / `icon-192.png` / `icon-512.png` / `icon-maskable.png` | Icon PWA |
| `README.md` | File ini |

---

## ⚠️ Catatan Penting

### Batas Firebase Free (Spark Plan)
- **Firestore**: 50k reads/hari + 20k writes/hari + 1 GiB storage — cukup untuk ribuan transaksi
- **Storage**: 5 GB total + 1 GB/hari download — cukup untuk ratusan foto bukti
- **Auth Anonymous**: gratis unlimited

### Anonymous Auth = Data Terikat Device
- User ID (uid) dibuat otomatis dan disimpan di localStorage browser
- Kalau clear browser data → uid baru → tidak bisa akses data lama (**data tetap ada di Firebase, hanya tidak terlihat**)
- **Selalu backup ke JSON secara berkala!**
- Untuk multi-device / recovery, upgrade ke Email/Google Auth (butuh sedikit modifikasi kode)

### Bukti (Evidence) Tidak Ter-backup ke JSON
- File di Firebase Storage tetap ada, tapi backup JSON hanya menyimpan **URL** (bukan file)
- Kalau URL Storage lama sudah tidak valid (karena project Firebase berbeda), bukti tidak bisa dibuka ulang saat import

### Update Aplikasi
- Ubah `index.html` di komputer → push ke GitHub → GitHub Pages auto-deploy dalam 1-2 menit
- **Naikkan versi cache** di `sw.js` (`kasflow-v1` → `v2`) supaya user dapat versi baru, atau tunggu 24 jam untuk auto-refresh

### Local Testing (Sebelum Deploy)
```bash
cd /app/static
python3 -m http.server 8080
# Buka http://localhost:8080
```

Selamat mencatat! 💰
