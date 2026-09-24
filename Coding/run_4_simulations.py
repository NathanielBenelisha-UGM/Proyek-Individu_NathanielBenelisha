
# ============================================================
# run_4_simulations.py  (v2 - faithful to notebook)
# Frequency-Constrained Unit Commitment (FCUC)
# 4-Scenario MILP Simulation using CPLEX Direct
#
# Skenario:
#   S1: UC + Inersia Minimum + QSS (Thermal Only)
#   S2: S1 + BESS Standard (tanpa VI)
#   S3: S1 + BESS Virtual Inertia (tanpa PV-WT)
#   S4: S3 + PV & WT sebagai pengotor (dengan curtailment cost)
#
# Solver: IBM ILOG CPLEX 22.1.1 (cplex_direct)
# Referensi: Coba_16_20260612_R00_vinertia_cplexdirect_FULL_EXECUTED.ipynb
# ============================================================

import os
import sys
import time
import pandas as pd
import numpy as np

from pyomo.environ import (
    ConcreteModel, Set, Param, Var,
    Constraint, Objective, Expression,
    NonNegativeReals, Binary, Reals,
    SolverFactory, minimize, value
)
from pyomo.opt import SolverStatus, TerminationCondition

# ============================================================
# 0. VERIFY CPLEX AVAILABILITY
# ============================================================

try:
    import cplex
    print(f"CPLEX Version: {cplex.__version__}")
except ImportError:
    print("[ERROR] cplex Python package not found!")
    sys.exit(1)

solver_test = SolverFactory("cplex_direct")
if not solver_test.available():
    print("[ERROR] cplex_direct solver tidak tersedia!")
    sys.exit(1)
print("CPLEX Direct: OK\n")

# ============================================================
# 1. GLOBAL FREQUENCY PARAMETERS
# ============================================================

f0           = 50.0     # Frekuensi nominal (Hz)
f_min        = 49.0     # Batas minimum UFLS (Hz)
f_qss_min    = 49.5     # Batas QSS minimum (Hz)
df_max       = f0 - f_min     # 1.0 Hz — digunakan di QSS constraint
D_frac       = 0.01           # Damping coefficient
RoCoF_limit  = 0.55           # Hz/s

# ============================================================
# 2. CURTAILMENT COST
# ============================================================
C_curt_WT = 30.0   # $/MWh
C_curt_PV = 30.0   # $/MWh

# ============================================================
# 3. READ DATA FROM EXCEL
# ============================================================

FILE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "DataSet_ModifikasiCandra_R02.xlsx"
)

print(f"Membaca data dari: {FILE_PATH}")
gen_df       = pd.read_excel(FILE_PATH, sheet_name="Gen")
demand_df    = pd.read_excel(FILE_PATH, sheet_name="Demand")
battery_df   = pd.read_excel(FILE_PATH, sheet_name="Battery")
wt_df        = pd.read_excel(FILE_PATH, sheet_name="WT")
potential_df = pd.read_excel(FILE_PATH, sheet_name="Potential")

print(f"  Generator units : {len(gen_df)}")
print(f"  Time periods    : {len(demand_df)}")
print(f"  Battery units   : {len(battery_df)}")
print(f"  Wind farms      : {len(wt_df)}\n")

# ============================================================
# 4. CONVERT DATAFRAME TO DICTIONARIES
# ============================================================

G = gen_df["Unit"].tolist()
T = demand_df["Hour"].tolist()

Pmin          = dict(zip(gen_df["Unit"], gen_df["Pmin"]))
Pmax          = dict(zip(gen_df["Unit"], gen_df["Pmax"]))
a_coef        = dict(zip(gen_df["Unit"], gen_df["a"]))
b_coef        = dict(zip(gen_df["Unit"], gen_df["b"]))
c_coef        = dict(zip(gen_df["Unit"], gen_df["c"]))
SU_cost       = dict(zip(gen_df["Unit"], gen_df["SU_Cost"]))
SD_cost       = dict(zip(gen_df["Unit"], gen_df["SD_Cost"]))
RampUp        = dict(zip(gen_df["Unit"], gen_df["Ramp_Up"]))
RampDown      = dict(zip(gen_df["Unit"], gen_df["Ramp_Down"]))
MinUp         = dict(zip(gen_df["Unit"], gen_df["Min_Up"]))
MinDown       = dict(zip(gen_df["Unit"], gen_df["Min_Down"]))
Droop         = dict(zip(gen_df["Unit"], gen_df["Droop"]))
PFR_Fraction  = dict(zip(gen_df["Unit"], gen_df["PFR_Fraction"]))
FreeGovernor  = dict(zip(gen_df["Unit"], gen_df["FreeGovernor"]))
PrimRampUp    = dict(zip(gen_df["Unit"], gen_df["PrimRampUp"]))
Type          = dict(zip(gen_df["Unit"], gen_df["Type"]))
H             = dict(zip(gen_df["Unit"], gen_df["H"]))
Tg            = dict(zip(gen_df["Unit"], gen_df["Tg"]))
InitialStatus = dict(zip(gen_df["Unit"], gen_df["InitialStatus"]))
InitialPower  = dict(zip(gen_df["Unit"], gen_df["InitialPower"]))
PrevUpTime    = dict(zip(gen_df["Unit"], gen_df["PrevUpTime"]))
PrevDownTime  = dict(zip(gen_df["Unit"], gen_df["PrevDownTime"]))
FreqDeadBand  = dict(zip(gen_df["Unit"], gen_df["FreqDeadBand"]))
GovRamp       = dict(zip(gen_df["Unit"], gen_df["GovRamp(MW/s)"]))
PrimResCost   = dict(zip(gen_df["Unit"], gen_df["PrimResCost"]))

Demand        = dict(zip(demand_df["Hour"], demand_df["Demand"]))
PV_Potential  = dict(zip(demand_df["Hour"], demand_df["Potensi PV (MW)"]))

BATT          = battery_df["Batt"].astype(str).tolist()
SOC_Max       = dict(zip(BATT, battery_df["SOC_Max"].astype(float)))
SOC_Min       = dict(zip(BATT, battery_df["SOC_Min"].astype(float)))
CR_Max        = dict(zip(BATT, battery_df["CR_Max"].astype(float)))
DR_Max        = dict(zip(BATT, battery_df["DR_Max"].astype(float)))
Charge_Eff    = dict(zip(BATT, battery_df["Charge_Eff"].astype(float)))
Discharge_Eff = dict(zip(BATT, battery_df["Discharge_Eff"].astype(float)))
InitialSOC    = dict(zip(BATT, battery_df["InitialSOC"].astype(float)))
FinalSOC      = dict(zip(BATT, battery_df["FinalSOC"].astype(float)))
Kb_VI         = dict(zip(BATT, battery_df["Kb_VI"].astype(float)))
Eff_VI        = dict(zip(BATT, battery_df["Eff_VI"].astype(float)))

WT            = wt_df["Wind"].astype(str).tolist()
WT_Num        = dict(zip(wt_df["Wind"].astype(str), wt_df["WT_Num"].astype(float)))
WT_Rated      = dict(zip(wt_df["Wind"].astype(str), wt_df["WT_Rated"].astype(float)))
WT_pu         = dict(zip(potential_df["Hour"], potential_df["WT_pu"].astype(float)))
Kw_VI         = dict(zip(WT, wt_df["Kw_VI"].astype(float)))
Effw_VI       = dict(zip(WT, wt_df["Effw_VI"].astype(float)))

WT_Available = {}
for w in WT:
    for t in T:
        WT_Available[w, t] = WT_Num[w] * WT_Rated[w] * WT_pu[t]

# ============================================================
# 5. DERIVED PARAMETERS
# ============================================================

PFR_Max     = {g: PFR_Fraction[g] * Pmax[g] for g in G}
ReserveCost = {g: 0.0 for g in G}

# ============================================================
# 6. SCENARIO DEFINITIONS
# ============================================================
# Note: Mengikuti CONFIG yang berhasil di notebook FULL_EXECUTED.
# Key: TotalPFR = sum(R[g,t]) dari spinning reserve (bukan variabel R_pfr).
# QSS constraint: LargestLoss <= (f0-f_min) * (D_frac*Demand + TotalPFR)
# Ini sama dengan batas nadir 49 Hz, bukan 49.5 Hz, tapi sesuai notebook.

BASE_CONFIG = {
    # Solver
    "solver": "cplex_direct",
    "tee": False,
    "mipgap": 0.001,
    "timelimit": 600,

    # Objective
    "obj_generation_cost": True,
    "obj_fixed_cost": True,
    "obj_startup_cost": True,
    "obj_shutdown_cost": True,
    "obj_reserve_cost": False,
    "obj_curtailment_cost": False,

    # UC Classic constraints
    "con_power_balance": True,
    "con_capacity_upper": True,
    "con_capacity_lower": True,
    "con_startup_shutdown_logic": True,
    "con_ramp_up": True,
    "con_ramp_down": True,
    "con_minimum_up_time": True,
    "con_minimum_down_time": True,
    "con_n1_spinning_reserve": True,
    "use_initial_condition": True,

    # FCUC: Inertia constraint (aktif semua skenario)
    "con_min_inertia": True,
    # FCUC: QSS / Primary Frequency Response (aktif semua skenario)
    # Menggunakan spinning reserve R[g,t] sebagai TotalPFR
    "con_qss_limit": True,

    # PFR sub-constraints: OFF sesuai notebook yang berhasil
    # (PFR sudah tercakup dalam spinning reserve + N-1 requirement)
    "con_pfr_within_reserve": False,
    "con_pfr_governor_only": False,
    "con_pfr_headroom": False,
    "con_pfr_ramp_capability": False,

    # Reserve settings
    "pfr_response_time": 10.0 / 60.0,
    "reserve_response_time": 60.0 / 60.0,

    # BESS & renewables (default off, ditimpa per skenario)
    "con_battery": False,
    "con_battery_vi": False,
    "con_wt": False,
    "con_wt_vi": False,
    "con_wt_curtailment": False,
    "con_pv": False,
    "con_pv_curtailment": False,
}

SCENARIOS = {
    "S1": {
        **BASE_CONFIG,
        "name": "S1: UC + Inersia Minimum + QSS (Thermal Only)",
        # Semua BESS/WT/PV off
    },
    "S2": {
        **BASE_CONFIG,
        "name": "S2: S1 + BESS Standard (tanpa Virtual Inertia)",
        "con_battery": True,
        "con_battery_vi": False,
    },
    "S3": {
        **BASE_CONFIG,
        "name": "S3: S1 + BESS Virtual Inertia (tanpa PV-WT)",
        "con_battery": True,
        "con_battery_vi": True,
    },
    "S4": {
        **BASE_CONFIG,
        "name": "S4: S3 + PV & WT sebagai Pengotor (dengan Curtailment Cost)",
        "con_battery": True,
        "con_battery_vi": True,
        "con_wt": True,
        "con_wt_vi": False,           # WT murni sebagai pengotor (zero inertia)
        "con_wt_curtailment": True,
        "con_pv": True,
        "con_pv_curtailment": True,
        "obj_curtailment_cost": True,
    },
}

# ============================================================
# 7. BUILD PYOMO MODEL
# ============================================================

def build_model(CONFIG):
    """Membangun model Pyomo FCUC berdasarkan CONFIG."""

    model = ConcreteModel()

    # ----------------------------------------------------------
    # SETS
    # ----------------------------------------------------------
    model.G    = Set(initialize=G)
    model.T    = Set(initialize=T, ordered=True)
    model.BATT = Set(initialize=BATT)
    model.WT   = Set(initialize=WT)

    # ----------------------------------------------------------
    # GENERATOR PARAMETERS
    # ----------------------------------------------------------
    model.Pmin         = Param(model.G, initialize=Pmin)
    model.Pmax         = Param(model.G, initialize=Pmax)
    model.a            = Param(model.G, initialize=a_coef)
    model.b            = Param(model.G, initialize=b_coef)
    model.c            = Param(model.G, initialize=c_coef)
    model.SU_cost      = Param(model.G, initialize=SU_cost)
    model.SD_cost      = Param(model.G, initialize=SD_cost)
    model.RampUp       = Param(model.G, initialize=RampUp)
    model.RampDown     = Param(model.G, initialize=RampDown)
    model.MinUp        = Param(model.G, initialize=MinUp)
    model.MinDown      = Param(model.G, initialize=MinDown)
    model.Droop        = Param(model.G, initialize=Droop)
    model.PFR_Fraction = Param(model.G, initialize=PFR_Fraction)
    model.PFR_Max      = Param(model.G, initialize=PFR_Max)
    model.FreeGovernor = Param(model.G, initialize=FreeGovernor)
    model.H            = Param(model.G, initialize=H)
    model.Tg           = Param(model.G, initialize=Tg)
    model.InitialStatus = Param(model.G, initialize=InitialStatus)
    model.InitialPower  = Param(model.G, initialize=InitialPower)
    model.PrevUpTime    = Param(model.G, initialize=PrevUpTime)
    model.PrevDownTime  = Param(model.G, initialize=PrevDownTime)
    model.Demand       = Param(model.T, initialize=Demand)
    model.PV_Potential = Param(model.T, initialize=PV_Potential)

    # ----------------------------------------------------------
    # BATTERY PARAMETERS
    # ----------------------------------------------------------
    model.SOC_max      = Param(model.BATT, initialize=SOC_Max)
    model.SOC_min      = Param(model.BATT, initialize=SOC_Min)
    model.CR_max       = Param(model.BATT, initialize=CR_Max)
    model.DR_max       = Param(model.BATT, initialize=DR_Max)
    model.eta_ch       = Param(model.BATT, initialize=Charge_Eff)
    model.eta_dis      = Param(model.BATT, initialize=Discharge_Eff)
    model.SOC_init     = Param(model.BATT, initialize=InitialSOC)
    model.SOC_final    = Param(model.BATT, initialize=FinalSOC)
    model.Kb_VI        = Param(model.BATT, initialize=Kb_VI, within=NonNegativeReals)
    model.Eff_VI       = Param(model.BATT, initialize=Eff_VI, within=NonNegativeReals)
    model.Kw_VI        = Param(model.WT, initialize=Kw_VI, within=NonNegativeReals)
    model.Effw_VI      = Param(model.WT, initialize=Effw_VI, within=NonNegativeReals)
    model.WT_Available = Param(model.WT, model.T, initialize=WT_Available)

    # ----------------------------------------------------------
    # DECISION VARIABLES
    # ----------------------------------------------------------
    model.P    = Var(model.G, model.T, domain=NonNegativeReals)
    model.u    = Var(model.G, model.T, domain=Binary)
    model.y    = Var(model.G, model.T, domain=Binary)
    model.z    = Var(model.G, model.T, domain=Binary)
    model.R    = Var(model.G, model.T, within=NonNegativeReals)   # spinning reserve
    model.Curt = Var(model.G, model.T, within=NonNegativeReals)   # curtailment generic

    # Largest contingency loss variable
    model.LargestLoss = Var(model.T, within=NonNegativeReals)

    # BESS variables
    model.ChargeStatus    = Var(model.BATT, model.T, within=Binary)
    model.DischargeStatus = Var(model.BATT, model.T, within=Binary)
    model.P_charge        = Var(model.BATT, model.T, within=NonNegativeReals)
    model.P_discharge     = Var(model.BATT, model.T, within=NonNegativeReals)
    model.SOC             = Var(model.BATT, model.T, within=NonNegativeReals)
    model.P_VI_batt       = Var(model.BATT, model.T, within=NonNegativeReals)

    # WT variables
    model.WT_Curt = Var(model.WT, model.T, within=NonNegativeReals)
    model.P_VI_wt = Var(model.WT, model.T, within=NonNegativeReals)

    # PV curtailment (satu nilai per jam, bersama semua PV unit)
    model.PV_Curt = Var(model.T, within=NonNegativeReals)

    # ----------------------------------------------------------
    # FREQUENCY EXPRESSIONS
    # ----------------------------------------------------------

    # 12.1 Total System Inertia (MWs)
    # Inersia thermal (dari unit yang ON) + VI dari BESS
    def hsys_rule(m, t):
        h_thermal = sum(
            m.H[g] * m.Pmax[g] * m.u[g, t]
            for g in m.G
            if Type[g] not in ["PV", "WT"]
        )
        h_batt_vi = (
            sum(m.Kb_VI[b] * m.P_VI_batt[b, t] for b in m.BATT)
            if CONFIG["con_battery_vi"]
            else 0.0
        )
        return h_thermal + h_batt_vi

    model.Hsys = Expression(model.T, rule=hsys_rule)

    # 12.2 Largest Online Contingency (MW)
    def largest_loss_rule(m, g, t):
        if Type[g] in ["PV", "WT"]:
            return Constraint.Skip
        return m.LargestLoss[t] >= m.P[g, t]

    model.LargestLossConstraint = Constraint(model.G, model.T, rule=largest_loss_rule)

    # 12.3 Total PFR = sum of spinning reserve R[g,t] dari unit thermal
    # (Consistent dengan notebook: TotalPFR = sum R[g,t])
    def total_pfr_rule(m, t):
        return sum(
            m.R[g, t]
            for g in m.G
            if Type[g] not in ["PV", "WT"]
        )

    model.TotalPFR = Expression(model.T, rule=total_pfr_rule)

    # ----------------------------------------------------------
    # OBJECTIVE FUNCTION
    # ----------------------------------------------------------
    def obj_rule(m):
        cost = 0.0
        if CONFIG["obj_generation_cost"]:
            cost += sum(m.b[g] * m.P[g, t] for g in m.G for t in m.T)
        if CONFIG["obj_fixed_cost"]:
            cost += sum(m.c[g] * m.u[g, t] for g in m.G for t in m.T)
        if CONFIG["obj_startup_cost"]:
            cost += sum(m.SU_cost[g] * m.y[g, t] for g in m.G for t in m.T)
        if CONFIG["obj_shutdown_cost"]:
            cost += sum(m.SD_cost[g] * m.z[g, t] for g in m.G for t in m.T)
        # Curtailment cost: hanya S4
        if CONFIG["obj_curtailment_cost"]:
            if CONFIG["con_wt"]:
                cost += C_curt_WT * sum(m.WT_Curt[w, t] for w in m.WT for t in m.T)
            if CONFIG["con_pv"]:
                cost += C_curt_PV * sum(m.PV_Curt[t] for t in m.T)
        return cost

    model.Obj = Objective(rule=obj_rule, sense=minimize)

    # ----------------------------------------------------------
    # 11.1 POWER BALANCE
    # Pgen + WT_net + BESS_net = Demand
    # ----------------------------------------------------------
    if CONFIG["con_power_balance"]:
        def balance_rule(m, t):
            gen_supply = sum(m.P[g, t] for g in m.G)

            wt_supply = 0.0
            if CONFIG["con_wt"]:
                wt_supply = sum(m.WT_Available[w, t] - m.WT_Curt[w, t] for w in m.WT)

            batt_net = 0.0
            if CONFIG["con_battery"]:
                batt_net = sum(
                    m.P_discharge[b, t] - m.P_charge[b, t]
                    for b in m.BATT
                )

            return gen_supply + wt_supply + batt_net == m.Demand[t]

        model.Balance = Constraint(model.T, rule=balance_rule)

    # ----------------------------------------------------------
    # 11.2 CAPACITY UPPER BOUND
    # ----------------------------------------------------------
    if CONFIG["con_capacity_upper"]:
        def max_cap_rule(m, g, t):
            if Type[g] == "PV":
                return m.P[g, t] <= m.PV_Potential[t]
            elif Type[g] == "WT":
                # WT di-handle via WT_Curt di power balance
                return m.P[g, t] == 0
            else:
                return m.P[g, t] <= m.Pmax[g] * m.u[g, t]

        model.MaxCap = Constraint(model.G, model.T, rule=max_cap_rule)

    # ----------------------------------------------------------
    # 11.3 CAPACITY LOWER BOUND
    # ----------------------------------------------------------
    if CONFIG["con_capacity_lower"]:
        def min_cap_rule(m, g, t):
            if Type[g] in ["PV", "WT"]:
                return m.P[g, t] >= 0
            return m.P[g, t] >= m.Pmin[g] * m.u[g, t]

        model.MinCap = Constraint(model.G, model.T, rule=min_cap_rule)

    # ----------------------------------------------------------
    # 11.4 STARTUP/SHUTDOWN LOGIC
    # ----------------------------------------------------------
    if CONFIG["con_startup_shutdown_logic"]:
        T_list = list(model.T)

        def startup_shutdown_rule(m, g, t):
            pos = T_list.index(t)
            if pos == 0:
                if CONFIG["use_initial_condition"]:
                    return m.u[g, t] - InitialStatus[g] == m.y[g, t] - m.z[g, t]
                return Constraint.Skip
            return m.u[g, t] - m.u[g, T_list[pos - 1]] == m.y[g, t] - m.z[g, t]

        model.StartupShutdown = Constraint(model.G, model.T, rule=startup_shutdown_rule)

    # ----------------------------------------------------------
    # 11.5-11.6 RAMP CONSTRAINTS
    # ----------------------------------------------------------
    if CONFIG["con_ramp_up"]:
        T_list = list(model.T)

        def ramp_up_rule(m, g, t):
            if Type[g] in ["PV", "WT"]:
                return Constraint.Skip
            pos = T_list.index(t)
            if pos == 0:
                if CONFIG["use_initial_condition"]:
                    return m.P[g, t] - InitialPower[g] <= m.RampUp[g]
                return Constraint.Skip
            return m.P[g, t] - m.P[g, T_list[pos - 1]] <= m.RampUp[g]

        model.RampUpConstr = Constraint(model.G, model.T, rule=ramp_up_rule)

    if CONFIG["con_ramp_down"]:
        T_list = list(model.T)

        def ramp_down_rule(m, g, t):
            if Type[g] in ["PV", "WT"]:
                return Constraint.Skip
            pos = T_list.index(t)
            if pos == 0:
                if CONFIG["use_initial_condition"]:
                    return InitialPower[g] - m.P[g, t] <= m.RampDown[g]
                return Constraint.Skip
            return m.P[g, T_list[pos - 1]] - m.P[g, t] <= m.RampDown[g]

        model.RampDownConstr = Constraint(model.G, model.T, rule=ramp_down_rule)

    # ----------------------------------------------------------
    # 11.7-11.8 MINIMUM UP/DOWN TIME
    # ----------------------------------------------------------
    if CONFIG["con_minimum_up_time"]:
        T_list = list(model.T)

        def min_up_rule(m, g, t):
            if Type[g] in ["PV", "WT"]:
                return Constraint.Skip
            pos = T_list.index(t)
            min_up = int(MinUp[g])
            window_end = min(pos + min_up - 1, len(T_list) - 1)
            return (
                sum(m.u[g, T_list[k]] for k in range(pos, window_end + 1))
                >= min_up * m.y[g, t]
            )

        model.MinUpTime = Constraint(model.G, model.T, rule=min_up_rule)

    if CONFIG["con_minimum_down_time"]:
        T_list = list(model.T)

        def min_down_rule(m, g, t):
            if Type[g] in ["PV", "WT"]:
                return Constraint.Skip
            pos = T_list.index(t)
            min_dn = int(MinDown[g])
            window_end = min(pos + min_dn - 1, len(T_list) - 1)
            return (
                sum(1 - m.u[g, T_list[k]] for k in range(pos, window_end + 1))
                >= min_dn * m.z[g, t]
            )

        model.MinDownTime = Constraint(model.G, model.T, rule=min_down_rule)

    # ----------------------------------------------------------
    # 11.9 N-1 SPINNING RESERVE
    # Total reserve dari thermal harus >= LargestLoss
    # ----------------------------------------------------------
    if CONFIG["con_n1_spinning_reserve"]:
        def n1_reserve_rule(m, t):
            return (
                sum(m.R[g, t] for g in m.G if Type[g] not in ["PV", "WT"])
                >= m.LargestLoss[t]
            )

        model.N1Reserve = Constraint(model.T, rule=n1_reserve_rule)

        # Reserve headroom: P + R <= Pmax * u
        def reserve_headroom_rule(m, g, t):
            if Type[g] in ["PV", "WT"]:
                return Constraint.Skip
            return m.P[g, t] + m.R[g, t] <= m.Pmax[g] * m.u[g, t]

        model.ReserveHeadroom = Constraint(model.G, model.T, rule=reserve_headroom_rule)

    # ----------------------------------------------------------
    # PV CURTAILMENT CONSTRAINTS
    # ----------------------------------------------------------
    if CONFIG["con_pv"] and CONFIG["con_pv_curtailment"]:
        # PV_Curt <= PV_Potential
        def pv_curt_limit_rule(m, t):
            return m.PV_Curt[t] <= m.PV_Potential[t]

        model.PVCurtailmentLimit = Constraint(model.T, rule=pv_curt_limit_rule)

        # Dispatch PV = PV_Potential - PV_Curt
        def pv_dispatch_rule(m, g, t):
            if Type[g] != "PV":
                return Constraint.Skip
            return m.P[g, t] == m.PV_Potential[t] - m.PV_Curt[t]

        model.PVDispatch = Constraint(model.G, model.T, rule=pv_dispatch_rule)

    else:
        # PV_Curt = 0 jika tidak aktif
        def pv_curt_off_rule(m, t):
            return m.PV_Curt[t] == 0

        model.PVCurtOff = Constraint(model.T, rule=pv_curt_off_rule)

    # ----------------------------------------------------------
    # WT CURTAILMENT CONSTRAINTS
    # ----------------------------------------------------------
    if CONFIG["con_wt"] and CONFIG["con_wt_curtailment"]:
        def wt_curt_limit_rule(m, w, t):
            return m.WT_Curt[w, t] <= m.WT_Available[w, t]

        model.WTCurtailmentLimit = Constraint(model.WT, model.T, rule=wt_curt_limit_rule)

    else:
        # WT_Curt = 0 jika WT tidak aktif
        def wt_curt_off_rule(m, w, t):
            return m.WT_Curt[w, t] == 0

        model.WTCurtOff = Constraint(model.WT, model.T, rule=wt_curt_off_rule)

    # ----------------------------------------------------------
    # BATTERY CONSTRAINTS
    # ----------------------------------------------------------
    if CONFIG["con_battery"]:
        T_list = list(model.T)

        # 1. Charge power limit
        def batt_charge_limit(m, b, t):
            return m.P_charge[b, t] <= m.CR_max[b] * m.ChargeStatus[b, t]

        model.BatteryChargeLimit = Constraint(model.BATT, model.T, rule=batt_charge_limit)

        # 2. Discharge limit + VI coupling constraint
        # P_dis + P_VI/eta_VI <= DR_max * u_dis  (headroom coupling)
        def batt_dis_limit(m, b, t):
            if CONFIG["con_battery_vi"]:
                return (
                    m.P_discharge[b, t] + m.P_VI_batt[b, t] / m.Eff_VI[b]
                    <= m.DR_max[b] * m.DischargeStatus[b, t]
                )
            return m.P_discharge[b, t] <= m.DR_max[b] * m.DischargeStatus[b, t]

        model.BatteryDischargeLimit = Constraint(model.BATT, model.T, rule=batt_dis_limit)

        # 2b. Force P_VI_batt = 0 jika VI tidak aktif
        if not CONFIG["con_battery_vi"]:
            def batt_vi_off(m, b, t):
                return m.P_VI_batt[b, t] == 0

            model.BatteryVIOff = Constraint(model.BATT, model.T, rule=batt_vi_off)

        # 3. No simultaneous charge/discharge
        def batt_no_simul(m, b, t):
            return m.ChargeStatus[b, t] + m.DischargeStatus[b, t] <= 1

        model.BatteryNoSimultaneous = Constraint(model.BATT, model.T, rule=batt_no_simul)

        # 4. SOC dynamics (MWh)
        def batt_soc_rule(m, b, t):
            pos = T_list.index(t)
            if pos == 0:
                return (
                    m.SOC[b, t]
                    == m.SOC_init[b]
                    + m.eta_ch[b] * m.P_charge[b, t]
                    - (1.0 / m.eta_dis[b]) * m.P_discharge[b, t]
                )
            t_prev = T_list[pos - 1]
            return (
                m.SOC[b, t]
                == m.SOC[b, t_prev]
                + m.eta_ch[b] * m.P_charge[b, t]
                - (1.0 / m.eta_dis[b]) * m.P_discharge[b, t]
            )

        model.BatterySOC = Constraint(model.BATT, model.T, rule=batt_soc_rule)

        # 5. Final SOC
        t_last = T_list[-1]

        def batt_final_soc(m, b):
            return m.SOC[b, t_last] == m.SOC_final[b]

        model.BatteryFinalSOC = Constraint(model.BATT, rule=batt_final_soc)

        # 6. SOC bounds
        def batt_soc_min(m, b, t):
            return m.SOC[b, t] >= m.SOC_min[b]

        model.BatterySOCMin = Constraint(model.BATT, model.T, rule=batt_soc_min)

        def batt_soc_max(m, b, t):
            return m.SOC[b, t] <= m.SOC_max[b]

        model.BatterySOCMax = Constraint(model.BATT, model.T, rule=batt_soc_max)

    else:
        # BESS off: semua variabel battery = 0
        model.BattChargeOff = Constraint(model.BATT, model.T,
            rule=lambda m, b, t: m.P_charge[b, t] == 0)
        model.BattDisOff = Constraint(model.BATT, model.T,
            rule=lambda m, b, t: m.P_discharge[b, t] == 0)
        model.BattVIOff = Constraint(model.BATT, model.T,
            rule=lambda m, b, t: m.P_VI_batt[b, t] == 0)
        model.BattCSOff = Constraint(model.BATT, model.T,
            rule=lambda m, b, t: m.ChargeStatus[b, t] == 0)
        model.BattDSOff = Constraint(model.BATT, model.T,
            rule=lambda m, b, t: m.DischargeStatus[b, t] == 0)
        model.SOCFixed = Constraint(model.BATT, model.T,
            rule=lambda m, b, t: m.SOC[b, t] == InitialSOC[b])

    # WT VI off (WT tidak menyediakan VI di model ini)
    model.WTVIOff = Constraint(model.WT, model.T,
        rule=lambda m, w, t: m.P_VI_wt[w, t] == 0)

    # ----------------------------------------------------------
    # FREQUENCY SECURITY CONSTRAINTS
    # ----------------------------------------------------------

    # FCUC-Inertia: 2 * RoCoF_limit * Hsys[t] >= f0 * LargestLoss[t]
    if CONFIG["con_min_inertia"]:
        def min_inertia_rule(m, t):
            return 2 * RoCoF_limit * m.Hsys[t] >= f0 * m.LargestLoss[t]

        model.MinInertiaConstraint = Constraint(model.T, rule=min_inertia_rule)

    # FCUC-QSS: LargestLoss[t] <= (f0-f_min) * (D_frac*Demand[t] + TotalPFR[t])
    # Note: (f0-f_min) = 1.0 Hz — konsisten dengan notebook, berbasis batas nadir
    if CONFIG["con_qss_limit"]:
        def qss_limit_rule(m, t):
            damping_term = D_frac * Demand[t]
            return (
                m.LargestLoss[t]
                <= df_max * (damping_term + m.TotalPFR[t])
            )

        model.QSSLimitConstraint = Constraint(model.T, rule=qss_limit_rule)

    return model


# ============================================================
# 8. SOLVE AND EXTRACT RESULTS
# ============================================================

def solve_scenario(scenario_id, CONFIG):
    """Jalankan satu skenario dan kembalikan hasil."""

    print(f"\n{'='*65}")
    print(f"  SCENARIO {scenario_id}: {CONFIG['name']}")
    print(f"{'='*65}")
    print("  Membangun model Pyomo...")

    t_start = time.time()
    model = build_model(CONFIG)
    t_build = time.time() - t_start
    print(f"  Model dibangun dalam {t_build:.1f} detik.")

    solver = SolverFactory("cplex_direct")
    solver.options["mipgap"]   = CONFIG["mipgap"]
    solver.options["timelimit"] = CONFIG["timelimit"]
    solver.options["threads"]  = 4

    print(f"  Menjalankan solver CPLEX...")
    t_solve_start = time.time()
    results = solver.solve(model, tee=CONFIG["tee"])
    t_solve = time.time() - t_solve_start

    status    = results.solver.status
    term_cond = results.solver.termination_condition

    is_optimal = (
        status == SolverStatus.ok
        and term_cond == TerminationCondition.optimal
    )

    print(f"  Waktu solver    : {t_solve:.1f}s")
    print(f"  Status          : {status}")
    print(f"  Termination     : {term_cond}")
    print(f"  Hasil           : {'OPTIMAL OK' if is_optimal else 'TIDAK OPTIMAL'}")

    if not is_optimal:
        return {
            "scenario_id": scenario_id, "name": CONFIG["name"],
            "status": str(term_cond), "is_optimal": False,
            "solve_time": t_solve, "df_hourly": None,
            "total_cost": 0.0, "fuel_cost": 0.0, "fixed_cost": 0.0,
            "startup_cost": 0.0, "shutdown_cost": 0.0, "curtailment_cost": 0.0,
            "curt_wt_mwh": 0.0, "curt_pv_mwh": 0.0,
            "avg_hsys": 0.0, "min_hsys": 0.0, "max_rocof": 0.0, "min_fqss": 0.0,
        }

    # Extract results
    rows = []
    tf_cost = ff_cost = sf_cost = sdf_cost = 0.0
    curt_wt_total = curt_pv_total = curt_cost_total = 0.0

    for t in model.T:
        row = {"Hour": t, "Demand": Demand[t]}

        for g in model.G:
            row[f"{g}_P"]  = value(model.P[g, t])
            row[f"{g}_u"]  = int(round(value(model.u[g, t])))
            row[f"{g}_R"]  = value(model.R[g, t])

        row["Total_Thermal"] = sum(
            value(model.P[g, t]) for g in model.G if Type[g] not in ["PV", "WT"]
        )

        # PV
        pv_avail    = PV_Potential[t]
        pv_curt_val = value(model.PV_Curt[t]) if CONFIG["con_pv"] else 0.0
        row["PV_Available"]   = pv_avail
        row["PV_Curtailment"] = pv_curt_val
        row["PV_Used"]        = pv_avail - pv_curt_val
        curt_pv_total += pv_curt_val

        # WT
        wt_avail    = sum(WT_Available[w, t] for w in WT)
        wt_curt_val = sum(value(model.WT_Curt[w, t]) for w in WT) if CONFIG["con_wt"] else 0.0
        row["WT_Available"]   = wt_avail
        row["WT_Curtailment"] = wt_curt_val
        row["WT_Used"]        = wt_avail - wt_curt_val
        curt_wt_total += wt_curt_val

        # BESS
        for b in model.BATT:
            row[f"{b}_Pch"]  = value(model.P_charge[b, t])
            row[f"{b}_Pdis"] = value(model.P_discharge[b, t])
            row[f"{b}_SOC"]  = value(model.SOC[b, t])
            row[f"{b}_P_VI"] = value(model.P_VI_batt[b, t])
            row[f"{b}_H_VI"] = (value(model.Kb_VI[b]) * value(model.P_VI_batt[b, t])
                                if CONFIG["con_battery_vi"] else 0.0)

        # Frequency metrics
        hsys_val = value(model.Hsys[t])
        loss_val = value(model.LargestLoss[t])
        pfr_val  = value(model.TotalPFR[t])
        damp_val = D_frac * Demand[t]

        row["Hsys"]        = hsys_val
        row["LargestLoss"] = loss_val
        row["TotalPFR"]    = pfr_val
        row["RoCoF_est"]   = (loss_val * f0 / (2 * hsys_val)
                              if hsys_val > 1e-6 else 999.0)
        row["f_qss_est"]   = (f0 - loss_val / (pfr_val + damp_val)
                              if (pfr_val + damp_val) > 1e-6 else 0.0)

        # Costs
        fuel_t     = sum(b_coef[g] * value(model.P[g, t]) for g in model.G)
        fixed_t    = sum(c_coef[g] * value(model.u[g, t]) for g in model.G)
        start_t    = sum(SU_cost[g] * value(model.y[g, t]) for g in model.G)
        shut_t     = sum(SD_cost[g] * value(model.z[g, t]) for g in model.G)
        curt_wt_t  = C_curt_WT * wt_curt_val if CONFIG["obj_curtailment_cost"] else 0.0
        curt_pv_t  = C_curt_PV * pv_curt_val if CONFIG["obj_curtailment_cost"] else 0.0

        row["Fuel_Cost"]    = fuel_t
        row["Fixed_Cost"]   = fixed_t
        row["Startup_Cost"] = start_t
        row["Shutdown_Cost"]= shut_t
        row["Curt_Cost"]    = curt_wt_t + curt_pv_t
        row["Total_Cost"]   = fuel_t + fixed_t + start_t + shut_t + curt_wt_t + curt_pv_t

        tf_cost  += fuel_t
        ff_cost  += fixed_t
        sf_cost  += start_t
        sdf_cost += shut_t
        curt_cost_total += (curt_wt_t + curt_pv_t)

        rows.append(row)

    df_hourly  = pd.DataFrame(rows)
    total_cost = tf_cost + ff_cost + sf_cost + sdf_cost + curt_cost_total

    print(f"\n  Fuel Cost         : ${tf_cost:,.2f}")
    print(f"  Fixed Cost        : ${ff_cost:,.2f}")
    print(f"  Startup Cost      : ${sf_cost:,.2f}")
    print(f"  Shutdown Cost     : ${sdf_cost:,.2f}")
    print(f"  Curtailment Cost  : ${curt_cost_total:,.2f}")
    print(f"  TOTAL COST        : ${total_cost:,.2f}")

    avg_hsys  = df_hourly["Hsys"].mean()
    min_hsys  = df_hourly["Hsys"].min()
    max_rocof = df_hourly["RoCoF_est"].max()
    min_fqss  = df_hourly["f_qss_est"].min()

    print(f"\n  Avg Hsys          : {avg_hsys:.2f} MWs")
    print(f"  Min Hsys          : {min_hsys:.2f} MWs")
    print(f"  Max RoCoF (est)   : {max_rocof:.4f} Hz/s  (limit: {RoCoF_limit} Hz/s)")
    print(f"  Min f_qss (est)   : {min_fqss:.3f} Hz")

    if CONFIG["con_wt"] or CONFIG["con_pv"]:
        print(f"\n  WT Curtailed      : {curt_wt_total:.2f} MWh")
        print(f"  PV Curtailed      : {curt_pv_total:.2f} MWh")

    return {
        "scenario_id": scenario_id, "name": CONFIG["name"],
        "status": str(term_cond), "is_optimal": True,
        "solve_time": t_solve, "obj_value": value(model.Obj),
        "total_cost": total_cost, "fuel_cost": tf_cost,
        "fixed_cost": ff_cost, "startup_cost": sf_cost,
        "shutdown_cost": sdf_cost, "curtailment_cost": curt_cost_total,
        "curt_wt_mwh": curt_wt_total, "curt_pv_mwh": curt_pv_total,
        "avg_hsys": avg_hsys, "min_hsys": min_hsys,
        "max_rocof": max_rocof, "min_fqss": min_fqss,
        "df_hourly": df_hourly, "model": model, "CONFIG": CONFIG,
    }


# ============================================================
# 9. MAIN: RUN ALL 4 SCENARIOS
# ============================================================

if __name__ == "__main__":

    print("\n" + "="*65)
    print("  FCUC 4-SCENARIO SIMULATION")
    print("  Frequency-Constrained Unit Commitment")
    print("  Solver: IBM ILOG CPLEX 22.1.1")
    print("="*65)

    all_results = {}
    for sc_id, sc_cfg in SCENARIOS.items():
        all_results[sc_id] = solve_scenario(sc_id, sc_cfg)

    # --- COMPARATIVE SUMMARY TABLE ---
    print("\n\n" + "="*65)
    print("  TABEL RINGKASAN PERBANDINGAN 4 SKENARIO")
    print("="*65)

    summary_rows = []
    for sc_id, res in all_results.items():
        ok = res["is_optimal"]
        summary_rows.append({
            "Scenario":            sc_id,
            "Status":              "OPTIMAL" if ok else res["status"],
            "Solve_Time(s)":       f"{res['solve_time']:.1f}",
            "Total_Cost($)":       f"{res['total_cost']:,.2f}" if ok else "N/A",
            "Fuel_Cost($)":        f"{res['fuel_cost']:,.2f}" if ok else "N/A",
            "Curt_Cost($)":        f"{res['curtailment_cost']:,.2f}" if ok else "N/A",
            "WT_Curt(MWh)":        f"{res['curt_wt_mwh']:.2f}" if ok else "N/A",
            "PV_Curt(MWh)":        f"{res['curt_pv_mwh']:.2f}" if ok else "N/A",
            "Avg_Hsys(MWs)":       f"{res['avg_hsys']:.2f}" if ok else "N/A",
            "Max_RoCoF(Hz/s)":     f"{res['max_rocof']:.4f}" if ok else "N/A",
            "Min_fQSS(Hz)":        f"{res['min_fqss']:.3f}" if ok else "N/A",
        })

    df_summary = pd.DataFrame(summary_rows)
    print(df_summary.to_string(index=False))

    # --- EXPORT TO EXCEL ---
    output_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "Hasil_UC_4_Simulasi_Summary.xlsx"
    )
    print(f"\nMenyimpan ke: {output_file}")

    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        df_summary.to_excel(writer, sheet_name="Summary", index=False)
        for sc_id, res in all_results.items():
            if res["is_optimal"] and res["df_hourly"] is not None:
                res["df_hourly"].to_excel(writer, sheet_name=sc_id, index=False)

    print(f"  Tersimpan: {output_file}")

    # --- FINAL STATUS ---
    print("\n" + "="*65)
    print("  STATUS AKHIR")
    print("="*65)
    all_ok = True
    for sc_id, res in all_results.items():
        s = "OK  OPTIMAL" if res["is_optimal"] else "FAIL"
        c = f"${res['total_cost']:,.2f}" if res["is_optimal"] else "N/A"
        print(f"  {sc_id}: {s}  | Cost: {c}  | t={res['solve_time']:.1f}s")
        if not res["is_optimal"]:
            all_ok = False

    print()
    if all_ok:
        print("  SEMUA 4 SKENARIO BERHASIL DISELESAIKAN SECARA OPTIMAL!")
    else:
        print("  Ada skenario yang tidak optimal. Periksa constraint.")
    print("="*65)
