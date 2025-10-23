"""
Global Quantum Circuit Manager for Quantum Poker

This module manages the global quantum circuit that contains all card registers
and ancilla bits needed for quantum operations during the game.
"""

import qiskit
from qiskit.circuit import AncillaRegister, QuantumRegister, ClassicalRegister
from typing import Dict, List, Tuple

from .card import Card


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

        # Ancilla identifier -> (register, index) mapping
        # e.g., "A0" -> (AncillaRegister, 0)
        self.ancilla_register_map: Dict[str, Tuple[AncillaRegister, int]] = {}

        # Track which cards have been added
        self.registered_cards: List[str] = []

        # Entanglement history: [(card1_id, card2_id, bit_index, operation_type)]
        self.entanglement_history: List[Tuple[str, str, int, str]] = []

        # Classical register for measurements (added at showdown)
        self.classical_register = None

    def add_card(self, card: Card, identifier: str) -> QuantumRegister:
        """
        Add a card to the global circuit with a unique identifier.

        Args:
            card: Card object to add
            identifier: Unique identifier (e.g., "P1H1", "F0", "T", "R")

        Returns:
            The quantum register slice for this card
        """
        if identifier in self.card_register_map:
            raise ValueError(f"Card identifier {identifier} already exists")

        # Create a 6-qubit register for this card
        register = QuantumRegister(6, name=identifier)
        self.circuit.add_register(register)

        # Store mapping
        start_idx = len(self.circuit.qubits) - 6
        end_idx = len(self.circuit.qubits)
        self.card_register_map[identifier] = (register, start_idx, end_idx)
        self.registered_cards.append(identifier)

        # Update card object
        card.set_identifier(identifier)
        card.register = register

        # Prepare the card state
        card.prepare(self.circuit, start_idx)

        return register

    def add_ancilla(self, identifier: str):
        """
        Add an ancilla qubit for quantum operations.

        Args:
            identifier: Unique identifier (e.g., "A0", "A1")

        Returns:
            The ancilla qubit
        """
        if identifier in self.ancilla_register_map:
            raise ValueError(f"Ancilla identifier {identifier} already exists")

        ancilla = AncillaRegister(1, name=identifier)
        self.circuit.add_register(ancilla)

        idx = len(self.circuit.qubits) - 1
        self.ancilla_register_map[identifier] = (ancilla, idx)

        return ancilla[0]

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

            self.entanglement_history.append((card1_id, card2_id, bit_index, "H+CNOT"))

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
        
        # Record in history as self-superposition
        self.entanglement_history.append((card_id, "SELF", bit_index, "H"))

    def apply_phase(self, card_id: str, bit_index: int):
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
        
        # Apply Z gate (phase flip)
        self.circuit.z(reg[bit_index])
        
        # Record in history
        self.entanglement_history.append((card_id, "PHASE", bit_index, "Z"))

    def prepare_measurement(self):
        """
        Add classical register for measurement at showdown.
        Should be called before measuring cards.
        """
        if self.classical_register is None:
            num_qubits = len(self.circuit.qubits)
            self.classical_register = ClassicalRegister(num_qubits, "meas")
            self.circuit.add_register(self.classical_register)

    def measure_card(self, card_id: str):
        """
        Measure a specific card's qubits.

        Args:
            card_id: Identifier of card to measure
        """
        if self.classical_register is None:
            self.prepare_measurement()

        if card_id not in self.card_register_map:
            raise ValueError(f"Card {card_id} not found")

        register, start_idx, end_idx = self.card_register_map[card_id]

        # Measure all 6 qubits of the card
        for i in range(6):
            self.circuit.measure(register[i], self.classical_register[start_idx + i])

    def measure_all_cards(self):
        """
        Measure all cards in the circuit (called at showdown).
        """
        if self.classical_register is None:
            self.prepare_measurement()

        for card_id in self.registered_cards:
            self.measure_card(card_id)

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

        for card1, card2, bit_idx, _ in self.entanglement_history:
            # Skip SELF and PHASE operations - they're not entanglements between cards
            if card2 in ["SELF", "PHASE"]:
                continue
            
            graph[card1].append((card2, bit_idx))
            graph[card2].append((card1, bit_idx))

        return graph

    def simulate(
        self,
        shots: int = 1024,
        filter_invalid: bool = True,
        max_shots: int = 50000,
        min_valid_ratio: float = 0.1,
    ) -> Dict:
        """
        Simulate the circuit and return measurement results.

        Args:
            shots: Number of simulation shots
            filter_invalid: If True, only return valid card measurements
            max_shots: Maximum number of shots before giving up
            min_valid_ratio: Minimum ratio of valid shots (default 10%)

        Returns:
            Dictionary of measurement outcomes and their counts
        """
        from qiskit_aer import Aer

        backend = Aer.get_backend("qasm_simulator")
        job = backend.run(self.circuit, shots=shots)
        result = job.result()
        counts = result.get_counts(self.circuit)

        if filter_invalid:
            # Filter out invalid measurements
            valid_counts = {}
            invalid_count = 0
            for bitstring, count in counts.items():
                if self._is_valid_measurement(bitstring):
                    valid_counts[bitstring] = count
                else:
                    invalid_count += count

            valid_total = sum(valid_counts.values())
            valid_ratio = valid_total / shots if shots > 0 else 0

            if valid_counts and valid_ratio >= min_valid_ratio:
                # Show validation statistics
                print(
                    f"Validation: {valid_total} valid, {invalid_count} invalid out of {shots} shots ({100*valid_ratio:.1f}% valid)"
                )
                return valid_counts

            # If not enough valid outcomes and we haven't hit max, try more shots
            if shots < max_shots:
                new_shots = min(shots * 3, max_shots)
                print(
                    f"Warning: Only {100*valid_ratio:.1f}% valid measurements ({valid_total}/{shots}). Increasing to {new_shots}..."
                )
                return self.simulate(
                    shots=new_shots,
                    filter_invalid=True,
                    max_shots=max_shots,
                    min_valid_ratio=min_valid_ratio,
                )
            else:
                # If we have some valid measurements, use them even if below threshold
                if valid_counts:
                    print(
                        f"Note: Using {valid_total} valid measurements out of {shots} ({100*valid_ratio:.1f}% valid)"
                    )
                    return valid_counts

                # Give up and return best effort
                print(
                    f"ERROR: Could not find enough valid measurements after {shots} shots!"
                )
                print("Returning unfiltered results. Cards may have invalid values.")
                return counts

        return counts

    def _is_valid_measurement(self, bitstring: str) -> bool:
        """
        Check if a measurement bitstring contains only valid card values.

        Args:
            bitstring: Full measurement bitstring

        Returns:
            True if all cards have valid rank and suit values
        """
        for card_id in self.registered_cards:
            rank, suit = self.decode_measurement(bitstring, card_id)
            if rank is None or suit is None:
                return False
        return True

    def decode_measurement(self, bitstring: str, card_id: str) -> Tuple[str, str]:
        """
        Decode a measurement bitstring to extract card rank and suit.

        Args:
            bitstring: Full measurement bitstring
            card_id: Card identifier to extract

        Returns:
            Tuple of (rank, suit) or (None, None) if invalid
        """
        if card_id not in self.card_register_map:
            raise ValueError(f"Card {card_id} not found")

        _, start_idx, end_idx = self.card_register_map[card_id]

        # Extract the 6 bits for this card
        # Bitstring is reversed in Qiskit
        total_bits = len(bitstring)
        card_bits = bitstring[total_bits - end_idx : total_bits - start_idx]

        # Reverse to get correct order
        card_bits = card_bits[::-1]

        # Extract rank (bits 0-3) and suit (bits 4-5)
        rank_bits = card_bits[:4]
        suit_bits = card_bits[4:6]

        rank_val = int(rank_bits, 2)
        suit_val = int(suit_bits, 2)

        # Validate rank (must be 1-13, excluding 0, 14-15)
        if rank_val == 0 or rank_val > 13:
            return None, None

        # Map to rank names
        rank_map = {
            1: "Ace",
            2: "2",
            3: "3",
            4: "4",
            5: "5",
            6: "6",
            7: "7",
            8: "8",
            9: "9",
            10: "10",
            11: "Jack",
            12: "Queen",
            13: "King",
        }

        suit_map = {0: "Spades", 1: "Diamonds", 2: "Clubs", 3: "Hearts"}

        return rank_map.get(rank_val), suit_map.get(suit_val)
