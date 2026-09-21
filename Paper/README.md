# 📁 Paper — Publikasi Ilmiah & Draf Naskah

Folder ini memuat naskah draf publikasi ilmiah dalam format PDF yang siap diunduh dan ditinjau. Naskah ini disiapkan sebagai luaran pengganti Skripsi / Tugas Akhir di Departemen Teknik Elektro dan Teknologi Informasi, Fakultas Teknik, Universitas Gadjah Mada.

---

## 🌟 Naskah Terkini (Active Latest Draft)

| File | Status | Keterangan |
|------|--------|------------|
| 📥 **[PI_Draf5.pdf](PI_Draf5.pdf)** | ⭐ **LATEST DRAFT** | Versi draf paling mutakhir (Draf 5) — memuat penyelarasan formulasi Cost & PFR dari referensi `[E02]`, pemodelan inersia virtual khusus BESS dengan *converter headroom coupling*, neraca daya terpadu PV & Wind, dan metodologi validasi transien DIgSILENT PowerFactory. |
| 🔗 **[LATEST_DRAFT.pdf](LATEST_DRAFT.pdf)** | 🔄 **Pointer Terkini** | File mirror yang selalu merefleksikan draf terbaru agar tautan eksternal selalu valid. |

---

## 📚 Riwayat Versi Draf (Version History)

| Versi | File PDF | Tanggal/Fase | Poin Pembaruan Utama |
|:-----:|:--------:|:------------:|----------------------|
| **v5** | **[PI_Draf5.pdf](PI_Draf5.pdf)** | **Terbaru** | Penyelarasan matematis penuh: Formulasi Cost linear ($a_g u_{g,t} + b_g P_{g,t}$), batasan PFR & *droop governor* sesuai `[E02]` ICITEE 2020, alokasi daya discharging BESS ($P_{b,t}^{\text{dis}} + P_{b,t}^{\text{VI}}/\eta_b^{\text{VI}} \le DR_b^{\max} u_{b,t}^{\text{dis}}$), isolasi VI khusus ke BESS, neraca daya PV+Wind, dan kerangka validasi transien DIgSILENT PowerFactory pada sistem IEEE 24-bus ekivalen 10-generator. |
| **v4** | **[PI_Draf4.pdf](PI_Draf4.pdf)** | Tahap 4 | Penajaman analisis ekonomi komparatif 7 skenario dan penyesuaian parameter IBR. |
| **v3** | **[PI_Draf3.pdf](PI_Draf3.pdf)** | Tahap 3 | Integrasi dataset hasil simulasi numerik 7 skenario dari Pyomo/CPLEX. |
| **v2** | **[PI_Draf2.pdf](PI_Draf2.pdf)** | Tahap 2 | Pengembangan formulasi matematis FCUC dan literature review komprehensif. |
| **v1** | **[PI_Draf1.pdf](PI_Draf1.pdf)** | Tahap 1 | Kerangka awal manuskrip dan penyusunan struktur bab. |

---

## 👥 Informasi Penulis & Pembimbing

- **Penulis 1 (Corresponding Author):** Nathaniel Benelisha (Mahasiswa S1 Teknik Elektro, Universitas Gadjah Mada)
- **Penulis 2:** Muhammad Aris Risnandar (Mahasiswa Program Doktor Teknik Elektro, Universitas Gadjah Mada)
- **Dosen Pembimbing:** Ir. Lesnanto Multa Putranto, S.T., M.Eng., Ph.D., IPM., ASEAN Eng., SMIEEE (Lektor Kepala / Associate Professor, Departemen Teknik Elektro dan Teknologi Informasi, FT UGM)

**Target Publikasi:** IEEE Transactions on Power Systems / IEEE Access / Energies (MDPI)

---

## 🛠️ Panduan Pembaruan Draf untuk Git Upload

Setiap kali Anda selesai memperbarui naskah:
1. Simpan file PDF baru dengan format penamaan berurutan (misal: `PI_Draf5.pdf`, `PI_Draf6.pdf`, dst.) di folder `Paper/`.
2. Salin atau perbarui file `LATEST_DRAFT.pdf`:
   ```bash
   cp Paper/PI_Draf5.pdf Paper/LATEST_DRAFT.pdf
   ```
3. Lakukan commit dan push ke GitHub:
   ```bash
   git add Paper/
   git commit -m "docs(paper): update latest paper draft to v5"
   git push origin main
   ```

