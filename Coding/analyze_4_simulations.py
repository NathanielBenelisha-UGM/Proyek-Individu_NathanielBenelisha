
# ============================================================
# analyze_4_simulations.py  — Tahap 2
# Ekstraksi & Analisis Komparatif 4 Skenario FCUC
# Fokus: Pengaruh BESS Virtual Inertia pada Sistem
# ============================================================

import os
import pandas as pd
import numpy as np

# ============================================================
# 0. LOAD DATA
# ============================================================

FILE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "Hasil_UC_4_Simulasi_Summary.xlsx"
)

print(f"Membaca: {FILE_PATH}\n")

df = {}
for sc in ["S1", "S2", "S3", "S4"]:
    df[sc] = pd.read_excel(FILE_PATH, sheet_name=sc)

df_summary_raw = pd.read_excel(FILE_PATH, sheet_name="Summary")

BATT    = ["B1", "B2"]
THERMAL = ["G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8", "G9", "G10"]

# Generator type & Pmax (dari parameter yang sudah diketahui)
GEN_INFO = {
    "G1":  {"type": "Thermal", "Pmax": 1176, "H": 4,  "fuel": "PLTU"},
    "G2":  {"type": "Thermal", "Pmax": 1125, "H": 9,  "fuel": "PLTGU"},
    "G3":  {"type": "Thermal", "Pmax": 969,  "H": 4,  "fuel": "PLTU"},
    "G4":  {"type": "Thermal", "Pmax": 130,  "H": 6,  "fuel": "PLTG"},
    "G5":  {"type": "Thermal", "Pmax": 108,  "H": 6,  "fuel": "PLTG"},
    "G6":  {"type": "Thermal", "Pmax": 1095, "H": 9,  "fuel": "PLTGU"},
    "G7":  {"type": "Thermal", "Pmax": 810,  "H": 9,  "fuel": "PLTGU"},
    "G8":  {"type": "Thermal", "Pmax": 773,  "H": 9,  "fuel": "PLTGU"},
    "G9":  {"type": "Thermal", "Pmax": 870,  "H": 4,  "fuel": "PLTU"},
    "G10": {"type": "Thermal", "Pmax": 840,  "H": 4,  "fuel": "PLTU"},
}

SCENARIO_NAMES = {
    "S1": "S1: Thermal + Inersia + QSS",
    "S2": "S2: S1 + BESS Standard",
    "S3": "S3: S1 + BESS VI",
    "S4": "S4: S3 + PV & WT Pengotor",
}

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def unit_on_hours(df_sc):
    """Hitung jam aktif (ON) tiap unit thermal."""
    return {g: df_sc[f"{g}_u"].sum() for g in THERMAL}

def avg_loading(df_sc, g):
    """Rata-rata loading saat unit ON."""
    on_mask = df_sc[f"{g}_u"] == 1
    if on_mask.sum() == 0:
        return 0.0
    return df_sc.loc[on_mask, f"{g}_P"].mean()

# ============================================================
# 1. TABEL A: RINGKASAN BIAYA & KINERJA
# ============================================================

print("=" * 70)
print("TABEL A: RINGKASAN BIAYA & KINERJA KEEMPAT SKENARIO")
print("=" * 70)

# Parse summary (string -> float)
def parse_cost(x):
    if isinstance(x, str):
        return float(x.replace(",", ""))
    return float(x)

cost_rows = []
for sc in ["S1", "S2", "S3", "S4"]:
    d = df[sc]
    row = {
        "Skenario":          sc,
        "Deskripsi":         SCENARIO_NAMES[sc],
        "Fuel_Cost($)":      d["Fuel_Cost"].sum(),
        "Fixed_Cost($)":     d["Fixed_Cost"].sum(),
        "Startup_Cost($)":   d["Startup_Cost"].sum(),
        "Shutdown_Cost($)":  d["Shutdown_Cost"].sum(),
        "Curt_Cost($)":      d["Curt_Cost"].sum(),
        "Total_Cost($)":     d["Total_Cost"].sum(),
    }
    cost_rows.append(row)

df_cost = pd.DataFrame(cost_rows)
df_cost_disp = df_cost.copy()
for col in ["Fuel_Cost($)", "Fixed_Cost($)", "Startup_Cost($)",
            "Shutdown_Cost($)", "Curt_Cost($)", "Total_Cost($)"]:
    df_cost_disp[col] = df_cost_disp[col].apply(lambda x: f"${x:,.2f}")

print(df_cost_disp[["Skenario", "Deskripsi", "Fuel_Cost($)",
                     "Fixed_Cost($)", "Curt_Cost($)", "Total_Cost($)"]].to_string(index=False))

# Hitung penghematan
s1_cost = df_cost.loc[df_cost["Skenario"] == "S1", "Total_Cost($)"].values[0]
print("\n  Penghematan relatif terhadap S1 (Baseline):")
for sc in ["S2", "S3", "S4"]:
    sc_cost = df_cost.loc[df_cost["Skenario"] == sc, "Total_Cost($)"].values[0]
    saving = s1_cost - sc_cost
    pct = saving / s1_cost * 100
    print(f"    {sc}: Hemat ${saving:,.2f}  ({pct:.2f}%)")

# ============================================================
# 2. TABEL B: STATISTIK INERSIA & FREKUENSI
# ============================================================

print("\n\n" + "=" * 70)
print("TABEL B: STATISTIK INERSIA SISTEM & FREKUENSI")
print("=" * 70)

freq_rows = []
for sc in ["S1", "S2", "S3", "S4"]:
    d = df[sc]
    # VI dari BESS
    vi_total_avg = 0.0
    for b in BATT:
        if f"{b}_H_VI" in d.columns:
            vi_total_avg += d[f"{b}_H_VI"].mean()

    # Inersia thermal saja
    h_thermal_avg = d["Hsys"].mean() - vi_total_avg

    row = {
        "Skenario":           sc,
        "Hsys_Avg(MWs)":      d["Hsys"].mean(),
        "Hsys_Min(MWs)":      d["Hsys"].min(),
        "Hsys_Max(MWs)":      d["Hsys"].max(),
        "H_Thermal_Avg(MWs)": h_thermal_avg,
        "H_VI_BESS_Avg(MWs)": vi_total_avg,
        "LargestLoss_Avg(MW)": d["LargestLoss"].mean(),
        "LargestLoss_Max(MW)": d["LargestLoss"].max(),
        "TotalPFR_Avg(MW)":   d["TotalPFR"].mean(),
        "RoCoF_Max(Hz/s)":    d["RoCoF_est"].max(),
        "RoCoF_Avg(Hz/s)":    d["RoCoF_est"].mean(),
        "f_qss_Min(Hz)":      d["f_qss_est"].min(),
        "f_qss_Avg(Hz)":      d["f_qss_est"].mean(),
    }
    freq_rows.append(row)

df_freq = pd.DataFrame(freq_rows)
print(df_freq[["Skenario", "Hsys_Avg(MWs)", "Hsys_Min(MWs)",
               "H_Thermal_Avg(MWs)", "H_VI_BESS_Avg(MWs)",
               "RoCoF_Max(Hz/s)", "f_qss_Min(Hz)"]].to_string(index=False))

# ============================================================
# 3. TABEL C: UNIT COMMITMENT STATUS (JAM ON PER UNIT)
# ============================================================

print("\n\n" + "=" * 70)
print("TABEL C: JAM AKTIF (ON) PER UNIT THERMAL (dari 24 jam)")
print("=" * 70)

uc_rows = []
for sc in ["S1", "S2", "S3", "S4"]:
    row_data = {"Skenario": sc}
    on_h = unit_on_hours(df[sc])
    for g in THERMAL:
        row_data[g] = int(on_h[g])
    row_data["Total_Unit_Hours"] = sum(on_h.values())
    uc_rows.append(row_data)

df_uc = pd.DataFrame(uc_rows)
print(df_uc.to_string(index=False))

# Highlight perbedaan S3 vs S4
print("\n  Perbedaan jam ON (S4 - S3):")
s3_on = unit_on_hours(df["S3"])
s4_on = unit_on_hours(df["S4"])
for g in THERMAL:
    diff = int(s4_on[g]) - int(s3_on[g])
    if diff != 0:
        print(f"    {g}: S3={int(s3_on[g])}h  ->  S4={int(s4_on[g])}h  (Δ={diff:+d}h)")

# ============================================================
# 4. TABEL D: HOURLY INERTIA & ROCOF — S3 vs S4
# ============================================================

print("\n\n" + "=" * 70)
print("TABEL D: PERBANDINGAN INERSIA PER JAM — S3 vs S4")
print("=" * 70)

d3 = df["S3"]
d4 = df["S4"]

inertia_rows = []
for idx, t in enumerate(d3["Hour"]):
    row = {
        "Hour": t,
        "Demand(MW)":      round(d3.loc[idx, "Demand"], 1),
        "S3_Hsys":         round(d3.loc[idx, "Hsys"], 1),
        "S3_VI_BESS":      round(sum(d3.loc[idx, f"{b}_H_VI"] for b in BATT if f"{b}_H_VI" in d3.columns), 1),
        "S3_RoCoF":        round(d3.loc[idx, "RoCoF_est"], 4),
        "S3_fqss":         round(d3.loc[idx, "f_qss_est"], 3),
        "S4_Hsys":         round(d4.loc[idx, "Hsys"], 1),
        "S4_VI_BESS":      round(sum(d4.loc[idx, f"{b}_H_VI"] for b in BATT if f"{b}_H_VI" in d4.columns), 1),
        "S4_WT_Available": round(d4.loc[idx, "WT_Available"], 1),
        "S4_WT_Curt":      round(d4.loc[idx, "WT_Curtailment"], 2),
        "S4_WT_Used":      round(d4.loc[idx, "WT_Used"], 1),
        "S4_PV_Used":      round(d4.loc[idx, "PV_Used"], 1),
        "S4_RoCoF":        round(d4.loc[idx, "RoCoF_est"], 4),
        "S4_fqss":         round(d4.loc[idx, "f_qss_est"], 3),
        "Delta_Hsys":      round(d4.loc[idx, "Hsys"] - d3.loc[idx, "Hsys"], 1),
    }
    inertia_rows.append(row)

df_inertia = pd.DataFrame(inertia_rows)
print(df_inertia[["Hour", "Demand(MW)", "S3_Hsys", "S3_VI_BESS", "S3_RoCoF",
                   "S4_Hsys", "S4_VI_BESS", "S4_WT_Used", "S4_WT_Curt",
                   "S4_RoCoF", "Delta_Hsys"]].to_string(index=False))

# ============================================================
# 5. ANALISIS S3 vs S4 — BESS VI DISPATCH
# ============================================================

print("\n\n" + "=" * 70)
print("TABEL E: DISPATCH BESS (S3 vs S4)")
print("=" * 70)

bess_rows = []
for idx, t in enumerate(d3["Hour"]):
    row = {"Hour": t, "Demand": round(d3.loc[idx, "Demand"], 1)}
    for b in BATT:
        for prefix, d_sc in [("S3", d3), ("S4", d4)]:
            row[f"{prefix}_{b}_Pdis"] = round(d_sc.loc[idx, f"{b}_Pdis"] if f"{b}_Pdis" in d_sc.columns else 0, 2)
            row[f"{prefix}_{b}_P_VI"] = round(d_sc.loc[idx, f"{b}_P_VI"] if f"{b}_P_VI" in d_sc.columns else 0, 2)
            row[f"{prefix}_{b}_SOC"]  = round(d_sc.loc[idx, f"{b}_SOC"] if f"{b}_SOC" in d_sc.columns else 0, 2)
    bess_rows.append(row)

df_bess = pd.DataFrame(bess_rows)
print(df_bess.to_string(index=False))

# ============================================================
# 6. ANALISIS NARATIF — KEY FINDINGS
# ============================================================

print("\n\n" + "=" * 70)
print("ANALISIS UTAMA: PENGARUH BESS VIRTUAL INERTIA PADA SISTEM")
print("=" * 70)

print("""
[A] PENGARUH VI TERHADAP UNIT COMMITMENT
----------------------------------------""")

# Hitung total unit-hours ON per skenario
for sc in ["S1", "S2", "S3", "S4"]:
    on_h = unit_on_hours(df[sc])
    total = sum(on_h.values())
    units_always_on = [g for g in THERMAL if on_h[g] == 24]
    units_never_on  = [g for g in THERMAL if on_h[g] == 0]
    print(f"  {sc}: Total unit-hours ON = {total}h | "
          f"Selalu ON={units_always_on} | Tidak pernah ON={units_never_on}")

print()
print("[B] PENGHEMATAN DARI BESS VI (S3 vs S2):")
s2_cost = df_cost.loc[df_cost["Skenario"] == "S2", "Total_Cost($)"].values[0]
s3_cost = df_cost.loc[df_cost["Skenario"] == "S3", "Total_Cost($)"].values[0]
saving_s3 = s2_cost - s3_cost
pct_s3 = saving_s3 / s2_cost * 100
print(f"  BESS VI memungkinkan penghematan: ${saving_s3:,.2f} ({pct_s3:.2f}%) vs BESS Standar")
print(f"  Mekanisme: BESS VI menyumbang inersia virtual, sehingga beberapa")
print(f"  unit thermal dengan H rendah dapat beroperasi di dispatch lebih rendah")

print()
print("[C] PENGARUH PV & WT (S4 vs S3 — Dampak 'Pengotor'):")
s4_cost = df_cost.loc[df_cost["Skenario"] == "S4", "Total_Cost($)"].values[0]
saving_s4 = s3_cost - s4_cost
pct_s4 = saving_s4 / s3_cost * 100
wt_curt = d4["WT_Curtailment"].sum()
wt_used = d4["WT_Used"].sum()
pv_used = d4["PV_Used"].sum()
pct_wt_curt = wt_curt / (wt_curt + wt_used) * 100 if (wt_curt + wt_used) > 0 else 0

print(f"  Penghematan biaya operasi     : ${saving_s4:,.2f} ({pct_s4:.2f}%)")
print(f"  WT energi tersedia total      : {wt_curt + wt_used:.2f} MWh")
print(f"  WT energi terserap grid       : {wt_used:.2f} MWh")
print(f"  WT energi di-curtail          : {wt_curt:.2f} MWh  ({pct_wt_curt:.1f}%)")
print(f"  PV energi terserap grid       : {pv_used:.2f} MWh")
print(f"  WT curtailment cost           : ${wt_curt * 30:,.2f}")
print()

# Jam kritis WT curtailment
curt_hours = d4[d4["WT_Curtailment"] > 0.1][["Hour", "Demand", "WT_Available",
                                               "WT_Curtailment", "WT_Used",
                                               "Hsys", "LargestLoss", "RoCoF_est"]]
print(f"  Jam terjadi WT Curtailment (threshold > 0.1 MWh):")
if len(curt_hours) > 0:
    print(curt_hours.to_string(index=False))
else:
    print("  Tidak ada jam dengan curtailment > 0.1 MWh")

print()
print("[D] INERSIA THERMAL ANJLOK KARENA EBT (S4):")
avg_hsys_s3 = d3["Hsys"].mean()
avg_hsys_s4 = d4["Hsys"].mean()
avg_vi_s4   = sum(d4[f"{b}_H_VI"].mean() for b in BATT if f"{b}_H_VI" in d4.columns)
print(f"  Rata-rata Hsys S3            : {avg_hsys_s3:.2f} MWs (tanpa EBT)")
print(f"  Rata-rata Hsys S4            : {avg_hsys_s4:.2f} MWs (dengan EBT pengotor)")
print(f"  Selisih Hsys S3->S4           : {avg_hsys_s4 - avg_hsys_s3:+.2f} MWs")
print(f"  Rata-rata VI BESS S4         : {avg_vi_s4:.2f} MWs")
print(f"  Note: EBT yang masuk = zero-inertia -> tidak menambah H_thermal")
print(f"  BESS VI yang 'menebus' defisit inersia saat EBT mengurangi thermal")

print()
print("[E] RINGKASAN: PERAN BESS VI DALAM SISTEM EBT TINGGI (S4):")
print(f"  1. BESS VI menyediakan inersia virtual ({avg_vi_s4:.1f} MWs rata-rata)")
print(f"     untuk mengkompensasi berkurangnya pembangkitan thermal saat EBT aktif")
print(f"  2. Tanpa BESS VI, masuknya WT & PV akan memaksa lebih banyak")
print(f"     unit thermal tetap ON untuk memenuhi batas RoCoF 0.55 Hz/s")
print(f"  3. Curtailment WT ({wt_curt:.1f} MWh) terjadi di jam-jam di mana")
print(f"     WT yang terserap akan menyebabkan LargestLoss melebihi batas QSS")
print(f"  4. Total penghematan S4 vs S1: ${s1_cost - s4_cost:,.2f} ({(s1_cost - s4_cost)/s1_cost*100:.2f}%)")

# ============================================================
# 7. TABEL F: DISPATCH THERMAL PER JAM — S3 vs S4 (Kritis)
# ============================================================

print("\n\n" + "=" * 70)
print("TABEL F: DISPATCH THERMAL — PERBANDINGAN KUNCI S3 vs S4")
print("=" * 70)

thermal_disp = []
for idx, t in enumerate(d3["Hour"]):
    thermal_s3 = d3.loc[idx, "Total_Thermal"]
    thermal_s4 = d4.loc[idx, "Total_Thermal"]
    wt_used_s4 = d4.loc[idx, "WT_Used"]
    pv_used_s4 = d4.loc[idx, "PV_Used"]
    thermal_disp.append({
        "Hour":            t,
        "Demand(MW)":      round(d3.loc[idx, "Demand"], 1),
        "S3_Thermal(MW)":  round(thermal_s3, 1),
        "S4_Thermal(MW)":  round(thermal_s4, 1),
        "S4_WT_Used(MW)":  round(wt_used_s4, 1),
        "S4_PV_Used(MW)":  round(pv_used_s4, 1),
        "S4_RES_Total(MW)":round(wt_used_s4 + pv_used_s4, 1),
        "Delta_Thermal":   round(thermal_s4 - thermal_s3, 1),
        "S3_Hsys":         round(d3.loc[idx, "Hsys"], 0),
        "S4_Hsys":         round(d4.loc[idx, "Hsys"], 0),
    })

df_td = pd.DataFrame(thermal_disp)
print(df_td.to_string(index=False))

# ============================================================
# 8. EXPORT ANALISIS KE EXCEL BARU
# ============================================================

output_file = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "Analisis_Hasil_4_Simulasi.xlsx"
)

with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
    df_cost.to_excel(writer, sheet_name="A_BiayaRingkasan", index=False)
    df_freq.to_excel(writer, sheet_name="B_InersiaPFR", index=False)
    df_uc.to_excel(writer, sheet_name="C_UnitCommitment", index=False)
    df_inertia.to_excel(writer, sheet_name="D_InersiaPerjam_S3vsS4", index=False)
    df_bess.to_excel(writer, sheet_name="E_BESSDispatch_S3vsS4", index=False)
    df_td.to_excel(writer, sheet_name="F_ThermalDispatch_S3vsS4", index=False)

print(f"\n\nHasil analisis disimpan ke: {output_file}")
print("Done.")
