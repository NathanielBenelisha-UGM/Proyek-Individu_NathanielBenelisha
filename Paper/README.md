# 📁 Paper — Draft Publikasi Ilmiah

Folder ini berisi draft paper dalam format **LaTeX (IEEEtran)** untuk publikasi ilmiah.

---

## File Utama

| File | Keterangan |
|------|------------|
| `main_v2.tex` | ⭐ **Draft terbaru (v2)** — lengkap dengan hasil simulasi 7 skenario, literature review komprehensif, dan 21 referensi dengan DOI tervalidasi |
| `main.tex` | Draft awal (v1) — template awal sebelum integrasi hasil |
| `explanation_virtual_inertia.tex` | Penjelasan detail model virtual inertia |
| `draft_paper.md` | Draft awal dalam format Markdown |

## Draft PDF

| File | Keterangan |
|------|------------|
| `PI_Draf1.pdf` | Draft PDF versi 1 |
| `PI_Draf2.pdf` | Draft PDF versi 2 |
| `PI_Draf3.pdf` | Draft PDF versi 3 |

## Subfolder

| Folder | Keterangan |
|--------|------------|
| `figures/` | Gambar dan grafik untuk dimasukkan ke paper |

---

## Judul Paper

**"Frequency-Constrained Unit Commitment with Multi-Source Virtual Inertia Provision from Inverter-Based Resources"**

### Penulis

1. Nathaniel Benelisha (corresponding author)
2. Muhammad Aris Risnandar
3. Ir. Lesnanto Multa Putranto, S.T., M.Eng., Ph.D., IPM., ASEAN Eng., SMIEEE

### Target Jurnal

IEEE Access / Energies (MDPI)

---

## Cara Kompilasi

```bash
# Compile LaTeX to PDF
pdflatex main_v2.tex
pdflatex main_v2.tex   # Run twice for references
```

Memerlukan distribusi LaTeX (MiKTeX atau TeX Live) dengan package `IEEEtran`.
