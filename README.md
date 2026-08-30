# Proyek Individu — Nathaniel Benelisha
## Optimisasi Penentuan Penjadwalan Pembangkit Mempertimbangkan Pembangkit Berbasis Inverter

**Mahasiswa:** Nathaniel Benelisha  
**Program Studi:** Teknik Elektro — Universitas Gadjah Mada  
**Jenis Luaran:** Publikasi Ilmiah (Pengganti Skripsi)  
**Semester:** 7 — TA 2026/2027

---

## Deskripsi Penelitian

Penelitian ini bertujuan mengembangkan metode optimisasi penjadwalan pembangkit (**generation scheduling / unit commitment**) pada sistem tenaga listrik dengan mempertimbangkan penetrasi **pembangkit berbasis inverter (Inverter-Based Resources/IBR)**, seperti:
- Pembangkit Listrik Tenaga Surya (PLTS)
- Pembangkit Listrik Tenaga Bayu (PLTB)
- Battery Energy Storage System (BESS)

Model optimisasi yang dikembangkan adalah **Frequency-Constrained Unit Commitment (FCUC)** yang tidak hanya meminimalkan biaya operasi, tetapi juga mempertimbangkan kekangan keamanan frekuensi melalui penyediaan **inersia virtual (virtual inertia)** dari BESS dan/atau IBR.

---

## Tahapan Pengerjaan

| No | Tahap | Deskripsi |
|----|-------|-----------|
| 1 | **Pemodelan Sistem** | Model pembangkit konvensional & IBR, model BESS sebagai penyedia inersia virtual, dinamika frekuensi pasca-kontingensi |
| 2 | **Formulasi Optimisasi** | Fungsi objektif (minimisasi biaya operasi), kekangan UC klasik, kekangan keamanan frekuensi (RoCoF, Nadir, inersia minimum) |
| 3 | **Simulasi** | Implementasi menggunakan MATLAB / Python / GAMS pada sistem uji dengan penetrasi IBR tinggi |
| 4 | **Analisis Dampak** | Evaluasi pengaruh inersia virtual terhadap biaya operasi (ekonomi) dan keamanan frekuensi (teknis) |

---

## Target Capaian / Kriteria Keberhasilan

1. **Pemodelan:** model pembangkit (IBR & non-IBR), BESS, stabilitas frekuensi akibat N-1, virtual inertia, dinamika frekuensi pasca-contingency
2. **Formulasi Optimasi:** fungsi objektif (biaya operasi), constraint UC klasik, keamanan frekuensi (RoCoF, Nadir, QSS), inersia sistem
3. **Simulasi:** implementasi optimasi menggunakan MATLAB/Python/GAMS
4. **Analisis Dampak:** pengaruh biaya pembangkitan atau keamanan frekuensi akibat penetrasi IBR dan virtual inertia

---

## Struktur Repositori

```
📁 Proyek-Individu_NathanielBenelisha/
├── 📁 Referensi/
│   ├── 📁 Full Referensi/       # Paper-paper utama (74 file)
│   └── 📁 Unit Commitment/      # Referensi khusus UC (10 file)
├── 📄 README.md
└── 📄 .gitignore
```

---

## Kata Kunci

`Unit Commitment` · `Frequency-Constrained UC` · `Inverter-Based Resources` · `Virtual Inertia` · `BESS` · `RoCoF` · `Frequency Nadir` · `N-1 Contingency` · `Power System Optimization`
