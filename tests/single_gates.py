from pulse.pulse_system import PulseSystem
from tests.helpers import possible_init_states
from tests.pipeline import generate_tests
import pennylane as qml

from utils.helpers import prints, statevector_similarity, statevector_fidelity, random_theta


# Pennylane Big Endian convention: |q0 q1 q2 q3 ... >
class PennyCircuit:

    def __init__(self, num_qubits):

        self.num_qubits = num_qubits

    def run_quick_circuit(self, thet, target_q, init_state=None):
        dev = qml.device('default.qubit', wires=self.num_qubits)

        @qml.qnode(dev)
        def general_circuit():
            if init_state is not None:
                qml.StatePrep(init_state, wires=range(self.num_qubits))

            for qubit in target_q:
                if 0 <= qubit < self.num_qubits:
                    qml.RZ(thet, wires=qubit)
                else:
                    print(f"Warning: Target qubit {qubit} is out of range (0 to {self.num_qubits - 1}).")
            return qml.state()

        return general_circuit()


# GLOBAL PHASE ERRORS:
# len(target_qubits) mod 4 = 0: 1 (no error)
# len(target_qubits) mod 4 = 1: j
# len(target_qubits) mod 4 = 2: -1
# len(target_qubits) mod 4 = 3: -j


# PARALLEL TEST GENERATION, passed with fid ~ 0.99995, sim ~ 0.995
test_cases = generate_tests(20)
sequence_repetitions = 3

for i, (num_qubits, target_qubits) in enumerate(test_cases):

    print(f"Test Case {i + 1}:")
    print(f"  Number of qubits (n): {num_qubits}")
    print(f"  Target qubits: {target_qubits} \n")

    c = PennyCircuit(num_qubits)
    for init_function in possible_init_states:

        init = init_function(num_qubits)
        theta = random_theta()

        penny_state = init.data
        for _ in range(sequence_repetitions):
            penny_state = c.run_quick_circuit(thet=theta, target_q=target_qubits, init_state=penny_state)

        prints(penny_state)

        pls = PulseSystem(num_qubits, init)

        for _ in range(sequence_repetitions):
            pls.rz(theta, target_qubits)

        result_state = pls.current_state
        prints(result_state)

        # manual_correction = global_phase_correction * current_state[-1].data
        # prints(manual_correction)
        # print("-")

        sim = statevector_similarity(penny_state, result_state)
        fid = statevector_fidelity(penny_state, result_state)
        print(f"sim = {sim}, fid = {fid}")
        print(20*"-", "\n")
        # manual_correction = global_phase_correction * current_state[-1].data
        # prints(manual_correction)
        # print("-")
