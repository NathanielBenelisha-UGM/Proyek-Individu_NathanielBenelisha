# 📋 Desain & Verifikasi 4 Skenario Simulasi Baru FCUC

Dokumen ini merangkum perancangan ulang simulasi optimasi *Frequency-Constrained Unit Commitment* (FCUC), verifikasi constraint BESS dan Virtual Inertia, serta identifikasi pemodelan PV dan Wind Turbine (WT) sebagai variabel pengotor beserta perhitungan *curtailment cost*.

---

## 📌 1. Matriks Aktivasi Constraint (Simulasi 1 s.d. 4)

Mengacu pada 10 constraint dasar UC Konvensional (dari lembar konfigurasi) ditambah constraint inkremental pada masing-masing skenario:

| No | Parameter / Constraint di Kode | Fungsi Fisis dalam Model | Sim 1: UC + Min Inertia | Sim 2: + BESS Standar | Sim 3: + BESS VI | Sim 4: + PV & WT (Pengotor) |
|:--:|:---|:---|:---:|:---:|:---:|:---:|
| 1 | `use_initial_condition` | Kondisi awal generator ($u_{g,0}, P_{g,0}$, riwayat status) | ✅ **Aktif** | ✅ **Aktif** | ✅ **Aktif** | ✅ **Aktif** |
| 2 | `con_startup_shutdown_logic` | Hubungan biner komitmen generator ($u, y, z$) | ✅ **Aktif** | ✅ **Aktif** | ✅ **Aktif** | ✅ **Aktif** |
| 3 | `con_power_balance` | Neraca daya pemenuhan beban ($\sum P = \text{Demand}$) | ✅ **Aktif** *(Thermal)* | ✅ **Aktif** *(+ BESS)* | ✅ **Aktif** *(+ BESS)* | ✅ **Aktif** *(+ BESS + WT + PV)* |
| 4 | `con_capacity_upper` | Batas kapasitas maksimum generator ($P \le P_{\max} \cdot u$) | ✅ **Aktif** | ✅ **Aktif** | ✅ **Aktif** | ✅ **Aktif** |
| 5 | `con_capacity_lower` | Batas minimum teknis generator ($P \ge P_{\min} \cdot u$) | ✅ **Aktif** | ✅ **Aktif** | ✅ **Aktif** | ✅ **Aktif** |
| 6 | `con_minimum_up_time` | Waktu operasi minimum generator sebelum dimatikan | ✅ **Aktif** | ✅ **Aktif** | ✅ **Aktif** | ✅ **Aktif** |
| 7 | `con_minimum_down_time` | Waktu padam minimum generator sebelum dinyalakan | ✅ **Aktif** | ✅ **Aktif** | ✅ **Aktif** | ✅ **Aktif** |
| 8 | `con_ramp_up` | Batas laju kenaikan output antar-jam ($RampUp$) | ✅ **Aktif** | ✅ **Aktif** | ✅ **Aktif** | ✅ **Aktif** |
| 9 | `con_ramp_down` | Batas laju penurunan output antar-jam ($RampDown$) | ✅ **Aktif** | ✅ **Aktif** | ✅ **Aktif** | ✅ **Aktif** |
| 10 | `con_n1_spinning_reserve` | Cadangan putar $N-1$ $\ge$ kapasitas generator terbesar | ✅ **Aktif** | ✅ **Aktif** | ✅ **Aktif** | ✅ **Aktif** |
| 11 | `con_min_inertia` | Batas minimum inersia sistem ($2 \cdot \text{RoCoF}_{\lim} \cdot H_{\text{sys}} \ge f_0 \cdot \Delta P^{\max}$) | ✅ **Aktif** *(100% Thermal)* | ✅ **Aktif** *(100% Thermal)* | ✅ **Aktif** *(Thermal + BESS VI)* | ✅ **Aktif** *(Thermal + BESS VI)* |
| 12 | `con_qss_limit` & PFR | Batasan frekuensi kuasi-tunak QSS ($f_{\text{qss}} \ge 49.5\text{ Hz}$) via cadangan PFR droop governor | ✅ **Aktif** *(PFR Thermal)* | ✅ **Aktif** *(PFR Thermal)* | ✅ **Aktif** *(PFR Thermal)* | ✅ **Aktif** *(PFR Thermal)* |
| 13 | `con_battery` | Dinamika BESS (P_ch, P_dis, SOC, batas kapasitas) | ❌ Non-Aktif | ✅ **Aktif** | ✅ **Aktif** | ✅ **Aktif** |
| 14 | `con_battery_vi` | Respon inersia virtual BESS ($P_{b,t}^{\text{VI}}$ & alokasi inverter) | ❌ Non-Aktif | ❌ Non-Aktif ($P^{\text{VI}} = 0$) | ✅ **Aktif** | ✅ **Aktif** |
| 15 | `con_wt` & `con_wt_curtailment` | Injeksi daya PLTB & batasan pembuangan daya angin | ❌ Non-Aktif | ❌ Non-Aktif | ❌ Non-Aktif | ✅ **Aktif** *(Pengotor)* |
| 16 | `con_pv` & `con_pv_curtailment` *(Baru)* | Injeksi daya PLTS & batasan pembuangan daya surya | ❌ Non-Aktif | ❌ Non-Aktif | ❌ Non-Aktif | ✅ **Aktif** *(Pengotor)* |
| 17 | `obj_curtailment_cost` *(Baru)* | Penalti biaya pembuangan energi terbarukan PV & WT | ❌ Non-Aktif | ❌ Non-Aktif | ❌ Non-Aktif | ✅ **Aktif** |
| 18 | `con_wt_vi` / `con_pv_vi` | Emulasi inersia dari WT / PV | ❌ Non-Aktif | ❌ Non-Aktif | ❌ Non-Aktif | ❌ Non-Aktif *(Murni 0 VI)* |

> [!NOTE]
> **Pilar Keamanan Frekuensi Dua Dimensi (RoCoF + QSS) Aktif di Keempat Simulasi:**
> - **Dimensi 1 — RoCoF Limit (`con_min_inertia`):** Menjaga laju penurunan frekuensi awal ($t = 0^+$) agar tidak melanggar batas $0.55\text{ Hz/s}$.
> - **Dimensi 2 — QSS Frequency Limit (`con_qss_limit` & PFR):** Menjamin titik pemulihan frekuensi kuasi-tunak ($t = 10\text{--}30\text{ s}$) tidak anjlok di bawah $49.5\text{ Hz}$ melalui penyediaan *Primary Frequency Response* (PFR) dari unit termal yang memiliki *free governor*.

---

## 🔍 2. Rincian Konsep & Perilaku Fisis Tiap Simulasi

### 🔹 Simulasi 1: UC Konvensional + Minimum Inertia
* **Konsep:** Baseline sistem tenaga konvensional dengan 10 unit generator termal (G1–G10) yang harus melayani beban sistem 24 jam.
* **Inersia Sistem:** 100% dipikul oleh generator sinkron termal yang sedang online:
  $$H_{\text{sys},t} = \sum_{g=1}^{10} H_g P_g^{\max} u_{g,t}$$
* **Constraint Inersia:**
  $$2 \cdot \text{RoCoF}_{\lim} \cdot H_{\text{sys},t} \ge f_0 \cdot \text{LargestLoss}_t$$
* **Karakteristik Operasi:** Karena inersia hanya berasal dari generator sinkron, unit termal dengan konstanta inersia besar terpaksa tetap dinyalakan (meskipun berbiaya bahan bakar mahal) demi mencegah pelanggaran RoCoF.
* **Status BESS & EBT:** Tidak ada (BESS = 0 MW, WT = 0 MW, PV = 0 MW).

---

### 🔹 Simulasi 2: Simulasi 1 + Constraint Battery (BESS Standar)
* **Konsep:** Memasukkan Battery Energy Storage System (BESS B1 & B2) untuk fungsi **arbitrase energi / load shifting murni**.
* **Peran BESS:**
  * Mengisi daya (*charging*, $P_{b,t}^{\text{ch}}$) saat beban rendah / harga marjinal murah.
  * Melepaskan daya (*discharging*, $P_{b,t}^{\text{dis}}$) saat beban puncak.
* **Perilaku Inersia:** BESS **TIDAK** menyediakan Virtual Inertia ($P_{b,t}^{\text{VI}} = 0$ via constraint `BatteryVIOff`).
* **Inersia Sistem:** Masih **100% dipikul oleh generator sinkron termal**. Keberadaan baterai hanya membantu memangkas biaya bahan bakar daya aktif, tetapi belum bisa mengurangi beban komitmen unit termal untuk inersia.
* **Status EBT:** Tidak ada (WT = 0 MW, PV = 0 MW).

---

### 🔹 Simulasi 3: Simulasi 2 + Constraint Battery Virtual Inertia (BESS VI)
* **Konsep:** BESS kini dioperasikan dengan kendali emulasi inersia sintetis (*Virtual Inertia*). Inverter BESS merespons deviasi laju frekuensi ($df/dt$).
* **Alokasi Daya Inverter (Coupling Headroom):**
  Kapasitas converter baterai ($DR_b^{\max}$) dialokasikan bersama untuk discharging daya aktif dan cadangan daya inersia virtual:
  $$P_{b,t}^{\text{dis}} + \frac{P_{b,t}^{\text{VI}}}{\eta_b^{\text{VI}}} \le DR_b^{\max} \cdot u_{b,t}^{\text{dis}}$$
* **Kontribusi Inersia Sistem:**
  $$H_{\text{batt\_vi},t} = \sum_{b \in \text{BATT}} K_b^{\text{VI}} \cdot P_{b,t}^{\text{VI}}$$
  $$H_{\text{sys},t} = \sum_{g=1}^{10} H_g P_g^{\max} u_{g,t} + H_{\text{batt\_vi},t}$$
* **Dampak Tekno-Ekonomi:** Keberadaan $H_{\text{batt\_vi}}$ mensubstitusi inersia mekanik generator termal. Unit-unit termal yang mahal yang sebelumnya wajib menyala di Simulasi 1 & 2 kini **bisa dimatikan (*de-commitment*)**, sehingga biaya operasi termal turun signifikan tanpa melanggar batasan RoCoF.
* **Status EBT:** Belum ada (WT = 0 MW, PV = 0 MW).

---

### 🔹 Simulasi 4: Simulasi 3 + Variabel PV + WT (Sebagai Pengotor)
* **Konsep:** Mengintegrasikan pembangkit energi terbarukan intermiten skala besar: PLTB (Wind Turbine 400 MW) dan PLTS (Solar PV hingga ~200 MW).
* **Definisi Filosofis & Fisis "Pengotor":**
  1. PV dan WT terhubung via inverter *grid-following* standar **tanpa emulasi inersia ($H_{\text{pv}} = 0, H_{\text{wt}} = 0, P^{\text{VI}} = 0$)**.
  2. Penetrasi daya PV dan WT mendesak turun output generator termal.
  3. Desakan ini memaksa unit termal dimatikan, yang berakibat **inersia inheren sistem anjlok secara drastis**. Kehadiran EBT yang fluktuatif ini merusak ketahanan inersia sistem (inilah esensi sebutan *"pengotor"*).
* **Peran BESS VI:** Menjadi benteng pertahanan utama untuk menyuplai inersia sintetis saat inersia termal runtuh akibat penetrasi EBT.
* **Curtailment & Curtailment Cost:**
  Jika daya PV/WT melimpah namun sistem tidak mampu menyerapnya karena batas minimum teknis generator termal ($P_{\min}$) atau keterbatasan inersia sistem, maka kelebihan daya EBT **wajib dibuang (*curtailed*)**, dan timbul biaya kerugian ekonomi (*Curtailment Cost*).

---

## ⚡ 3. Pembedaan Konsep: Deloading vs Curtailment

| Parameter | Deloading (Jika EBT sebagai VI) | Curtailment (Karena EBT sebagai Pengotor) |
|:---|:---|:---|
| **Peran EBT** | Penyedia Inersia Virtual / Cadangan Frekuensi | Murni Pembangkit Energi Intermiten (Zero Inertia) |
| **Titik Kerja Operasi** | Di bawah kurva MPPT optimal (menyisakan margin 10–20%) | Pada titik daya maksimum (MPPT) |
| **Tujuan Margin** | Menyimpan cadangan daya kinetik/daya aktif untuk disuntikkan saat frekuensi turun | Tidak ada margin cadangan yang disimpan |
| **Kondisi Pemotongan** | Disengaja secara kontinu sepanjang waktu (*headroom*) | Hanya terjadi jika terjadi *over-generation* atau krisis inersia sistem |
| **Konsekuensi Biaya** | Biaya peluang hilangnya energi (Opportunity Cost) | **Curtailment Cost** (Penalti pembuangan energi hijau) |

---

## 🛠️ 4. Temuan Audit Kode Python Eksisting (`Coba_16_...ipynb`)

Pemeriksaan baris-per-baris pada file kode notebook membuktikan kebenaran pengamatan Anda:

### 1) Model PV Belum Pernah Dibuat di Pyomo
* Data `Potensi PV (MW)` tersedia di Excel sheet `Demand`.
* Pada Cell 12, parameter sempat dibaca ke dictionary `PV_Potential`, namun **tidak pernah didefinisikan sebagai Set, Param, maupun Var di model Pyomo**.
* Pada constraint `con_power_balance` (Cell 29), persamaannya hanya:
  ```python
  gen_supply + wt_supply + batt_discharge - batt_charge == Demand[t]
  ```
  **Sama sekali belum ada `pv_supply`!**

### 2) Komponen Biaya Curtailment Belum Masuk ke Fungsi Objektif
* Flag `"obj_curtailment_cost"` tertulis di `CONFIG`, namun pada fungsi `obj_rule` (Cell 28) flag ini **sama sekali tidak dibaca maupun dihitung**.
* Akibatnya, pemodelan WT yang ada sebelumnya tidak memperhitungkan penalti pembuangan energi angin.

### 3) Modifikasi yang Harus Kita Tambahkan untuk Simulasi 4:
1. Menambahkan parameter Pyomo `model.PV_Available[t] = PV_Potential[t]`.
2. Menambahkan variabel Pyomo `model.PV_Curt[t] >= 0`.
3. Menambahkan constraint batasan curtailment PV:
   $$0 \le P_{\text{pv},t}^{\text{curt}} \le P_{\text{pv},t}^{\text{avail}}$$
4. Memperbarui `con_power_balance` menjadi:
   $$\sum_{g=1}^{10} P_{g,t} + \left(P_{\text{wt},t}^{\text{avail}} - P_{\text{wt},t}^{\text{curt}}\right) + \left(P_{\text{pv},t}^{\text{avail}} - P_{\text{pv},t}^{\text{curt}}\right) + P_{b,t}^{\text{dis}} - P_{b,t}^{\text{ch}} = D_t$$
5. Menambahkan **Curtailment Cost** ke fungsi objektif:
   $$\text{Total Cost} = \text{Fuel} + \text{Fixed} + \text{Startup} + \text{Shutdown} + \sum_{t=1}^{24} \left( C_{\text{curt}}^{\text{WT}} \cdot P_{\text{wt},t}^{\text{curt}} + C_{\text{curt}}^{\text{PV}} \cdot P_{\text{pv},t}^{\text{curt}} \right)$$

---

## 🔬 5. Verifikasi Matematis Pemodelan BESS & BESS Virtual Inertia

Pemodelan BESS pada Cell 52 dan Cell 22 telah diverifikasi dan **sudah tepat secara fisis**:

1. **Batasan Daya Discharging & VI Headroom (Cell 52):**
   ```python
   if CONFIG["con_battery_vi"]:
       return (
           m.P_discharge[b, t] + m.P_VI_batt[b, t] / m.Eff_VI[b]
           <= m.DR_max[b] * m.DischargeStatus[b, t]
       )
   return m.P_discharge[b, t] <= m.DR_max[b] * m.DischargeStatus[b, t]
   ```
   * *Status:* **Sangat Tepat**. Mengikuti formulasi alokasi converter dari referensi IEEE (Xu et al., 2018 / Fang et al., 2021).
2. **Kondisi BESS VI Non-Aktif (Simulasi 2):**
   ```python
   if not CONFIG["con_battery_vi"]:
       def battery_vi_off_rule(m, b, t):
           return m.P_VI_batt[b, t] == 0
       model.BatteryVIOff = Constraint(model.BATT, model.T, rule=battery_vi_off_rule)
   ```
   * *Status:* **Tepat**. Memaksa $P^{\text{VI}} = 0$ sehingga BESS murni berfungsi arbitrase tanpa menyuntikkan inersia.
3. **Kontribusi ke Inersia Total Sistem (Cell 22):**
   ```python
   h_batt_vi = sum(
       m.Kb_VI[b] * m.P_VI_batt[b, t] for b in m.BATT
   ) if CONFIG["con_battery"] and CONFIG["con_battery_vi"] else 0
   return h_thermal + h_batt_vi
   ```
   * *Status:* **Tepat**. Linear dan kompatibel penuh dengan solver CPLEX MILP.
4. **Dinamika State of Charge (SOC):**
   Perhitungan pertambahan/pengurangan SOC berbasis efisiensi charging ($\eta_{\text{ch}}$) dan discharging ($\eta_{\text{dis}}$) serta batasan $\text{SOC}_{\min} \le \text{SOC}_t \le \text{SOC}_{\max}$ dan kondisi akhir $\text{SOC}_{24} = \text{SOC}_{\text{init}}$ sudah terdefinisi secara baku.

---

## 📊 6. Rencana Komparasi Kritis: "DENGAN PV+WT vs TANPA PV+WT"

Komparasi performa sistem akan membandingkan:
* **Kasus TANPA PV & WT (Simulasi 3):**
  * Beban hanya dilayani Thermal + BESS VI.
  * Inersia sistem stabil, komitmen unit terprediksi, biaya curtailment = \$0.
* **Kasus DENGAN PV & WT (Simulasi 4):**
  * Beban dilayani Thermal + BESS VI + PV + WT.
  * Biaya bahan bakar termal turun karena penetrasi energi murah EBT, **tetapi inersia termal terancam anjlok**.
  * BESS VI diuji secara maksimal untuk menahan RoCoF sistem.
  * Jika kapasitas BESS VI dan fleksibilitas termal jenuh, sebagian daya PV/WT terpaksa di-*curtail* dengan konsekuensi munculnya **Curtailment Cost**.

---

## 📑 7. Roadmap Selanjutnya

1. **Pembuatan Skrip Eksekutor Terpadu:**
   Menulis modul Python (`run_4_scenarios.py`) yang mengimplementasikan model PV, WT curtailment, dan fungsi objektif curtailment cost secara modular dan mengeksekusinya via IBM CPLEX 22.1.1.
2. **Penyusunan Manuskrip Paper Baru (`Paper/main_v3.tex`):**
   Setelah seluruh data numerik dan grafik respon transien diperoleh, dokumen LaTeX baru `Paper/main_v3.tex` akan dibuat secara komprehensif tanpa mengganggu `main_v2.tex`.
