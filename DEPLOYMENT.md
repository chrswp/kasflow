# Panduan Deploy KasFlow (Manual)

Panduan lengkap deploy aplikasi KasFlow menggunakan:
- **Frontend** → GitHub Pages (gratis)
- **Backend** → Railway (free tier)
- **Database** → MongoDB Atlas (free tier M0)

Estimasi waktu setup: **60–90 menit**

---

## PRASYARAT

1. Akun **GitHub** (https://github.com)
2. Akun **MongoDB Atlas** (https://www.mongodb.com/cloud/atlas/register)
3. Akun **Railway** (https://railway.app) — login pakai GitHub
4. **Git** terinstal di komputer lokal
5. **Node.js 18+** dan **yarn** terinstal di lokal

---

## STEP 1 — Push Kode ke GitHub

1. Buat repo baru di GitHub, misal: `kasflow`
2. Di komputer lokal, dari folder `/app`:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/USERNAME/kasflow.git
   git push -u origin main
   ```

---

## STEP 2 — Setup MongoDB Atlas (Database)

1. Login ke https://cloud.mongodb.com
2. Klik **"Build a Database"** → pilih **M0 FREE**
3. Pilih provider (AWS) & region terdekat → klik **Create**
4. Buat **Database User**:
   - Username: `kasflow_admin`
   - Password: (buat password kuat, catat!)
5. **Network Access** → **Add IP Address** → **Allow Access from Anywhere** (`0.0.0.0/0`)
6. Kembali ke **Database** → klik **Connect** → **Drivers**
7. Copy connection string. Contoh:
   ```
   mongodb+srv://kasflow_admin:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
8. Ganti `<password>` dengan password asli, tambahkan nama DB `/kasflow`:
   ```
   mongodb+srv://kasflow_admin:PASSWORD_ANDA@cluster0.xxxxx.mongodb.net/kasflow?retryWrites=true&w=majority
   ```
9. **Simpan connection string ini** — akan dipakai di Railway.

---

## STEP 3 — Deploy Backend ke Railway

1. Login https://railway.app → pakai GitHub
2. Klik **"New Project"** → **"Deploy from GitHub repo"** → pilih repo `kasflow`
3. Railway akan detect otomatis, klik **"Add Service"**
4. Buka service yang dibuat → **Settings**:
   - **Root Directory**: `backend`
   - **Start Command**: sudah otomatis dari `Procfile` (tidak perlu diubah)
5. Buka tab **Variables** → tambahkan 3 environment variables:
   | Key | Value |
   |---|---|
   | `MONGO_URL` | connection string dari Step 2 (yang sudah diganti password + `/kasflow`) |
   | `DB_NAME` | `kasflow` |
   | `CORS_ORIGINS` | `https://USERNAME.github.io` (nanti diisi setelah Step 4) |
6. Buka tab **Settings** → **Networking** → klik **Generate Domain**
7. Copy URL yang muncul, contoh: `https://kasflow-production.up.railway.app`
8. Test dengan buka `https://kasflow-production.up.railway.app/api/` di browser — harus muncul:
   ```json
   {"message": "KasFlow API aktif"}
   ```

---

## STEP 4 — Deploy Frontend ke GitHub Pages

### 4.1. Set backend URL di frontend

Edit file `/app/frontend/.env.production`, ganti dengan URL Railway Anda:
```
REACT_APP_BACKEND_URL=https://kasflow-production.up.railway.app
```

### 4.2. Install gh-pages

Dari folder `/app/frontend`:
```bash
yarn add --dev gh-pages
```

### 4.3. Edit `frontend/package.json`

Tambahkan di paling atas (setelah `"private": true,`):
```json
"homepage": "https://USERNAME.github.io/kasflow",
```

Di bagian `"scripts"`, tambahkan:
```json
"predeploy": "yarn build",
"deploy": "gh-pages -d build"
```

### 4.4. Build & deploy

```bash
cd frontend
yarn deploy
```

Command ini akan:
- Build project React ke folder `build/`
- Push isi folder `build/` ke branch `gh-pages` di GitHub

### 4.5. Aktifkan GitHub Pages

1. Buka repo di GitHub → **Settings** → **Pages**
2. Di bagian **Branch**, pilih **`gh-pages`** + folder **`/ (root)`** → klik **Save**
3. Tunggu 1–2 menit, situs akan aktif di:
   ```
   https://USERNAME.github.io/kasflow
   ```

---

## STEP 5 — Update CORS di Railway

1. Kembali ke Railway → project → **Variables**
2. Update variable `CORS_ORIGINS`:
   ```
   https://USERNAME.github.io
   ```
3. Railway akan otomatis restart backend

---

## STEP 6 — Test Deployment

1. Buka `https://USERNAME.github.io/kasflow` di browser (atau Android)
2. Coba:
   - Buat transaksi cash in / cash out
   - Lihat balance
   - Export ke Excel

Jika ada error, cek:
- **Console browser** (F12) → tab Console/Network untuk lihat error API
- **Railway logs** → project → **Deployments** → **View Logs**

---

## ⚠️ CAVEATS PENTING

### 1. Upload Bukti (Evidence) — Ephemeral Storage
Railway free tier menggunakan **ephemeral disk** — artinya setiap kali backend restart, file yang di-upload di `backend/uploads/` akan **hilang**.

**Solusi:** Migrasi ke object storage (S3 / Cloudflare R2 / MongoDB GridFS).
Jika belum, dokumen bukti hanya bertahan sampai deployment berikutnya.

### 2. Railway Free Tier Limits
- $5 credit/bulan gratis (± 500 jam runtime service kecil)
- Sleep otomatis jika tidak dipakai lama
- Untuk produksi jangka panjang, upgrade atau pakai alternatif: **Render.com** (free tier tidak habis credit, tapi cold start 30 detik).

### 3. MongoDB Atlas M0 Limits
- Storage: 512 MB
- Cukup untuk ribuan transaksi

### 4. HTTPS Wajib untuk PWA
GitHub Pages sudah otomatis HTTPS ✅. PWA install akan berfungsi.

### 5. Update Deployment
Setiap perubahan kode:
- **Backend**: `git push` ke GitHub → Railway auto-deploy
- **Frontend**: jalankan `yarn deploy` lagi dari folder `frontend`

---

## ALTERNATIF BACKEND HOSTING (kalau Railway tidak cocok)

| Provider | Free Tier | Kelebihan | Kekurangan |
|---|---|---|---|
| **Railway** | $5 credit/bulan | Setup mudah, auto-deploy dari GitHub | Credit bisa habis |
| **Render** | 750 jam/bulan | Selalu gratis untuk 1 service | Cold start 30 detik |
| **Fly.io** | 3 shared VM gratis | Global edge, cepat | Setup CLI perlu Docker |
| **Koyeb** | 1 service gratis | Simple, cepat | Terbatas 1 service |

Semua provider di atas support `Procfile` + `runtime.txt` yang sudah dibuat, jadi bisa langsung deploy tanpa ubah kode.

---

## FILE YANG SUDAH DISIAPKAN

- `/app/backend/Procfile` — start command untuk Railway/Render
- `/app/backend/runtime.txt` — Python 3.11
- `/app/backend/nixpacks.toml` — build config Railway
- `/app/frontend/.env.production` — env untuk production build
- `/app/.gitignore` — ignore file yang tidak perlu di-commit

---

Selamat deploy! 🚀
