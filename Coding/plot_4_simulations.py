
# ============================================================
# plot_4_simulations.py  — Tahap 3
# IEEE Publication-Quality Visualization (300 DPI)
# Frequency-Constrained Unit Commitment — 4 Scenario Analysis
#
# Figures generated:
#   Fig 1: Cost comparison bar chart (4 scenarios)
#   Fig 2: Generation dispatch stack — S1 (thermal baseline)
#   Fig 3: Generation dispatch stack — S4 (full EBT + BESS VI)
#   Fig 4: Unit commitment heatmap (4 scenarios)
#   Fig 5: BESS dispatch & Virtual Inertia — S3 vs S4
#   Fig 6: System inertia & RoCoF profile (4 scenarios)
#   Fig 7: Frequency security metrics — S3 vs S4 comparison
#   Fig 8: WT/PV curtailment & energy composition — S4
# ============================================================

import os
import sys
import warnings
warnings.filterwarnings("ignore")

import matplotlib
matplotlib.use("Agg")   # Non-interactive backend for headless rendering
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from matplotlib.ticker import MultipleLocator, AutoMinorLocator
import matplotlib.colors as mcolors
import numpy as np
import pandas as pd

# ============================================================
# 0. PATHS & GLOBAL SETTINGS
# ============================================================

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "Hasil_UC_4_Simulasi_Summary.xlsx")
FIG_DIR   = os.path.join(BASE_DIR, "..", "Paper", "figures")
os.makedirs(FIG_DIR, exist_ok=True)

print(f"Data  : {DATA_FILE}")
print(f"Output: {FIG_DIR}\n")

# ============================================================
# IEEE STYLE CONFIGURATION
# ============================================================

plt.rcParams.update({
    # Font — IEEE requires Times New Roman or similar serif
    "font.family":        "serif",
    "font.serif":         ["Times New Roman", "DejaVu Serif", "Palatino"],
    "font.size":          9,
    "axes.titlesize":     10,
    "axes.labelsize":     9,
    "xtick.labelsize":    8,
    "ytick.labelsize":    8,
    "legend.fontsize":    8,
    "legend.framealpha":  0.85,
    "legend.edgecolor":   "0.8",
    # Lines
    "lines.linewidth":    1.5,
    "lines.markersize":   4,
    # Axes
    "axes.linewidth":     0.8,
    "axes.grid":          True,
    "axes.grid.which":    "both",
    "grid.alpha":         0.35,
    "grid.linewidth":     0.5,
    "grid.linestyle":     "--",
    # Figure
    "figure.dpi":         150,
    "savefig.dpi":        300,
    "savefig.bbox":       "tight",
    "savefig.pad_inches": 0.05,
    # Math text
    "mathtext.fontset":   "cm",
})

# ============================================================
# COLOR PALETTES — IEEE-friendly, colorblind-safe
# ============================================================

SC_COLORS = {
    "S1": "#D62728",   # Red  — Baseline
    "S2": "#9467BD",   # Purple — +BESS Std
    "S3": "#1F77B4",   # Blue  — +BESS VI
    "S4": "#2CA02C",   # Green — +PV&WT+BESS VI
}

SC_LABELS = {
    "S1": "S1: Thermal + Inertia + QSS",
    "S2": "S2: S1 + BESS Std",
    "S3": "S3: S1 + BESS VI",
    "S4": "S4: S3 + PV & WT",
}

# Generator color map (thermal units, stacked)
GEN_COLORS = {
    "G1":  "#AEC6CF",
    "G2":  "#77A8D9",
    "G3":  "#5B9BD5",
    "G4":  "#FFCC80",
    "G5":  "#FFD54F",
    "G6":  "#4472C4",
    "G7":  "#70AD47",
    "G8":  "#ED7D31",
    "G9":  "#FFC000",
    "G10": "#92D050",
    "WT":  "#00B0F0",
    "PV":  "#FF9900",
    "BESS_dis": "#C55A11",
}

THERMAL = [f"G{i}" for i in range(1, 11)]

# ============================================================
# 1. LOAD DATA
# ============================================================

df = {}
for sc in ["S1", "S2", "S3", "S4"]:
    df[sc] = pd.read_excel(DATA_FILE, sheet_name=sc)

T = df["S1"]["Hour"].values   # 1..24

# Summary data
COSTS = {
    "S1": {"fuel": 3656807, "fixed": 584301, "curt": 0,    "total": 4241108},
    "S2": {"fuel": 3652283, "fixed": 584301, "curt": 0,    "total": 4236584},
    "S3": {"fuel": 3638315, "fixed": 581718, "curt": 0,    "total": 4220033},
    "S4": {"fuel": 3413847, "fixed": 581718, "curt": 2285, "total": 3997851},
}

INERTIA_AVG = {sc: df[sc]["Hsys"].mean() for sc in df}
INERTIA_MIN = {sc: df[sc]["Hsys"].min()  for sc in df}

# ============================================================
# HELPER: save figure
# ============================================================

def save_fig(fig, filename, tight=True):
    path = os.path.join(FIG_DIR, filename)
    fig.savefig(path, dpi=300, bbox_inches="tight" if tight else None)
    plt.close(fig)
    print(f"  Saved: {filename}")
    return path

# ============================================================
# FIG 1: COST COMPARISON BAR CHART
# ============================================================

def plot_fig1_cost():
    fig, axes = plt.subplots(1, 2, figsize=(7.16, 3.0))

    scenarios = ["S1", "S2", "S3", "S4"]
    x = np.arange(len(scenarios))
    w = 0.22

    # --- Left: Stacked cost breakdown ---
    ax = axes[0]
    fuel_vals  = [COSTS[s]["fuel"]  / 1e6 for s in scenarios]
    fixed_vals = [COSTS[s]["fixed"] / 1e6 for s in scenarios]
    curt_vals  = [COSTS[s]["curt"]  / 1e6 for s in scenarios]

    bars_fuel  = ax.bar(x, fuel_vals,  color="#4472C4", label="Fuel Cost")
    bars_fixed = ax.bar(x, fixed_vals, bottom=fuel_vals, color="#ED7D31", label="Fixed/No-load Cost")
    bars_curt  = ax.bar(x, curt_vals,
                        bottom=[f + fxd for f, fxd in zip(fuel_vals, fixed_vals)],
                        color="#FF0000", alpha=0.7, label="Curtailment Cost")

    # Annotate total cost
    for i, sc in enumerate(scenarios):
        total = COSTS[sc]["total"] / 1e6
        ax.text(i, total + 0.02, f"${total:.2f}M", ha="center", va="bottom",
                fontsize=7, fontweight="bold",
                color=SC_COLORS[sc])

    ax.set_xticks(x)
    ax.set_xticklabels(scenarios, fontweight="bold")
    ax.set_ylabel("Operating Cost (million USD)")
    ax.set_title("(a) Cost Breakdown by Scenario")
    ax.legend(loc="upper right", fontsize=7)
    ax.set_ylim(0, 5.2)
    ax.yaxis.set_minor_locator(AutoMinorLocator(5))

    # --- Right: Total cost + savings ---
    ax2 = axes[1]
    totals = [COSTS[s]["total"] / 1e6 for s in scenarios]
    clrs   = [SC_COLORS[s] for s in scenarios]
    bars   = ax2.bar(x, totals, color=clrs, width=0.5, edgecolor="k", linewidth=0.5)

    # Annotate savings vs S1
    s1_t = COSTS["S1"]["total"] / 1e6
    for i, sc in enumerate(scenarios):
        tc = COSTS[sc]["total"] / 1e6
        if sc != "S1":
            saving = s1_t - tc
            pct    = saving / s1_t * 100
            ax2.text(i, tc + 0.05, f"-{pct:.2f}%", ha="center", va="bottom",
                     fontsize=7, color="green", fontweight="bold")
        ax2.text(i, tc / 2, f"${tc:.3f}M", ha="center", va="center",
                 fontsize=7, color="white", fontweight="bold")

    ax2.set_xticks(x)
    ax2.set_xticklabels([SC_LABELS[s] for s in scenarios], rotation=12,
                        ha="right", fontsize=7)
    ax2.set_ylabel("Total Operating Cost (million USD)")
    ax2.set_title("(b) Total Cost Comparison")
    ax2.set_ylim(3.7, 4.6)
    ax2.yaxis.set_minor_locator(AutoMinorLocator(5))

    # Reference line S1
    ax2.axhline(y=s1_t, color="red", linestyle="--", linewidth=0.8, alpha=0.7, label=f"S1 baseline")
    ax2.legend(fontsize=7)

    fig.suptitle("Fig. 1: Operating Cost Comparison — 4 FCUC Scenarios",
                 fontsize=9, fontweight="bold", y=1.01)
    plt.tight_layout()
    return save_fig(fig, "fig1_cost_comparison.pdf")


# ============================================================
# FIG 2: GENERATION DISPATCH STACK — S1 (THERMAL BASELINE)
# ============================================================

def plot_fig2_dispatch_s1():
    fig, ax = plt.subplots(figsize=(7.16, 3.2))
    d = df["S1"]
    T_arr = d["Hour"].values

    bottom = np.zeros(len(T_arr))
    for g in THERMAL:
        vals = d[f"{g}_P"].values
        ax.bar(T_arr, vals, bottom=bottom, color=GEN_COLORS[g],
               label=g, width=0.85, edgecolor="none")
        bottom += vals

    # Demand line
    ax.step(T_arr, d["Demand"].values, where="mid",
            color="black", linewidth=1.8, linestyle="-", label="Demand", zorder=5)

    # BESS (zero in S1)
    ax.fill_between(T_arr, 0, 0, color=GEN_COLORS["BESS_dis"], alpha=0.5, label="BESS Dis.")

    ax.set_xlabel("Hour (h)")
    ax.set_ylabel("Power (MW)")
    ax.set_title("Fig. 2: Generation Dispatch — S1: Thermal Only (Baseline)")
    ax.set_xlim(0.5, 24.5)
    ax.set_xticks(range(1, 25))
    ax.set_ylim(0, 6500)
    ax.yaxis.set_minor_locator(MultipleLocator(250))

    # Legend — 2 columns
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels, loc="upper left", ncol=4,
              fontsize=7, handlelength=1.2, columnspacing=0.8)

    plt.tight_layout()
    return save_fig(fig, "fig2_dispatch_S1.pdf")


# ============================================================
# FIG 3: GENERATION DISPATCH STACK — S4 (FULL EBT + BESS VI)
# ============================================================

def plot_fig3_dispatch_s4():
    fig, ax = plt.subplots(figsize=(7.16, 3.2))
    d = df["S4"]
    T_arr = d["Hour"].values

    bottom = np.zeros(len(T_arr))

    # Thermal units
    for g in THERMAL:
        vals = d[f"{g}_P"].values
        ax.bar(T_arr, vals, bottom=bottom, color=GEN_COLORS[g],
               label=g, width=0.85, edgecolor="none")
        bottom += vals

    # BESS discharge
    bess_dis = (d["B1_Pdis"].values + d["B2_Pdis"].values)
    ax.bar(T_arr, bess_dis, bottom=bottom, color=GEN_COLORS["BESS_dis"],
           label="BESS Dis.", width=0.85, alpha=0.85, edgecolor="none")
    bottom += bess_dis

    # WT
    wt_used = d["WT_Used"].values
    ax.bar(T_arr, wt_used, bottom=bottom, color=GEN_COLORS["WT"],
           label="Wind (WT)", width=0.85, alpha=0.90, edgecolor="none")
    bottom += wt_used

    # PV
    pv_used = d["PV_Used"].values
    ax.bar(T_arr, pv_used, bottom=bottom, color=GEN_COLORS["PV"],
           label="Solar (PV)", width=0.85, alpha=0.90, edgecolor="none")

    # Demand line
    ax.step(T_arr, d["Demand"].values, where="mid",
            color="black", linewidth=1.8, linestyle="-", label="Demand", zorder=5)

    # BESS charging (negative bar below axis)
    bess_ch = -(d["B1_Pch"].values + d["B2_Pch"].values)
    ax.bar(T_arr, bess_ch, color=GEN_COLORS["BESS_dis"],
           alpha=0.4, width=0.85, edgecolor="none", label="BESS Chg.")

    ax.set_xlabel("Hour (h)")
    ax.set_ylabel("Power (MW)")
    ax.set_title("Fig. 3: Generation Dispatch — S4: Thermal + BESS VI + PV & WT")
    ax.set_xlim(0.5, 24.5)
    ax.set_xticks(range(1, 25))
    ax.set_ylim(-200, 6500)
    ax.yaxis.set_minor_locator(MultipleLocator(250))
    ax.axhline(0, color="k", linewidth=0.5)

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels, loc="upper left", ncol=4,
              fontsize=7, handlelength=1.2, columnspacing=0.8)

    plt.tight_layout()
    return save_fig(fig, "fig3_dispatch_S4.pdf")


# ============================================================
# FIG 4: UNIT COMMITMENT HEATMAP — ALL 4 SCENARIOS
# ============================================================

def plot_fig4_uc_heatmap():
    fig, axes = plt.subplots(4, 1, figsize=(7.16, 5.5), sharex=True)

    for ax_idx, sc in enumerate(["S1", "S2", "S3", "S4"]):
        ax = axes[ax_idx]
        d  = df[sc]

        # Build UC matrix: rows=generators, cols=hours
        gen_labels = THERMAL + ["BESS B1", "BESS B2"]
        n_gen = len(gen_labels)
        uc_matrix = np.zeros((n_gen, 24))

        for gi, g in enumerate(THERMAL):
            uc_matrix[gi, :] = d[f"{g}_u"].values

        # BESS: show discharge status
        if "B1_Pdis" in d.columns:
            uc_matrix[10, :] = (d["B1_Pdis"].values > 0.01).astype(int)
        if "B2_Pdis" in d.columns:
            uc_matrix[11, :] = (d["B2_Pdis"].values > 0.01).astype(int)

        # Color: ON=blue, OFF=lightgrey, BESS=green
        cmap = matplotlib.colors.ListedColormap(["#E8E8E8", SC_COLORS[sc]])
        ax.imshow(uc_matrix, aspect="auto", cmap=cmap, vmin=0, vmax=1,
                  interpolation="none",
                  extent=[0.5, 24.5, -0.5, n_gen - 0.5])

        ax.set_yticks(range(n_gen))
        ax.set_yticklabels(gen_labels, fontsize=7)
        ax.set_ylabel(sc, fontsize=8, fontweight="bold", rotation=0,
                      labelpad=28, va="center")

        # Hour separators
        for h in range(1, 25):
            ax.axvline(h - 0.5, color="white", linewidth=0.3)

        # ON count
        on_count = uc_matrix[:10, :].sum()
        ax.text(24.6, n_gen / 2, f"{int(on_count)}h", fontsize=7,
                va="center", color=SC_COLORS[sc], fontweight="bold")

    axes[-1].set_xlabel("Hour (h)")
    axes[-1].set_xticks(range(1, 25))

    # Custom legend
    on_patch  = mpatches.Patch(label="ON / Discharging")
    off_patch = mpatches.Patch(color="#E8E8E8", edgecolor="k",
                                linewidth=0.5, label="OFF / Idle")
    fig.legend(handles=[on_patch, off_patch], loc="lower center",
               ncol=2, fontsize=7, bbox_to_anchor=(0.5, -0.01))

    fig.suptitle("Fig. 4: Unit Commitment Status — All 4 Scenarios (24-Hour Horizon)",
                 fontsize=9, fontweight="bold")
    plt.tight_layout(rect=[0, 0.04, 1, 0.97])
    return save_fig(fig, "fig4_uc_heatmap.pdf")


# ============================================================
# FIG 5: BESS DISPATCH & VIRTUAL INERTIA — S3 vs S4
# ============================================================

def plot_fig5_bess_vi():
    fig, axes = plt.subplots(3, 1, figsize=(7.16, 5.5), sharex=True)

    T_arr = df["S3"]["Hour"].values

    # --- (a) BESS Power Dispatch ---
    ax = axes[0]
    d3, d4 = df["S3"], df["S4"]

    # S3 BESS
    s3_dis = d3["B1_Pdis"].values + d3["B2_Pdis"].values
    s3_ch  = -(d3["B1_Pch"].values + d3["B2_Pch"].values)
    s3_vi  = d3["B1_P_VI"].values + d3["B2_P_VI"].values

    # S4 BESS
    s4_dis = d4["B1_Pdis"].values + d4["B2_Pdis"].values
    s4_ch  = -(d4["B1_Pch"].values + d4["B2_Pch"].values)
    s4_vi  = d4["B1_P_VI"].values + d4["B2_P_VI"].values

    ax.bar(T_arr - 0.2, s3_dis, width=0.38, color=SC_COLORS["S3"], alpha=0.85,
           label="S3 BESS Dis.")
    ax.bar(T_arr - 0.2, s3_ch,  width=0.38, color=SC_COLORS["S3"], alpha=0.45,
           label="S3 BESS Chg.")
    ax.bar(T_arr + 0.2, s4_dis, width=0.38, color=SC_COLORS["S4"], alpha=0.85,
           label="S4 BESS Dis.")
    ax.bar(T_arr + 0.2, s4_ch,  width=0.38, color=SC_COLORS["S4"], alpha=0.45,
           label="S4 BESS Chg.")
    ax.axhline(0, color="k", linewidth=0.5)
    ax.set_ylabel("Power (MW)")
    ax.set_title("(a) BESS Active Power Dispatch (B1 + B2 combined)")
    ax.legend(ncol=4, fontsize=7)
    ax.set_ylim(-120, 140)

    # --- (b) Virtual Inertia Power ---
    ax2 = axes[1]
    ax2.bar(T_arr - 0.2, s3_vi, width=0.38, color=SC_COLORS["S3"], alpha=0.85,
            label="S3: $P^{VI}_{BESS}$")
    ax2.bar(T_arr + 0.2, s4_vi, width=0.38, color=SC_COLORS["S4"], alpha=0.85,
            label="S4: $P^{VI}_{BESS}$")
    ax2.set_ylabel("VI Power (MW)")
    ax2.set_title(r"(b) BESS Virtual Inertia Active Power $P^{VI}_{BESS}$")
    ax2.legend(ncol=2, fontsize=7)
    ax2.set_ylim(0, 90)

    # --- (c) Virtual Inertia Contribution to H_sys ---
    ax3 = axes[2]
    s3_h_vi = d3["B1_H_VI"].values + d3["B2_H_VI"].values
    s4_h_vi = d4["B1_H_VI"].values + d4["B2_H_VI"].values

    ax3.fill_between(T_arr, s3_h_vi, step="mid", alpha=0.35,
                     color=SC_COLORS["S3"], label="S3: $H^{VI}_{BESS}$")
    ax3.fill_between(T_arr, s4_h_vi, step="mid", alpha=0.35,
                     color=SC_COLORS["S4"], label="S4: $H^{VI}_{BESS}$")
    ax3.step(T_arr, s3_h_vi, where="mid", color=SC_COLORS["S3"],
             linewidth=1.5, label="_nolegend_")
    ax3.step(T_arr, s4_h_vi, where="mid", color=SC_COLORS["S4"],
             linewidth=1.5, label="_nolegend_")

    ax3.set_xlabel("Hour (h)")
    ax3.set_ylabel("Virtual Inertia (MWs)")
    ax3.set_title(r"(c) BESS Inertia Contribution $H^{VI}_{BESS} = K_b \cdot P^{VI}_{BESS}$")
    ax3.legend(ncol=2, fontsize=7)
    ax3.set_ylim(0, 500)

    axes[-1].set_xticks(range(1, 25))
    axes[-1].set_xlim(0.5, 24.5)

    fig.suptitle("Fig. 5: BESS Virtual Inertia (VI) Operation — S3 vs S4",
                 fontsize=9, fontweight="bold")
    plt.tight_layout()
    return save_fig(fig, "fig5_bess_vi.pdf")


# ============================================================
# FIG 6: SYSTEM INERTIA & ROCOF PROFILE — ALL 4 SCENARIOS
# ============================================================

def plot_fig6_inertia_rocof():
    fig, axes = plt.subplots(3, 1, figsize=(7.16, 5.5), sharex=True)

    T_arr = df["S1"]["Hour"].values

    # --- (a) System Inertia H_sys ---
    ax = axes[0]
    for sc in ["S1", "S2", "S3", "S4"]:
        ax.step(T_arr, df[sc]["Hsys"].values / 1000,  # Convert to GWs
                where="mid",
                color=SC_COLORS[sc], linewidth=1.6,
                label=SC_LABELS[sc],
                linestyle="-" if sc in ["S3", "S4"] else "--")

    ax.set_ylabel("$H_{sys}$ (GWs)")
    ax.set_title("(a) System Inertia $H_{sys}$")
    ax.legend(ncol=2, fontsize=7, loc="lower right")
    ax.set_ylim(41.0, 52.0)
    ax.yaxis.set_minor_locator(AutoMinorLocator(5))

    # --- (b) BESS VI contribution to Hsys ---
    ax2 = axes[1]

    for sc in ["S3", "S4"]:
        d = df[sc]
        h_vi = (d["B1_H_VI"].values + d["B2_H_VI"].values) / 1000
        h_thermal = (d["Hsys"].values - d["B1_H_VI"].values - d["B2_H_VI"].values) / 1000
        T_arr2 = d["Hour"].values

        ax2.fill_between(T_arr2, h_thermal, d["Hsys"].values / 1000,
                         step="mid", alpha=0.4, color=SC_COLORS[sc],
                         label=f"{sc}: $H^{{VI}}_{{BESS}}$")
        ax2.step(T_arr2, d["Hsys"].values / 1000, where="mid",
                 color=SC_COLORS[sc], linewidth=1.3, alpha=0.8)

    # Baseline S1 for reference
    ax2.step(T_arr, df["S1"]["Hsys"].values / 1000, where="mid",
             color=SC_COLORS["S1"], linewidth=1.0, linestyle="--",
             alpha=0.6, label="S1 baseline")

    ax2.set_ylabel("$H_{sys}$ (GWs)")
    ax2.set_title(r"(b) Virtual Inertia Contribution $H^{VI}_{BESS}$ (shaded area)")
    ax2.legend(ncol=3, fontsize=7)
    ax2.set_ylim(41.0, 52.0)

    # --- (c) Estimated RoCoF ---
    ax3 = axes[2]
    for sc in ["S1", "S2", "S3", "S4"]:
        rocof = df[sc]["RoCoF_est"].values
        ax3.step(T_arr, rocof, where="mid",
                 color=SC_COLORS[sc], linewidth=1.5,
                 label=SC_LABELS[sc],
                 linestyle="-" if sc in ["S3", "S4"] else "--")

    ax3.axhline(y=0.55, color="red", linewidth=1.0, linestyle="-.", alpha=0.8,
                label="RoCoF limit = 0.55 Hz/s", zorder=5)
    ax3.set_xlabel("Hour (h)")
    ax3.set_ylabel("RoCoF (Hz/s)")
    ax3.set_title(r"(c) Estimated RoCoF $= \frac{f_0 \cdot P_{loss}}{2 H_{sys}}$")
    ax3.legend(ncol=2, fontsize=7, loc="lower right")
    ax3.set_ylim(0.40, 0.62)
    ax3.yaxis.set_minor_locator(AutoMinorLocator(5))

    axes[-1].set_xticks(range(1, 25))
    axes[-1].set_xlim(0.5, 24.5)

    fig.suptitle("Fig. 6: System Inertia and Estimated RoCoF — 4 Scenarios",
                 fontsize=9, fontweight="bold")
    plt.tight_layout()
    return save_fig(fig, "fig6_inertia_rocof.pdf")


# ============================================================
# FIG 7: FREQUENCY SECURITY METRICS — S3 vs S4
# ============================================================

def plot_fig7_freq_security():
    fig, axes = plt.subplots(2, 2, figsize=(7.16, 5.0))

    T_arr = df["S3"]["Hour"].values
    d3, d4 = df["S3"], df["S4"]

    # --- (a) H_sys comparison ---
    ax = axes[0, 0]
    ax.step(T_arr, d3["Hsys"].values / 1000, where="mid",
            color=SC_COLORS["S3"], linewidth=1.8, label="S3 (BESS VI, no EBT)")
    ax.step(T_arr, d4["Hsys"].values / 1000, where="mid",
            color=SC_COLORS["S4"], linewidth=1.8, linestyle="--",
            label="S4 (BESS VI + PV & WT)")
    # Shade difference
    ax.fill_between(T_arr,
                    d3["Hsys"].values / 1000,
                    d4["Hsys"].values / 1000,
                    step="mid", alpha=0.2, color="purple",
                    label=r"$\Delta H_{sys}$")
    ax.set_title(r"(a) $H_{sys}$ — S3 vs S4")
    ax.set_ylabel("$H_{sys}$ (GWs)")
    ax.legend(fontsize=7)
    ax.set_ylim(40.5, 52.0)

    # --- (b) Largest Loss (LargestLoss[t]) ---
    ax2 = axes[0, 1]
    ax2.step(T_arr, d3["LargestLoss"].values, where="mid",
             color=SC_COLORS["S3"], linewidth=1.8, label="S3")
    ax2.step(T_arr, d4["LargestLoss"].values, where="mid",
             color=SC_COLORS["S4"], linewidth=1.8, linestyle="--", label="S4")
    ax2.fill_between(T_arr,
                     d3["LargestLoss"].values,
                     d4["LargestLoss"].values,
                     step="mid", alpha=0.2, color="orange",
                     label=r"$\Delta$ Largest Loss")
    ax2.set_title(r"(b) Largest Online Loss $P^{loss}_{max}$")
    ax2.set_ylabel("Power (MW)")
    ax2.legend(fontsize=7)

    # --- (c) Total PFR ---
    ax3 = axes[1, 0]
    ax3.step(T_arr, d3["TotalPFR"].values, where="mid",
             color=SC_COLORS["S3"], linewidth=1.8, label="S3: TotalPFR")
    ax3.step(T_arr, d4["TotalPFR"].values, where="mid",
             color=SC_COLORS["S4"], linewidth=1.8, linestyle="--", label="S4: TotalPFR")
    ax3.set_title("(c) Total Primary Frequency Response (PFR)")
    ax3.set_ylabel("TotalPFR (MW)")
    ax3.set_xlabel("Hour (h)")
    ax3.legend(fontsize=7)

    # --- (d) f_QSS estimate ---
    ax4 = axes[1, 1]
    ax4.step(T_arr, d3["f_qss_est"].values, where="mid",
             color=SC_COLORS["S3"], linewidth=1.8, label="S3: $f_{QSS}$")
    ax4.step(T_arr, d4["f_qss_est"].values, where="mid",
             color=SC_COLORS["S4"], linewidth=1.8, linestyle="--", label="S4: $f_{QSS}$")
    ax4.axhline(y=49.5, color="red", linewidth=1.0, linestyle="-.",
                alpha=0.8, label="Limit = 49.5 Hz")
    ax4.axhline(y=49.0, color="darkred", linewidth=0.8, linestyle=":",
                alpha=0.6, label="UFLS = 49.0 Hz")
    ax4.set_title(r"(d) Estimated QSS Frequency $f_{QSS}$")
    ax4.set_ylabel("Frequency (Hz)")
    ax4.set_xlabel("Hour (h)")
    ax4.legend(fontsize=7)
    ax4.set_ylim(49.0, 50.2)

    for ax_row in axes:
        for ax_ in ax_row:
            ax_.set_xticks(range(1, 25, 2))
            ax_.set_xlim(0.5, 24.5)
            ax_.xaxis.set_minor_locator(MultipleLocator(1))

    fig.suptitle("Fig. 7: Frequency Security Metrics — S3 vs S4 Comparison",
                 fontsize=9, fontweight="bold")
    plt.tight_layout()
    return save_fig(fig, "fig7_freq_security_S3vsS4.pdf")


# ============================================================
# FIG 8: WT/PV ENERGY & CURTAILMENT — S4
# ============================================================

def plot_fig8_curtailment():
    fig, axes = plt.subplots(2, 1, figsize=(7.16, 5.0), sharex=True)

    T_arr = df["S4"]["Hour"].values
    d4    = df["S4"]

    # --- (a) Energy composition (stacked area) ---
    ax = axes[0]

    thermal_s4 = d4["Total_Thermal"].values
    bess_dis_s4 = d4["B1_Pdis"].values + d4["B2_Pdis"].values
    bess_ch_s4  = d4["B1_Pch"].values  + d4["B2_Pch"].values
    wt_used_s4  = d4["WT_Used"].values
    pv_used_s4  = d4["PV_Used"].values
    wt_avail_s4 = d4["WT_Available"].values
    pv_avail_s4 = d4["PV_Available"].values

    # Stack
    b1 = thermal_s4
    ax.bar(T_arr, thermal_s4, color="#4472C4", alpha=0.85, width=0.85,
           label="Thermal", edgecolor="none")

    b2 = b1 + bess_dis_s4
    ax.bar(T_arr, bess_dis_s4, bottom=b1, color=GEN_COLORS["BESS_dis"],
           alpha=0.85, width=0.85, label="BESS Discharge", edgecolor="none")

    b3 = b2 + wt_used_s4
    ax.bar(T_arr, wt_used_s4, bottom=b2, color=GEN_COLORS["WT"],
           alpha=0.90, width=0.85, label="Wind (WT) Used", edgecolor="none")

    b4 = b3 + pv_used_s4
    ax.bar(T_arr, pv_used_s4, bottom=b3, color=GEN_COLORS["PV"],
           alpha=0.90, width=0.85, label="Solar (PV) Used", edgecolor="none")

    # Curtailed WT (hatched)
    wt_curt = d4["WT_Curtailment"].values
    pv_curt = d4["PV_Curtailment"].values
    ax.bar(T_arr, wt_curt, bottom=b4, color=GEN_COLORS["WT"],
           alpha=0.4, width=0.85, hatch="//", edgecolor=GEN_COLORS["WT"],
           linewidth=0.5, label="WT Curtailed")
    ax.bar(T_arr, pv_curt, bottom=b4 + wt_curt, color=GEN_COLORS["PV"],
           alpha=0.4, width=0.85, hatch="\\\\", edgecolor=GEN_COLORS["PV"],
           linewidth=0.5, label="PV Curtailed")

    # Demand
    ax.step(T_arr, d4["Demand"].values, where="mid",
            color="black", linewidth=1.8, label="Demand")

    # BESS charging
    ax.bar(T_arr, -bess_ch_s4, color=GEN_COLORS["BESS_dis"],
           alpha=0.4, width=0.85, edgecolor="none", label="BESS Charging")

    ax.axhline(0, color="k", linewidth=0.4)
    ax.set_ylabel("Power (MW)")
    ax.set_title("(a) S4 Energy Composition with WT/PV Curtailment")
    ax.legend(ncol=4, fontsize=7, loc="upper left")
    ax.set_ylim(-200, 6500)

    # --- (b) WT Available vs Used vs Curtailed ---
    ax2 = axes[1]

    ax2.fill_between(T_arr, 0, wt_avail_s4, step="mid",
                     alpha=0.15, color=GEN_COLORS["WT"], label="WT Available")
    ax2.step(T_arr, wt_avail_s4, where="mid",
             color=GEN_COLORS["WT"], linewidth=1.2, linestyle="--",
             label="WT Available")
    ax2.step(T_arr, wt_used_s4, where="mid",
             color=SC_COLORS["S4"], linewidth=1.8,
             label="WT Dispatched")
    ax2.fill_between(T_arr, wt_used_s4, wt_avail_s4, step="mid",
                     alpha=0.35, color="red", label="WT Curtailed")

    ax2.step(T_arr, pv_avail_s4, where="mid",
             color=GEN_COLORS["PV"], linewidth=1.2, linestyle="--",
             label="PV Available")
    ax2.step(T_arr, pv_used_s4, where="mid",
             color="#FF6600", linewidth=1.8,
             label="PV Dispatched")

    ax2.set_xlabel("Hour (h)")
    ax2.set_ylabel("Power (MW)")
    ax2.set_title("(b) WT & PV: Available vs. Dispatched (Curtailment = shaded red)")
    ax2.legend(ncol=3, fontsize=7)
    ax2.set_ylim(0, 500)

    axes[-1].set_xticks(range(1, 25))
    axes[-1].set_xlim(0.5, 24.5)

    # Annotate curtailment at t=1
    ax2.annotate(f"WT Curt.\n76.2 MWh\n(t=1)",
                 xy=(1, (wt_used_s4[0] + wt_avail_s4[0]) / 2),
                 xytext=(3.5, 370),
                 fontsize=7, color="red",
                 arrowprops=dict(arrowstyle="->", color="red", lw=0.8))

    fig.suptitle("Fig. 8: WT/PV Energy Dispatch and Curtailment — Scenario S4",
                 fontsize=9, fontweight="bold")
    plt.tight_layout()
    return save_fig(fig, "fig8_curtailment_S4.pdf")


# ============================================================
# FIG 9: COMPARATIVE SUMMARY — SOC PROFILE BESS
# ============================================================

def plot_fig9_soc_profile():
    fig, axes = plt.subplots(2, 1, figsize=(7.16, 4.5), sharex=True)

    T_arr = df["S3"]["Hour"].values

    BATT_COLORS = {"B1": "#1F77B4", "B2": "#FF7F0E"}

    for ai, sc in enumerate(["S3", "S4"]):
        ax = axes[ai]
        d  = df[sc]

        for b, bc in BATT_COLORS.items():
            soc = d[f"{b}_SOC"].values
            ax.fill_between(T_arr, 0, soc, step="mid", alpha=0.20, color=bc)
            ax.step(T_arr, soc, where="mid", color=bc, linewidth=1.8,
                    label=f"{b} SOC")

            # VI power on secondary axis
            vi = d[f"{b}_P_VI"].values
            ax_twin = ax.twinx()
            ax_twin.step(T_arr, vi, where="mid", color=bc, linewidth=1.0,
                         linestyle=":", alpha=0.7, label=f"{b} $P^{{VI}}$")
            ax_twin.set_ylabel("$P^{VI}$ (MW)", fontsize=7)
            ax_twin.set_ylim(0, 80)
            ax_twin.tick_params(axis="y", labelsize=7)

        # SOC limits
        ax.axhline(y=155, color="gray", linewidth=0.8, linestyle="--",
                   alpha=0.6, label="SOC$_{max}$ B1")
        ax.axhline(y=15.5, color="gray", linewidth=0.8, linestyle=":",
                   alpha=0.6, label="SOC$_{min}$ B1")

        ax.set_ylabel("State of Charge (MWh)")
        ax.set_title(f"({chr(97+ai)}) {sc}: BESS SOC and Virtual Inertia Power")
        ax.legend(fontsize=7, loc="upper left")
        ax.set_ylim(0, 200)

    axes[-1].set_xlabel("Hour (h)")
    axes[-1].set_xticks(range(1, 25))
    axes[-1].set_xlim(0.5, 24.5)

    fig.suptitle("Fig. 9: BESS State of Charge and Virtual Inertia Power — S3 vs S4",
                 fontsize=9, fontweight="bold")
    plt.tight_layout()
    return save_fig(fig, "fig9_bess_soc_vi.pdf")


# ============================================================
# FIG 10: SPINNING RESERVE PROFILE — S1 vs S3 vs S4
# ============================================================

def plot_fig10_reserve():
    fig, axes = plt.subplots(2, 1, figsize=(7.16, 4.5), sharex=True)

    T_arr = df["S1"]["Hour"].values

    # --- (a) Total Spinning Reserve ---
    ax = axes[0]
    for sc in ["S1", "S3", "S4"]:
        d = df[sc]
        total_res = sum(d[f"{g}_R"].values for g in THERMAL)
        ax.step(T_arr, total_res, where="mid",
                color=SC_COLORS[sc], linewidth=1.6,
                label=SC_LABELS[sc],
                linestyle="-" if sc in ["S3", "S4"] else "--")

    # Demand reference (LargestLoss)
    ax.step(T_arr, df["S1"]["LargestLoss"].values, where="mid",
            color="black", linewidth=1.0, linestyle="-.",
            alpha=0.7, label="LargestLoss (N-1)")

    ax.set_ylabel("Spinning Reserve (MW)")
    ax.set_title("(a) Total Spinning Reserve vs. N-1 Largest Loss")
    ax.legend(ncol=2, fontsize=7)

    # --- (b) Reserve margin per generator (S4) ---
    ax2 = axes[1]
    d4 = df["S4"]
    bottom = np.zeros(24)
    for g in THERMAL:
        res = d4[f"{g}_R"].values
        ax2.bar(T_arr, res, bottom=bottom, color=GEN_COLORS[g],
                width=0.85, label=g, edgecolor="none", alpha=0.85)
        bottom += res

    # Demand
    ax2.step(T_arr, d4["LargestLoss"].values, where="mid",
             color="red", linewidth=1.5, linestyle="-.", label="LargestLoss")

    ax2.set_xlabel("Hour (h)")
    ax2.set_ylabel("Spinning Reserve (MW)")
    ax2.set_title("(b) Reserve Contribution by Unit — S4")
    ax2.legend(ncol=5, fontsize=7)

    axes[-1].set_xticks(range(1, 25))
    axes[-1].set_xlim(0.5, 24.5)

    fig.suptitle("Fig. 10: Spinning Reserve Profile — Comparison",
                 fontsize=9, fontweight="bold")
    plt.tight_layout()
    return save_fig(fig, "fig10_reserve_profile.pdf")


# ============================================================
# MAIN: RUN ALL FIGURES
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("  TAHAP 3: IEEE PUBLICATION FIGURES (300 DPI)")
    print(f"  Output folder: {FIG_DIR}")
    print("=" * 60 + "\n")

    figures = [
        ("Fig 1: Cost Comparison",          plot_fig1_cost),
        ("Fig 2: Dispatch S1 (Baseline)",   plot_fig2_dispatch_s1),
        ("Fig 3: Dispatch S4 (Full EBT)",   plot_fig3_dispatch_s4),
        ("Fig 4: UC Heatmap",               plot_fig4_uc_heatmap),
        ("Fig 5: BESS VI Dispatch",         plot_fig5_bess_vi),
        ("Fig 6: Inertia & RoCoF Profile",  plot_fig6_inertia_rocof),
        ("Fig 7: Freq Security S3 vs S4",   plot_fig7_freq_security),
        ("Fig 8: Curtailment Analysis S4",  plot_fig8_curtailment),
        ("Fig 9: BESS SOC & VI Power",      plot_fig9_soc_profile),
        ("Fig 10: Spinning Reserve",        plot_fig10_reserve),
    ]

    generated = []
    failed    = []

    for name, func in figures:
        print(f"  Generating {name}...", end=" ", flush=True)
        try:
            path = func()
            generated.append((name, path))
            print("OK")
        except Exception as e:
            failed.append((name, str(e)))
            print(f"FAILED: {e}")

    print(f"\n{'='*60}")
    print(f"  SELESAI: {len(generated)}/{len(figures)} figures berhasil")
    if failed:
        print(f"  GAGAL ({len(failed)}):")
        for n, e in failed:
            print(f"    - {n}: {e}")
    print(f"  Output: {FIG_DIR}")
    print("=" * 60)
