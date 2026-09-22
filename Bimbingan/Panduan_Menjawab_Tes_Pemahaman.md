# 🎓 Panduan Menjawab Tes Pemahaman & Pertanyaan Kritis Bimbingan
## Riset Proyek Individual: Frequency-Constrained Unit Commitment (FCUC) dengan Battery Virtual Inertia

Dokumen ini disusun sebagai panduan komprehensif, terstruktur, dan taktis bagi **Nathaniel Benelisha** saat diuji pemahamannya oleh Dosen Pembimbing (**Ir. Lesnanto Multa Putranto, Ph.D.**) maupun Co-Mentor (**Muhammad Aris Risnandar, M.T.**).

---

## 🎙️ Bagian 1: "Elevator Pitch" 2 Menit (Ringkasan Riset)
*Gunakan narasi ini jika diminta: "Coba ceritakan riset kamu ini tentang apa dan apa tujuannya?"*

> "Penelitian saya berfokus pada **Frequency-Constrained Unit Commitment (FCUC) dengan Battery Virtual Inertia dan Regulasi Frekuensi pada Penetrasi EBT Tinggi** menggunakan studi kasus sistem ekuivalen IEEE 24-bus 10 generator termal.
>
> **Latar Belakang Masalah:**
> Saat penetrasi energi terbarukan intermiten (PLTS dan PLTB) meningkat pesat menggantikan generator termal sinkron, sistem mengalami fenomena hilangnya inersia mekanik alamiah (**low-inertia grid**). Akibatnya, saat terjadi gangguan kontingensi $N-1$ trip unit terbesar, frekuensi anjlok sangat curam (**RoCoF tinggi**) dan berisiko menembus batas pelepasan beban darurat (**UFLS 49.0 Hz**). Unit Commitment klasik tidak mampu mengatasi hal ini karena hanya berfokus pada biaya bahan bakar tanpa memperhitungkan batasan dinamika frekuensi.
>
> **Solusi & Kebaruan Pemodelan:**
> Saya merancang model optimasi operasi harian **FCUC berbasis Mixed-Integer Linear Programming (MILP)** menggunakan solver IBM CPLEX 22.1.1 yang mengoordinasikan generator termal dan BESS dengan kebaruan:
> 1. **Alokasi Konverter BESS Terkopel (*Headroom Coupling*):** Memodelkan batas fisik inverter baterai secara realistis di mana daya discharging aktif dan cadangan inersia virtual harus saling berbagi kapasitas ($P_{\text{dis}} + P_{\text{VI}}/\eta \le DR_{\max}$).
> 2. **Penegasan EBT sebagai 'Pengotor' (Zero Virtual Inertia):** PLTS dan PLTB dimaksimalkan pada kurva MPPT dan tidak dioperasikan secara *deloading*. Pemotongan daya EBT murni bersifat *curtailment* dengan memperhitungkan **Curtailment Cost**.
> 3. **Dua Pilar Keamanan Frekuensi Terpadu:** Menjamin batasan **RoCoF** ($t = 0^+$ s) via inersia gabungan termal dan BESS VI, serta batasan kuasi-tunak **QSS** ($t = 10\text{--}30$ s) via respon *droop governor* unit termal.
> 4. **Validasi Transien Dinamis Dua Tahap:** Jadwal komitmen dan dispatch hasil optimasi divalidasi ke dalam simulasi dinamik domain-waktu (*RMS simulation*) pada **DIgSILENT PowerFactory**."

---

## 📐 Bagian 2: Penjelasan Model Matematika Baris-per-Baris
*Gunakan bagian ini jika dosen meminta Anda membuka formula dan menjelaskan arti fisis setiap simbol.*

### 1. Fungsi Objektif (Minimasi Total Biaya Operasi Sistem)
$$\min \sum_{t=1}^{24} \left[ \sum_{g=1}^{10} \underbrace{(a_g u_{g,t} + b_g P_{g,t})}_{\text{Biaya Operasional Bahan Bakar}} + \underbrace{SU_g y_{g,t}}_{\text{Biaya Startup}} + \underbrace{SD_g z_{g,t}}_{\text{Biaya Shutdown}} + \sum_{w} \underbrace{C_{\text{curt}}^{\text{WT}} P_{\text{wt},t}^{\text{curt}}}_{\text{Penalti Curtailment PLTB}} + \sum_{v} \underbrace{C_{\text{curt}}^{\text{PV}} P_{\text{pv},t}^{\text{curt}}}_{\text{Penalti Curtailment PLTS}} \right]$$

* **Arti Fisis Suku-Suku Rumus:**
  * $u_{g,t} \in \{0, 1\}$: Variabel keputusan biner status unit generator $g$ pada jam $t$ ($1 = \text{ON}, 0 = \text{OFF}$).
  * $a_g u_{g,t}$: *No-load cost* / biaya tetap bahan bakar per jam saat mesin menyala berputar sinkron meskipun belum memikul beban besar.
  * $b_g P_{g,t}$: Biaya bahan bakar marjinal linear per MW output daya aktif generator.
  * $SU_g y_{g,t}$: Biaya penyalaan awal (*startup cost*) yang timbul saat unit beralih dari OFF ke ON ($y_{g,t} = 1$).
  * $SD_g z_{g,t}$: Biaya pemadaman (*shutdown cost*) saat unit beralih dari ON ke OFF ($z_{g,t} = 1$).
  * $C_{\text{curt}}^{\text{WT}} P_{\text{wt},t}^{\text{curt}}$ & $C_{\text{curt}}^{\text{PV}} P_{\text{pv},t}^{\text{curt}}$: Biaya penalti ekonomi akibat pembuangan potensi energi hijau yang tidak dapat diserap oleh jaringan listrik.

---

### 2. Neraca Daya Terpadu (Power Balance Constraint)
$$\sum_{g=1}^{10} P_{g,t} + \underbrace{\left(P_{b,t}^{\text{dis}} - P_{b,t}^{\text{ch}}\right)}_{\text{Injeksi Neto BESS}} + \underbrace{\left(P_{\text{wt},t}^{\text{avail}} - P_{\text{wt},t}^{\text{curt}}\right)}_{\text{Daya PLTB Aktual ke Grid}} + \underbrace{\left(P_{\text{pv},t}^{\text{avail}} - P_{\text{pv},t}^{\text{curt}}\right)}_{\text{Daya PLTS Aktual ke Grid}} = D_t, \quad \forall t$$

* **Arti Fisis:**
  Total pembangkitan daya termal + injeksi bersih baterai (discharging dikurangi charging) + daya aktual EBT harus tepat seimbang memenuhi kebutuhan beban sistem $D_t$ pada setiap interval waktu 1 jam.

---

### 3. Inersia Sistem Terpadu & Batasan RoCoF (Linearized)
$$H_{\text{sys},t} = \sum_{g=1}^{10} H_g P_g^{\max} u_{g,t} + \sum_{b \in \text{BATT}} K_b^{\text{VI}} P_{b,t}^{\text{VI}}$$

$$2 \cdot \text{RoCoF}_{\lim} \cdot H_{\text{sys},t} \ge f_0 \cdot \text{LargestLoss}_t, \quad \forall t$$

* **Arti Fisis:**
  * $H_g$: Konstanta inersia mekanik generator termal sinkron (satuan detik).
  * $K_b^{\text{VI}}$: Koefisien emulasi inersia virtual BESS (MWs/MW).
  * $\text{RoCoF}_{\lim} = 0.55\text{ Hz/s}$: Batas laju penurunan frekuensi maksimum yang diizinkan sistem.
  * $f_0 = 50.0\text{ Hz}$: Frekuensi nominal sistem.
  * $\text{LargestLoss}_t = \max_{g} (P_{g,t})$: Kontingensi terburuk $N-1$ kehilangan pembangkit terbesar yang sedang aktif.
* **Trik Matematis Linearitas (Penting!):**
  Rumus asli RoCoF adalah non-linear: $\text{RoCoF} = \frac{f_0 \cdot \Delta P}{2 H_{\text{sys}}}$. Dengan mengalikan silang penyebut $H_{\text{sys}}$, persamaan berubah menjadi **pertidaksamaan linear murni (MILP)** tanpa aproksimasi pecahan, sehingga menjamin solusi *global optimal* pada CPLEX.

---

### 4. Kopling Alokasi Konverter BESS (*Converter Headroom Coupling*)
$$P_{b,t}^{\text{dis}} + \frac{P_{b,t}^{\text{VI}}}{\eta_b^{\text{VI}}} \le DR_b^{\max} \cdot u_{b,t}^{\text{dis}}, \quad \forall b, t$$

* **Apa itu $DR_b^{\max}$?**
  * **$DR$ = *Discharge Rate*** (Laju / Batas Daya Pengosongan Maksimum).
  * $DR_b^{\max}$ adalah **Kapasitas Rating Daya Inverter / Konverter Maksimum (*Maximum Converter Power Rating*)** dari unit BESS $b$, dinyatakan dalam satuan **Megawatt (MW)**. Ini adalah batasan fisik semu/arus tertinggi dari perangkat elektronika daya (*Power Conversion System / PCS*) baterai.
  * Pasangannya adalah $CR_b^{\max}$ (*Charge Rate Maximum*), yaitu batas daya pengisian: $P_{b,t}^{\text{ch}} \le CR_b^{\max} \cdot u_{b,t}^{\text{ch}}$.

* **Apa itu Konsep *Headroom* dan Mengapa Harus Dikopel?**
  * ***Headroom* (Ruang Cadangan):** Adalah sisa kapasitas inverter yang sengaja disisakan agar sewaktu-waktu siap menyuntikkan daya respon inersia virtual ($P_{b,t}^{\text{VI}}$) saat frekuensi anjlok mendadak.
  * **Analogi Fisis Nyata:** Jika konverter baterai memiliki kapasitas $DR_b^{\max} = 100\text{ MW}$, dan baterai sedang menjadwalkan discharging daya aktif untuk melayani beban sebesar $P_{b,t}^{\text{dis}} = 60\text{ MW}$, maka *headroom* sisa yang dapat dijanjikan untuk respon Virtual Inertia hanyalah sebesar:
    $$\frac{P_{b,t}^{\text{VI}}}{\eta_b^{\text{VI}}} \le 100\text{ MW} - 60\text{ MW} = 40\text{ MW}$$
  * **Bahaya jika Tidak Ada Persamaan Ini (*Klaim Ganda / Double Booking*):** Tanpa batasan ini, solver optimasi akan "berbuat curang" dengan menjadwalkan discharging penuh $100\text{ MW}$ untuk mencari keuntungan ekonomi, sekaligus menjanjikan inersia virtual $100\text{ MW}$. Saat gangguan $N-1$ terjadi, konverter baterai akan dipaksa mengalirkan total $200\text{ MW}$ (melebihi rating fisiknya), yang di dunia nyata akan menyebabkan inverter trip seketika karena *overcurrent/overload* dan memicu pemadaman sistem (*cascading blackout*).

* **Peran Parameter Lainnya:**
  * $\eta_b^{\text{VI}}$ (Efisiensi Konversi Inersia Virtual): Memperhitungkan rugi-rugi penyaklaran (*switching loss*) pada semikonduktor IGBT/SiC saat inverter merespons dinamika frekuensi cepat.
  * $u_{b,t}^{\text{dis}} \in \{0, 1\}$ (Status Biner Discharging): Karena baterai mematuhi batasan tidak boleh mengisi dan mengosongkan daya secara bersamaan ($u_{b,t}^{\text{ch}} + u_{b,t}^{\text{dis}} \le 1$), maka saat baterai sedang charging ($u_{b,t}^{\text{ch}} = 1$), otomatis $u_{b,t}^{\text{dis}} = 0$. Akibatnya, $P_{b,t}^{\text{VI}}$ dipaksa 0 karena inverter sedang menarik daya masuk ke baterai dan tidak dapat menginjeksi inersia ke kisi.

---

### 5. Batasan Frekuensi Kuasi-Tunak (QSS & PFR)
$$\text{LargestLoss}_t \le (f_0 - f_{\text{qss}}^{\min}) \cdot \left( D_{\text{frac}} \cdot \text{Demand}_t + \sum_{g=1}^{10} R_{g,t}^{\text{pfr}} \right), \quad \forall t$$

* **Arti Fisis:**
  * Menjamin bahwa setelah inersia menahan penurunan awal pada $t = 0^+$, cadangan regulasi frekuensi primer (*Primary Frequency Response / PFR*) dari *droop governor* unit termal sanggup menahan frekuensi kuasi-tunak ($t = 10\text{--}30$ s) di atas ambang $f_{\text{qss}}^{\min} = 49.5\text{ Hz}$.
  * $D_{\text{frac}} \cdot \text{Demand}_t$: Efek peredaman beban (*load damping effect*, $1\%/\text{Hz}$).
  * $R_{g,t}^{\text{pfr}}$: Cadangan daya PFR yang hanya dapat disuplai oleh unit termal yang memiliki *free governor* (`FreeGovernor = 1`), memiliki sisa *headroom* kapasitas, dan mematuhi batas *ramp rate* 10 detik.

---

## 🎯 Bagian 3: Cara Menjelaskan Alur 4 Skenario Simulasi Baru
*Gunakan bagian ini saat menjelaskan mengapa kita menyusun 4 skenario simulasi secara inkremental.*

| Skenario | Konfigurasi Pemodelan | Perilaku Fisis & Hasil yang Dibuktikan |
|:---|:---|:---|
| **Simulasi 1** | **UC Konvensional + Min Inersia + QSS** *(Termal saja)* | **Baseline Sistem Tenaga Klasik:** Seluruh inersia dipikul generator sinkron termal. Generator termal berbiaya mahal terpaksa tetap dinyalakan (*must-run*) hanya demi menjaga inersia sistem agar RoCoF tidak melanggar batas, menyebabkan biaya bahan bakar membengkak. |
| **Simulasi 2** | **Simulasi 1 + BESS Standar** *($P^{\text{VI}} = 0$)* | **Arbitrase Energi Murni:** BESS mengisi daya saat beban rendah dan melepas saat beban puncak. Biaya bahan bakar turun sedikit melalui *peak shaving*, namun **unit termal mahal tetap tidak bisa dimatikan** karena inersia sistem masih defisit. |
| **Simulasi 3** | **Simulasi 2 + BESS Virtual Inertia** *($P^{\text{VI}} > 0$)* | **Pembuktian Keunggulan BESS VI:** Inersia sintetis dari BESS menggantikan inersia mekanik generator termal. Unit-unit termal mahal yang boros bahan bakar **berhasil dimatikan (*de-commitment*)**, menghasilkan penurunan biaya operasional yang sangat signifikan dengan RoCoF dan QSS yang tetap aman. |
| **Simulasi 4** | **Simulasi 3 + PV & WT sebagai Pengotor** | **Uji Ketahanan pada Penetrasi EBT Nyata:** PLTB 400 MW dan PLTS 200 MW masuk menyuplai energi murah namun tanpa inersia. Masuknya daya EBT mendesak generator termal turun, memicu anjloknya inersia sistem. Di sini diuji ketahanan BESS VI menopang kisi, serta dihitung berapa MWh daya EBT yang terpaksa di-*curtail* beserta nilai **Curtailment Cost**-nya. |

---

## 🛡️ Bagian 4: Tanya-Jawab Kritis (*Defense Questions & Answers*)

### Pertanyaan 1: "Kenapa PV dan WT disebut 'pengotor'? Kenapa tidak difungsikan saja sebagai penyedia Virtual Inertia?"
> **Jawaban:**
> "Secara operasional eksisting, mayoritas turbin angin dan panel surya terhubung melalui konverter tipe *grid-following* yang diprogram untuk mengekstraksi daya maksimum (MPPT). 
> 
> Jika PV atau WT difungsikan sebagai penyedia Virtual Inertia, keduanya harus dioperasikan secara **deloading** (beroperasi 10–20% di bawah kapasitas puncak MPPT) demi menyimpan cadangan daya kinetik rotor atau kapasitas inverter. Operasi *deloading* ini menyebabkan hilangnya potensi energi hijau (*opportunity cost*) secara kontinu setiap detik sepanjang hari.
> 
> Oleh karena itu, dalam penelitian ini tugas penyediaan inersia virtual difokuskan secara khusus pada BESS yang beroperasi *grid-forming*, sedangkan PV dan WT dimaksimalkan murni sebagai pemasok energi murah. Namun karena EBT tidak berinersia dan outputnya fluktuatif, penetrasinya justru mendesak generator sinkron termal padam sehingga mengikis inersia sistem—inilah alasan teknis mengapa EBT diposisikan sebagai 'pengotor' dari sudut pandang stabilitas frekuensi."

---

### Pertanyaan 2: "Apa perbedaan mendasar antara Deloading dan Curtailment?"
> **Jawaban:**
> * **Deloading:** Strategi operasional yang **disengaja** untuk menahan titik kerja pembangkit di bawah kurva MPPT secara terus-menerus demi menyisakan margin cadangan daya aktif/kinetik untuk respon frekuensi cepat.
> * **Curtailment:** Pemotongan output daya EBT yang terjadi **sewaktu-waktu** hanya jika sistem mengalami kelebihan pasokan (*over-generation*) atau keterbatasan fleksibilitas/inersia sistem di mana generator termal sudah menyentuh batas generasi minimum teknis ($P_{\min}$) dan tidak bisa diturunkan lagi tanpa melanggar kestabilan kisi."

---

### Pertanyaan 3: "Kenapa daya inersia virtual BESS ($P_{\text{VI}}$) tidak mengurangi State of Charge (SOC) baterai pada persamaan jadwal harian?"
> **Jawaban:**
> "Karena $P_{\text{VI}}$ dalam model optimasi Unit Commitment berstatus sebagai **alokasi kapasitas ruang cadangan (*headroom reserve capability*)**, serupa dengan cadangan putar (*spinning reserve*). 
> 
> Pada kondisi operasi normal harian (*steady-state*), BESS tidak menginjeksikan energi inersia virtual tersebut ke kisi, sehingga energi elektrokimia baterai tidak terkuras. Energi $P_{\text{VI}}$ hanya diinjeksikan secara transien selama beberapa detik apabila terjadi gangguan kontingensi hilangnya pembangkit ($N-1$)."

---

### Pertanyaan 4: "Mengapa menggunakan model sistem tembaga (copper-plate 1-bus), apakah aliran daya dan rugi-rugi saluran tidak penting?"
> **Jawaban:**
> "Dinamika frekuensi sistem tenaga pasca-kontingensi (baik RoCoF pada detik pertama maupun nadir) adalah fenomena kesetimbangan daya aktif global di mana seluruh mesin di dalam interkoneksi berayun serempak di sekitar *Center of Inertia* (COI). 
> 
> Oleh sebab itu, penyederhanaan *copper-plate* 1-bus merupakan pendekatan standar yang sah dan diakui secara luas dalam literatur FCUC internasional (seperti paper Restrepo & Galiana, Wen et al., dan Chu et al.). Untuk membuktikan bahwa tidak ada batasan transmisi dan batas stabilitas tegangan/sudut lokal yang terlanggar, jadwal komitmen dan dispatch hasil optimasi ini divalidasi ke dalam pemodelan jaringan penuh di software domain-waktu **DIgSILENT PowerFactory** pada Tahap 4."

---

### Pertanyaan 5: "Apa bedanya batasan RoCoF dengan batasan QSS?"
> **Jawaban:**
> * **Batasan RoCoF ($t = 0^+$ detik):** Berada pada domain **inersia sistem**. Batasan ini mengatur kecuraman penurunan frekuensi tepat saat gangguan terjadi ($df/dt$) agar relay RoCoF tidak trip.
> * **Batasan QSS ($t = 10\text{--}30$ detik):** Berada pada domain **regulasi frekuensi primer (governor)**. Batasan ini menjamin titik keseimbangan baru frekuensi pasca-gangguan tidak anjlok melewati batas pelepasan beban darurat ($f_{\text{qss}} \ge 49.5\text{ Hz}$) melalui cadangan daya dari *droop governor* unit termal."

---

## 💡 Tips Praktis saat Menghadapi Dosen Pembimbing
1. **Bicara dengan Tenang & Percaya Diri:** Jangan terburu-buru. Tarik napas, dengarkan pertanyaan dosen hingga tuntas sebelum menjawab.
2. **Kaitkan Rumus dengan Fenomena Fisis:** Dosen menyukai mahasiswa yang tidak hanya hafal rumus, tetapi memahami arti fisis di dunia nyata (misal: kapasitas inverter BESS terbatas sehingga harus berbagi ruang antara baterai discharge dan inersia).
3. **Posisikan Diri sebagai Peneliti yang Berproses:** Jika ada masukan dari Pak Lesnanto, catat dengan antusias: *"Terima kasih banyak atas arahannya Pak, poin tersebut sangat tepat dan akan segera kami integrasikan ke dalam pemodelan Tahap 1/Tahap 2."*
