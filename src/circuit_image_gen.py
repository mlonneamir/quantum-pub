from qiskit import QuantumCircuit
import os

# Create a directory to save the circuit images
output_dir = "quantum_circuit_diagrams"
os.makedirs(output_dir, exist_ok=True)

def save_circuit(qc, filename):
    # Use the matplotlib backend for high-quality publication images
    qc.draw(output='mpl', filename=os.path.join(output_dir, filename))

# ==========================================
# Exp 1: Depth Scaling (12 circuits)
# ==========================================
depths = [2, 128, 512, 1024]
for qubit in [0, 1, 2]:
    for d in depths:
        qc = QuantumCircuit(3, 1)
        for _ in range(d):
            qc.x(qubit)
        qc.measure(qubit, 0)
        save_circuit(qc, f"Exp1_Depth_{d}_Q{qubit}.png")

# ==========================================
# Exp 2: Topology Superposition (3 circuits)
# ==========================================
for qubit in [0, 1, 2]:
    qc = QuantumCircuit(3, 1)
    qc.h(qubit)
    qc.measure(qubit, 0)
    save_circuit(qc, f"Exp2_Superposition_Q{qubit}.png")

# ==========================================
# Exp 3: Temporal Bell Pairs (2 circuits)
# ==========================================
pairs = [(0, 1), (1, 2)]
for q_ctrl, q_trgt in pairs:
    qc = QuantumCircuit(3, 2)
    qc.h(q_ctrl)
    qc.cx(q_ctrl, q_trgt)
    qc.measure([q_ctrl, q_trgt], [0, 1])
    save_circuit(qc, f"Exp3_BellPair_Q{q_ctrl}_Q{q_trgt}.png")

# ==========================================
# Exp 4: GHZ Scaling (3 circuits)
# ==========================================
# 1-Qubit Baseline
qc_1 = QuantumCircuit(3, 1)
qc_1.h(0)
qc_1.measure(0, 0)
save_circuit(qc_1, "Exp4_GHZ_1Q.png")

# 2-Qubit Entanglement
qc_2 = QuantumCircuit(3, 2)
qc_2.h(0)
qc_2.cx(0, 1)
qc_2.measure([0, 1], [0, 1])
save_circuit(qc_2, "Exp4_GHZ_2Q.png")

# 3-Qubit GHZ State
qc_3 = QuantumCircuit(3, 3)
qc_3.h(0)
qc_3.cx(0, 1)
qc_3.cx(1, 2)
qc_3.measure([0, 1, 2], [0, 1, 2])
save_circuit(qc_3, "Exp4_GHZ_3Q.png")

# ==========================================
# Exp 5: SPAM Readout (6 circuits)
# ==========================================
for qubit in [0, 1, 2]:
    # State |0>
    qc_0 = QuantumCircuit(3, 1)
    qc_0.measure(qubit, 0) # No gates, just measure default |0>
    save_circuit(qc_0, f"Exp5_SPAM_Q{qubit}_State0.png")
    
    # State |1>
    qc_1 = QuantumCircuit(3, 1)
    qc_1.x(qubit) # Flip to |1> before measuring
    qc_1.measure(qubit, 0)
    save_circuit(qc_1, f"Exp5_SPAM_Q{qubit}_State1.png")

# ==========================================
# Exp 6: Path Distance Routing (2 circuits)
# ==========================================
# 1-Hop Path (Q0 to Q1)
qc_1hop = QuantumCircuit(3, 2)
qc_1hop.h(0)
qc_1hop.cx(0, 1)
qc_1hop.measure([0, 1], [0, 1])
save_circuit(qc_1hop, "Exp6_Path_1Hop_Q0_Q1.png")

# 2-Hop Path (Q0 to Q2 routed through Q1)
qc_2hop = QuantumCircuit(3, 2)
qc_2hop.h(0)
qc_2hop.cx(0, 1) # Entangle Q0 to Q1
qc_2hop.cx(1, 2) # Entangle Q1 to Q2 (propagating the state)
qc_2hop.measure([0, 2], [0, 1]) # Measure origin and final destination
save_circuit(qc_2hop, "Exp6_Path_2Hop_Q0_Q2.png")

print("All 28 circuit diagrams have been successfully generated and saved!")