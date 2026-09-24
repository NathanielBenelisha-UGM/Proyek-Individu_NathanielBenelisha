
# ============================================================
# digsilent_n1_contingency.py  — Tahap 4b
# DIgSILENT PowerFactory Python API — N-1 Contingency Simulation
#
# Cara menjalankan:
#   1. Buka DIgSILENT PowerFactory 2024
#   2. Buka project yang sudah di-setup (sistem IEEE 9-bus atau sistem custom)
#   3. Tools > Python > Run Script > pilih file ini
#      ATAU jalankan via: PowerFactory.exe /Py digsilent_n1_contingency.py
#
# Skenario simulasi:
#   - N-1: Trip generator terbesar di t=0s
#   - Reclose: Generator ON kembali di t=15s atau t=30s
#   - Diulang untuk S1/S3/S4 × 3 jam kritis × 2 reclose time
#
# Dependencies: powerfactory (built-in PF Python API)
# ============================================================

import sys
import os
import csv
import math

# ============================================================
# 0. CHECK ENVIRONMENT
# ============================================================

try:
    import powerfactory as pf
    PF_AVAILABLE = True
except ImportError:
    PF_AVAILABLE = False
    print("[WARNING] powerfactory module not found.")
    print("          Script must be run from within DIgSILENT PowerFactory.")
    print("          Running in DEMO mode for validation only.\n")

# ============================================================
# 1. CONFIGURATION
# ============================================================

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
DATA_DIR  = os.path.join(BASE_DIR, "DigSilent")
CONT_FILE = os.path.join(DATA_DIR, "contingency_test_matrix.csv")
OUT_DIR   = os.path.join(DATA_DIR, "Results")
os.makedirs(OUT_DIR, exist_ok=True)

# Simulation parameters
SIM_DURATION_S  = 120.0    # Total simulation time (s)
STEP_SIZE_MS    = 10.0     # Integration step (ms) — 10ms untuk RMS accuracy
FREQ_NOMINAL    = 50.0     # Hz
ROCOF_LIMIT     = 0.55     # Hz/s
F_QSS_LIMIT     = 49.5     # Hz
F_NADIR_LIMIT   = 49.0     # Hz (UFLS threshold)

# BESS Virtual Inertia control gain (untuk model DIgSILENT)
# P_VI = Kb_VI * (-df/dt) × P_rated
# Model: VI controller -> frequency measurement -> droop output
KB_VI_B1 = 4.0   # MWs/MW
KB_VI_B2 = 5.0   # MWs/MW

# Generator names in DIgSILENT project (must match exact PF object names)
GEN_NAMES_PF = {
    "G1":  "Gen_G1",     # PLTU 1176 MW
    "G2":  "Gen_G2",     # PLTGU 1125 MW
    "G3":  "Gen_G3",     # PLTU 969 MW
    "G4":  "Gen_G4",     # PLTG 130 MW
    "G5":  "Gen_G5",     # PLTG 108 MW
    "G6":  "Gen_G6",     # PLTGU 1095 MW
    "G7":  "Gen_G7",     # PLTGU 810 MW
    "G8":  "Gen_G8",     # PLTGU 773 MW
    "G9":  "Gen_G9",     # PLTU 870 MW
    "G10": "Gen_G10",    # PLTU 840 MW
    "B1":  "BESS_B1",    # Battery 1
    "B2":  "BESS_B2",    # Battery 2
    "WT1": "Wind_WT1",   # Wind Farm
}

# ============================================================
# 2. HELPER FUNCTIONS
# ============================================================

def read_dispatch_csv(filepath):
    """Baca file CSV dispatch yang dihasilkan export_dispatch_for_digsilent.py"""
    import csv
    header_info = {}
    gen_data    = []

    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(
            (line for line in f if not line.startswith("#")),
        )
        for row in reader:
            gen_data.append(row)

    return gen_data


def load_contingency_matrix(filepath):
    """Load test matrix dari CSV"""
    tests = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tests.append(row)
    return tests


# ============================================================
# 3. POWERFACTORY FUNCTIONS
# (These run only when inside PF environment)
# ============================================================

def get_pf_app():
    """Dapatkan PowerFactory application object."""
    app = pf.GetApplication()
    if app is None:
        raise RuntimeError("Tidak dapat terhubung ke PowerFactory!")
    app.ClearOutputWindow()
    app.PrintInfo("DIgSILENT N-1 Contingency Simulation — Started")
    return app


def set_initial_conditions(app, gen_data, scenario_id):
    """
    Set dispatch dari hasil UC ke model PowerFactory.
    gen_data: list of dict dari dispatch CSV
    """
    app.PrintInfo(f"Setting initial conditions for {scenario_id}...")

    project = app.GetActiveProject()
    ldf     = app.GetFromStudyCase("ComLdf")   # Load flow object

    for unit in gen_data:
        obj_name = unit["object_name"]
        p_mw     = float(unit.get("P_dispatch_MW", 0) or 0)
        status   = int(unit.get("status_on", 0) or 0)
        q_mvar   = float(unit.get("Q_dispatch_MVAr", 0) or 0)

        if obj_name not in GEN_NAMES_PF:
            continue

        pf_name = GEN_NAMES_PF[obj_name]

        # Find object in PF
        gen_obj = app.GetCalcRelevantObjects(f"{pf_name}.ElmSym")
        if not gen_obj:
            gen_obj = app.GetCalcRelevantObjects(f"{pf_name}.ElmBatt")
        if not gen_obj:
            app.PrintWarn(f"Object not found: {pf_name}")
            continue

        gen = gen_obj[0]

        # Set dispatch
        gen.SetAttribute("outserv", 0 if status else 1)  # In/Out of service
        if status:
            gen.SetAttribute("pgini", p_mw)   # Active power setpoint (MW)
            gen.SetAttribute("qgini", q_mvar) # Reactive power (MVAr)

        # Set BESS-specific attributes
        if "B" in obj_name and unit.get("P_VI_MW"):
            p_vi = float(unit.get("P_VI_MW", 0) or 0)
            kb   = float(unit.get("Kb_VI", 0) or 0)
            soc  = float(unit.get("SOC_MWh", 0) or 0)
            # Set VI gain in BESS controller
            ctrl_objs = app.GetCalcRelevantObjects(f"{pf_name}_VI_Ctrl.ElmComp")
            if ctrl_objs:
                ctrl_objs[0].SetAttribute("Kb_VI", kb)
                ctrl_objs[0].SetAttribute("p_vi_init", p_vi)
            gen.SetAttribute("usetp", soc)    # SOC initial condition

    # Run initial load flow
    app.PrintInfo("Running initial load flow...")
    ldf.Execute()
    app.PrintInfo("Initial conditions set successfully.")


def setup_generator_trip_event(app, gen_name_pf, t_trip_s, t_reclose_s=None):
    """
    Buat event trip generator dan reclose di simulation events.
    gen_name_pf: nama generator di PF (string)
    t_trip_s:    waktu trip (detik)
    t_reclose_s: waktu nyala kembali (None = tidak nyala)
    """
    # Get simulation events container
    sim_events = app.GetFromStudyCase("IntEvt")
    if sim_events is None:
        app.PrintError("Cannot find IntEvt — simulation events container!")
        return

    # Clear existing events
    existing = sim_events.GetContents()
    for ev in existing:
        ev.Delete()

    # Find generator object
    gen_objs = app.GetCalcRelevantObjects(f"{gen_name_pf}.ElmSym")
    if not gen_objs:
        app.PrintError(f"Generator not found: {gen_name_pf}")
        return
    gen = gen_objs[0]

    # Create TRIP event at t_trip_s
    evt_trip = sim_events.CreateObject("EvtSwitch", f"Trip_{gen_name_pf}")
    evt_trip.SetAttribute("time", t_trip_s)
    evt_trip.SetAttribute("i_switch", 0)     # 0 = OPEN (trip)
    evt_trip.SetAttribute("p_target", gen)

    app.PrintInfo(f"  Event: Trip {gen_name_pf} at t={t_trip_s}s")

    # Create RECLOSE event if specified
    if t_reclose_s is not None:
        evt_close = sim_events.CreateObject("EvtSwitch", f"Reclose_{gen_name_pf}")
        evt_close.SetAttribute("time", t_reclose_s)
        evt_close.SetAttribute("i_switch", 1)    # 1 = CLOSE (reconnect)
        evt_close.SetAttribute("p_target", gen)
        app.PrintInfo(f"  Event: Reclose {gen_name_pf} at t={t_reclose_s}s")


def run_rms_simulation(app, duration_s, step_ms):
    """
    Jalankan simulasi RMS (quasi-steady-state transient).
    Returns: result object
    """
    # Get RMS simulation object
    rms = app.GetFromStudyCase("ComSim")
    if rms is None:
        app.PrintError("RMS simulation object not found!")
        return None

    rms.SetAttribute("tstop",    duration_s)
    rms.SetAttribute("dtgrd",    step_ms / 1000.0)  # step in seconds
    rms.SetAttribute("iopt_sim", 0)  # 0=RMS, 1=EMT

    app.PrintInfo(f"Starting RMS simulation: {duration_s}s, step={step_ms}ms")
    rms.Execute()
    app.PrintInfo("RMS simulation completed.")

    return rms


def extract_results(app, gen_name_pf, out_dir, test_id):
    """
    Ekstrak hasil simulasi: frekuensi, RoCoF, tegangan.
    Returns: dict of metrics
    """
    # Get result objects
    res = app.GetFromStudyCase("ElmRes")   # Result file

    # Get frequency at slack bus / reference generator
    # Typical PF result variables:
    #   c:fi   = frequency deviation (Hz)
    #   c:dfdt = df/dt = RoCoF (Hz/s)
    #   m:Psum:bus1 = total active power

    # Export result to CSV
    exporter = app.GetFromStudyCase("ComRes")
    if exporter:
        csv_path = os.path.join(out_dir, f"{test_id}_timeseries.csv")
        exporter.SetAttribute("f_name", csv_path)
        exporter.SetAttribute("iopt_csel", 0)   # All results
        exporter.Execute()
        app.PrintInfo(f"Results exported: {csv_path}")

    # Extract scalar metrics
    metrics = {
        "test_id":       test_id,
        "sim_completed": True,
    }

    try:
        # Frequency nadir
        freq_obj = app.GetCalcRelevantObjects("*.ElmSym")[0] if app.GetCalcRelevantObjects("*.ElmSym") else None
        if freq_obj and res:
            # These are PF result variable names
            metrics["f_nadir_Hz"]  = res.GetMinValue(freq_obj, "c:fi") + 50.0
            metrics["f_nadir_t_s"] = res.GetMinValueTime(freq_obj, "c:fi")
            metrics["f_ss_Hz"]     = res.GetValue(freq_obj, "c:fi", SIM_DURATION_S) + 50.0
    except Exception as e:
        app.PrintWarn(f"Could not extract nadir: {e}")

    return metrics


# ============================================================
# 4. BESS VIRTUAL INERTIA CONTROLLER SETUP
# ============================================================

def setup_bess_vi_controller(app, batt_name, kb_vi, enabled=True):
    """
    Konfigurasi Virtual Inertia controller untuk BESS.
    Model: P_VI = -Kb_VI * df/dt * P_rated
    Controller tipe: Synchronverter atau droop berbasis df/dt
    """
    ctrl = app.GetCalcRelevantObjects(f"{batt_name}_VI_Ctrl.ElmComp")
    if not ctrl:
        app.PrintWarn(f"VI Controller not found for {batt_name}, skip.")
        return

    ctrl_obj = ctrl[0]
    ctrl_obj.SetAttribute("Kb_VI",    kb_vi)
    ctrl_obj.SetAttribute("vi_active", 1 if enabled else 0)
    ctrl_obj.SetAttribute("droop_db", 0.01)   # dead band 0.01 Hz
    ctrl_obj.SetAttribute("T_filter", 0.02)   # frequency filter 20ms

    app.PrintInfo(f"  BESS VI Controller {batt_name}: Kb={kb_vi}, Enabled={enabled}")


# ============================================================
# 5. SCENARIO RUNNER
# ============================================================

def run_one_test(app, test):
    """
    Jalankan satu test case dari contingency matrix.
    test: dict dengan kolom dari contingency_test_matrix.csv
    """
    test_id      = test["test_id"]
    scenario_uc  = test["scenario_UC"]
    hour_uc      = int(test["hour_UC"])
    cont_gen     = test["contingency_gen"]
    p_loss       = float(test["P_loss_MW"])
    t_trip       = float(test["t_trip_s"])
    t_reclose_raw = test["t_reclose_s"]
    t_reclose    = float(t_reclose_raw) if t_reclose_raw and t_reclose_raw != "" else None
    has_bess_vi  = int(test["has_BESS_VI"]) == 1
    has_ebt      = int(test["has_EBT"]) == 1

    app.PrintInfo(f"\n{'='*50}")
    app.PrintInfo(f"TEST: {test_id}")
    app.PrintInfo(f"  UC={scenario_uc} | t={hour_uc}h | Trip={cont_gen} ({p_loss:.1f}MW)")
    app.PrintInfo(f"  Reclose={'t='+str(t_reclose)+'s' if t_reclose else 'None'}")
    app.PrintInfo(f"  BESS VI={has_bess_vi} | EBT={has_ebt}")

    # 1. Load dispatch CSV
    dispatch_file = os.path.join(DATA_DIR, test["dispatch_file"])
    if not os.path.exists(dispatch_file):
        app.PrintError(f"Dispatch file not found: {dispatch_file}")
        return {"test_id": test_id, "status": "FAILED_NO_DATA"}

    gen_data = read_dispatch_csv(dispatch_file)

    # 2. Set initial conditions
    set_initial_conditions(app, gen_data, test_id)

    # 3. Configure BESS VI
    setup_bess_vi_controller(app, "BESS_B1", KB_VI_B1, enabled=has_bess_vi)
    setup_bess_vi_controller(app, "BESS_B2", KB_VI_B2, enabled=has_bess_vi)

    # 4. Set up contingency events
    pf_gen_name = GEN_NAMES_PF.get(cont_gen, cont_gen)
    setup_generator_trip_event(app, pf_gen_name, t_trip, t_reclose)

    # 5. Run RMS simulation
    rms = run_rms_simulation(app, SIM_DURATION_S, STEP_SIZE_MS)
    if rms is None:
        return {"test_id": test_id, "status": "FAILED_SIM"}

    # 6. Extract results
    metrics = extract_results(app, pf_gen_name, OUT_DIR, test_id)
    metrics.update({
        "scenario_UC":    scenario_uc,
        "hour_UC":        hour_uc,
        "cont_gen":       cont_gen,
        "P_loss_MW":      p_loss,
        "t_trip_s":       t_trip,
        "t_reclose_s":    t_reclose,
        "has_BESS_VI":    has_bess_vi,
        "has_EBT":        has_ebt,
        "H_sys_MWs":      float(test["H_sys_MWs"]),
        "RoCoF_UC_est":   float(test["expected_RoCoF"]),
        "f_QSS_UC_est":   float(test["expected_fQSS"]),
        "status":         "COMPLETED",
    })

    app.PrintInfo(f"  DONE: {test_id}")
    return metrics


# ============================================================
# 6. MAIN EXECUTION
# ============================================================

def main():

    if not PF_AVAILABLE:
        # Demo mode: print test matrix
        print("\n" + "=" * 60)
        print("  DEMO MODE (DIgSILENT tidak tersedia)")
        print("  Menampilkan test matrix yang akan dijalankan...")
        print("=" * 60)

        if not os.path.exists(CONT_FILE):
            print(f"\n[ERROR] Contingency matrix tidak ditemukan: {CONT_FILE}")
            print("  Jalankan export_dispatch_for_digsilent.py terlebih dahulu!")
            return

        tests = load_contingency_matrix(CONT_FILE)
        print(f"\n  Total test cases: {len(tests)}")
        print()
        print(f"  {'Test ID':<45} {'SC':>3} {'hr':>3} {'Gen':>4} {'PLoss':>7} {'Reclose':>8} {'VI':>3}")
        print("  " + "-" * 80)
        for t in tests:
            rc = t['t_reclose_s'] if t['t_reclose_s'] else "None"
            print(f"  {t['test_id']:<45} {t['scenario_UC']:>3} {t['hour_UC']:>3} "
                  f"{t['contingency_gen']:>4} {float(t['P_loss_MW']):>7.1f} "
                  f"{'t='+rc+'s':>8} {t['has_BESS_VI']:>3}")
        return

    # ---- ACTUAL PF RUN ----
    app = get_pf_app()

    tests   = load_contingency_matrix(CONT_FILE)
    results = []

    app.PrintInfo(f"Total test cases to run: {len(tests)}")

    for i, test in enumerate(tests):
        app.PrintInfo(f"\nProgress: {i+1}/{len(tests)}")
        try:
            result = run_one_test(app, test)
            results.append(result)
        except Exception as e:
            app.PrintError(f"Test FAILED: {test['test_id']} — {e}")
            results.append({"test_id": test["test_id"], "status": f"ERROR: {e}"})

    # Save results summary
    if results:
        import csv
        out_file = os.path.join(OUT_DIR, "simulation_results_summary.csv")
        with open(out_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)

        app.PrintInfo(f"\nResults saved: {out_file}")
        app.PrintInfo(f"Completed: {sum(1 for r in results if r.get('status')=='COMPLETED')} / {len(results)}")

    app.PrintInfo("\nTahap 4 — N-1 Contingency Simulation SELESAI.")


if __name__ == "__main__":
    main()
