# SOP API — Software Order Product

API berbasis **FastAPI** untuk proses **pembelian (purchasing)**, **penjualan (sales)**,
dan **stok** (termasuk perhitungan **HPP metode moving average**). Struktur data dan
alur mengikuti file `docs/Software Order Product.xlsx`.

Database memakai **SQLite lokal** (`sop.db`) untuk sementara. Tinggal ganti
`DATABASE_URL` untuk pindah ke PostgreSQL/MySQL nanti.

## Fitur / Modul

Mengikuti sheet **Flow** pada Excel:

1. Login multi-instance (akses user ke beberapa instance)
2. Pembelian via modul purchasing (`Purchase` + `PurchaseDetail`)
3. Pembuatan invoice dari purchasing
4. Peletakan barang ke lokasi (placement) — paralel dengan invoice
5. HPP terhitung saat barang masuk lokasi (ledger `MASUK`)
6. Payment hanya setelah invoice dibuat
7. Retur invoice (hanya barang yang sudah masuk lokasi)
8. Penjualan via modul sales (ledger `JUAL`)
9. HPP ikut tercatat per baris penjualan
10. Refund penjualan: **REFUND** (barang masuk lagi) atau **REFUND_RUSAK**
11. Refund rusak tidak menambah stok dan tidak masuk lokasi
12. Stok opname + Laporan Stok + Laporan Penjualan Bulanan

## Perhitungan HPP (Moving Average)

- Transaksi **MASUK/BEGBAL** mengubah HPP:
  `hpp_baru = (hpp_lama × saldo_lama + harga_beli × qty) / saldo_baru`
- **JUAL** dan **RETUR** mengurangi stok, HPP tetap (memakai HPP berjalan).
- **REFUND** menambah stok kembali, HPP tetap.
- **REFUND_RUSAK** tidak menambah stok.
- **OPNAME** menyesuaikan stok sesuai hasil hitung fisik, HPP tetap.

Contoh dari sheet terverifikasi: MASUK 10@65.000 di atas sisa 3@60.000
menghasilkan HPP `63.846,15`.

## Menjalankan

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m uvicorn app.main:app --reload
```

Buka dokumentasi interaktif di http://127.0.0.1:8000/docs

## Autentikasi (sementara)

Belum memakai JWT/password. Alurnya:

1. `POST /api/v1/instances` buat instance.
2. `POST /api/v1/users` buat user (sertakan `instance_ids`).
3. `POST /api/v1/auth/login` dengan `user_id` untuk melihat instance yang bisa diakses.
4. Pada setiap request transaksi kirim header:
   - `X-Instance-Id` (wajib) — instance aktif
   - `X-User-Id` (opsional) — pelaku, dicatat pada `created_by`

## Endpoint Utama (prefix `/api/v1`)

| Modul | Endpoint |
|-------|----------|
| Auth / Master | `POST /instances`, `POST /users`, `POST /auth/login`, `POST /vendors`, `POST /barang`, `POST /lokasi` |
| Purchasing | `POST /purchases`, `POST /purchases/{id}/placements` |
| Invoice | `POST /invoices`, `POST /invoices/{id}/retur` |
| Payment | `POST /payments` |
| Sales | `POST /sales`, `POST /sales/{id}/refund` |
| Stok | `GET /ledger`, `POST /opname` |
| Laporan | `GET /laporan/stok`, `GET /laporan/penjualan-bulanan?tahun=&bulan=` |

## Uji Cepat (smoke test)

Menjalankan alur end-to-end dan memverifikasi HPP moving average:

```bash
PYTHONPATH=. .venv/bin/python scripts/smoke_test.py
```

## Struktur Proyek

```
app/
  config.py        # konfigurasi (DATABASE_URL, prefix)
  database.py      # engine SQLAlchemy + session + init_db
  models.py        # ORM: master, transaksi, stock ledger, opname
  schemas.py       # Pydantic request/response
  deps.py          # konteks instance/user via header
  services/stock.py# logika HPP moving average + kartu stok
  routers/         # master, purchasing, invoice, payment, sales, stock
  main.py          # entry point FastAPI
scripts/smoke_test.py
```
