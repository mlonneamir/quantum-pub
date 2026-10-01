import argparse
from datetime import datetime
import time
import pandas as pd
from qiskit import QuantumCircuit
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

# ==========================================
# 1. INITIALIZE SERVICE & BACKEND
# ==========================================
print("Connecting to IBM Quantum Service...")
service = QiskitRuntimeService()
backend = service.backend("ibm_marrakesh")
MASTER_CSV = f"master_quantum_experiments_{backend.name}_subgraph.csv"

# We confirmed [0, 1, 2] is a valid physical chain on this backend
PHYSICAL_QUBITS = [0, 1, 2]
LOGICAL_QUBITS = len(PHYSICAL_QUBITS)

def wait_for_job(job):
    last_status = None
    while True:
        status = job.status()
        if status != last_status:
            print(
                f"    [{datetime.now().strftime('%H:%M:%S')}] Job Status: {status}"
            )
            last_status = status
        if status in ["DONE", "CANCELLED", "ERROR"]:
            break
        time.sleep(10)
    return status == "DONE"

def append_to_master(records):
    df = pd.DataFrame(records)
    df.to_csv(
        MASTER_CSV,
        mode="a",
        index=False,
        header=not pd.io.common.file_exists(MASTER_CSV),
    )

# ==========================================
# 2. BUILD THE 29-CIRCUIT SUB-GRAPH SUITE
# ==========================================
def build_master_circuits():
    circuits = []
    metadata = []
    
    # --- Exp 1: Depth Test (Depths 2, 128, 512, 1024) [12 circuits] ---
    depth_gates = [2, 128, 512, 1024]
    for logical_q in range(LOGICAL_QUBITS):
        for n in depth_gates:
            qc = QuantumCircuit(LOGICAL_QUBITS, 1)
            for _ in range(n):
                qc.x(logical_q)
            qc.measure(logical_q, 0)
            circuits.append(qc)
            metadata.append(
                {
                    "exp": "Exp1_Depth",
                    "target": f"Qubit_{PHYSICAL_QUBITS[logical_q]}",
                    "param_n": n,
                    "q_idx": PHYSICAL_QUBITS[logical_q],
                }
            )

    # --- Exp 2: Topology Superposition [3 circuits] ---
    for logical_q in range(LOGICAL_QUBITS):
        qc = QuantumCircuit(LOGICAL_QUBITS, 1)
        qc.h(logical_q)
        qc.measure(logical_q, 0)
        circuits.append(qc)
        metadata.append(
            {
                "exp": "Exp2_Topology",
                "target": f"Qubit_{PHYSICAL_QUBITS[logical_q]}",
                "param_n": 1,
                "q_idx": PHYSICAL_QUBITS[logical_q],
            }
        )

    # --- Exp 3: Contiguous Bell Pairs [2 circuits] ---
    # Logical pairs (0,1) and (1,2) map to physical pairs [0,1] and [1,2]
    for q1, q2 in [(0, 1), (1, 2)]:
        qc = QuantumCircuit(LOGICAL_QUBITS, 2)
        qc.h(q1)
        qc.cx(q1, q2)
        qc.measure([q1, q2], [0, 1])
        circuits.append(qc)
        metadata.append(
            {
                "exp": "Exp3_TemporalBell",
                "target": f"Pair_Q{PHYSICAL_QUBITS[q1]}-Q{PHYSICAL_QUBITS[q2]}",
                "param_n": 2,
                "q_idx": PHYSICAL_QUBITS[q1],
            }
        )

    # --- Exp 4: GHZ Scaling (1, 2, and 3 Qubits) [3 circuits] ---
    for n in range(1, LOGICAL_QUBITS + 1):
        qc = QuantumCircuit(LOGICAL_QUBITS, n)
        qc.h(0)
        for i in range(1, n):
            qc.cx(i - 1, i)
        qc.measure(range(n), range(n))
        circuits.append(qc)
        metadata.append(
            {
                "exp": "Exp4_GHZScaling",
                "target": f"Register_{n}Q",
                "param_n": n,
                "q_idx": PHYSICAL_QUBITS[0],
            }
        )

    # --- Exp 6: SPAM Readout (|0> and |1> States) [6 circuits] ---
    for logical_q in range(LOGICAL_QUBITS):
        # State |0>
        qc0 = QuantumCircuit(LOGICAL_QUBITS, 1)
        qc0.measure(logical_q, 0)
        circuits.append(qc0)
        metadata.append(
            {
                "exp": "Exp6_SPAMReadout",
                "target": f"Qubit_{PHYSICAL_QUBITS[logical_q]}_State0",
                "param_n": 0,
                "q_idx": PHYSICAL_QUBITS[logical_q],
            }
        )
        
        # State |1>
        qc1 = QuantumCircuit(LOGICAL_QUBITS, 1)
        qc1.x(logical_q)
        qc1.measure(logical_q, 0)
        circuits.append(qc1)
        metadata.append(
            {
                "exp": "Exp6_SPAMReadout",
                "target": f"Qubit_{PHYSICAL_QUBITS[logical_q]}_State1",
                "param_n": 1,
                "q_idx": PHYSICAL_QUBITS[logical_q],
            }
        )

    # --- Exp 7: Path Distance Penalty (Q0 to Q1, Q0 to Q2) [2 circuits] ---
    for target_q in range(1, LOGICAL_QUBITS):
        qc = QuantumCircuit(LOGICAL_QUBITS, 2)
        qc.h(0)
        qc.cx(0, target_q)
        qc.measure([0, target_q], [0, 1])
        circuits.append(qc)
        metadata.append(
            {
                "exp": "Exp7_PathDistance",
                "target": f"Path_Q{PHYSICAL_QUBITS[0]}_to_Q{PHYSICAL_QUBITS[target_q]}",
                "param_n": target_q,
                "q_idx": PHYSICAL_QUBITS[0],
            }
        )

    return circuits, metadata

# ==========================================
# 3. EXECUTION AND DATA PARSING
# ==========================================
def run_master_suite(shots=8192):
    print(
        f"\n🚀 Preparing Sub-Graph Diagnostic Suite for '{backend.name}'..."
    )
    circuits, metadata = build_master_circuits()
    print(f"📁 Total compiled circuits in suite: {len(circuits)}")

    properties = backend.properties()
    
    # Transpile targeting our specific 3-qubit physical chain
    pm = generate_preset_pass_manager(
        backend=backend, 
        optimization_level=1,
        initial_layout=PHYSICAL_QUBITS 
    )
    print("⚡ Transpiling circuits to ISA (mapping to physical Q0, Q1, Q2)...")
    isa_circuits = [pm.run(qc) for qc in circuits]

    sampler = Sampler(mode=backend)
    all_records = []

    print(f"\n📤 Submitting Job ({len(isa_circuits)} circuits at {shots} shots)...")
    job = sampler.run(isa_circuits, shots=shots)
    job_id = job.job_id()
    print(f"    Job ID: {job_id}")

    if not wait_for_job(job):
        print(f"⚠️ Job failed. Exiting.")
        return

    results = job.result()
    metrics = job.metrics()
    
    if "timestamps" in metrics and "running" in metrics["timestamps"]:
        timestamp = metrics["timestamps"]["running"]
    else:
        timestamp = (
            job.created.isoformat()
            if hasattr(job.created, "isoformat")
            else str(job.created)
        )

    for meta, pub_result in zip(metadata, results):
        data_bin = pub_result.data
        counts = getattr(data_bin, list(data_bin.keys())[0]).get_counts()
        q_idx = meta["q_idx"]

        t1_us = properties.t1(q_idx) * 1e6 if properties else None
        t2_us = properties.t2(q_idx) * 1e6 if properties else None
        ro_err = (
            properties.readout_error(q_idx) if properties else None
        )

        if meta["exp"] in ["Exp1_Depth", "Exp2_Topology", "Exp6_SPAMReadout"]:
            count_0 = counts.get("0", 0)
            count_1 = counts.get("1", 0)
            if meta["exp"] == "Exp2_Topology":
                metric = abs(count_0 - count_1) / shots
            elif meta["exp"] == "Exp6_SPAMReadout" and meta["param_n"] == 1:
                metric = count_1 / shots
            else:
                metric = count_0 / shots
        elif meta["exp"] in ["Exp3_TemporalBell", "Exp7_PathDistance"]:
            count_0 = counts.get("00", 0)
            count_1 = counts.get("11", 0)
            metric = (count_0 + count_1) / shots
        elif meta["exp"] == "Exp4_GHZScaling":
            n = meta["param_n"]
            count_0 = counts.get("0" * n, 0)
            count_1 = counts.get("1" * n, 0)
            metric = (count_0 + count_1) / shots

        all_records.append(
            {
                "timestamp": timestamp,
                "backend_name": backend.name,
                "job_id": job_id,
                "experiment_type": meta["exp"],
                "target_entity": meta["target"],
                "parameter_n": meta["param_n"],
                "shots": shots,
                "count_0": count_0,
                "count_1": count_1,
                "metric_primary": metric,
                "ibm_calibrated_t1_us": t1_us,
                "ibm_calibrated_t2_us": t2_us,
                "ibm_calibrated_readout_err": ro_err,
            }
        )

    append_to_master(all_records)
    print(f"\n✅ Successfully written 8192-shot results to '{MASTER_CSV}'!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run Sub-Graph Quantum Diagnostic Suite."
    )
    parser.add_argument(
        "--shots",
        type=int,
        default=8192,
        help="Number of shots per circuit execution.",
    )
    args = parser.parse_args()

    run_master_suite(shots=args.shots)