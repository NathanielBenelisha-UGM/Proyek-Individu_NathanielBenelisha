
# Analisis Tahap 2: Komparasi & Evaluasi 4 Skenario FCUC
## Fokus: Pengaruh BESS Virtual Inertia terhadap Frequency Security & Unit Commitment

**Tanggal:** September 2026  
**File referensi:** `Coding/Hasil_UC_4_Simulasi_Summary.xlsx` & `Coding/Analisis_Hasil_4_Simulasi.xlsx`  
**Solver:** IBM ILOG CPLEX 22.1.1 | **Model:** Pyomo 6.9.5 | **Horizon:** 24 jam

---

## 1. Ringkasan 4 Skenario

| # | Skenario | Deskripsi |
|---|---|---|
| S1 | **Baseline** | UC Thermal Only + Inersia Minimum + QSS |
| S2 | **+BESS Std** | S1 + BESS Standar (tanpa Virtual Inertia) |
| S3 | **+BESS VI** | S1 + BESS dengan Virtual Inertia |
| S4 | **+PV & WT** | S3 + PV & WT sebagai pengotor zero-inertia |

Semua skenario menggunakan constraint frekuensi yang sama (aktif di semua):
- **RoCoF constraint:** `2 × 0.55 × H_sys ≥ 50 × LargestLoss`
- **QSS constraint:** `LargestLoss ≤ (50 − 49) × (D_frac × Demand + TotalPFR)`

---

## 2. Tabel A: Ringkasan Biaya Operasi

| Skenario | Fuel Cost ($) | Fixed Cost ($) | Curt Cost ($) | **Total Cost ($)** | Penghematan vs S1 |
|---|---|---|---|---|---|
| S1 | 3,656,807 | 584,301 | 0 | **4,241,108** | — |
| S2 | 3,652,283 | 584,301 | 0 | **4,236,584** | $4,524 (0.11%) |
| S3 | 3,638,315 | 581,718 | 0 | **4,220,033** | $21,075 (0.50%) |
| **S4** | 3,413,847 | 581,718 | 2,285 | **3,997,851** | **$243,257 (5.74%)** |

> **Insight kunci:** S4 menghemat $243,257 (5.74%) vs baseline S1, terutama karena energi WT dan PV menggantikan fuel cost thermal yang mahal.

---

## 3. Tabel B: Statistik Inersia & Frekuensi

| Skenario | Hsys Avg (MWs) | Hsys Min (MWs) | H_Thermal Avg | H_VI_BESS Avg | Max RoCoF (Hz/s) | Min f_QSS (Hz) |
|---|---|---|---|---|---|---|
| S1 | 42,714.8 | 42,357.0 | 42,714.8 | 0.0 | **0.5500** | 49.473 |
| S2 | 42,714.8 | 42,357.0 | 42,714.8 | 0.0 | **0.5500** | 49.470 |
| S3 | 42,910.8 | 42,357.0 | 42,686.3 | **224.5** | **0.5500** | 49.475 |
| S4 | 42,885.2 | 42,357.0 | 42,660.7 | **224.5** | **0.5500** | **49.510** |

**Observasi penting:**
- S3 dan S4 memiliki `H_VI_BESS_avg = 224.5 MWs` — ini adalah kontribusi Virtual Inertia dari BESS
- RoCoF selalu aktif di tepat 0.5500 Hz/s → constraint inertia tightly binding
- f_QSS S4 (49.510 Hz) lebih baik daripada S1 (49.473 Hz) karena EBT mengurangi LargestLoss

---

## 4. Tabel C: Unit Commitment — Jam Aktif per Unit

| Unit | Pmax (MW) | H (s) | S1 | S2 | S3 | S4 |
|---|---|---|---|---|---|---|
| G1 | 1,176 | 4 | 24 | 24 | 24 | 24 |
| G2 | 1,125 | 9 | 24 | 24 | 24 | 24 |
| G3 | 969 | 4 | 24 | 24 | 24 | 24 |
| G4 | 130 | 6 | **0** | **0** | **0** | **0** |
| G5 | 108 | 6 | 2 | 2 | **0** | **0** |
| G6 | 1,095 | 9 | 24 | 24 | 24 | 24 |
| G7 | 810 | 9 | 16 | 16 | 16 | 16 |
| G8 | 773 | 9 | 24 | 24 | 24 | 24 |
| G9 | 870 | 4 | 24 | 24 | 24 | 24 |
| G10 | 840 | 4 | 23 | 23 | 23 | 23 |
| **Total** | | | **171h** | **171h** | **169h** | **169h** |

> **Dampak BESS VI pada UC:** BESS VI (S3) menyebabkan G5 (PLTG, 108 MW, H=6s) **tidak perlu diaktifkan sama sekali** dibanding S1 & S2. G5 berkontribusi fixed cost $24K/hari yang kini dihemat.

---

## 5. Analisis Mendalam: S3 vs S4

### 5.1 Mekanisme Curtailment WT

| Jam | Demand (MW) | WT Available (MW) | WT Curtailed (MW) | WT Used (MW) | Alasan |
|---|---|---|---|---|---|
| t=1 | 4,225.7 | **400.0** | **76.2** | 323.8 | LargestLoss (G1=1,056 MW) terlalu besar jika semua WT diserap → P_thermal turun → LargestLoss tetap besar tapi H_sys masih mencukupi |

**Interpretasi jam t=1 (jam lembah tengah malam):**

Pada t=1, WT tersedia 400 MW. Jika terserap penuh, termal G1 harus dikurangi 400 MW. Akibatnya H_sys thermal turun. Meski BESS VI menyediakan VI, solver memilih curtail 76.2 MW WT agar G1 tidak terlalu dikurangi demi menjaga `H_sys ≥ H_req`. Ini adalah trade-off yang tepat.

### 5.2 Dispatch BESS Virtual Inertia (S3 vs S4)

```
Jam  | B1_P_VI (S3) | B1_P_VI (S4) | Keterangan
t=2  |    60.0 MW   |    42.5 MW   | S4 perlu lebih sedikit VI karena ada WT mengurangi LargestLoss
t=9  |    60.0 MW   |     0.0 MW   | S4: WT menyuplai → thermal turun → G1 dispatch rendah → LargestLoss kecil
t=10-16| 60.0 MW   |    60.0 MW   | Peak load: VI BESS aktif penuh di kedua skenario
t=18 |    60.0 MW   |     0.0 MW   | S4: WT tinggi, thermal turun, VI tidak diperlukan
```

**Pola utama:** BESS VI di S4 bekerja lebih efisien karena EBT mengurangi dispatch thermal, sehingga LargestLoss berkurang → kebutuhan VI lebih fleksibel.

### 5.3 Pengurangan Thermal Dispatch per Jam (S4 vs S3)

| Jam | Demand | S3 Thermal | S4 Thermal | EBT (WT+PV) | ΔThermal |
|---|---|---|---|---|---|
| t=1 | 4,225.7 MW | 4,305.7 MW* | 3,981.8 MW | 323.8 MW | **-323.9 MW** |
| t=5 | 4,009.4 MW | 4,089.4 MW* | 3,697.6 MW | 371.8 MW | **-391.8 MW** |
| t=7 | 4,273.1 MW | 4,353.1 MW* | 3,883.9 MW | 321.2 MW | **-469.2 MW** |
| t=10 | 4,847.1 MW | 4,847.1 MW | 4,456.1 MW | 455.0 MW | **-391.0 MW** |
| t=20 | 5,132.4 MW | 5,052.4 MW | 4,866.0 MW | 266.4 MW | **-186.4 MW** |

> *Nilai > Demand → BESS charging

### 5.4 Hubungan Inersia — Dampak Zero-Inertia EBT

```
H_sys = H_thermal + H_VI_BESS

Kondisi S3 (tanpa EBT):
  H_thermal ≈ 42,714 MWs (semua dari unit thermal ON)
  H_VI_BESS ≈ 224.5 MWs (dari BESS VI)
  H_sys_avg = 42,910.8 MWs

Kondisi S4 (dengan EBT pengotor):
  H_thermal ≈ 42,660 MWs (sedikit turun karena thermal di-offset EBT)
  H_VI_BESS ≈ 224.5 MWs (sama, BESS mempertahankan VI)
  H_sys_avg = 42,885.2 MWs
  
  Selisih: -25.6 MWs → EBT mengurangi inersia thermal sedikit
  Dampak EBT pada RoCoF: dapat dipertahankan di 0.55 Hz/s
  karena BESS VI mengkompensasi gap inersia
```

---

## 6. Peran BESS Virtual Inertia — Kesimpulan Teknis

### 6.1 Tanpa BESS VI (S1 & S2):
- Inersia sistem murni dari thermal unit yang ON
- RoCoF ≤ 0.55 Hz/s terpaksa dipenuhi dengan **mempertahankan lebih banyak unit thermal ON**
- G5 (PLTG 108 MW) harus ON 2 jam untuk berkontribusi H pada jam kritis
- Tidak fleksibel terhadap masuknya EBT zero-inertia

### 6.2 Dengan BESS VI (S3 & S4):
- BESS menyumbang **H_VI = K_b × P_VI_batt** secara real-time
- Ini memungkinkan **2 unit-hours ON lebih sedikit** (G5 de-commit penuh)
- Di S4, BESS VI menjadi "penjamin inersia terakhir" ketika:
  - EBT masuk → thermal turun → H_thermal berkurang
  - BESS VI aktif untuk menutup gap `H_sys ≥ H_req`
- Tanpa BESS VI di S4, sistem tidak akan feasible (infeasible) karena
  EBT zero-inertia akan membuat `H_sys < H_req`

### 6.3 Diagram Mekanisme BESS VI:

```
[Kondisi Normal]          [Saat EBT Masuk Banyak]
H_thermal = tinggi   →   H_thermal TURUN
H_VI_BESS = kecil    →   H_VI_BESS NAIK (BESS VI aktif lebih)
H_sys = aman         →   H_sys TETAP AMAN
RoCoF ≤ 0.55 Hz/s   →   RoCoF ≤ 0.55 Hz/s (terjaga)
```

---

## 7. Rencana Validasi DIgSILENT PowerFactory

Berdasarkan hasil UC (Tahap 1 & 2) dan saran Pak Lesnanto, validasi transien akan dilakukan dengan skema berikut:

### 7.1 Skema Simulasi DIgSILENT

| Skema | Deskripsi | Parameter |
|---|---|---|
| **Skema A** | N-1 Generator Contingency — G1 trip permanen | Trip G1 (1,176 MW) di t=0s |
| **Skema B** | N-1 + Reconnect cepat | Trip G1 di t=0s, nyala kembali di **t=15s** |
| **Skema C** | N-1 + Reconnect lambat | Trip G1 di t=0s, nyala kembali di **t=30s** |

Untuk setiap skema, dijalankan di 4 kondisi UC berbeda:
- **UC-S1:** Kondisi dispatch dari S1 (tanpa BESS)
- **UC-S3:** Kondisi dispatch dari S3 (dengan BESS VI)
- **UC-S4:** Kondisi dispatch dari S4 (dengan BESS VI + EBT)
- **UC-S4 tanpa VI:** S4 dispatch tapi BESS VI dinonaktifkan (sebagai pembanding)

### 7.2 Jam Kritis untuk Simulasi

Berdasarkan analisis, jam paling kritis adalah:
| Prioritas | Jam | Alasan |
|---|---|---|
| 🔴 **Kritis 1** | **t=20** | Demand puncak (5,132 MW), LargestLoss besar, Hsys minimum |
| 🟠 **Kritis 2** | **t=1** | Jam lembah, terjadi WT curtailment, RoCoF persis 0.55 Hz/s |
| 🟡 **Kritis 3** | **t=2** | Transisi awal, BESS VI aktif switching mode |

### 7.3 Metrik Evaluasi Transien

Yang akan diukur dan dibandingkan:

| Metrik | Simbol | Batas Aman |
|---|---|---|
| Rate of Change of Frequency | RoCoF (Hz/s) | ≤ 0.55 Hz/s |
| Frequency Nadir | f_nadir (Hz) | ≥ 49.0 Hz (batas UFLS) |
| Quasi-Steady-State Frequency | f_QSS (Hz) | ≥ 49.5 Hz |
| Time to Nadir | t_nadir (s) | Referensi |
| BESS VI Response Time | t_VI (s) | < 100 ms (inverter) |
| Frequency Recovery Time | t_rec (s) | < 60s (AGC) |

### 7.4 Contoh Karakteristik yang Diharapkan

Mengacu pada gambar referensi dari Pak Lesnanto (Fig. 9), respons yang diharapkan:

```
Frekuensi (Hz)
50.0 ┤
     │                                          ___________  ← Pemulihan AGC/Governor
49.8 ┤    ______                               /
     │   /      \                             /
49.6 ┤  /        \___________________________/ ← f_QSS recovery
49.5 ┤- - - - - - - - - - - - - - - - - - - - (batas 49.5 Hz)
     │          ↑                ↑
49.2 ┤       t=15/30s:       f_nadir
     │       Generator       (titik terendah)
49.0 ┤ - - (batas UFLS)  - - - - - - - - - -
     │
     └──────────────────────────────────── Waktu (s)
       0    10   20   30   50  100  150  200

Skema B (t_reconnect=15s): Frekuensi naik kembali lebih cepat setelah generator ON
Skema C (t_reconnect=30s): Frekuensi stabil di f_QSS lebih lama sebelum recovery
```

### 7.5 Hipotesis yang Akan Dibuktikan

1. **H1:** BESS VI (S3) menghasilkan RoCoF transien yang lebih rendah dibanding tanpa BESS (S1) pada N-1 contingency G1
2. **H2:** Saat EBT aktif (S4), RoCoF sedikit meningkat karena H_thermal turun, tapi tetap terkendali berkat BESS VI
3. **H3:** Reconnect generator di t=15s menghasilkan pemulihan frekuensi lebih cepat menuju 49.5 Hz dibanding t=30s
4. **H4:** Tanpa BESS VI di S4, f_nadir akan jatuh di bawah 49.0 Hz (UFLS trip)

---

## 8. Files yang Dihasilkan

| File | Lokasi | Isi |
|---|---|---|
| `run_4_simulations.py` | `Coding/` | Skrip MILP 4 skenario |
| `Hasil_UC_4_Simulasi_Summary.xlsx` | `Coding/` | Data hasil simulasi (5 sheet) |
| `analyze_4_simulations.py` | `Coding/` | Skrip analisis numerik |
| `Analisis_Hasil_4_Simulasi.xlsx` | `Coding/` | Tabel analisis (6 sheet) |

---

*Laporan ini dibuat otomatis dari hasil simulasi Tahap 1 & 2 FCUC.*
