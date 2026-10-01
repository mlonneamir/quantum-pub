# An Analysis of Circuit Fidelity and Error Accumulation in IBM Quantum Computers

[![License: MIT](https://shields.io)](https://opensource.org)

### Paper and supporting code for an analysis of circuit fidelity and error accumulation in IBM Quantum Computers.
---

##  Paper Abstract

Quantum computers in the Noisy Intermediate-Scale Quantum (NISQ) era are heavily constrained by environmental noise and decoherence. While daily automated calibrations track static error baselines, they fail to track the constant intra-day fluctuations that decrease measurement accuracy. In this study, we conducted a 24-hour diagnostic benchmark on a contiguous three-qubit sub-graph of the 156-qubit ibm_marrakesh heavy-hex processor from IBM. Every four hours, we executed a suite of 28 unique circuits across six experimental categories at 8,192 shots per circuit. Single-qubit operations showed high stability, maintaining measurement fidelities above 99.6% across depths up to 1,024 Pauli-X gates. Conversely, multi-qubit entanglement and excited-state measurements showed much weaker stability, noticeably during a localized thermal event that caused 3-qubit GHZ state fidelity to drop from 97.3% to 93.6% along with routing errors. Our measured error exceeded the theoretical error up to 11.8 times greater, demonstrating that these fluctuations come from physical calibration drift rather than statistical artifacts. Aside from measuring the error loss contributors, these findings show that static, daily calibrations are insufficient for characterizing NISQ hardware stability.

##  Repo Layout

* src: code
* data: collected data
* images: graphs of data
* quantum_circuit_diagrams: circuit diagrams

##  Setup

1. Get an IBM Qiskit account and connect API and token
2. Enter token and run in cred.py 
3. Run master_single.py for single run
4. Run caffeinate.sh for 24-hour test
