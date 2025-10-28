"""
Global Quantum Circuit Manager for Quantum Poker

This module manages the global quantum circuit that contains all card registers
needed for quantum operations during the game.
"""

import qiskit
from qiskit.circuit import QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
from typing import Dict, List, Tuple, Optional
import math

from .card import Card, SUITS, RANKS

SUITS_INVERSE = {v: k for k, v in SUITS.items()}
RANKS_INVERSE = {v: k for k, v in RANKS.items()}


class QuantumPokerCircuit:
    """
    Manages the global quantum circuit for the poker game.
    All cards share this circuit with designated qubit slices.
    """

    def __init__(self):
        # Main quantum circuit
        self.circuit = qiskit.QuantumCircuit()

        # Card identifier -> (register, start_index, end_index) mapping
        # e.g., "P1H1" -> (QuantumRegister, 0, 6) for Player 1 Hole Card 1
        self.card_register_map: Dict[str, Tuple[QuantumRegister, int, int]] = {}

        # Track which cards have been added
        self.registered_cards: List[str] = []
        # Entanglement history entries are tuples with flexible payloads:
        # (card1_id, card2_id, bit_index, op_name, optional_param)
        # For H+CNOT and SELF entries optional_param is None.
        # For PHASE/RZ entries optional_param contains the angle (float, radians).
        self.entanglement_history: List[Tuple] = []

        self.classical_register = None

    def add_card(self, card: Card, identifier: str) -> QuantumRegister:
        """
        Add a card to the global circuit with a unique identifier.

        Args:
            card: Card object to add
            identifier: Unique identifier (e.g., "P1H1", "F0", "T", "R")

        Returns:
            The quantum register for this card
        """
        if identifier in self.card_register_map:
            raise ValueError(f"Card identifier {identifier} already exists")

        # Create register, add to circuit, and prepare
        card.register = QuantumRegister(6, name=identifier)
        self.circuit.add_register(card.register)
        card.set_identifier(identifier)
        card.prepare(self.circuit)

        # Store mapping
        start_idx = len(self.circuit.qubits) - 6
        end_idx = len(self.circuit.qubits)
        self.card_register_map[identifier] = (card.register, start_idx, end_idx)
        self.registered_cards.append(identifier)

        return card.register

    def entangle_cards(
        self, card1_id: str, card2_id: str, bit_index: int, option: int = 1
    ):
        """
        Entangle a specific bit of two cards using quantum gates.

        Option 1: H + CNOT entanglement
            - Apply Hadamard to card1's bit
            - Apply CNOT with card1 as control and card2 as target

        Args:
            card1_id: Identifier of first card (control)
            card2_id: Identifier of second card (target)
            bit_index: Which rank bit to entangle (0-2 only for safe rank entanglement)
                      Bit 0: ±1 rank variation (minimal)
                      Bit 1: ±2 rank variation (moderate)
                      Bit 2: ±4 rank variation (significant)
            option: Entanglement strategy (1-5)
        """
        if card1_id not in self.card_register_map:
            raise ValueError(f"Card {card1_id} not found in circuit")
        if card2_id not in self.card_register_map:
            raise ValueError(f"Card {card2_id} not found in circuit")

        # Only allow rank bits 0-2 (not 3 which can create invalid ranks, not 4-5 which are suit)
        if bit_index < 0 or bit_index > 2:
            raise ValueError(
                f"Invalid bit index: {bit_index}. Must be 0-2 (rank bits only).\n"
                f"  Bit 0: ±1 rank change\n"
                f"  Bit 1: ±2 rank change\n"
                f"  Bit 2: ±4 rank change"
            )

        reg1, start1, _ = self.card_register_map[card1_id]
        reg2, start2, _ = self.card_register_map[card2_id]

        if option == 1:
            # H + CNOT entanglement
            self.circuit.h(reg1[bit_index])
            self.circuit.cx(reg1[bit_index], reg2[bit_index])

            # Record entanglement (no extra parameter)
            self.entanglement_history.append(
                (card1_id, card2_id, bit_index, "H+CNOT", None)
            )

        # TODO: Implement options 2-5
        else:
            raise NotImplementedError(
                f"Entanglement option {option} not yet implemented"
            )

    def apply_hadamard(self, card_id: str, bit_index: int):
        """
        Apply Hadamard gate to a specific bit of a card to put it in superposition.

        Args:
            card_id: Identifier of the card
            bit_index: Which rank bit to put in superposition (0-2 only)
        """
        if card_id not in self.card_register_map:
            raise ValueError(f"Card {card_id} not found in circuit")

        if bit_index < 0 or bit_index > 2:
            raise ValueError(
                f"Invalid bit index: {bit_index}. Must be 0-2 (rank bits only).\n"
                f"  Bit 0: ±1 rank change\n"
                f"  Bit 1: ±2 rank change\n"
                f"  Bit 2: ±4 rank change"
            )

        reg, start, _ = self.card_register_map[card_id]

        # Apply Hadamard to create superposition
        self.circuit.h(reg[bit_index])
        # Record in history as self-superposition (no extra parameter)
        self.entanglement_history.append((card_id, "SELF", bit_index, "H", None))

    def apply_phase(self, card_id: str, bit_index: int, angle: Optional[float] = None):
        """
        Apply Phase (Z) gate to a specific bit of a card to create interference.

        Args:
            card_id: Identifier of the card
            bit_index: Which rank bit to apply phase to (0-2 only)
        """
        if card_id not in self.card_register_map:
            raise ValueError(f"Card {card_id} not found in circuit")

        if bit_index < 0 or bit_index > 2:
            raise ValueError(
                f"Invalid bit index: {bit_index}. Must be 0-2 (rank bits only).\n"
                f"  Bit 0: ±1 rank change\n"
                f"  Bit 1: ±2 rank change\n"
                f"  Bit 2: ±4 rank change"
            )

        reg, start, _ = self.card_register_map[card_id]

        # Default to pi (Z equivalent) if no angle provided
        if angle is None:
            angle = math.pi

        # Apply RZ rotation by `angle` (radians)
        # Qiskit expects the angle in radians
        self.circuit.rz(angle, reg[bit_index])

        # Record in history including the angle parameter
        self.entanglement_history.append((card_id, "PHASE", bit_index, "RZ", angle))

    # def prepare_measurement(self):
    #     """
    #     Add classical register for measurement at showdown.
    #     Should be called before measuring cards.
    #     """
    #     if self.classical_register is None:
    #         num_qubits = len(self.circuit.qubits)
    #         self.classical_register = ClassicalRegister(num_qubits, "meas")
    #         self.circuit.add_register(self.classical_register)

    def measure_cards(self):
        """
        Measure a specific card's qubits.

        Args:
            card_id: Identifier of card to measure
        """
        # Create one classical register sized to all qubits, only once
        if self.classical_register is None:
            num_qubits = len(self.circuit.qubits)
            self.classical_register = ClassicalRegister(num_qubits, "meas")
            self.circuit.add_register(self.classical_register)

            # Wire up all measurements exactly once
            for card_id in self.registered_cards:
                register, start_idx, _ = self.card_register_map[card_id]
                for i in range(6):
                    self.circuit.measure(
                        register[i], self.classical_register[start_idx + i]
                    )

    def get_circuit_diagram(self) -> str:
        """
        Get a text representation of the circuit.
        """
        return str(self.circuit.draw(output="text"))

    def get_entanglement_graph(self) -> Dict[str, List[Tuple[str, int]]]:
        """
        Get a graph representation of entangled cards.

        Returns:
            Dictionary mapping card_id -> list of (entangled_card_id, bit_index)
        """
        graph: Dict[str, List[Tuple[str, int]]] = {
            card_id: [] for card_id in self.registered_cards
        }

        for entry in self.entanglement_history:
            # entry layout: (card1, card2, bit_idx, op_name, optional)
            card1 = entry[0]
            card2 = entry[1]
            bit_idx = entry[2]

            # Skip SELF and PHASE entries - they're not bipartite entanglements
            if card2 in ["SELF", "PHASE"]:
                continue

            graph[card1].append((card2, bit_idx))
            graph[card2].append((card1, bit_idx))

        return graph

    def decode_measurement(self, card_id: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Decode a card after measurement, reading from the circuit's classical bitsring
        """
        bitstring = self._last_bitstring[0]
        total_bits = len(bitstring)
        _, start_idx, _ = self.card_register_map[card_id]

        # Read one bit from the global classical bitstring
        def read_bit(global_idx: int) -> int:
            pos = total_bits - 1 - global_idx
            return 1 if bitstring[pos] == "1" else 0

        rank_val = 0
        for i in range(4):
            rank_val |= read_bit(start_idx + i) << i

        suit_val = 0
        for i in range(2):
            suit_val |= read_bit(start_idx + 4 + i) << i

        rank = RANKS_INVERSE.get(rank_val, None)
        suit = SUITS_INVERSE.get(suit_val, None)

        return rank, suit

    def simulate(
        self,
        shots: int = 1024,
    ) -> Dict:
        """
        Simulate the circuit and return measurement results.

        Args:
            shots: Number of simulation shots
            max_shots: Maximum number of shots before giving up
            min_valid_ratio: Minimum ratio of valid shots (default 10%)

        Returns:
            Dictionary of measurement outcomes and their counts
        """
        backend = AerSimulator(method="matrix_product_state")
        job = backend.run(self.circuit, shots=shots)
        result = job.result()
        counts = result.get_counts(self.circuit)

        self._last_counts = counts
        self._last_bitstring = max(counts.items(), key=lambda kv: kv[1])

        return counts
