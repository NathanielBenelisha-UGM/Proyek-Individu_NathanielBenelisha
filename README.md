# Proyek Individu — Nathaniel Benelisha

## Frequency-Constrained Unit Commitment with Multi-Source Virtual Inertia Provision from Inverter-Based Resources

**Mahasiswa:** Nathaniel Benelisha  
**Mahasiswa S3 (Penulis 2):** Muhammad Aris Risnandar  
**Pembimbing:** Ir. Lesnanto Multa Putranto, S.T., M.Eng., Ph.D., IPM., ASEAN Eng., SMIEEE  
**Program Studi:** Teknik Elektro — Universitas Gadjah Mada  
**Jenis Luaran:** Publikasi Ilmiah (Pengganti Skripsi)  
**Semester:** 7 — TA 2026/2027

---

## Deskripsi Penelitian

Penelitian ini mengembangkan model optimisasi **Frequency-Constrained Unit Commitment (FCUC)** yang secara simultan meng-co-optimize penjadwalan pembangkit konvensional dan penyediaan **virtual inertia** dari **Inverter-Based Resources (IBR)** — termasuk Battery Energy Storage System (BESS) dan turbin angin — dalam framework **Mixed-Integer Linear Programming (MILP)**.

Model diimplementasikan menggunakan **Python 3.9 / Pyomo** dan diselesaikan dengan **IBM CPLEX 22.1.1**. Tujuh skenario simulasi dievaluasi pada sistem uji IEEE 10-unit yang dimodifikasi, menunjukkan bahwa co-optimizing renewable integration dan virtual inertia dapat **menurunkan biaya operasi 2.24%** sambil **memenuhi semua constraint keamanan frekuensi** (RoCoF ≤ 0.55 Hz/s).

---

## Struktur Repositori

```
📁 Proyek-Individu_NathanielBenelisha/
│
├── 📄 README.md                    # Dokumen ini
├── 📄 .gitignore                   # File yang diabaikan Git
├── 📄 persiapan_bimbingan.md       # Catatan persiapan bimbingan
│
├── 📁 Coding/                      # Source code & data simulasi
│   ├── 📁 Presentasi/              # Slide presentasi bimbingan
│   ├── 📄 Coba_16_*.ipynb          # Notebook utama (versi final)
│   ├── 📄 DataSet_*.xlsx           # Dataset generator & beban
│   ├── 📄 Hasil_UC_*.xlsx          # Hasil simulasi 7 skenario
│   └── 📄 README.md
│
├── 📁 Paper/                       # Draft publikasi ilmiah (LaTeX)
│   ├── 📄 main_v2.tex              # Draft paper v2 (terbaru)
│   ├── 📄 main.tex                 # Draft paper v1 (awal)
│   ├── 📁 figures/                 # Gambar/grafik untuk paper
│   └── 📄 README.md
│
├── 📁 Referensi/                   # Koleksi paper referensi (84 file)
│   ├── 📁 Full Referensi/          # Semua referensi terkategorisasi
│   ├── 📁 Unit Commitment/         # Referensi khusus fundamental UC
│   └── 📄 README.md
│
├── 📁 CAPSTONE/                    # Dokumen Capstone Design terkait
│   └── 📄 README.md
│
└── 📄 A_NathanielBenelisha_*.pdf   # Surat pernyataan akademik
```

---

## Ringkasan Hasil Simulasi

| Skenario | Deskripsi | Total Cost (USD/day) | vs. S1 | Freq. Secure? |
|----------|-----------|---------------------|--------|---------------|
| **S1** | Classical UC | 4,029,223 | — | ❌ (24/24 violasi) |
| **S2** | + BESS | 4,019,885 | −0.23% | ❌ |
| **S3** | + BESS + Wind | 3,716,391 | −7.76% | ❌ |
| **S4** | + Min Inertia (SG only) | 4,176,358 | +3.65% | ✅ |
| **S5** | + Min Inertia + Wind | 3,944,158 | −2.11% | ✅ |
| **S6** | + BESS-VI | 3,938,983 | −2.24% | ✅ |
| **S7** | **Full Model (BESS-VI + WT-VI + QSS)** | **3,939,091** | **−2.24%** | **✅** |

---

## Teknologi & Tools

| Tool | Versi | Penggunaan |
|------|-------|------------|
| Python | 3.9 | Bahasa pemrograman utama |
| Pyomo | 6.9.5 | Algebraic modeling language |
| IBM CPLEX | 22.1.1 | MILP solver |
| LaTeX (IEEEtran) | — | Penulisan paper |
| Jupyter Notebook | — | Eksperimen & visualisasi |

---

## Kata Kunci

`Unit Commitment` · `Frequency-Constrained UC (FCUC)` · `Virtual Inertia` · `Inverter-Based Resources (IBR)` · `Battery Energy Storage System (BESS)` · `Wind Turbine` · `RoCoF` · `Frequency Nadir` · `MILP` · `Pyomo` · `CPLEX` · `Indonesia` · `RUPTL 2025-2034`
