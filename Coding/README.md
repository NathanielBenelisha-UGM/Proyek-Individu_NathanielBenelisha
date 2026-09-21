# 📁 Coding — Source Code & Data Simulasi

Folder ini berisi seluruh kode sumber, dataset, dan hasil simulasi untuk model **Frequency-Constrained Unit Commitment (FCUC)** dengan virtual inertia.

---

## Struktur File

### 🔬 Notebook Utama (Versi Final)

| File | Keterangan |
|------|------------|
| `Coba_16_20260612_R00_vinertia_cplexdirect.ipynb` | ⭐ **Notebook utama** — formulasi FCUC lengkap dengan virtual inertia dari BESS dan wind turbine |
| `Coba_16_*_EXECUTED.ipynb` | Versi yang sudah dieksekusi (dengan output) |
| `Coba_16_*_FULL.ipynb` | Versi full (semua skenario) |
| `Coba_16_*_FULL_EXECUTED.ipynb` | Versi full yang sudah dieksekusi |

### 📊 Dataset

| File | Keterangan |
|------|------------|
| `DataSet_ModifikasiCandra_R02.xlsx` | ⭐ **Dataset final** — data generator 10-unit, demand 24-jam, BESS, dan wind turbine |
| `DataSet_ModifikasiCandra_R00/R01.xlsx` | Versi dataset sebelumnya |
| `DataSet_R00` s.d. `DataSet_R05.xlsx` | Dataset iterasi awal (eksplorasi) |

### 📈 Hasil Simulasi

| File | Keterangan |
|------|------------|
| `Hasil_UC_AllScenarios_Summary.xlsx` | ⭐ **Rekap seluruh skenario** — total cost, inertia, RoCoF |
| `Hasil_UC_Skenario1.xlsx` s.d. `Skenario7.xlsx` | Hasil detail per skenario (jadwal unit, daya, SoC, dll.) |
| `Analisis Data R01.xlsx` | Analisis tambahan |

### 📓 Notebook Iterasi Pengembangan (Coba_1 s.d. Coba_15)

Notebook bertahap yang mendokumentasikan proses pengembangan model:

| Tahap | Notebook | Fitur yang Ditambahkan |
|-------|----------|------------------------|
| Eksplorasi | `Coba_1` s.d. `Coba_5` | UC dasar, economic dispatch, formulasi awal |
| MILP UC | `Coba_6` s.d. `Coba_9` | Constraint UC lengkap, migrasi ke CPLEX |
| + BESS | `Coba_10` s.d. `Coba_12` | Integrasi Battery Energy Storage |
| + Battery | `Coba_13` | Model baterai lanjutan |
| + Wind | `Coba_14` | Integrasi turbin angin |
| + Inertia | `Coba_15` | Constraint inersia minimum |
| + V.Inertia | `Coba_16` | ⭐ Virtual inertia (BESS-VI + WT-VI) |

### 📁 Presentasi/

Slide presentasi untuk sesi bimbingan dengan pembimbing:

| File | Tanggal | Topik |
|------|---------|-------|
| `Presentasi 20260611-LMP R00.pptx` | 11 Juni 2026 | Progress awal |
| `Presentasi 20260615-LMP R01.pptx` | 15 Juni 2026 | Hasil UC + frequency analysis |
| `Presentasi 20260623-LMP R00.pptx` | 23 Juni 2026 | Hasil 7 skenario lengkap |

---

## Cara Menjalankan

### Prasyarat

1. **Python 3.9+** dengan packages: `pyomo`, `openpyxl`, `pandas`, `numpy`, `matplotlib`
2. **IBM CPLEX 22.1.1** — instal dari folder `cplex-22.1.1/` (tidak di-track Git karena ukuran besar)

### Eksekusi

```bash
# Buka notebook utama
jupyter notebook Coba_16_20260612_R00_vinertia_cplexdirect.ipynb

# Ubah CONFIG dictionary untuk memilih skenario (S1-S7)
# Jalankan semua cell
```

### Konfigurasi Skenario

Skenario dikontrol melalui dictionary `CONFIG` di notebook:

```python
CONFIG = {
    'con_battery': True/False,      # Aktifkan BESS
    'con_wt': True/False,           # Aktifkan Wind Turbine
    'con_min_inertia': True/False,  # Constraint inersia minimum
    'con_battery_vi': True/False,   # Virtual inertia dari BESS
    'con_wt_vi': True/False,        # Virtual inertia dari WT
    'con_qss_limit': True/False,    # Constraint QSS frequency
}
```
