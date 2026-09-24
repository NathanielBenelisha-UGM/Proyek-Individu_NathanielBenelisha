
# Tahap 4: Validasi DIgSILENT PowerFactory
## Skenario Pengujian Transien Kontingensi N-1

**Tanggal:** September 2026  
**Software:** DIgSILENT PowerFactory 2024  
**Referensi UC:** `Coding/Hasil_UC_4_Simulasi_Summary.xlsx`

---

## 1. Struktur File yang Disiapkan

```
Proyek Individual/
├── Coding/
│   ├── export_dispatch_for_digsilent.py   ← Skrip ekspor data UC
│   └── digsilent_n1_contingency.py        ← Skrip otomasi PF (Python API)
│
└── DigSilent/
    ├── dispatch_critical_hours.xlsx       ← Master data semua snapshot
    ├── contingency_test_matrix.csv        ← 27 test cases yang akan dijalankan
    ├── dispatch_S1_t01_valley.csv         ← Kondisi awal S1, jam t=1
    ├── dispatch_S1_t12_midday.csv         ← Kondisi awal S1, jam t=12
    ├── dispatch_S1_t20_peak.csv           ← Kondisi awal S1, jam t=20
    ├── dispatch_S3_t01_valley.csv         ← Kondisi awal S3 (dengan BESS VI)
    ├── dispatch_S3_t12_midday.csv
    ├── dispatch_S3_t20_peak.csv
    ├── dispatch_S4_t01_valley.csv         ← Kondisi awal S4 (BESS VI + EBT)
    ├── dispatch_S4_t12_midday.csv
    ├── dispatch_S4_t20_peak.csv
    └── Results/                           ← Output simulasi transien
```

---

## 2. Matriks Pengujian N-1 (27 Test Cases)

### Dimensi Simulasi

| Dimensi | Variasi |
|---|---|
| **Skenario UC** | S1 (Thermal), S3 (BESS VI), S4 (BESS VI + EBT) |
| **Jam kritis** | t=1 (lembah), t=12 (siang EBT), t=20 (peak demand) |
| **Skema reclose** | t=15s, t=30s, tanpa reclose |

### Tabel Kondisi Awal per Skenario & Jam Kritis

| Skenario | Jam | Demand (MW) | H_sys (MWs) | Largest Loss (MW) | RoCoF_est (Hz/s) | f_QSS_est (Hz) |
|---|---|---|---|---|---|---|
| S1 | t=1  | 4,225.7 | 50,295 | 1,056.0 | 0.5249 | 49.705 |
| S1 | t=12 | 5,032.1 | 42,357 | 931.9   | 0.5500 | 49.501 |
| S1 | t=20 | 5,132.4 | 42,357 | 931.9   | 0.5500 | 49.473 |
| S3 | t=1  | 4,225.7 | 49,647 | 1,056.0 | 0.5318 | 49.689 |
| S3 | t=12 | 5,032.1 | 42,757 | 940.7   | 0.5500 | 49.496 |
| S3 | t=20 | 5,132.4 | 42,357 | 931.9   | 0.5500 | 49.496 |
| S4 | t=1  | 4,225.7 | 49,647 | 1,056.0 | 0.5318 | 49.716 |
| S4 | t=12 | 5,032.1 | 42,757 | 940.7   | 0.5500 | 49.540 |
| S4 | t=20 | 5,132.4 | 42,757 | 940.7   | 0.5500 | 49.537 |

> **Generator yang di-trip: G1 (PLTU, 1,176 MW)** — selalu menjadi contingency N-1 karena memiliki Pmax terbesar.  
> Actual output G1 saat simulasi bervariasi: ~932-1,056 MW tergantung jam.

---

## 3. Langkah Setup DIgSILENT PowerFactory

### 3.1 Persiapan Project

1. **Buka PowerFactory 2024** → Load/buat project sistem tenaga yang sesuai
2. **Pastikan model jaringan sudah ada:**
   - Generator: `Gen_G1` s.d. `Gen_G10` (type: `ElmSym`)
   - BESS: `BESS_B1`, `BESS_B2` (type: `ElmBatt` atau `ElmGenStat`)
   - Wind: `Wind_WT1` (type: `ElmGenStat`)
   - Bus referensi (slack): sesuai sistem

3. **Verifikasi controller BESS VI:**
   - BESS B1: controller VI dengan `Kb_VI = 4.0` MWs/MW
   - BESS B2: controller VI dengan `Kb_VI = 5.0` MWs/MW
   - Formula: `P_VI = -Kb_VI × (df/dt) × P_rated`
   - Model controller: `ElmComp` (composite model) dengan:
     - Input: sinyal frekuensi dari jaringan (df/dt)
     - Output: setpoint daya aktif tambahan P_VI

### 3.2 Import Kondisi Awal dari File CSV

Gunakan DPL script atau Python API:

```python
# Contoh via Python API (jalankan dari PF)
import sys
sys.path.insert(0, r"C:\...\Coding")
from digsilent_n1_contingency import set_initial_conditions, read_dispatch_csv

dispatch_file = r"...\DigSilent\dispatch_S3_t20_peak.csv"
gen_data = read_dispatch_csv(dispatch_file)
app = powerfactory.GetApplication()
set_initial_conditions(app, gen_data, "S3_t20")
```

Atau import manual:
- Buka setiap generator → Tab **Load Flow** → Set `P [MW]` sesuai `P_dispatch_MW` di CSV
- Set status: `out of service` jika `status_on = 0`

### 3.3 Konfigurasi Simulasi RMS

1. **Study Case → Simulation Events (`IntEvt`)**:
   ```
   Event 1: EvtSwitch — Gen_G1 — OPEN  — t = 0.0 s  (TRIP)
   Event 2: EvtSwitch — Gen_G1 — CLOSE — t = 15.0 s (RECLOSE) ← Skema B
   ```

2. **RMS Simulation (`ComSim`)** — Settings:
   ```
   Start time   : 0 s
   Stop time    : 120 s
   Step size    : 0.010 s (10 ms)
   Simulation   : RMS (quasi-steady-state)
   ```

3. **Result Variables yang dimonitor** (tambahkan ke ElmRes):
   ```
   *.ElmSym:c:fi        → Frekuensi (Hz deviation)
   *.ElmSym:c:dfdt      → df/dt = RoCoF (Hz/s)
   *.ElmSym:m:P         → Active power (MW)
   *.ElmSym:m:xspd      → Speed deviation (pu)
   BESS_B1:m:P          → BESS discharge power
   BESS_B1:m:P_VI       → Virtual inertia power
   ```

---

## 4. Skema Event Simulasi

### Skema A: Trip Permanen (No Reclose)
```
t =  0.0 s : G1 TRIP (1,056 MW hilang)
t = 10.0 s : Governor/AGC mulai bereaksi
t = 60.0 s : Frekuensi steady-state (f_QSS)
t = 120.0 s: End simulation
```

### Skema B: Trip + Reclose t=15s (Saran Pak Lesnanto)
```
t =  0.0 s : G1 TRIP
t =  0.0⁺ s: BESS VI instantly responds (< 100 ms)
t =  3-8 s : f_nadir (titik minimum frekuensi)
t = 15.0 s : G1 RECONNECT (nyala kembali)
t = 15⁺ s : Frequency bump (transien reconnection)
t = 60.0 s : Frekuensi recovery menuju 50 Hz
t = 120.0 s: End
```

### Skema C: Trip + Reclose t=30s
```
t =  0.0 s : G1 TRIP
t =  3-8 s : f_nadir
t = 20-25 s: f_QSS stabilized (primary response exhausted)
t = 30.0 s : G1 RECONNECT
t = 45.0 s : Frequency recovery
t = 120.0 s: End
```

---

## 5. Hipotesis & Hasil yang Diharapkan

### H1: BESS VI Memperlambat RoCoF

| Kondisi | Expected RoCoF |
|---|---|
| S1 (no BESS VI) | ≈ 0.5249 Hz/s (lebih rendah karena H_sys > S3 di t=1) |
| S3 (BESS VI ON) | Lebih rendah dari nilai UC estimate karena VI bereaksi instan |
| S4 (VI ON + EBT) | Mirip S3 tapi H_thermal sedikit lebih rendah |

> BESS VI bereaksi dalam **< 100 ms** (power elektronik) vs governor yang butuh **2-3 detik**. Ini berarti RoCoF awal (dalam 1-2 detik pertama) sangat bergantung pada BESS VI.

### H2: f_nadir Lebih Tinggi dengan BESS VI

Perkiraan berdasarkan model SFR (System Frequency Response):
```
f_nadir = f0 - (R_loss × R_droop) / (2H_sys × D)

S1 (no VI): H_sys = 42,357 MWs → f_nadir ≈ 49.05-49.15 Hz
S3 (VI ON): H_sys_eff = H_sys + H_VI ≈ 42,757 MWs → f_nadir ≈ 49.15-49.25 Hz
```

> UFLS threshold: 49.0 Hz. Tanpa VI, sistem mendekati UFLS!

### H3: Reclose t=15s vs t=30s

- **t=15s**: Generator reconnect saat frekuensi masih dalam transien PFR → frekuensi naik lebih cepat, tapi ada transisi reconnection yang bisa menyebabkan frekuensi bump +/-
- **t=30s**: Sistem sudah mencapai f_QSS sebelum reconnect → recovery lebih smooth, frekuensi naik kembali ke ~50 Hz dengan AGC

### H4: Kontribusi BESS VI vs Inertia Thermal

```
Tanpa BESS VI (S1, t=20): H_sys = 42,357 MWs, RoCoF_estimate = 0.550 Hz/s
Dengan BESS VI (S3, t=20): H_sys = 42,357 + 400 = ~42,757 MWs eff (saat VI aktif)
→ RoCoF_with_VI = 50 × 931.9 / (2 × 42757) ≈ 0.5446 Hz/s
→ Improvement: 0.55 - 0.5446 = 0.005 Hz/s (-1%)

Note: Angka kecil karena H_VI relatif kecil vs H_thermal.
Tapi dampak utama BESS VI ada di milliseconds pertama (peak RoCoF reduction).
```

---

## 6. Metrik Output yang Akan Diukur

| Metrik | Simbol | Target/Batas | Cara Ukur di PF |
|---|---|---|---|
| RoCoF awal (0-1s) | dF/dt | ≤ 0.55 Hz/s | max(abs(c:dfdt)) di t=[0,1] |
| Frekuensi nadir | f_nadir | ≥ 49.0 Hz | min(c:fi) + 50 |
| Waktu nadir | t_nadir | ≤ 10 s | t pada min(c:fi) |
| QSS frekuensi | f_QSS | ≥ 49.5 Hz | avg(c:fi) di t=[60,90] |
| Waktu recovery | t_rec | ≤ 60 s | t saat c:fi mencapai 49.5 Hz |
| BESS VI response | t_VI | ≤ 0.1 s | t saat P_VI pertama kali > threshold |
| BESS VI peak power | P_VI_peak | — | max(m:P_VI) di t=[0,5] |
| Overshoot setelah reconnect | Δf_over | < 0.3 Hz | max(c:fi)-49.5 setelah t_reclose |

---

## 7. Prosedur Menjalankan Otomatis via Python API

```bash
# Dari terminal (PowerFactory harus running)
"C:\Program Files\DIgSILENT\PowerFactory 2024\PowerFactory.exe" \
    /Py "D:\UGM\...\Coding\digsilent_n1_contingency.py"
```

Atau dari dalam PF:
- **Tools > Python > Run Script** → pilih `digsilent_n1_contingency.py`

Script akan:
1. Baca `contingency_test_matrix.csv` (27 test cases)
2. Untuk setiap test:
   - Load dispatch CSV → set initial conditions di model PF
   - Configure BESS VI controller (ON/OFF sesuai skenario)
   - Set events (trip + reclose)
   - Run RMS 120s
   - Export time-series CSV + ringkasan metrics
3. Simpan `DigSilent/Results/simulation_results_summary.csv`

---

## 8. Persiapan Manual (Jika Otomasi Tidak Berhasil)

Untuk uji coba awal manual di PF:

### Test Case Prioritas 1: `S3_t20_peak_G1_rc15`
**Kondisi awal S3, t=20 (peak demand, BESS VI aktif):**

| Unit | P (MW) | Status |
|---|---|---|
| G1 | 931.9 | ON |
| G2 | 340.0 | ON |
| G3 | 931.9 | ON |
| G6 | 790.8 | ON |
| G8 | 347.8 | ON |
| G9 | 870.0 | ON |
| G10 | 840.0 | ON |
| G4, G5 | 0 | OFF |
| B1 (BESS) | 60.0 MW discharge + 60 MW VI | ON |
| B2 (BESS) | 0 MW discharge + 20 MW VI | ON |

**Events:**
- t=0s: G1 TRIP
- t=15s: G1 RECLOSE

**Expected:**
- RoCoF(0-1s) ≈ 0.55 Hz/s (dengan VI: sedikit lebih rendah)
- f_nadir ≈ 49.10-49.25 Hz (di atas 49.0 Hz UFLS)
- f_QSS (t=10-15s) ≈ 49.5 Hz
- Setelah reconnect t=15s: frekuensi naik kembali ke ~49.8-50.0 Hz

### Test Case Prioritas 2: `S1_t20_peak_G1_rc15` (baseline pembanding)
Same conditions tapi BESS VI = OFF → compare f_nadir dan RoCoF

---

## 9. Interpretasi Hasil vs Gambar Pak Lesnanto

Mengacu pada **Fig. 9** referensi (Case 1-5 frequency response):

| Case di Paper | Analoginya di Project |
|---|---|
| Case 1: No AGC, 50% PFR | ≈ S1 dengan governor conventional |
| Case 2: No AGC, 100% PFR | ≈ S1 dengan semua governor aktif |
| Case 3: Case 1 + AGC | ≈ S1 + AGC (recovery penuh) |
| **Case 4: Case 1 + AGC + BESS** | ≈ **S3/S4 dengan BESS VI** ← fokus utama |
| Case 5: Case 2 + AGC | ≈ S3 + AGC |

> **Key observation**: Case 4 (dengan BESS) di gambar menunjukkan:
> - f_nadir lebih tinggi (~49.3 Hz) vs Case 1 (~49.15 Hz)
> - Recovery lebih cepat karena BESS menyokong frekuensi
> - Setelah reconnect (t≈45s di grafik), ada "dip kedua" karena transisi
>
> Hasil yang diharapkan di project ini akan mengikuti pola Case 4 untuk S3/S4
> dan Case 1 untuk S1 (baseline).

---

*Laporan ini merangkum persiapan Tahap 4 — Validasi DIgSILENT PowerFactory.*  
*Skrip tersedia di `Coding/` dan data di `DigSilent/`.*
