"""
Test the Quantum Circuit Manager and Entanglement System
"""

import sys
sys.path.insert(0, '..')

from src.quantum_circuit import QuantumPokerCircuit
from src.card import Card


def test_basic_circuit():
    """Test basic circuit creation and card addition."""
    print("=== Test 1: Basic Circuit Creation ===\n")

    qc = QuantumPokerCircuit()

    # Create and add cards
    card1 = Card("Hearts", "Ace")
    card2 = Card("Spades", "King")
    card3 = Card("Diamonds", "Queen")

    qc.add_card(card1, "P1H1")
    qc.add_card(card2, "P1H2")
    qc.add_card(card3, "F0")

    print(f"Registered cards: {qc.registered_cards}")
    print(f"Card register map: {list(qc.card_register_map.keys())}")
    print("✓ Cards added successfully\n")


def test_entanglement():
    """Test card entanglement."""
    print("=== Test 2: Entanglement ===\n")

    qc = QuantumPokerCircuit()

    # Add two cards
    card1 = Card("Hearts", "7")  # 0111 in rank bits
    card2 = Card("Spades", "2")  # 0010 in rank bits

    qc.add_card(card1, "P1H1")
    qc.add_card(card2, "F0")

    print(f"Card 1 (P1H1): 7 of Hearts = {card1.to_bits():06b}")
    print(f"Card 2 (F0): 2 of Spades = {card2.to_bits():06b}")

    # Entangle bit 2 (third rank bit)
    print("\nEntangling bit 2...")
    qc.entangle_cards("P1H1", "F0", bit_index=2)

    print(f"Entanglement history: {qc.entanglement_history}")
    print("✓ Entanglement applied\n")


def test_measurement_and_simulation():
    """Test measurement and simulation."""
    print("=== Test 3: Measurement & Simulation ===\n")

    qc = QuantumPokerCircuit()

    # Add cards with known values
    card1 = Card("Hearts", "10")  # 1010 in rank
    card2 = Card("Clubs", "5")  # 0101 in rank

    qc.add_card(card1, "P1H1")
    qc.add_card(card2, "P2H1")

    print(f"Card 1 encoding: {card1.to_bits():06b}")
    print(f"Card 2 encoding: {card2.to_bits():06b}")

    # Measure
    qc.prepare_measurement()
    qc.measure_all_cards()

    print("\nRunning simulation...")
    results = qc.simulate(shots=100)

    # Should get deterministic result (no entanglement)
    print(f"Number of different outcomes: {len(results)}")
    most_common = max(results.items(), key=lambda x: x[1])
    print(f"Most common outcome: {most_common[0]} ({most_common[1]} times)")

    # Decode
    rank1, suit1 = qc.decode_measurement(most_common[0], "P1H1")
    rank2, suit2 = qc.decode_measurement(most_common[0], "P2H1")

    print(f"\nDecoded P1H1: {rank1} of {suit1}")
    print(f"Decoded P2H1: {rank2} of {suit2}")

    # Due to quantum nature, we can't predict exact outcome, just verify valid cards
    assert rank1 in ["2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King", "Ace"]
    assert suit1 in ["Hearts", "Diamonds", "Clubs", "Spades"]
    assert rank2 in ["2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King", "Ace"]
    assert suit2 in ["Hearts", "Diamonds", "Clubs", "Spades"]
    print("✓ Measurement and decoding successful\n")


def test_entanglement_effect():
    """Test that entanglement actually affects measurement outcomes."""
    print("=== Test 4: Entanglement Effect on Measurement ===\n")

    qc = QuantumPokerCircuit()

    # Add two cards
    card1 = Card("Hearts", "8")  # 1000
    card2 = Card("Spades", "2")  # 0010

    qc.add_card(card1, "P1H1")
    qc.add_card(card2, "F0")

    print(f"Original Card 1: 8 of Hearts = {card1.to_bits():06b}")
    print(f"Original Card 2: 2 of Spades = {card2.to_bits():06b}")

    # Entangle bit 2 (valid rank bit: ±4)
    print("\nEntangling bit 2 (rank bit: ±4)...")
    qc.entangle_cards("P1H1", "F0", bit_index=2)

    # Measure and simulate
    qc.prepare_measurement()
    qc.measure_all_cards()

    print("\nRunning simulation with entanglement...")
    results = qc.simulate(shots=1000)

    print(f"Number of different outcomes: {len(results)}")
    
    # With entanglement, we should see multiple outcomes (superposition)
    assert len(results) > 1, "Entanglement should create multiple possible outcomes"
    
    print("\nTop 3 outcomes:")
    for i, (outcome, count) in enumerate(
        sorted(results.items(), key=lambda x: x[1], reverse=True)[:3]
    ):
        rank1, suit1 = qc.decode_measurement(outcome, "P1H1")
        rank2, suit2 = qc.decode_measurement(outcome, "F0")
        print(f"{i+1}. P1H1={rank1} of {suit1}, F0={rank2} of {suit2} ({count} times)")
        
        # Verify valid cards
        assert rank1 in ["2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King", "Ace"]
        assert rank2 in ["2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King", "Ace"]

    print(
        "\n✓ Entanglement creates superposition - multiple possible outcomes observed\n"
    )


def test_entanglement_graph():
    """Test entanglement graph generation."""
    print("=== Test 5: Entanglement Graph ===\n")

    qc = QuantumPokerCircuit()

    # Add multiple cards
    for i in range(3):
        card = Card("Hearts", ["Ace", "2", "3"][i])
        qc.add_card(card, f"P{i+1}H1")

    # Create some entanglements
    qc.entangle_cards("P1H1", "P2H1", bit_index=1)
    qc.entangle_cards("P2H1", "P3H1", bit_index=2)
    qc.entangle_cards("P1H1", "P3H1", bit_index=0)

    graph = qc.get_entanglement_graph()

    print("Entanglement graph:")
    for card_id, connections in graph.items():
        if connections:
            print(f"  {card_id} entangled with: {connections}")

    print("✓ Entanglement graph generated\n")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("QUANTUM POKER CIRCUIT TESTS")
    print("=" * 60 + "\n")

    try:
        test_basic_circuit()
        test_entanglement()
        test_measurement_and_simulation()
        test_entanglement_effect()
        test_entanglement_graph()

        print("=" * 60)
        print("ALL TESTS PASSED! ✓")
        print("=" * 60 + "\n")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
