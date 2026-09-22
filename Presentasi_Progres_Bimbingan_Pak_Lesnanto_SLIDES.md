# 📊 SLIDE DECK: Laporan Progres Riset Proyek Individual
## Frequency-Constrained Unit Commitment (FCUC) dengan Battery Virtual Inertia dan Regulasi Frekuensi pada Penetrasi EBT Tinggi

---

### 📌 Slide 1: Judul Presentasi
* **Judul Penelitian:** Frequency-Constrained Unit Commitment (FCUC) dengan Battery Virtual Inertia dan Regulasi Frekuensi pada Penetrasi EBT Tinggi
* **Sub-judul:** Penyelarasan Formulasi Matematika, Pemodelan PV-WT Pengotor, & Rencana Eksekusi 4 Skenario Baru
* **Mahasiswa (Penulis 1):** Nathaniel Benelisha (Teknik Elektro, FT UGM)
* **Pendamping / Co-Mentor (S3):** Muhammad Aris Risnandar, S.T., M.T. (Kandidat Doktor DTETI UGM)
* **Dosen Pembimbing:** Ir. Lesnanto Multa Putranto, S.T., M.Eng., Ph.D., IPM., ASEAN Eng., SMIEEE
* **Institusi:** Departemen Teknik Elektro dan Teknologi Informasi, Fakultas Teknik, Universitas Gadjah Mada

---

### 📌 Slide 2: Agenda Pembahasan Progres
1. **Latar Belakang & Masalah:** Isu penurunan inersia kisi (*low-inertia grid*), risiko lonjakan RoCoF, dan keterbatasan UC klasik.
2. **Metode & Formulasi Matematis:** Pendekatan 2 tahap: Optimasi MILP (CPLEX) dan Validasi Transien Dinamis (DIgSILENT PowerFactory).
3. **Capaian Progres Sejauh Ini:** Review 84 paper, penyelarasan matematis cost linear & PFR, serta arsip draf paper Draf 1 s.d. 5.
4. **Desain 4 Skenario Simulasi Baru:** Restrukturisasi inkremental yang elegan: Sim 1 (Baseline), Sim 2 (+BESS), Sim 3 (+BESS VI), Sim 4 (+PV-WT Pengotor).
5. **Rencana Kerja ke Depan (5 Tahap):** Roadmap terstruktur: Eksekusi Pyomo, Analisis Komparatif, Plot Publikasi IEEE, DIgSILENT, & Paper v3.
6. **Permohonan Arahan Pembimbing:** Diskusi penalti curtailment cost, representativitas sistem uji IEEE 24-bus, dan target publikasi.

---

### 📌 Slide 3: Latar Belakang — Krisis Inersia pada Kisi Tenaga Modern
* **Penetrasi EBT Skala Besar:**
  - PLTS dan PLTB terhubung melalui konverter elektronika daya (*Inverter-Based Resources / IBR*).
  - IBR beroperasi secara *decoupled* sehingga **TIDAK menyumbang inersia mekanik alamiah ke grid**.
* **Ancaman Keamanan Frekuensi:**
  - Penurunan drastis inersia sistem memicu lonjakan **RoCoF curam** saat kontingensi $N-1$ trip unit terbesar.
  - Penurunan tajam titik terendah frekuensi (*frequency nadir*) melewati ambang batas UFLS (49.0 Hz).
* **Solusi yang Diajukan:**
  - Mengintegrasikan batasan keamanan frekuensi dinamik langsung ke optimasi jadwal komitmen unit (FCUC).
  - Pemanfaatan BESS *grid-forming* penyedia *Virtual Inertia* (VI) untuk menyubstitusi inersia termal secara ekonomis.

---

### 📌 Slide 4: Metode Penelitian — Kerangka Kerja Dua Tahap (Two-Stage Framework)
* **Tahap 1 — Optimasi FCUC (Python Pyomo + IBM CPLEX 22.1.1):**
  - Formulasi *Mixed-Integer Linear Programming* (MILP).
  - Mengoptimasi jadwal biner komitmen unit ($u_{g,t}, y, z$) dan variabel daya kontinu ($P, P_{\text{ch}}, P_{\text{dis}}, P_{\text{VI}}$).
  - Mengakomodasi 10 batasan teknis generator termal, dinamika SOC baterai, dan batasan inersia sistem.
* **Tahap 2 — Validasi Dinamik Transien (DIgSILENT PowerFactory):**
  - Jadwal dispatch hasil CPLEX diimpor ke DIgSILENT.
  - Pengujian simulasi dinamik domain-waktu (*RMS simulation*) untuk gangguan $N-1$ trip unit terbesar (G1 400 MW).
  - Verifikasi trayektori kurva respon frekuensi $f(t)$ dan nadir secara realistis.

---

### 📌 Slide 5: Konfigurasi Sistem Uji IEEE 24-Bus (10 Unit Generator)
* **Pembangkit Termal (10 Unit, Total 3.405 MW):**
  - G1: PLTU 1 (Coal) — 627.0 MW s.d. 1.176.0 MW, $H = 5.0\text{ s}$, Droop 5%
  - G2: PLTGU 1 (CCGT) — 340.0 MW s.d. 1.125.0 MW, $H = 4.0\text{ s}$, Droop 4%
  - G3: PLTU 2 (Coal) — 600.0 MW s.d. 969.0 MW, $H = 5.0\text{ s}$, Droop 5%
  - G4: PLTG 1 (Gas) — 85.0 MW s.d. 130.0 MW, $H = 3.5\text{ s}$, Droop 4%
  - G5: PLTG 2 (Gas) — 66.0 MW s.d. 108.0 MW, $H = 3.5\text{ s}$, Droop 4%
  - G6 s.d. G8: PLTGU 2–4 (CCGT) — Kapasitas 773–1.095 MW, $H = 4.0\text{ s}$, Droop 4%
  - G9 & G10: PLTU 3 & 4 (Coal) — Kapasitas 840–870 MW, $H = 5.0\text{ s}$, Droop 5%
* **Beban Sistem 24 Jam:** Rata-rata 1.168 MW, Beban Puncak 1.500 MW.
* **EBT Intermiten:** PLTB 400 MW (100 turbin @ 4 MW) dan PLTS dengan potensi puncak ~200 MW.
* **BESS:** 2 unit BESS (B1 & B2), total kapasitas 200 MW / 400 MWh.

---

### 📌 Slide 6: Formulasi Kunci — Alokasi Konverter BESS & Keamanan Frekuensi
1. **Kopling Alokasi Daya Konverter BESS (*Converter Headroom Coupling*):**
   $$P_{b,t}^{\text{dis}} + \frac{P_{b,t}^{\text{VI}}}{\eta_b^{\text{VI}}} \le DR_b^{\max} \cdot u_{b,t}^{\text{dis}}$$
   - Mencegah baterai mengklaim kapasitas inverter melebihi rating fisik ($DR_{\max}$).
   - BESS VI disuplai saat baterai tidak sedang diisi ($u_{b,t}^{\text{dis}} = 1$).
2. **Dua Pilar Batasan Frekuensi (RoCoF + QSS):**
   - **Pilar 1 (RoCoF Limit, $t = 0^+$ s):**
     $$2 \cdot \text{RoCoF}_{\lim} \cdot H_{\text{sys},t} \ge f_0 \cdot \text{LargestLoss}_t \quad (\text{RoCoF}_{\lim} = 0.55\text{ Hz/s})$$
   - **Pilar 2 (QSS Frequency Limit, $t = 10\text{--}30$ s):**
     $$\text{LargestLoss}_t \le (f_0 - f_{\text{qss}}^{\min}) \cdot \left( D_{\text{frac}} \cdot \text{Demand}_t + \text{TotalPFR}_t \right) \quad (f_{\text{qss}}^{\min} = 49.5\text{ Hz})$$

---

### 📌 Slide 7: Penegasan Konsep — EBT sebagai "Pengotor" vs Deloading
* **EBT sebagai Penyedia VI (Deloading):**
  - EBT harus beroperasi 10–20% di bawah kurva MPPT optimal.
  - Menyimpan cadangan kinetik untuk dilepas saat frekuensi anjlok.
  - Menimbulkan kehilangan energi hijau (*Opportunity Cost*) secara kontinu sepanjang hari.
* **EBT sebagai Pengotor (Riset Ini):**
  - PV & WT ditegaskan **MURNI sebagai pengotor (Zero Virtual Inertia)**.
  - Beroperasi pada MPPT optimal untuk memanen energi hijau semaksimal mungkin.
  - Masuknya daya EBT mendesak generator termal turun, memicu anjloknya inersia sistem.
  - Pemotongan daya EBT bersifat **CURTAILMENT** murni jika sistem mengalami kelebihan daya / terancam krisis inersia, disertai perhitungan **Curtailment Cost**:
    $$\text{Cost}_{\text{curt}} = \sum_{t=1}^{24} \left( C_{\text{curt}}^{\text{WT}} \cdot P_{\text{wt},t}^{\text{curt}} + C_{\text{curt}}^{\text{PV}} \cdot P_{\text{pv},t}^{\text{curt}} \right)$$

---

### 📌 Slide 8: Capaian Progres Sejauh Ini (Bersama Mas Aris)
* ✔ **Koleksi & Telaah Literatur:** Telah mengumpulkan dan menelaah 84 paper akademik internasional (IEEE, Elsevier), mencakup kajian fundamental BESS VI dan regulasi frekuensi primer Pak Lesnanto (ICITEE 2020).
* ✔ **Perumusan Kode Pyomo MILP:** Membangun model optimasi matematis FCUC di Python Pyomo terintegrasi solver CPLEX 22.1.1 (`cplex_direct`) yang mampu menyelesaikan jadwal 24 jam dalam waktu hitung cepat.
* ✔ **Penyelarasan Formulasi Matematis:** Memperbaiki fungsi biaya menjadi bentuk linear murni ($a_g u + b_g P$), menyelaraskan alokasi converter BESS VI headroom, dan mengisolasi VI secara tegas hanya pada BESS.
* ✔ **Penyusunan Manuskrip Publikasi:** Telah menyusun naskah paper IEEEtran secara berkala dari Draf 1 hingga Draf 5 (tersedia dalam kompilasi PDF mutakhir di direktori `Paper/PI_Draf5.pdf`).

---

### 📌 Slide 9: Desain 4 Skenario Simulasi Baru (Inti Diskusi Hari Ini)
| Parameter Pemodelan | Simulasi 1 (Baseline FCUC) | Simulasi 2 (+ BESS Standar) | Simulasi 3 (+ BESS VI) | Simulasi 4 (+ PV-WT Pengotor) |
|:---|:---:|:---:|:---:|:---:|
| **Generator Termal (G1–G10)** | Aktif (10 unit) | Aktif (10 unit) | Aktif (10 unit) | Aktif (10 unit) |
| **10 Batasan Dasar UC Konvensional** | Aktif | Aktif | Aktif | Aktif |
| **Batasan RoCoF (Inersia Min.)** | Aktif ($\le 0.55\text{ Hz/s}$) | Aktif ($\le 0.55\text{ Hz/s}$) | Aktif ($\le 0.55\text{ Hz/s}$) | Aktif ($\le 0.55\text{ Hz/s}$) |
| **Regulasi Frekuensi Primer (QSS)** | Aktif ($\ge 49.5\text{ Hz}$) | Aktif ($\ge 49.5\text{ Hz}$) | Aktif ($\ge 49.5\text{ Hz}$) | Aktif ($\ge 49.5\text{ Hz}$) |
| **Penyedia Inersia Sistem** | **100% Termal SG** | **100% Termal SG** | **Termal SG + BESS VI** | **Termal SG + BESS VI** |
| **Operasi BESS (B1 & B2)** | Non-Aktif | Arbitrase Saja ($P^{\text{VI}}=0$) | Arbitrase + VI Headroom | Arbitrase + VI Headroom |
| **PLTB & PLTS (Pengotor)** | Non-Aktif | Non-Aktif | Non-Aktif | Aktif (Zero Inersia) |
| **Curtailment Cost EBT** | \$0 | \$0 | \$0 | **Dihitung & Diminimasi** |

---

### 📌 Slide 10: Rencana Aksi ke Depan (5 Tahapan Terstruktur)
* 📍 **Tahap 1: Eksekusi Pyomo & CPLEX:** Menyusun skrip `run_4_simulations.py`, membangun model PV dan WT curtailment limit, serta menjalankan optimasi 4 simulasi dengan solver CPLEX 22.1.1.
* 📍 **Tahap 2: Ekstraksi & Analisis Komparatif:** Mengekstrak tabel komparasi detail biaya (Fuel, Startup, Curtailment Cost) dan menganalisis perbandingan "Dengan vs Tanpa PV-WT".
* 📍 **Tahap 3: Visualisasi Grafik Publikasi IEEE:** Menghasilkan 4 grafik standar IEEE 300 DPI di `Paper/figures/` (Stacked Dispatch, Inersia & RoCoF 24h, BESS VI Headroom, Curtailment Area).
* 📍 **Tahap 4: Validasi Transien DIgSILENT:** Mengimpor jadwal dispatch ke DIgSILENT PowerFactory untuk simulasi domain-waktu $N-1$ contingency trip unit terbesar dan mengekstrak kurva $f(t)$.
* 📍 **Tahap 5: Manuskrip Paper Baru (`main_v3.tex`):** Menyusun manuskrip lengkap baru `main_v3.tex` (mempertahankan v2) dengan formulasi baru, tabel hasil numerik, dan mengompilasi PDF terbaru.

---

### 📌 Slide 11: Poin Diskusi & Permohonan Arahan kepada Dosen Pembimbing
1. **Nilai Penalti Biaya Curtailment ($C_{\text{curt}}$):** Apakah penetapan nilai penalti pembuangan energi terbarukan sebesar \$30/MWh atau \$50/MWh dipandang cukup representatif dalam mencerminkan kerugian ekonomi di sistem tenaga modern?
2. **Representativitas Sistem Uji IEEE 24-Bus:** Apakah penyederhanaan sistem uji IEEE 24-bus menjadi model tembaga 10 generator sinkron sudah cukup kuat untuk luaran publikasi jurnal bereputasi (IEEE / MDPI), atau diperlukan variasi beban ekstrem?
3. **Skenario Uji Transien di DIgSILENT PowerFactory:** Untuk simulasi transien di DIgSILENT (Tahap 4), apakah cukup difokuskan pada kontingensi $N-1$ trip unit terbesar (G1 400 MW), ataukah perlu diuji pula saat jam penetrasi EBT puncak (jam 12.00–13.00)?
4. **Rekomendasi Target Publikasi Jurnal:** Dengan struktur pembuktian 4 skenario baru dan validasi transien DIgSILENT, mohon arahan Bapak mengenai target jurnal internasional bereputasi yang paling tepat untuk disasar.

---

### 📌 Slide 12: Penutup
* **Ucapan Terima Kasih:** Terima kasih atas bimbingan dan arahan Bapak Ir. Lesnanto Multa Putranto, Ph.D.
* **Departemen:** Departemen Teknik Elektro dan Teknologi Informasi, Fakultas Teknik, Universitas Gadjah Mada
