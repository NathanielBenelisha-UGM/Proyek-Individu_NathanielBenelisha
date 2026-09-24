
# ============================================================
# export_dispatch_for_digsilent.py  — Tahap 4a
# Ekspor data dispatch UC ke format CSV untuk import DIgSILENT
#
# Output:
#   DigSilent/dispatch_S{sc}_t{hour}.csv  — snapshot per jam
#   DigSilent/dispatch_all_scenarios.xlsx — semua data konsolidasi
#   DigSilent/critical_hours_summary.csv  — jam kritis untuk simulasi
# ============================================================

import os
import sys
import pandas as pd
import numpy as np

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "Hasil_UC_4_Simulasi_Summary.xlsx")
OUT_DIR   = os.path.join(BASE_DIR, "..", "DigSilent")
os.makedirs(OUT_DIR, exist_ok=True)

print("=" * 60)
print("  TAHAP 4a: EKSPOR DATA UNTUK DIGSILENT POWERFACTORY")
print("=" * 60)

# ============================================================
# 1. LOAD DATA
# ============================================================

df = {}
for sc in ["S1", "S2", "S3", "S4"]:
    df[sc] = pd.read_excel(DATA_FILE, sheet_name=sc)

THERMAL = [f"G{i}" for i in range(1, 11)]
BATT    = ["B1", "B2"]

# Generator parameters (untuk DIgSILENT model reference)
GEN_PARAMS = {
    "G1":  {"Pmax": 1176, "Pmin": 100, "H": 4,  "type": "PLTU",  "bus": "Bus_G1"},
    "G2":  {"Pmax": 1125, "Pmin": 200, "H": 9,  "type": "PLTGU", "bus": "Bus_G2"},
    "G3":  {"Pmax": 969,  "Pmin": 80,  "H": 4,  "type": "PLTU",  "bus": "Bus_G3"},
    "G4":  {"Pmax": 130,  "Pmin": 20,  "H": 6,  "type": "PLTG",  "bus": "Bus_G4"},
    "G5":  {"Pmax": 108,  "Pmin": 20,  "H": 6,  "type": "PLTG",  "bus": "Bus_G5"},
    "G6":  {"Pmax": 1095, "Pmin": 200, "H": 9,  "type": "PLTGU", "bus": "Bus_G6"},
    "G7":  {"Pmax": 810,  "Pmin": 80,  "H": 9,  "type": "PLTGU", "bus": "Bus_G7"},
    "G8":  {"Pmax": 773,  "Pmin": 80,  "H": 9,  "type": "PLTGU", "bus": "Bus_G8"},
    "G9":  {"Pmax": 870,  "Pmin": 80,  "H": 4,  "type": "PLTU",  "bus": "Bus_G9"},
    "G10": {"Pmax": 840,  "Pmin": 80,  "H": 4,  "type": "PLTU",  "bus": "Bus_G10"},
}

BATT_PARAMS = {
    "B1": {"SOC_max": 155.0, "SOC_min": 15.5, "CR_max": 60.0, "DR_max": 60.0, "Kb_VI": 4.0, "bus": "Bus_B1"},
    "B2": {"SOC_max": 50.0,  "SOC_min": 10.0, "CR_max": 20.0, "DR_max": 20.0, "Kb_VI": 5.0, "bus": "Bus_B2"},
}

# ============================================================
# 2. CRITICAL HOURS DEFINITION
# ============================================================

# Jam kritis berdasarkan analisis Tahap 2
CRITICAL_HOURS = {
    "t01_valley":    {"hour": 1,  "reason": "Jam lembah, RoCoF paling kritis, WT curtailment"},
    "t12_midday":    {"hour": 12, "reason": "Siang hari, PV+WT aktif, BESS VI penuh"},
    "t20_peak":      {"hour": 20, "reason": "Peak demand 5132 MW, H_sys minimum"},
}

print(f"\n  Jam kritis yang akan diekspor:")
for name, info in CRITICAL_HOURS.items():
    print(f"    {name}: t={info['hour']:02d}h — {info['reason']}")

# ============================================================
# 3. GENERATE DIGSILENT DISPATCH CSV PER HOUR PER SCENARIO
# ============================================================
# Format: Setiap kolom = parameter, setiap baris = unit
# DIgSILENT dapat membaca ini via DPL script atau Python API

all_snapshots = []

for sc in ["S1", "S3", "S4"]:
    for t_name, t_info in CRITICAL_HOURS.items():
        t_hour = t_info["hour"]
        t_idx  = t_hour - 1   # 0-indexed

        row = df[sc].iloc[t_idx]
        demand = row["Demand"]
        hsys   = row["Hsys"]
        ll     = row["LargestLoss"]
        rocof  = row["RoCoF_est"]
        pfr    = row["TotalPFR"]
        fqss   = row["f_qss_est"]

        # Build generator dispatch table
        gen_rows = []
        for g in THERMAL:
            p_val  = float(row[f"{g}_P"])
            u_val  = int(round(float(row[f"{g}_u"])))
            r_val  = float(row[f"{g}_R"])
            gp     = GEN_PARAMS[g]
            gen_rows.append({
                "object_name":     g,
                "object_class":    "ElmSym",
                "bus":             gp["bus"],
                "type":            gp["type"],
                "H_const":         gp["H"],
                "Pmax_MW":         gp["Pmax"],
                "Pmin_MW":         gp["Pmin"],
                "P_dispatch_MW":   round(p_val, 3),
                "Q_dispatch_MVAr": 0.0,
                "status_on":       u_val,
                "reserve_MW":      round(r_val, 3),
                "loading_pct":     round(p_val / gp["Pmax"] * 100 if u_val else 0, 2),
            })

        # Battery rows
        for b in BATT:
            pdis = float(row[f"{b}_Pdis"]) if f"{b}_Pdis" in row.index else 0.0
            pch  = float(row[f"{b}_Pch"])  if f"{b}_Pch"  in row.index else 0.0
            soc  = float(row[f"{b}_SOC"])  if f"{b}_SOC"  in row.index else 0.0
            p_vi = float(row[f"{b}_P_VI"]) if f"{b}_P_VI" in row.index else 0.0
            bp   = BATT_PARAMS[b]
            gen_rows.append({
                "object_name":     b,
                "object_class":    "ElmBatt",
                "bus":             bp["bus"],
                "type":            "BESS_LFP",
                "H_const":         0.0,
                "Pmax_MW":         bp["DR_max"],
                "Pmin_MW":         -bp["CR_max"],
                "P_dispatch_MW":   round(pdis - pch, 3),
                "Q_dispatch_MVAr": 0.0,
                "status_on":       1 if (pdis > 0.01 or pch > 0.01 or p_vi > 0.01) else 0,
                "reserve_MW":      0.0,
                "loading_pct":     round(pdis / bp["DR_max"] * 100 if pdis > 0.01 else 0, 2),
                "SOC_MWh":         round(soc, 3),
                "P_VI_MW":         round(p_vi, 3),
                "Kb_VI":           bp["Kb_VI"],
                "H_VI_MWs":        round(bp["Kb_VI"] * p_vi, 3),
            })

        # WT/PV for S4
        if sc == "S4":
            gen_rows.append({
                "object_name":     "WT1",
                "object_class":    "ElmPVSys",
                "bus":             "Bus_WT1",
                "type":            "WindTurbine_DFIG",
                "H_const":         0.0,
                "Pmax_MW":         400.0,
                "Pmin_MW":         0.0,
                "P_dispatch_MW":   round(float(row["WT_Used"]), 3),
                "Q_dispatch_MVAr": 0.0,
                "status_on":       1 if float(row["WT_Used"]) > 0.1 else 0,
                "reserve_MW":      0.0,
                "loading_pct":     round(float(row["WT_Used"]) / 400 * 100, 2),
                "SOC_MWh":         None,
                "P_VI_MW":         0.0,
                "Kb_VI":           0.0,
                "H_VI_MWs":        0.0,
            })

        df_gen = pd.DataFrame(gen_rows)

        # System info header
        sys_info = {
            "scenario":          sc,
            "hour":              t_hour,
            "demand_MW":         round(demand, 3),
            "Hsys_MWs":          round(hsys, 2),
            "LargestLoss_MW":    round(ll, 3),
            "TotalPFR_MW":       round(pfr, 3),
            "RoCoF_est_Hz_s":    round(rocof, 6),
            "f_QSS_est_Hz":      round(fqss, 4),
            "H_required_MWs":    round(50.0 * ll / (2 * 0.55), 2),
        }

        # Save CSV
        filename = f"dispatch_{sc}_{t_name}.csv"
        filepath = os.path.join(OUT_DIR, filename)

        # Write: header block + generator table
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# DIgSILENT PowerFactory — Initial Conditions\n")
            f.write(f"# Scenario: {sc} | Hour: t={t_hour:02d} | {t_info['reason']}\n")
            for k, v in sys_info.items():
                f.write(f"# {k}: {v}\n")
            f.write("#\n")

        df_gen.to_csv(filepath, mode="a", index=False, encoding="utf-8")
        print(f"  Saved: {filename}")

        # Collect for master Excel
        for r in gen_rows:
            r.update({"scenario": sc, "hour": t_hour, "t_name": t_name})
            r.update(sys_info)
            all_snapshots.append(r)

# ============================================================
# 4. MASTER EXCEL — ALL CRITICAL SNAPSHOTS
# ============================================================

df_master = pd.DataFrame(all_snapshots)
master_file = os.path.join(OUT_DIR, "dispatch_critical_hours.xlsx")

with pd.ExcelWriter(master_file, engine="openpyxl") as writer:
    df_master.to_excel(writer, sheet_name="All_Snapshots", index=False)

    # Pivot: system-level per scenario per hour
    sys_cols = ["scenario", "hour", "demand_MW", "Hsys_MWs",
                "LargestLoss_MW", "TotalPFR_MW", "RoCoF_est_Hz_s",
                "f_QSS_est_Hz", "H_required_MWs"]
    df_sys = df_master[sys_cols].drop_duplicates().reset_index(drop=True)
    df_sys.to_excel(writer, sheet_name="System_Summary", index=False)

    # Per-scenario generator dispatch at t=20 (peak)
    for sc in ["S1", "S3", "S4"]:
        mask = (df_master["scenario"] == sc) & (df_master["hour"] == 20)
        df_sc = df_master[mask][["object_name", "P_dispatch_MW", "status_on",
                                  "reserve_MW", "loading_pct", "P_VI_MW", "H_VI_MWs"]]
        df_sc.to_excel(writer, sheet_name=f"t20_{sc}", index=False)

print(f"\n  Master Excel: {master_file}")

# ============================================================
# 5. CONTINGENCY DEFINITION FILE
# ============================================================
# Format yang dapat dibaca oleh DPL Script DIgSILENT

contingency_data = []

# Semua kombinasi: skenario UC × jam kritis × skema trip
for sc in ["S1", "S3", "S4"]:
    for t_name, t_info in CRITICAL_HOURS.items():
        t_hour = t_info["hour"]
        t_idx  = t_hour - 1
        row    = df[sc].iloc[t_idx]

        # Generator yang ON → kandidat trip (N-1)
        on_gens = [g for g in THERMAL if float(row[f"{g}_u"]) > 0.5]
        # Pilih generator terbesar (LargestLoss = output terbesar)
        largest_gen = max(on_gens, key=lambda g: float(row[f"{g}_P"]))
        largest_p   = float(row[f"{largest_gen}_P"])

        for t_trip_s in [0]:            # Trip selalu di t=0s
            for t_reclose_s in [15, 30, 9999]:  # Reclose: 15s, 30s, never
                reclose_label = f"t={t_reclose_s}s" if t_reclose_s < 9999 else "no_reclose"

                contingency_data.append({
                    "test_id":         f"{sc}_{t_name}_{largest_gen}_rc{t_reclose_s}",
                    "scenario_UC":     sc,
                    "hour_UC":         t_hour,
                    "t_name":          t_name,
                    "dispatch_file":   f"dispatch_{sc}_{t_name}.csv",
                    "contingency_gen": largest_gen,
                    "P_loss_MW":       round(largest_p, 2),
                    "t_trip_s":        t_trip_s,
                    "t_reclose_s":     t_reclose_s if t_reclose_s < 9999 else None,
                    "reclose_label":   reclose_label,
                    "H_sys_MWs":       round(float(row["Hsys"]), 2),
                    "expected_RoCoF":  round(float(row["RoCoF_est"]), 4),
                    "expected_fQSS":   round(float(row["f_qss_est"]), 4),
                    "has_BESS_VI":     1 if sc in ["S3", "S4"] else 0,
                    "has_EBT":         1 if sc == "S4" else 0,
                    "sim_duration_s":  120,
                    "step_size_ms":    10,
                })

df_cont = pd.DataFrame(contingency_data)
cont_file = os.path.join(OUT_DIR, "contingency_test_matrix.csv")
df_cont.to_csv(cont_file, index=False)
print(f"  Contingency matrix: {cont_file}")
print(f"  Total test cases: {len(df_cont)}")

# ============================================================
# 6. SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("  EKSPOR SELESAI")
print("=" * 60)
print(f"  Output folder : {OUT_DIR}")
print(f"  Dispatch CSVs : {3 * len(CRITICAL_HOURS)} files")
print(f"  Master Excel  : dispatch_critical_hours.xlsx")
print(f"  Contingency   : contingency_test_matrix.csv ({len(df_cont)} tests)")
print()

print("  Ringkasan jam kritis untuk DIgSILENT:")
df_sys_print = df_sys.sort_values(["hour", "scenario"])
print(df_sys_print[["scenario","hour","demand_MW","Hsys_MWs",
                     "LargestLoss_MW","RoCoF_est_Hz_s","f_QSS_est_Hz"]].to_string(index=False))
