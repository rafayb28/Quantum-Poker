import qiskit

SUITS = {
    "Spades": 0b00,
    "Diamonds": 0b01,
    "Clubs": 0b10,
    "Hearts": 0b11,
}
RANKS = {
    "Ace": 0b0001,
    "2": 0b0010,
    "3": 0b0011,
    "4": 0b0100,
    "5": 0b0101,
    "6": 0b0110,
    "7": 0b0111,
    "8": 0b1000,
    "9": 0b1001,
    "10": 0b1010,
    "Jack": 0b1011,
    "Queen": 0b1100,
    "King": 0b1101,
}  # NOTE: values 0, 14-15 are unused/invalid


class Card:
    def __init__(self, suit: str, rank: str):
        if suit not in SUITS:
            raise ValueError(f"Invalid suit: {suit}")
        if rank not in RANKS:
            raise ValueError(f"Invalid rank: {rank}")

        self.suit = suit
        self.rank = rank
        self.identifier = "N"
        self.register = qiskit.QuantumRegister(6)

    def __str__(self):
        return self.identifier

    def __repr__(self):
        return f"Card({self.suit}, {self.rank}, {self.identifier})"

    def set_identifier(self, identifier: str):
        self.identifier = identifier

    def to_bits(self) -> int:
        suit_bits = SUITS[self.suit]
        rank_bits = RANKS[self.rank]
        return (suit_bits << 4) | rank_bits

    def prepare(self, qc: qiskit.QuantumCircuit):
        """
        Called once the register has been added to the global
        circuit. Apply X gates to prepare the needed state
        """
        bits = self.to_bits()
        for i in range(6):
            if (bits >> i) & 1:
                qc.x(self.register[i])
