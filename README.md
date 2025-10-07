# 1 | Representation of cards
- Definition: A hole card is any of the two private cards held by each player. Community cards are the public cards dealt in the flop, turn, and river.
- 1.1: Each card is its own register containing 6 bits (0-64) with 0-51 used to encode the 52 cards.
    - Values 52-64 must be enforced to be invalid.
- 1.2: Bits 0-3 (0-15) used to represent value of card (A,2,...,Q,K).
    - The values of 13-15 must be enforced to be invalid.
- 1.3: The remaining 2 bits are used to represent the suit: 00 = spades, 01 = diamonds, 10 = clubs, 11 = hearts
- 1.4: All registers shall be part of a global circuit, where each card is its own slice within the circuit.
    - There will be a global dictionary containing a card identifier and the register for that card within the global circuit. Community cards are identified by F0, F1, F2, T, and R. Hole cards are identified by PxHx for a *player x* and *hole card x*.
    - There will be another global dictionary containing an ancilla bit identifier (A0, A1, ...) and its index within the global circuit.
- 1.5: All registers remain unmeasured until showdown.

# 2 | Entanglement
- 2.1: You may entangle your card with any other card, including community cards.
    - Option 1: Entangle one bit of your cards encoding with one bit of the other cards encoding (of the 4 possible value bits). The source and target bits are the same.

    $$\text{Given two states} \ket{A}, \ket{B} \text{we can entangle one qubit of each state, } x. \\ \text{1. Apply H onto } \ket{A_x} \\ \text{2. Apply } CNOT_{A_x \rightarrow B_x}$$

    - Option 2: TBD
    - Option 3: TBD
    - Option 4: TBD
    - Option 5: TBD