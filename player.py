class Player:
    def __init__(self, name, number):
        self.name = name
        self.number = number
        self.hand = []
        self.chips = 1000
        self.quantum_chips = 5
        self.current_bet = 0
        self.folded = False
