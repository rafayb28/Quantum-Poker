class Player:
    def __init__(self, name, number, starting_chips=1000, starting_quantum_chips=2):
        self.name = name
        self.number = number
        self.hand = []
        self.chips = starting_chips
        self.quantum_chips = starting_quantum_chips
        self.current_bet = 0
        self.folded = False
        self.all_in = False
        self.total_bet_this_round = 0
        self.entanglement_history = []  # Track entanglements this hand

    def bet(self, amount: int) -> int:
        """Place a bet. Returns actual amount bet (could be less if all-in)."""
        if self.folded or self.all_in:
            return 0

        if amount >= self.chips:
            # All-in
            actual_bet = self.chips
            self.chips = 0
            self.current_bet += actual_bet
            self.total_bet_this_round += actual_bet
            self.all_in = True
            return actual_bet

        self.chips -= amount
        self.current_bet += amount
        self.total_bet_this_round += amount
        return amount

    def call(self, amount_to_call: int) -> int:
        """Call the current bet. Returns actual amount called."""
        return self.bet(amount_to_call)

    def raise_bet(self, current_bet: int, raise_amount: int) -> int:
        """Raise the bet. Returns total amount raised."""
        amount_to_call = current_bet - self.current_bet
        total_bet = amount_to_call + raise_amount
        return self.bet(total_bet)

    def check(self) -> bool:
        """Check (only valid if no bet to call). Returns True if successful."""
        if self.folded or self.all_in:
            return False
        return True

    def fold(self):
        """Fold the hand."""
        if not self.all_in:
            self.folded = True

    def reset_for_new_round(self):
        """Reset player state for a new betting round."""
        self.current_bet = 0
        self.total_bet_this_round = 0

    def reset_for_new_hand(self):
        """Reset player state for a new hand."""
        self.hand = []
        self.current_bet = 0
        self.total_bet_this_round = 0
        self.folded = False
        self.all_in = False

    def use_quantum_chip(self) -> bool:
        """Use a quantum chip for quantum action. Returns True if successful."""
        if self.quantum_chips > 0:
            self.quantum_chips -= 1
            return True
        return False

    def to_dict(self, reveal_cards: bool = False):
        """Convert player state to dictionary for API."""
        return {
            "name": self.name,
            "number": self.number,
            "chips": self.chips,
            "quantum_chips": self.quantum_chips,
            "current_bet": self.current_bet,
            "total_bet_this_round": self.total_bet_this_round,
            "folded": self.folded,
            "all_in": self.all_in,
            "hand": (
                [{"suit": card.suit, "rank": card.rank} for card in self.hand]
                if reveal_cards
                else None
            ),
            "entanglement_history": self.entanglement_history if reveal_cards else [],
        }
