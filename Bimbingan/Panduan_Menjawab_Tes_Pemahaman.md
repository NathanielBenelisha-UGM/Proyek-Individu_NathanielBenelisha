# 📘 Penjelasan Komprehensif & Penguasaan Materi Proyek Individual
## Frequency-Constrained Unit Commitment (FCUC) dengan Battery Virtual Inertia dan Regulasi Frekuensi pada Penetrasi EBT Tinggi

Dokumen ini memuat penjelasan konseptual, matematis, dan keteknikan secara mandiri dan utuh mengenai seluruh aspek riset Proyek Individual. Narasi ini disusun secara langsung dalam format penjelasan akademik (*expository presentation*) untuk memandu penyampaian materi di hadapan Dosen Pembimbing (**Ir. Lesnanto Multa Putranto, Ph.D.**) dan Co-Mentor (**Muhammad Aris Risnandar, M.T.**).

---

## 🎙️ 1. Ikhtisar Eksekutif Riset (Urgensi, Masalah, & Solusi)

Penelitian yang saya laksanakan berfokus pada **Frequency-Constrained Unit Commitment (FCUC) dengan Battery Virtual Inertia dan Regulasi Frekuensi pada Penetrasi EBT Tinggi**, dengan studi kasus sistem tenaga listrik ekuivalen IEEE 24-bus yang dilayani oleh 10 unit generator termal.

### Latar Belakang & Urgensi Permasalahan:
Sistem tenaga listrik modern sedang mengalami transformasi besar menuju dekarbonisasi melalui penetrasi masif pembangkit energi terbarukan (EBT) seperti Pembangkit Listrik Tenaga Surya (PLTS) dan Pembangkit Listrik Tenaga Bayu (PLTB). Namun, secara teknis, pembangkit EBT ini terhubung ke kisi listrik melalui konverter elektronika daya (*Inverter-Based Resources / IBR*). Konverter IBR beroperasi secara terpisah (*decoupled*) dari frekuensi kisi, sehingga tidak memiliki massa berputar yang menyumbang energi kinetik sinkron ke sistem.

Ketika daya dari EBT masuk menggantikan pembangkit termal sinkron, inersia total sistem merosot secara drastis (*low-inertia grid*). Pada kondisi ini, jika terjadi gangguan kontingensi hilangnya pembangkit terbesar ($N-1$ *trip*), sistem akan mengalami dua ancaman kestabilan frekuensi yang sangat berbahaya:
1. **Laju perubahan frekuensi awal yang sangat curam (*high Rate of Change of Frequency / RoCoF*):** Terjadi tepat setelah gangguan ($t = 0^+$ detik) akibat ketiadaan inersia penahan.
2. **Penurunan titik terendah frekuensi yang ekstrem (*deep frequency nadir*):** Frekuensi anjlok menembus ambang batas skema pelepasan beban darurat (*Under-Frequency Load Shedding / UFLS* 49.0 Hz), yang dapat memicu pemadaman meluas (*cascading blackout*).

Model penjadwalan Unit Commitment (UC) konvensional tidak mampu mengatasi hal ini karena hanya meminimalkan biaya bahan bakar tanpa batasan dinamika frekuensi, sehingga solver cenderung mematikan generator termal demi efisiensi biaya.

### Solusi & Kontribusi yang Saya Bangun:
Untuk menjembatani dilema antara efisiensi ekonomi dan kestabilan frekuensi, saya merancang formulasi **Frequency-Constrained Unit Commitment (FCUC) berbasis Mixed-Integer Linear Programming (MILP)** yang diselesaikan secara eksak menggunakan solver IBM ILOG CPLEX 22.1.1. Model ini mengoordinasikan penjadwalan komitmen generator termal bersama sistem penyimpan energi baterai (*Battery Energy Storage System / BESS*) yang difungsikan menyediakan inersia sintetis (*Virtual Inertia / VI*).

Empat pilar utama yang menjadi fokus dan kebaruan dalam riset ini adalah:
1. **Pemodelan Kopling Konverter BESS (*Headroom Coupling*):** Memodelkan batasan fisik inverter baterai secara nyata, di mana daya discharging harian dan cadangan inersia virtual harus saling berbagi kapasitas rating konverter.
2. **Penegasan EBT sebagai 'Pengotor' (Zero Virtual Inertia):** PLTS dan PLTB dimaksimalkan untuk memanen energi murah pada titik kerja MPPT tanpa operasi *deloading*. Pemotongan daya EBT murni berstatus *curtailment* dengan memperhitungkan biaya penalti (*Curtailment Cost*).
3. **Keamanan Frekuensi Dua Dimensi:** Memadukan pertahanan domain inersia (RoCoF limit via inersia termal dan BESS VI) dan domain regulasi primer (QSS limit via cadangan *droop governor* unit termal).
4. **Validasi Transien Dinamis Dua Tahap:** Hasil optimasi diskrit divalidasi ke dalam simulasi dinamik domain-waktu kontinu (*RMS simulation*) pada software **DIgSILENT PowerFactory**.

---

## 📐 2. Penjelasan Matematis Model Formulasi FCUC

Berikut adalah pembedahan matematis baris-per-baris dari model optimasi yang saya formulasikan, beserta arti fisis dari setiap suku persamaan:

### 2.1 Fungsi Objektif: Minimasi Biaya Operasi Sistem
Tujuan optimasi adalah meminimalkan total biaya operasional sistem tenaga listrik selama horizon perencanaan 24 jam:

$$\min \sum_{t=1}^{24} \left[ \sum_{g=1}^{10} \Big( a_g u_{g,t} + b_g P_{g,t} \Big) + \sum_{g=1}^{10} SU_g y_{g,t} + \sum_{g=1}^{10} SD_g z_{g,t} + \sum_{w \in \text{WT}} C_{\text{curt}}^{\text{WT}} P_{w,t}^{\text{curt}} + \sum_{v \in \text{PV}} C_{\text{curt}}^{\text{PV}} P_{v,t}^{\text{curt}} \right]$$

**Penjelasan Suku-Suku Rumus:**
* **$u_{g,t} \in \{0, 1\}$:** Variabel biner komitmen generator termal $g$ pada jam $t$. Bernilai $1$ jika generator menyala (*committed/online*), dan $0$ jika padam (*offline*).
* **$a_g u_{g,t}$ (*No-Load Cost*):** Biaya bahan bakar tetap yang harus dikeluarkan per jam agar mesin termal tetap berputar sinkron pada frekuensi kerja, terlepas dari apakah mesin tersebut memikul beban besar atau kecil.
* **$b_g P_{g,t}$ (*Marginal Fuel Cost*):** Biaya bahan bakar variabel yang sebanding lurus dengan daya listrik aktif ($P_{g,t}$) yang dibangkitkan oleh generator (dalam USD/MWh).
* **$SU_g y_{g,t}$ (*Startup Cost*):** Biaya yang timbul akibat konsumsi bahan bakar pemanasan dan stres termal saat generator beralih dari status padam menjadi menyala ($y_{g,t} = 1$).
* **$SD_g z_{g,t}$ (*Shutdown Cost*):** Biaya transisi saat unit dimatikan ($z_{g,t} = 1$).
* **$C_{\text{curt}}^{\text{WT}} P_{w,t}^{\text{curt}}$ dan $C_{\text{curt}}^{\text{PV}} P_{v,t}^{\text{curt}}$ (*Curtailment Cost*):** Biaya penalti ekonomi yang dikenakan pada sistem apabila potensi daya hijau dari turbin angin atau sel surya terpaksa dibuang karena ketidakmampuan kisi menyerapnya.

---

### 2.2 Neraca Daya Multi-Pembangkit Terpadu (*Power Balance Constraint*)
Keseimbangan daya antara pasokan dan kebutuhan beban harus terpenuhi secara presisi pada setiap jam $t$:

$$\sum_{g=1}^{10} P_{g,t} + \left( P_{b,t}^{\text{dis}} - P_{b,t}^{\text{ch}} \right) + \left( P_{w,t}^{\text{avail}} - P_{w,t}^{\text{curt}} \right) + \left( P_{v,t}^{\text{avail}} - P_{v,t}^{\text{curt}} \right) = D_t, \quad \forall t$$

**Penjelasan Fisis:**
* $\sum P_{g,t}$: Total pasokan daya aktif dari seluruh generator termal yang beroperasi.
* $(P_{b,t}^{\text{dis}} - P_{b,t}^{\text{ch}})$: Injeksi daya netto dari sistem baterai (BESS). Bernilai positif saat baterai melepas daya (*discharging*) untuk membantu beban puncak, dan bernilai negatif saat baterai menyerap daya (*charging*) saat beban rendah.
* $(P_{w,t}^{\text{avail}} - P_{w,t}^{\text{curt}})$: Daya listrik aktual yang disalurkan oleh pembangkit listrik tenaga bayu (PLTB) ke kisi, di mana potensi daya tersedia ($P^{\text{avail}}$) dikurangi daya yang dibuang ($P^{\text{curt}}$).
* $(P_{v,t}^{\text{avail}} - P_{v,t}^{\text{curt}})$: Daya listrik aktual yang disalurkan oleh pembangkit listrik tenaga surya (PLTS).
* $D_t$: Kebutuhan beban sistem keseluruhan pada jam $t$.

---

### 2.3 Pemodelan Inersia Sistem Terpadu & Batasan Linear RoCoF
Inersia total sistem ($H_{\text{sys},t}$) merepresentasikan besarnya cadangan energi kinetik yang tersedia untuk menahan laju anjloknya frekuensi:

$$H_{\text{sys},t} = \sum_{g=1}^{10} H_g P_g^{\max} u_{g,t} + \sum_{b \in \text{BATT}} K_b^{\text{VI}} P_{b,t}^{\text{VI}}$$

$$2 \cdot \text{RoCoF}_{\lim} \cdot H_{\text{sys},t} \ge f_0 \cdot \text{LargestLoss}_t, \quad \forall t$$

**Penjelasan Fisis & Matematis:**
* **$H_g$:** Konstanta inersia mekanik generator termal sinkron (detik).
* **$K_b^{\text{VI}}$:** Koefisien emulasi inersia virtual dari BESS (MWs/MW), yang mengonversikan kapasitas daya respon cepat baterai menjadi padanan inersia rotasi.
* **$H_{\text{BESS},t} = \sum K_b^{\text{VI}} P_{b,t}^{\text{VI}}$:** Kontribusi inersia sintetis dari seluruh konverter baterai.
* **$\text{LargestLoss}_t$:** Besarnya daya dari unit pembangkit terbesar yang sedang menyala pada jam $t$ ($\max_g P_{g,t}$), yang menjadi acuan kontingensi terburuk $N-1$.
* **Linearisasi Persamaan RoCoF:** Persamaan fisik RoCoF yang asli berbentuk non-linear pecahan:
  $$\text{RoCoF} = \frac{f_0 \cdot \text{LargestLoss}_t}{2 H_{\text{sys},t}} \le \text{RoCoF}_{\lim}$$
  Persamaan ini saya linearisasi secara eksak dengan mengalikan silang penyebut $H_{\text{sys},t}$. Karena $f_0$ (50.0 Hz) dan $\text{RoCoF}_{\lim}$ (0.55 Hz/s) merupakan konstanta konstan, persamaan bertransformasi menjadi pertidaksamaan linear murni sehingga solver CPLEX dapat menemukan solusi *global optimal* dengan cepat.

---

### 2.4 Kopling Alokasi Konverter BESS (*Converter Headroom Coupling*)
Persamaan ini memodelkan interaksi fisik pada perangkat inverter konverter baterai:

$$P_{b,t}^{\text{dis}} + \frac{P_{b,t}^{\text{VI}}}{\eta_b^{\text{VI}}} \le DR_b^{\max} \cdot u_{b,t}^{\text{dis}}, \quad \forall b, t$$

**Penjelasan Parameter dan Konsep Headroom:**
* **Makna Parameter $DR_b^{\max}$:** 
  $DR$ merupakan singkatan dari *Discharge Rate*. Parameter $DR_b^{\max}$ adalah **Kapasitas Rating Daya Maksimum Inverter Konverter (*Maximum Converter Power Rating*)** dari BESS dalam satuan Megawatt (MW). Ini adalah batas kemampuan fisik arus semikonduktor daya (*Power Conversion System / PCS*) baterai.
* **Konsep *Headroom* (Ruang Cadangan):**
  Inverter baterai memiliki kapasitas terbatas sebesar $DR_b^{\max}$. Jika baterai menggunakan sebagian kapasitasnya untuk menyalurkan daya aktif terjadwal $P_{b,t}^{\text{dis}}$ guna melayani beban harian, maka sisa kapasitas inverter yang dapat disisakan (*headroom*) untuk merespons frekuensi secara virtual ($P_{b,t}^{\text{VI}}$) menjadi terbatas:
  $$\frac{P_{b,t}^{\text{VI}}}{\eta_b^{\text{VI}}} \le DR_b^{\max} - P_{b,t}^{\text{dis}}$$
* **Alasan Mengapa Persamaan Ini Krusial:**
  Tanpa persamaan kopling ini, model optimasi akan melakukan kesalahan fatal berupa klaim ganda (*double booking*): baterai dijadwalkan discharging 100% untuk mencari keuntungan ekonomi energi, sekaligus menjanjikan respon inersia virtual 100%. Saat gangguan sistem terjadi, inverter baterai akan dipaksa mengalirkan daya sebesar 200% dari kapasitas fisiknya, yang di dunia nyata akan menyebabkan inverter trip seketika karena kelebihan arus (*overcurrent*), memicu pemadaman sistem secara luas.
* **Peran Status Biner $u_{b,t}^{\text{dis}}$:**
  Baterai memiliki batasan interlock fisik: tidak boleh charge dan discharge pada jam yang sama ($u^{\text{ch}} + u^{\text{dis}} \le 1$). Ketika baterai sedang dalam proses pengisian energi ($u^{\text{ch}} = 1$), otomatis $u^{\text{dis}} = 0$. Hal ini memaksa $P_{b,t}^{\text{VI}} = 0$, karena inverter sedang menarik daya masuk ke baterai dan secara fisik tidak dapat menginjeksikan inersia ke kisi.
* **Peran Efisiensi $\eta_b^{\text{VI}}$:**
  Memperhitungkan rugi-rugi daya penyaklaran (*switching losses*) semikonduktor konverter saat merespons dinamika frekuensi tinggi dalam orde milidetik.

---

### 2.5 Dinamika State of Charge (SOC) BESS
Dinamika energi elektrokimia yang tersimpan di dalam baterai dimodelkan sebagai berikut:

$$SoC_{b,t} = SoC_{b,t-1} + \left( \eta_b^{\text{ch}} P_{b,t}^{\text{ch}} - \frac{P_{b,t}^{\text{dis}}}{\eta_b^{\text{dis}}} \right) \cdot \Delta t, \quad \forall b, t$$

$$SoC_b^{\min} \le SoC_{b,t} \le SoC_b^{\max}$$

$$SoC_{b,24} = SoC_{b,0}$$

**Penjelasan Fisis:**
* Efisiensi pengisian ($\eta_b^{\text{ch}}$) dan pengosongan ($\eta_b^{\text{dis}}$) membatasi konversi energi baterai.
* Batas $SoC^{\min}$ dan $SoC^{\max}$ menjaga baterai agar tidak mengalami pengosongan berlebih (*over-discharge*) atau pengisian berlebih (*over-charge*), yang dapat merusak usia pakai sel baterai.
* Batasan periodik harian $SoC_{24} = SoC_0$ memastikan bahwa kondisi simpanan energi baterai pada akhir hari sama dengan kondisi awal hari, menjaga keberlanjutan siklus untuk operasi hari berikutnya.

---

### 2.6 Batasan Regulasi Frekuensi Primer (PFR) & Frekuensi Kuasi-Tunak (QSS)
Setelah inersia sistem menahan laju penurunan frekuensi pada detik pertama, sistem mengandalkan cadangan regulasi frekuensi primer (*Primary Frequency Response / PFR*) dari *droop governor* unit termal untuk menahan frekuensi kuasi-tunak ($t = 10\text{--}30$ detik) di atas batas aman:

$$\text{LargestLoss}_t \le (f_0 - f_{\text{qss}}^{\min}) \cdot \left( D_{\text{frac}} \cdot \text{Demand}_t + \sum_{g=1}^{10} R_{g,t}^{\text{pfr}} \right), \quad \forall t$$

**Penjelasan Fisis:**
* $f_{\text{qss}}^{\min} = 49.5\text{ Hz}$: Batas frekuensi terendah yang diizinkan pada kondisi kuasi-tunak sebelum frekuensi dipulihkan penuh oleh kontrol sekunder (AGC).
* $D_{\text{frac}} \cdot \text{Demand}_t$: Karakteristik peredaman beban alamiah (*load damping effect*, $1\%/\text{Hz}$), di mana konsumsi motor listrik beban otomatis turun saat frekuensi sistem turun.
* $R_{g,t}^{\text{pfr}}$: Cadangan daya aktif respon primer yang disediakan oleh unit termal. Cadangan ini dibatasi secara ketat oleh ketersediaan *headroom* kapasitas generator ($P_{g,t} + R_{g,t}^{\text{pfr}} \le P_g^{\max} u_{g,t}$), kemampuan laju kenaikan daya (*ramp rate* dalam 10 detik), dan hanya dapat disuplai oleh unit yang memiliki *free governor* (`FreeGovernor = 1`).

---

## 🔬 3. Landasan Teoretis & Justifikasi Keputusan Rekayasa Pemodelan

Bagian ini memaparkan argumentasi ilmiah di balik keputusan pemodelan yang saya terapkan:

### 3.1 Mengapa PV dan WT Ditegaskan sebagai 'Pengotor' (Bukan Virtual Inertia)?
Dalam riset ini, saya secara tegas memosisikan PLTB dan PLTS murni sebagai pemasok energi intermiten non-inersia (*pengotor*), dan tidak difungsikan sebagai penyedia Virtual Inertia. Alasan teknisnya adalah:
1. **Karakteristik Operasional Lapangan:** Mayoritas pembangkit turbin angin dan fotovoltaik terpasang saat ini menggunakan konverter tipe *grid-following* yang diprogram untuk mengekstraksi daya maksimum (MPPT) demi keekonomian investasi energi hijau.
2. **Konsekuensi Operasi Deloading:** Jika PV atau WT dipaksa menyediakan Virtual Inertia, keduanya harus dioperasikan secara **deloading** (beroperasi sengaja 10–20% di bawah titik daya optimal MPPT) agar memiliki sisa cadangan daya untuk respon frekuensi. Menahan operasi EBT di bawah kapasitas optimalnya berarti membuang potensi energi terbarukan secara kontinu setiap detik sepanjang hari (*opportunity cost* yang sangat mahal).
3. **Pemisahan Peran yang Optimal:** Oleh karena itu, tugas penyediaan inersia virtual difokuskan secara khusus pada BESS yang memang merupakan aset penyimpan energi fleksibel (*grid-forming*), sedangkan PV dan WT dimaksimalkan untuk memasok daya murah. Namun, karena penetrasi daya EBT mendesak generator termal padam dan mengikis inersia kisi, keberadaannya bersikap sebagai 'pengotor' terhadap ketahanan frekuensi sistem.

---

### 3.2 Pembedaan Fisis: Operasi Deloading vs Curtailment pada EBT
Terdapat perbedaan mendasar antara kedua konsep pemotongan daya ini:
* **Deloading (Operasi Terencana Penyedia Inersia):** Adalah strategi operasional terencana di mana titik kerja turbin angin atau sel surya secara sengaja ditahan menyimpang di bawah kurva MPPT sepanjang waktu untuk menyimpan cadangan energi kinetik rotor atau cadangan kapasitas inverter.
* **Curtailment (Pembuangan Daya Darurat Akibat Keterbatasan Sistem):** Adalah pemotongan daya yang terjadi sewaktu-waktu hanya ketika pasokan daya EBT melebihi kebutuhan atau saat sistem mengalami keterbatasan fleksibilitas/inersia di mana generator termal sudah menyentuh batas generasi minimum ($P_{\min}$) dan tidak dapat diturunkan lagi. Karena pada model ini EBT murni sebagai pengotor, pemotongan daya yang terjadi adalah **curtailment**, yang dihitung kerugian ekonominya melalui **Curtailment Cost**.

---

### 3.3 Mengapa Daya Inersia Virtual ($P^{\text{VI}}$) Tidak Menguras SOC Baterai pada Jadwal Harian?
Dalam persamaan dinamika baterai yang saya bangun, variabel $P_{b,t}^{\text{VI}}$ tidak mengurangi simpanan energi elektrokimia ($SoC$) harian. Alasan ilmiahnya adalah:
* Variabel $P_{b,t}^{\text{VI}}$ dalam model optimasi Unit Commitment merepresentasikan **alokasi kapasitas daya cadangan (*headroom capability*)**, yang memiliki sifat serupa dengan cadangan putar (*spinning reserve*).
* Pada kondisi operasi normal harian (*steady-state*), baterai tidak mengalirkan daya inersia virtual tersebut ke kisi. Daya inersia virtual baru benar-benar diinjeksikan selama rentang waktu beberapa detik (transien) apabila terjadi peristiwa gangguan darurat ($N-1$ kontingensi). Oleh karena itu, energi simpanan baterai tidak terkuras dalam jadwal operasi tunak normal.

---

### 3.4 Validitas Pendekatan Sistem Ekuivalen Tembaga (*Copper-Plate 1-Bus*)
Penyederhanaan sistem uji IEEE 24-bus menjadi model tembaga 1-bus didasarkan pada landasan bahwa:
* Respon frekuensi sistem pasca-gangguan (baik RoCoF pada detik pertama maupun nilai nadir) merupakan **fenomena kesetimbangan daya aktif global sistem**, di mana seluruh rotor mesin yang saling terinterkoneksi berayun serempak di sekitar *Center of Inertia* (COI).
* Penyederhanaan ini merupakan standar metodologis yang diakui secara luas dalam literatur FCUC tingkat internasional (misalnya penelitian Restrepo & Galiana, Wen et al., dan Chu et al.). Untuk menjamin bahwa penyederhanaan ini tidak melanggar batasan termal transmisi atau batas stabilitas tegangan/sudut lokal, jadwal komitmen ini divalidasi ke dalam pemodelan jaringan penuh di software domain-waktu **DIgSILENT PowerFactory** pada Tahap 4.

---

### 3.5 Integrasi Dua Dimensi Keamanan Frekuensi: Inersia (RoCoF) dan Regulasi Primer (QSS)
Kestabilan frekuensi yang tangguh menuntut kehadiran dua lapisan pertahanan frekuensi yang bekerja pada domain waktu berbeda secara harmonis:
1. **Lapisan Pertama — Domain Inersia / RoCoF Limit ($t = 0^+$ detik):**
   Bekerja menahan kecuraman laju penurunan frekuensi seketika saat gangguan terjadi melalui sumbangan inersia mekanik generator termal dan respon inersia sintetis BESS VI agar relay proteksi RoCoF tidak trip ($\le 0.55\text{ Hz/s}$).
2. **Lapisan Kedua — Domain Regulasi Primer / QSS Limit ($t = 10\text{--}30$ detik):**
   Setelah laju penurunan awal tertahan, aksi *droop speed governor* generator termal segera menyuntikkan cadangan daya aktif primer (PFR) untuk menstabilkan frekuensi pada titik ekuilibrium baru kuasi-tunak agar tidak jatuh menembus ambang pelepasan beban ($f_{\text{qss}} \ge 49.5\text{ Hz}$).

---

## 📊 4. Alur Pembuktian Ilmiah 4 Skenario Simulasi Baru

Penyusunan 4 skenario simulasi secara inkremental dirancang untuk membuktikan hipotesis riset secara bertahap dan meyakinkan:

```
[Simulasi 1: UC Konvensional + Min Inertia + QSS]
       │ (Baseline: 100% Inersia Termal SG, Beban Inersia Tinggi, Biaya Mahal)
       ▼
[Simulasi 2: Simulasi 1 + BESS Standar (P_VI = 0)]
       │ (BESS Arbitrase Saja, Inersia Tetap 100% Termal, Mesin Mahal Tetap Wajib Menyala)
       ▼
[Simulasi 3: Simulasi 2 + BESS Virtual Inertia (P_VI > 0)]
       │ (BESS VI Menggantikan Inersia Termal, Mesin Mahal Berhasil Di-decommit, Biaya Turun)
       ▼
[Simulasi 4: Simulasi 3 + Variabel PV + WT (Sebagai Pengotor)]
         (EBT Masuk Merusak Inersia, Uji Ketahanan BESS VI, Hitung Nilai Curtailment Cost)
```

### Rincian Perilaku Tiap Skenario:
1. **Simulasi 1 (Baseline Sistem Konvensional):**
   Menunjukkan kondisi dasar di mana pemenuhan inersia minimum dan batasan QSS sepenuhnya dibebankan pada generator termal sinkron. Hasilnya, generator termal besar berbiaya bahan bakar tinggi terpaksa tetap dinyalakan (*must-run units*) semata-mata demi menjaga inersia sistem, yang menyebabkan biaya operasi membengkak.
2. **Simulasi 2 (Penambahan BESS Standar Tanpa VI):**
   Menunjukkan bahwa BESS yang hanya difungsikan untuk arbitrase energi (*peak shaving*) memang mampu sedikit memotong biaya beban puncak, namun **gagal mengurangi jumlah komitmen generator termal**. Mesin termal mahal tetap harus menyala karena inersia sistem masih mengalami defisit.
3. **Simulasi 3 (Aktivasi BESS Virtual Inertia — *Kemenangan Model*):**
   Membuktikan bahwa dengan mengaktifkan fitur Virtual Inertia pada konverter BESS, inersia sintetis baterai berhasil mensubstitusi inersia mekanik generator termal. Mesin-mesin termal mahal yang boros bahan bakar **berhasil dimatikan (*de-commitment*)**, menghasilkan penghematan biaya operasional yang sangat signifikan dengan batas RoCoF dan QSS yang tetap patuh.
4. **Simulasi 4 (Integrasi PV dan WT sebagai Pengotor Nyata):**
   Menguji ketahanan sistem pada kondisi nyata penetrasi energi terbarukan tinggi. Masuknya daya PV dan WT mendesak generasi termal turun, memicu anjloknya inersia sistem. Simulasi ini menguji seberapa besar alokasi daya $P_{\text{VI}}$ BESS yang dikerahkan untuk menyelamatkan kestabilan kisi, serta mengukur berapa MWh daya EBT yang terpaksa dibuang beserta besaran **Curtailment Cost** yang timbul.

---

## 🛠️ 5. Rencana Kerja Terstruktur (5 Tahapan Menuju Naskah Final)

Pekerjaan lanjutan akan dilaksanakan melalui 5 tahapan kerja yang terisolasi dan terukur:
* **Tahap 1:** Membangun skrip eksekusi Pyomo `run_4_simulations.py` (menyempurnakan model PV, WT curtailment, dan batasan QSS/PFR) serta mengeksekusi solver CPLEX 22.1.1.
* **Tahap 2:** Mengekstrak hasil numerik biaya operasional, profil inersia, worst RoCoF, volume curtailment, dan menyusun analisis komparatif *"Dengan PV-WT vs Tanpa PV-WT"*.
* **Tahap 3:** Menghasilkan 4 set grafik visualisasi standar publikasi IEEE (300 DPI) di folder `Paper/figures/`.
* **Tahap 4:** Memvalidasi jadwal komitmen dan dispatch hasil optimasi ke simulasi transien domain-waktu di **DIgSILENT PowerFactory** untuk kontingensi $N-1$ trip unit terbesar.
* **Tahap 5:** Menyusun naskah paper lengkap baru `Paper/main_v3.tex` dan mengompilasinya menjadi dokumen publikasi PDF draf akhir.
