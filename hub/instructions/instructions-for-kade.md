Architected by doctorcodex/ drferdiiskandar
Developed by doctorcodex/ drferdiiskandar

# 📘 INSTRUKSI UNTUK KADE (v2025)

## 🎯 TUJUAN
Membangun sistem monorepo SENTRA yang berisi:
- Infrastructure Hub (pusat data & logika AI)
- Dashboard (Next.js) sebagai alat kontrol manual
- MCP (Main Connection Points) sebagai jalur resmi antar-AI dan antar-proyek

---

## 🧱 STRUKTUR UTAMA
sentra/
├─ infrastructure/
│  ├─ hub/
│  │  ├─ instructions/
│  │  ├─ sessions/
│  │  ├─ discussions/
│  │  └─ version.json
│  ├─ ops/
│  ├─ agents/
│  ├─ configs/
│  ├─ scripts/
│  └─ dashboard/
│     ├─ app/
│     ├─ lib/
│     ├─ public/
│     ├─ styles/
│     ├─ next.config.mjs
│     ├─ package.json
│     └─ .env.local
├─ cortex/
├─ aadi/
├─ pogs/
└─ README.md

---

## ⚙️ MCP & TOOLS WAJIB

Setiap AI (Dex, Kade, Rex, Nova, dsb.) wajib menggunakan alat resmi berikut:

| Tool | Fungsi |
|------|---------|
| Dashboard (Next.js) | UI + API utama untuk semua aksi (rehydrate, memory, rollup, packet). |
| Hub (Filesystem/GitHub) | Sumber kebenaran tunggal (hub/, version.json, sessions, discussions). |
| Ops Scripts (Python/Shell) | Untuk health-check, fix, dan compliance. |
| LLM Bridge (Clipboard/API) | Jalur komunikasi eksternal ke LLM. |

Semua interaksi harus melalui salah satu MCP resmi:
/infrastructure/hub/
/infrastructure/dashboard/
/infrastructure/scripts/
/infrastructure/configs/

Dilarang:
- Menulis langsung di luar /infrastructure/ atau /hub/
- Menggunakan API tidak resmi
- Mengubah arsitektur tanpa izin dari Chief

---

## 🧩 LANGKAH IMPLEMENTASI

1. **Siapkan lingkungan dev**
   node -v
   npm -v
   python3 --version
   git --version

2. **Pastikan folder sesuai struktur di atas**
   Jika hub/ belum lengkap, ambil dari paket Boss (the-infrastructure-hub.zip).

3. **Buat .env.local**
   Lokasi: sentra/infrastructure/dashboard/.env.local

   DATA_BACKEND=fs

   (dev pakai fs untuk baca/tulis langsung ke file. Saat deploy ke Vercel → DATA_BACKEND=github + token.)

---

## 🧠 ENDPOINT WAJIB (4 FUNGSI DASAR)

Semua endpoint disimpan di:
sentra/infrastructure/dashboard/app/api/

| Endpoint | Fungsi |
|-----------|--------|
| GET /api/rehydrate | Baca hub/version.json, ambil sesi terbaru, tampilkan data. |
| POST /api/memory | Simpan note/decision/issue/context ke hub/discussions/. Jika context → update version.json. |
| POST /api/rollup | Buat hub/sessions/<date>.md + append ops/health/daily.md. |
| GET /api/packet | Keluarkan LLM Context Packet (text/plain) untuk copy. |

---

## 📁 LIBRARY PENDUKUNG

lib/git.ts
- Tentukan backend (fs atau github):
  const mode = process.env.DATA_BACKEND || 'fs';
- Jika fs → gunakan fs/promises untuk baca/tulis lokal.
- Jika github → gunakan GitHub REST API (v3, contents API).

lib/hub.ts
- Fungsi pembantu:
  ensureCredits()
  appendMarkdownSection()
  updateVersionContext()
  sessionTemplate()
  discussionTemplate()

---

## 🧩 UJI CEPAT (LOCAL)

1. Jalankan dashboard:
   cd sentra/infrastructure/dashboard
   npm install
   npm run dev

2. Buka http://localhost:3000

3. Klik “Rehydrate” → data tampil dari hub/version.json
4. Tambah Note/Context → file baru muncul di hub/discussions/
5. Klik “Rollup” → file baru muncul di hub/sessions/
6. Klik “Copy Packet” → teks muncul (LLM-ready)

---

## 🔒 COMPLIANCE

Semua hasil kerja:
- Harus punya kredit:
  Architected by doctorcodex/ drferdiiskandar
  Developed by doctorcodex/ drferdiiskandar
- Dicatat di ops/health/daily.md
- Dapat diaudit lewat commit dashboard

---

## 💬 PESAN DARI CHIEF

Kade, mulai implementasi monorepo sesuai dokumen terbaru.
Gunakan struktur sentra/infrastructure/, pastikan semua AI bekerja melalui MCP resmi,
dan hanya pakai alat yang sudah disetujui.
Fokus dulu pada implementasi 4 endpoint utama (backend fs).
Setelah stabil, baru integrasi ke GitHub untuk deploy.
