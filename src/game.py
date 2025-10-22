"""
Main Poker Game Logic with Quantum Circuit Integration
"""

from typing import List, Optional, Dict
import random

from .card import Card, SUITS, RANKS
from .player import Player
from .quantum_circuit import QuantumPokerCircuit
from .hand_evaluator import HandEvaluator
from .side_pot_manager import SidePotManager


class QuantumPoker:
    """
    Main game class that manages the poker game with quantum mechanics.
    """

    def __init__(self, num_players: int, starting_chips: int = 1000, small_blind: int = 10, big_blind: int = 20):
        if num_players < 2 or num_players > 10:
            raise ValueError("Number of players must be between 2 and 10")

        self.num_players = num_players
        self.starting_chips = starting_chips
        self.small_blind = small_blind
        self.big_blind = big_blind
        
        # Initialize players with empty names - names will be set when players join
        self.players: List[Player] = [
            Player("", i + 1, starting_chips=starting_chips) for i in range(num_players)
        ]

        # Initialize quantum circuit manager
        self.qc_manager = QuantumPokerCircuit()

        # Create full deck
        self.deck: List[Card] = []
        for suit in SUITS:
            for rank in RANKS:
                self.deck.append(Card(suit, rank))

        self.shuffle_deck()

        # Community cards
        self.flop: List[Optional[Card]] = [None, None, None]
        self.turn: Optional[Card] = None
        self.river: Optional[Card] = None

        # Game state
        self.current_round = "waiting"  # waiting, pre-flop, flop, turn, river, showdown
        self.pot = 0
        self.current_bet = 0
        self.dealer_position = 0
        self.current_player_idx = 0

        # Betting round tracking
        self.players_acted_this_round = set()  # Track which player indices have acted
        self.last_aggressor_idx = -1  # Track who last raised (to know when round is complete)
        self.betting_round_active = False

        # Deck index for dealing
        self.deck_index = 0
        
        # Session tracking
        self.hand_number = 0
        self.session_active = False
        self.hands_played = 0
        self.game_started = False
        
        # Winner info from last showdown
        self.last_winner_info = None

    def shuffle_deck(self):
        """Shuffle the deck randomly."""
        random.shuffle(self.deck)

    def start_game(self):
        """
        Start the game by dealing initial cards and posting blinds.
        Transitions from 'waiting' to 'pre-flop' state.
        """
        if self.game_started:
            raise ValueError("Game has already been started")
        
        if self.current_round != "waiting":
            raise ValueError("Game must be in 'waiting' state to start")
        
        # Transition to pre-flop
        self.current_round = "pre-flop"
        self.game_started = True
        
        # Post blinds (ante)
        self.post_blinds()
        
        # Deal hole cards to all players
        self.deal_hole_cards()
        
        # Start the first betting round
        self.start_betting_round()

    def start_next_hand(self):
        """
        Start a new hand after showdown or complete.
        - Eliminates players with 0 chips
        - Rotates dealer position
        - Resets game state for new hand
        - Deals new cards
        """
        if self.current_round not in ["showdown", "complete"]:
            raise ValueError("Can only start next hand after showdown or complete")
        
        # Remove players with no chips left
        self.players = [p for p in self.players if p.chips > 0]
        
        if len(self.players) < 2:
            raise ValueError("Not enough players with chips to continue")
        
        # Rotate dealer position
        self.dealer_position = (self.dealer_position + 1) % len(self.players)
        
        # Reset game state
        self.pot = 0
        self.current_bet = 0
        self.players_acted_this_round = set()
        self.last_aggressor_idx = -1
        self.betting_round_active = False
        self.last_winner_info = None
        
        # Reset deck and shuffle
        self.deck = []
        for suit in SUITS:
            for rank in RANKS:
                self.deck.append(Card(suit, rank))
        self.shuffle_deck()
        self.deck_index = 0
        
        # Reset community cards
        self.flop = [None, None, None]
        self.turn = None
        self.river = None
        
        # Reset quantum circuit
        self.qc_manager = QuantumPokerCircuit()
        
        # Reset all players for new hand
        for player in self.players:
            player.hand = []
            player.folded = False
            player.all_in = False
            player.current_bet = 0
            player.quantum_chips = 2  # Refresh quantum chips each hand
        
        # Increment hand counter
        self.hand_number += 1
        self.hands_played += 1
        
        # Start new hand
        self.current_round = "pre-flop"
        self.post_blinds()
        self.deal_hole_cards()
        self.start_betting_round()

    def deal_hole_cards(self):
        """
        Deal two hole cards to each player and add them to the quantum circuit.
        """
        for player in self.players:
            if player.folded:
                continue

            # Deal two cards
            card1 = self.deck[self.deck_index]
            card2 = self.deck[self.deck_index + 1]
            self.deck_index += 2

            # Add to quantum circuit with identifiers
            identifier1 = f"P{player.number}H1"
            identifier2 = f"P{player.number}H2"

            self.qc_manager.add_card(card1, identifier1)
            self.qc_manager.add_card(card2, identifier2)

            # Add to player's hand
            player.hand = [card1, card2]

    def deal_flop(self):
        """
        Deal the flop (3 community cards).
        """
        if self.current_round != "pre-flop":
            raise ValueError("Flop can only be dealt after pre-flop")

        # Burn one card (optional in quantum version, but keeping for tradition)
        self.deck_index += 1

        # Deal 3 cards
        for i in range(3):
            card = self.deck[self.deck_index]
            self.deck_index += 1

            identifier = f"F{i}"
            self.qc_manager.add_card(card, identifier)
            self.flop[i] = card

        self.current_round = "flop"

    def deal_turn(self):
        """
        Deal the turn (4th community card).
        """
        if self.current_round != "flop":
            raise ValueError("Turn can only be dealt after flop")

        # Burn one card
        self.deck_index += 1

        card = self.deck[self.deck_index]
        self.deck_index += 1

        self.qc_manager.add_card(card, "T")
        self.turn = card

        self.current_round = "turn"

    def deal_river(self):
        """
        Deal the river (5th community card).
        """
        if self.current_round != "turn":
            raise ValueError("River can only be dealt after turn")

        # Burn one card
        self.deck_index += 1

        card = self.deck[self.deck_index]
        self.deck_index += 1

        self.qc_manager.add_card(card, "R")
        self.river = card

        self.current_round = "river"

    def entangle_cards(
        self, player: Player, source_card_idx: int, target_card_id: str, bit_index: int
    ):
        """
        Allow a player to entangle one of their cards with another card.

        Args:
            player: The player performing the entanglement
            source_card_idx: Index of player's hole card (0 or 1)
            target_card_id: Identifier of target card (e.g., "F0", "P2H1")
            bit_index: Which rank bit to entangle (0-2 only)
                      0 = ±1 rank, 1 = ±2 rank, 2 = ±4 rank
        """
        if player.quantum_chips <= 0:
            raise ValueError("Player has no quantum chips left")

        if source_card_idx not in [0, 1]:
            raise ValueError("Invalid hole card index")
        
        if bit_index < 0 or bit_index > 2:
            raise ValueError(
                f"Invalid bit index: {bit_index}. Only rank bits 0-2 allowed.\n"
                f"  Bit 0: ±1 rank variation\n"
                f"  Bit 1: ±2 rank variation\n"
                f"  Bit 2: ±4 rank variation"
            )

        # Get source card identifier
        source_card_id = f"P{player.number}H{source_card_idx + 1}"

        # Perform entanglement
        self.qc_manager.entangle_cards(source_card_id, target_card_id, bit_index)

        # Deduct quantum chip
        player.quantum_chips -= 1

        bit_effect = ["±1", "±2", "±4"][bit_index]
        print(
            f"{player.name} entangled {source_card_id} with {target_card_id} "
            f"(bit {bit_index}: {bit_effect} rank change)"
        )
    
    def is_betting_round_complete(self) -> bool:
        """
        Check if the current betting round is complete.
        A round is complete when:
        1. All active players who have joined have acted at least once
        2. All bets are matched (everyone at same bet level or all-in)
        3. Or only one player remains (everyone else folded)
        """
        # Check if only one player hasn't folded
        active_players = [p for p in self.players if not p.folded and p.name and p.name.strip()]
        if len(active_players) <= 1:
            print(f"[Betting] Only {len(active_players)} active player(s) remaining - round complete!")
            return True
        
        # Check if all active non-all-in players have matched the current bet
        players_who_can_act = [p for p in active_players if not p.all_in]
        
        # If everyone is all-in, betting is complete
        if not players_who_can_act:
            print(f"[Betting] All {len(active_players)} active players are all-in - auto-progressing!")
            return True
        
        # Check if all players who can act have:
        # 1. Acted at least once this round
        # 2. Matched the current bet
        for i, player in enumerate(self.players):
            # Skip players who haven't joined
            if not player.name or not player.name.strip():
                continue
            if player.folded or player.all_in:
                continue
            
            # Check if player has acted
            if i not in self.players_acted_this_round:
                return False
            
            # Check if player has matched the bet
            if player.current_bet < self.current_bet:
                return False
        
        # If there was a raise, ensure we've gone back to the raiser
        # (everyone after the raiser has had a chance to respond)
        if self.last_aggressor_idx >= 0:
            # Check if all players after the aggressor have acted
            for i in range(self.num_players):
                player = self.players[i]
                # Skip players who haven't joined
                if not player.name or not player.name.strip():
                    continue
                if player.folded or player.all_in:
                    continue
                if i not in self.players_acted_this_round:
                    return False
        
        return True
    
    def start_betting_round(self):
        """
        Initialize a new betting round by resetting tracking and player bets.
        """
        # Reset player bets for new round
        for player in self.players:
            player.reset_for_new_round()
        
        # Reset betting round tracking
        self.current_bet = 0
        self.players_acted_this_round = set()
        self.last_aggressor_idx = -1
        self.betting_round_active = True
        
        # Set starting player based on round
        if self.current_round == "pre-flop":
            # After ante system, start with player after dealer
            self.current_player_idx = (self.dealer_position + 1) % self.num_players
        else:
            # Post-flop rounds start with player after dealer
            self.current_player_idx = (self.dealer_position + 1) % self.num_players
        
        # Skip to first non-folded, non-all-in player who has joined
        attempts = 0
        while attempts < self.num_players:
            player = self.players[self.current_player_idx]
            # Skip if: folded, all-in, OR hasn't joined the game (empty name)
            if not player.folded and not player.all_in and player.name and player.name.strip():
                break
            self.current_player_idx = (self.current_player_idx + 1) % self.num_players
            attempts += 1

    def auto_progress_round(self) -> Dict:
        """
        Automatically progress to the next round if betting is complete.
        Returns dict with info about what happened.
        """
        if not self.is_betting_round_complete():
            return {"progressed": False, "message": "Betting not complete"}
        
        # Mark betting round as inactive
        self.betting_round_active = False
        
        # Check for single winner (everyone else folded)
        # Only count players who have actually joined the game
        active_players = [p for p in self.players if not p.folded and p.name and p.name.strip()]
        print(f"[Auto Progress] Active players: {len(active_players)} ({[p.name for p in active_players]})")
        if len(active_players) == 1:
            winner = active_players[0]
            pot_amount = self.pot
            winner.chips += self.pot
            print(f"\n🏆 {winner.name} wins {pot_amount} chips (all others folded)!")
            print(f"   {winner.name} now has {winner.chips} chips")
            self.pot = 0
            self.current_round = "complete"
            return {
                "progressed": True,
                "action": "winner_by_fold",
                "winner": winner.name,
                "pot_won": pot_amount,
                "new_round": "complete"
            }
        
        # Progress to next betting round
        if self.current_round == "pre-flop":
            self.deal_flop()
            self.start_betting_round()
            return {"progressed": True, "action": "deal_flop", "new_round": "flop"}
        elif self.current_round == "flop":
            self.deal_turn()
            self.start_betting_round()
            return {"progressed": True, "action": "deal_turn", "new_round": "turn"}
        elif self.current_round == "turn":
            self.deal_river()
            self.start_betting_round()
            return {"progressed": True, "action": "deal_river", "new_round": "river"}
        elif self.current_round == "river":
            # Trigger showdown
            showdown_results = self.showdown()
            return {
                "progressed": True,
                "action": "showdown",
                "new_round": "showdown",
                "results": showdown_results
            }
        
        return {"progressed": False, "message": "Already at final round"}

    def betting_round(self, round_name: str = None):
        """
        Execute a betting round with quantum action support.
        
        Args:
            round_name: Optional name of the round (pre-flop, flop, turn, river)
        """
        if round_name:
            print(f"\n=== {round_name.upper()} BETTING ROUND ===")
        
        # Reset bets for new round
        for player in self.players:
            player.reset_for_new_round()
        
        self.current_bet = 0
        last_aggressor_idx = -1  # Track who last raised
        
        # Start betting after big blind (or dealer for post-flop)
        if round_name == "pre-flop":
            start_idx = (self.dealer_position + 3) % self.num_players
        else:
            start_idx = (self.dealer_position + 1) % self.num_players
        
        self.current_player_idx = start_idx
        players_acted = 0
        players_to_act = sum(1 for p in self.players if not p.folded and not p.all_in)
        
        # Continue until all players have acted and bets are matched
        while players_acted < len(self.players):
            player = self.players[self.current_player_idx]
            
            # Skip if folded or all-in
            if player.folded or player.all_in:
                self.current_player_idx = (self.current_player_idx + 1) % self.num_players
                players_acted += 1
                continue
            
            # Check if player needs to act
            amount_to_call = self.current_bet - player.current_bet
            
            # If everyone has matched the bet and we've gone full circle, round is over
            if amount_to_call == 0 and players_acted >= players_to_act:
                break
            
            # Player's turn
            print(f"\n{player.name}'s turn:")
            print(f"  Chips: {player.chips} | Quantum Chips: {player.quantum_chips}")
            print(f"  Current bet: {player.current_bet} | To call: {amount_to_call}")
            print(f"  Pot: {self.pot}")
            
            # In actual implementation, this would come from user input or AI
            # For now, we'll have a placeholder that can be overridden
            action = self._get_player_action(player, amount_to_call)
            
            if action["type"] == "fold":
                player.fold()
                print(f"{player.name} folds")
                players_to_act -= 1
                
            elif action["type"] == "check":
                if amount_to_call > 0:
                    print(f"Cannot check, must call {amount_to_call}")
                    continue
                print(f"{player.name} checks")
                
            elif action["type"] == "call":
                actual_bet = player.call(amount_to_call)
                self.pot += actual_bet
                print(f"{player.name} calls {actual_bet}")
                if player.all_in:
                    print(f"{player.name} is ALL-IN!")
                    players_to_act -= 1
                    
            elif action["type"] == "raise":
                raise_amount = action.get("amount", 0)
                if raise_amount < self.current_bet * 2:
                    print(f"Minimum raise is {self.current_bet * 2}")
                    continue
                
                actual_bet = player.raise_bet(self.current_bet, raise_amount)
                self.pot += actual_bet
                self.current_bet = player.current_bet
                last_aggressor_idx = self.current_player_idx
                print(f"{player.name} raises to {self.current_bet}")
                
                if player.all_in:
                    print(f"{player.name} is ALL-IN!")
                    players_to_act -= 1
                
                # Reset action counter since everyone needs to respond to raise
                players_acted = 0
                
            elif action["type"] == "quantum":
                # Quantum action during betting round
                self._handle_quantum_action(player, action)
                # Quantum action doesn't count as betting action, player still needs to bet
                continue
            
            self.current_player_idx = (self.current_player_idx + 1) % self.num_players
            players_acted += 1
            
            # Check if only one player remains
            active_players = sum(1 for p in self.players if not p.folded)
            if active_players == 1:
                print("\nAll other players folded!")
                break
        
        print(f"\nBetting round complete. Pot: {self.pot}")
    
    def _get_player_action(self, player: Player, amount_to_call: int) -> Dict:
        """
        Get player action. Override this method for AI or network input.
        Default: simple logic for demonstration.
        """
        # Placeholder logic - in real game, this comes from UI/API
        if amount_to_call == 0:
            return {"type": "check"}
        elif amount_to_call < player.chips * 0.3:
            return {"type": "call"}
        else:
            return {"type": "fold"}
    
    def _handle_quantum_action(self, player: Player, action: Dict):
        """
        Handle quantum action during betting round.
        """
        try:
            source_idx = action.get("source_card_idx", 0)
            target_id = action.get("target_card_id", "")
            bit_index = action.get("bit_index", 0)
            
            if not player.use_quantum_chip():
                print(f"{player.name} has no quantum chips left!")
                return
            
            source_id = f"P{player.number}H{source_idx + 1}"
            self.qc_manager.entangle_cards(source_id, target_id, bit_index)
            
            bit_effect = ["±1", "±2", "±4"][bit_index]
            print(f"{player.name} used quantum action: entangled {source_id} with {target_id} (bit {bit_index}: {bit_effect})")
            
        except Exception as e:
            print(f"Quantum action failed: {e}")
            player.quantum_chips += 1  # Refund on error
    
    def post_blinds(self, ante: int = 10):
        """
        All players post ante to enter the round.
        
        Args:
            ante: Ante amount (default 10 chips)
        """
        print(f"\nAll players ante {ante} chips to enter")
        
        for player in self.players:
            if player.chips > 0 and not player.folded:
                ante_amount = player.bet(ante)
                self.pot += ante_amount
                print(f"  {player.name} antes: {ante_amount}")
        
        # No current bet after antes - everyone starts equal
        self.current_bet = 0
    
    def play_hand(self, ante: int = 10):
        """
        Play a complete hand with all betting rounds.
        
        Args:
            ante: Ante amount all players pay to enter (default 10)
        """
        print("\n" + "="*50)
        print("NEW HAND")
        print("="*50)
        
        # Reset players
        for player in self.players:
            player.reset_for_new_hand()
        
        # Reset game state
        self.pot = 0
        self.current_bet = 0
        self.deck_index = 0
        self.shuffle_deck()
        
        # Reset quantum circuit for new hand
        self.qc_manager = QuantumPokerCircuit()
        
        # Reset community cards
        self.flop = [None, None, None]
        self.turn = None
        self.river = None
        
        # Deal hole cards
        print("\nDealing hole cards...")
        self.deal_hole_cards()
        
        # Post ante
        self.post_blinds(ante)
        
        # Pre-flop betting
        self.current_round = "pre-flop"
        self.betting_round("pre-flop")
        
        # Check if hand is over
        if sum(1 for p in self.players if not p.folded) == 1:
            return self._award_pot()
        
        # Flop
        self.deal_flop()
        self.betting_round("flop")
        
        if sum(1 for p in self.players if not p.folded) == 1:
            return self._award_pot()
        
        # Turn
        self.deal_turn()
        self.betting_round("turn")
        
        if sum(1 for p in self.players if not p.folded) == 1:
            return self._award_pot()
        
        # River
        self.deal_river()
        self.betting_round("river")
        
        if sum(1 for p in self.players if not p.folded) == 1:
            return self._award_pot()
        
        # Showdown
        return self.showdown()
    
    def _award_pot(self):
        """Award pot to remaining player (when all others fold)."""
        winner = next(p for p in self.players if not p.folded)
        winner.chips += self.pot
        print(f"\n{winner.name} wins {self.pot} chips!")
        self.pot = 0
        return {"winner": winner.name, "amount": self.pot}

    def showdown(self) -> Dict:
        """
        Perform showdown: measure all cards and determine winner.

        Returns:
            Dictionary with simulation results and decoded cards
        """
        print("\n=== SHOWDOWN ===")
        
        # Check if only one player remains (shouldn't happen, but handle it)
        active_players = [p for p in self.players if not p.folded]
        if len(active_players) == 1:
            winner = active_players[0]
            pot_amount = self.pot
            winner.chips += self.pot
            print(f"\n🏆 {winner.name} wins {pot_amount} chips (only player remaining)!")
            print(f"   {winner.name} now has {winner.chips} chips")
            self.pot = 0
            self.current_round = "showdown"
            return {
                "results": {},
                "winning_bitstring": "",
                "decoded_cards": {},
                "total_shots": 0,
                "has_errors": False,
                "winner_info": {
                    "winners": [{
                        "player_num": winner.number,
                        "player_name": winner.name,
                        "hand_name": "Winner by Default",
                        "kickers": [],
                        "best_cards": []
                    }],
                    "all_hands": {}
                }
            }

        # Measure all cards
        self.qc_manager.measure_all_cards()

        # Run simulation without strict filtering (accept quantum measurement errors as part of gameplay)
        print("Running quantum measurement simulation...")
        results = self.qc_manager.simulate(shots=2048, filter_invalid=False)

        # Get most common outcome
        most_common = max(results.items(), key=lambda x: x[1])
        winning_bitstring = most_common[0]
        total_shots = sum(results.values())

        print(f"Most common outcome: {most_common[1]} shots ({100*most_common[1]/total_shots:.1f}%)\n")

        # Decode all cards
        decoded_cards = {}
        print("Final Card Values:")
        print("-" * 40)
        
        has_invalid = False
        for card_id in self.qc_manager.registered_cards:
            rank, suit = self.qc_manager.decode_measurement(winning_bitstring, card_id)
            
            # Handle invalid measurements as "quantum errors" - re-measure that specific card
            if rank is None or suit is None:
                has_invalid = True
                # For now, just mark as error - in production, could trigger re-measurement
                rank, suit = "ERROR", "ERROR"
            
            decoded_cards[card_id] = (rank, suit)
            
            # Pretty print card type
            if card_id.startswith("P"):
                player_num = card_id[1]
                card_num = card_id[3]
                card_display = f"{rank} of {suit}" if rank != "ERROR" else "⚠️ QUANTUM ERROR"
                print(f"Player {player_num} - Hole Card {card_num}: {card_display}")
            elif card_id.startswith("F"):
                flop_num = int(card_id[1]) + 1
                card_display = f"{rank} of {suit}" if rank != "ERROR" else "⚠️ QUANTUM ERROR"
                print(f"Flop Card {flop_num}: {card_display}")
            elif card_id == "T":
                card_display = f"{rank} of {suit}" if rank != "ERROR" else "⚠️ QUANTUM ERROR"
                print(f"Turn: {card_display}")
            elif card_id == "R":
                card_display = f"{rank} of {suit}" if rank != "ERROR" else "⚠️ QUANTUM ERROR"
                print(f"River: {card_display}")

        if has_invalid:
            print("\n⚠️  Note: Quantum errors occurred due to entanglement creating invalid card states.")
            print("   Using original (pre-measurement) cards for winner determination.")

        # Evaluate hands and determine winner
        # If quantum errors occurred, use original cards; otherwise use measured cards
        winner_info = None
        if has_invalid:
            winner_info = self._determine_winner_from_original_cards()
        else:
            winner_info = self._determine_winner(decoded_cards)
            
        if winner_info:
            print("\n" + "=" * 40)
            print("HAND EVALUATION")
            print("=" * 40)
            
            for player_num, hand_info in winner_info["all_hands"].items():
                print(f"\nPlayer {player_num}: {hand_info['hand_name']}")
                # best_cards are dicts with 'suit' and 'rank' keys
                cards_str = ', '.join([f"{c['rank']} of {c['suit']}" for c in hand_info['best_cards']])
                print(f"  Best 5 cards: {cards_str}")
            
            print("\n" + "=" * 40)
            if len(winner_info["winners"]) == 1:
                winner = winner_info["winners"][0]
                print(f"🏆 WINNER: Player {winner['player_num']} with {winner['hand_name']}!")
                print(f"   Wins {self.pot} chips")
            else:
                winner_nums = [w['player_num'] for w in winner_info["winners"]]
                print(f"🤝 TIE between Players {', '.join(map(str, winner_nums))}")
                print(f"   Split pot: {self.pot // len(winner_info['winners'])} chips each")
            print("=" * 40)
            
            # Award pot
            self._award_pot_to_winners(winner_info["winners"])

        self.current_round = "showdown"
        self.last_winner_info = winner_info  # Store for frontend access

        return {
            "results": results,
            "winning_bitstring": winning_bitstring,
            "decoded_cards": decoded_cards,
            "total_shots": total_shots,
            "has_errors": has_invalid,
            "winner_info": winner_info,
        }
    
    def _determine_winner(self, decoded_cards: Dict) -> Optional[Dict]:
        """
        Determine winner(s) from decoded cards.
        
        Returns:
            Dict with winner info or None if cards are invalid
        """
        try:
            # Reconstruct community cards from quantum measurement
            # decoded_cards format: {card_id: (rank, suit)}
            # Card constructor format: Card(suit, rank)
            community_cards = []
            for i in range(3):
                if f"F{i}" in decoded_cards:
                    rank, suit = decoded_cards[f"F{i}"]
                    if rank != "ERROR" and suit != "ERROR":
                        community_cards.append(Card(suit, rank))
            
            if "T" in decoded_cards:
                rank, suit = decoded_cards["T"]
                if rank != "ERROR" and suit != "ERROR":
                    community_cards.append(Card(suit, rank))
            
            if "R" in decoded_cards:
                rank, suit = decoded_cards["R"]
                if rank != "ERROR" and suit != "ERROR":
                    community_cards.append(Card(suit, rank))
            
            # Evaluate each player's hand
            player_hands = {}
            for player in self.players:
                if player.folded:
                    continue
                
                # Reconstruct player cards from quantum measurement
                player_cards = []
                for i in range(2):
                    card_id = f"P{player.number}H{i+1}"
                    if card_id in decoded_cards:
                        rank, suit = decoded_cards[card_id]
                        if rank != "ERROR" and suit != "ERROR":
                            player_cards.append(Card(suit, rank))
                
                if len(player_cards) == 2 and len(community_cards) >= 3:
                    hand_name, kickers, best_cards = HandEvaluator.get_best_hand(
                        player_cards, community_cards
                    )
                    player_hands[player.number] = {
                        "hand_name": hand_name,
                        "kickers": kickers,
                        "best_cards": best_cards,
                        "player": player
                    }
            
            if not player_hands:
                return None
            
            # Find winner(s) with suit-based tie-breaking
            best_hand = None
            best_hand_cards = None
            winners = []
            
            for player_num, hand_info in player_hands.items():
                if best_hand is None:
                    best_hand = (hand_info["hand_name"], hand_info["kickers"])
                    best_hand_cards = hand_info["best_cards"]
                    winners = [hand_info]
                else:
                    comparison = HandEvaluator.compare_hands(
                        (hand_info["hand_name"], hand_info["kickers"]),
                        best_hand,
                        hand_info["best_cards"],
                        best_hand_cards
                    )
                    if comparison > 0:
                        # New winner
                        best_hand = (hand_info["hand_name"], hand_info["kickers"])
                        best_hand_cards = hand_info["best_cards"]
                        winners = [hand_info]
                    elif comparison == 0:
                        # Tie (even after suit comparison)
                        winners.append(hand_info)
            
            return {
                "winners": [
                    {
                        "player_num": w["player"].number,
                        "player_name": w["player"].name,
                        "hand_name": w["hand_name"],
                        "kickers": w["kickers"],
                        "best_cards": [{"suit": c.suit, "rank": c.rank} for c in w["best_cards"]]
                    }
                    for w in winners
                ],
                "all_hands": {
                    player_num: {
                        "hand_name": hand_info["hand_name"],
                        "kickers": hand_info["kickers"],
                        "best_cards": [{"suit": c.suit, "rank": c.rank} for c in hand_info["best_cards"]],
                        "player_name": hand_info["player"].name,
                        "player_num": player_num
                    }
                    for player_num, hand_info in player_hands.items()
                }
            }
            
        except Exception as e:
            print(f"Error determining winner: {e}")
            return None
    
    def _determine_winner_from_original_cards(self) -> Optional[Dict]:
        """
        Determine winner using the original (pre-measurement) cards.
        This is used as a fallback when quantum measurement produces errors.
        
        Returns:
            Dict with winner info or None if cards are invalid
        """
        try:
            # Use existing flop, turn, river cards
            community_cards = []
            for card in self.flop:
                if card:
                    community_cards.append(card)
            if self.turn:
                community_cards.append(self.turn)
            if self.river:
                community_cards.append(self.river)
            
            # Evaluate each player's hand using their original hole cards
            player_hands = {}
            for player in self.players:
                if player.folded:
                    continue
                
                # Use the player's original hole cards
                player_cards = player.hand
                
                if len(player_cards) == 2 and len(community_cards) >= 3:
                    hand_name, kickers, best_cards = HandEvaluator.get_best_hand(
                        player_cards, community_cards
                    )
                    player_hands[player.number] = {
                        "hand_name": hand_name,
                        "kickers": kickers,
                        "best_cards": best_cards,
                        "player": player
                    }
            
            if not player_hands:
                return None
            
            # Find winner(s) with suit-based tie-breaking
            best_hand = None
            best_hand_cards = None
            winners = []
            
            for player_num, hand_info in player_hands.items():
                if best_hand is None:
                    best_hand = (hand_info["hand_name"], hand_info["kickers"])
                    best_hand_cards = hand_info["best_cards"]
                    winners = [hand_info]
                else:
                    comparison = HandEvaluator.compare_hands(
                        (hand_info["hand_name"], hand_info["kickers"]),
                        best_hand,
                        hand_info["best_cards"],
                        best_hand_cards
                    )
                    if comparison > 0:
                        # New winner
                        best_hand = (hand_info["hand_name"], hand_info["kickers"])
                        best_hand_cards = hand_info["best_cards"]
                        winners = [hand_info]
                    elif comparison == 0:
                        # Tie (even after suit comparison)
                        winners.append(hand_info)
            
            return {
                "winners": [
                    {
                        "player_num": w["player"].number,
                        "player_name": w["player"].name,
                        "hand_name": w["hand_name"],
                        "kickers": w["kickers"],
                        "best_cards": [{"suit": c.suit, "rank": c.rank} for c in w["best_cards"]]
                    }
                    for w in winners
                ],
                "all_hands": {
                    player_num: {
                        "hand_name": hand_info["hand_name"],
                        "kickers": hand_info["kickers"],
                        "best_cards": [{"suit": c.suit, "rank": c.rank} for c in hand_info["best_cards"]],
                        "player_name": hand_info["player"].name,
                        "player_num": player_num
                    }
                    for player_num, hand_info in player_hands.items()
                }
            }
            
        except Exception as e:
            print(f"Error determining winner from original cards: {e}")
            return None
    
    def _award_pot_to_winners(self, winners: List[Dict]):
        """
        Award pot to winner(s) using side pot logic for all-in scenarios.
        """
        if not winners:
            print("⚠️ No winners to award pot to!")
            return
        
        print(f"\n💰 Awarding pot of {self.pot} chips to {len(winners)} winner(s)")
        
        # Check if any players are all-in (need side pots)
        has_all_in = any(p.all_in for p in self.players if not p.folded)
        
        if not has_all_in:
            # Simple case: split pot among winners
            pot_share = self.pot // len(winners)
            remainder = self.pot % len(winners)
            
            print(f"Simple pot split: {pot_share} chips each (no all-ins)")
            
            for i, winner in enumerate(winners):
                player = next(p for p in self.players if p.number == winner["player_num"])
                # Give remainder to first winner(s) in position order
                extra = 1 if i < remainder else 0
                total_award = pot_share + extra
                player.chips += total_award
                print(f"  {player.name} (Player {player.number}): +{total_award} chips (now has {player.chips})")
            
            self.pot = 0
            print(f"Pot is now: {self.pot}")
        else:
            # Complex case: use side pot manager
            side_pot_mgr = SidePotManager()
            
            # Calculate players' total bets this hand
            players_bets = {}
            for player in self.players:
                if not player.folded:
                    # total_bet_this_round only tracks current round, we need hand total
                    # For now, use a simple approach based on pot and all-in status
                    players_bets[player.number] = (player.total_bet_this_round, player.all_in)
            
            # Calculate side pots
            pots = side_pot_mgr.calculate_pots(players_bets)
            
            # Build hand rankings for side pot distribution
            player_hands_dict = {}
            for winner in winners:
                player_hands_dict[winner["player_num"]] = (
                    winner["hand_name"],
                    winner["kickers"]
                )
            
            # Award side pots
            winnings = side_pot_mgr.award_pots(player_hands_dict)
            
            for player_num, amount in winnings.items():
                player = next(p for p in self.players if p.number == player_num)
                player.chips += amount
                print(f"{player.name} wins {amount} chips")
            
            self.pot = 0

    def get_game_state(self, viewing_player: Optional[int] = None) -> Dict:
        """
        Get current game state for API/frontend consumption.
        
        Args:
            viewing_player: Player number (1-indexed). If provided, hide other players' hole cards.

        Returns:
            Dictionary representing current game state
        """
        state = {
            "round": self.current_round,
            "pot": self.pot,
            "current_bet": self.current_bet,
            "dealer_position": self.dealer_position,
            "current_player": self.current_player_idx + 1,  # Convert to 1-indexed to match player numbers
            "players": [p.to_dict(reveal_cards=(viewing_player is None or p.number == viewing_player)) for p in self.players],
            "community_cards": {
                "flop": [{"suit": c.suit, "rank": c.rank} for c in self.flop if c] if any(self.flop) else [],
                "turn": {"suit": self.turn.suit, "rank": self.turn.rank} if self.turn else None,
                "river": {"suit": self.river.suit, "rank": self.river.rank} if self.river else None,
            },
            "entanglements": self.qc_manager.get_entanglement_graph(),
        }
        
        # Include winner info if showdown has occurred
        if self.current_round == "showdown" and self.last_winner_info:
            state["winner_info"] = self.last_winner_info
        
        return state
    
    def to_dict(self, viewing_player: Optional[int] = None) -> Dict:
        """Alias for get_game_state for consistency."""
        return self.get_game_state(viewing_player)

    def get_circuit_diagram(self) -> str:
        """
        Get visual representation of the quantum circuit.
        """
        return self.qc_manager.get_circuit_diagram()
    
    # ============================================================================
    # Session Management
    # ============================================================================
    
    def start_session(self):
        """Start a new game session."""
        self.session_active = True
        self.hands_played = 0
        self.hand_number = 0
        print(f"🎮 Game session started with {self.num_players} players")
        print(f"   Starting chips: {self.starting_chips}")
        print(f"   Blinds: {self.small_blind}/{self.big_blind}")
    
    def play_next_hand(self) -> Optional[Dict]:
        """
        Play the next hand in the session.
        
        Returns:
            Hand result dict, or None if session should end
        """
        if not self.session_active:
            raise ValueError("Session not started. Call start_session() first.")
        
        # Check if we have enough players
        active_players = [p for p in self.players if p.chips > 0 and not p.folded]
        if len(active_players) < 2:
            print(f"\n🏁 Game over! Only {len(active_players)} player(s) remaining.")
            self.end_session()
            return None
        
        self.hand_number += 1
        print(f"\n{'='*60}")
        print(f"HAND #{self.hand_number}")
        print(f"{'='*60}")
        
        # Rotate dealer button
        if self.hand_number > 1:
            self._rotate_dealer()
        
        # Show chip stacks
        print("\nChip Stacks:")
        for player in self.players:
            if player.chips > 0:
                print(f"  {player.name}: {player.chips} chips")
        
        # Play hand with ante (default 10 from play_hand signature)
        result = self.play_hand()
        self.hands_played += 1
        
        return result
    
    def _rotate_dealer(self):
        """Rotate dealer button to next active player."""
        initial_dealer = self.dealer_position
        
        while True:
            self.dealer_position = (self.dealer_position + 1) % self.num_players
            
            # Find player with chips
            dealer_player = self.players[self.dealer_position]
            if dealer_player.chips > 0:
                break
            
            # Prevent infinite loop
            if self.dealer_position == initial_dealer:
                break
        
        dealer_player = self.players[self.dealer_position]
        print(f"🔘 Dealer: {dealer_player.name}")
    
    def end_session(self):
        """End the current session."""
        self.session_active = False
        
        print(f"\n{'='*60}")
        print("GAME SESSION ENDED")
        print(f"{'='*60}")
        print(f"Hands played: {self.hands_played}")
        
        # Sort players by chips
        sorted_players = sorted(self.players, key=lambda p: p.chips, reverse=True)
        
        print("\nFinal Standings:")
        for i, player in enumerate(sorted_players, 1):
            profit = player.chips - self.starting_chips
            profit_str = f"+{profit}" if profit > 0 else str(profit)
            print(f"  {i}. {player.name}: {player.chips} chips ({profit_str})")
        
        winner = sorted_players[0]
        print(f"\n🏆 Winner: {winner.name} with {winner.chips} chips!")
    
    def get_session_stats(self) -> Dict:
        """Get session statistics."""
        active_players = sum(1 for p in self.players if p.chips > 0)
        eliminated_players = self.num_players - active_players
        
        player_stats = []
        for player in self.players:
            profit = player.chips - self.starting_chips
            player_stats.append({
                "name": player.name,
                "number": player.number,
                "chips": player.chips,
                "profit": profit,
                "active": player.chips > 0
            })
        
        return {
            "hand_number": self.hand_number,
            "hands_played": self.hands_played,
            "active_players": active_players,
            "eliminated_players": eliminated_players,
            "session_active": self.session_active,
            "player_stats": player_stats
        }


def example_game():
    """
    Example game flow demonstrating quantum entanglement.
    """
    print("=== Quantum Poker Example Game ===\n")

    # Create game with 2 players
    game = QuantumPoker(num_players=2)

    # Deal hole cards
    print("Dealing hole cards...")
    game.deal_hole_cards()

    print("\nPlayer hands (identifiers):")
    for player in game.players:
        print(
            f"{player.name}: {player.hand[0].identifier}, {player.hand[1].identifier}"
        )

    # Deal flop
    print("\nDealing flop...")
    game.deal_flop()
    print(f"Flop: {[card.identifier for card in game.flop]}")

    # Player 1 entangles their first card with first flop card (bit 1 - ±2 rank)
    print("\nPlayer 1 performs quantum entanglement...")
    print("  (Entangling rank bit 1 - creates ±2 rank variation)")
    game.entangle_cards(
        player=game.players[0],
        source_card_idx=0,  # First hole card
        target_card_id="F0",  # First flop card
        bit_index=1,  # Bit 1 of rank: ±2 rank variation
    )

    # Deal turn and river
    print("\nDealing turn...")
    game.deal_turn()
    print(f"Turn: {game.turn.identifier}")

    print("\nDealing river...")
    game.deal_river()
    print(f"River: {game.river.identifier}")

    # Player 2 entangles their second card with the river (bit 0 - ±1 rank)
    print("\nPlayer 2 performs quantum entanglement...")
    print("  (Entangling rank bit 0 - creates ±1 rank variation)")
    game.entangle_cards(
        player=game.players[1],
        source_card_idx=1,  # Second hole card
        target_card_id="R",  # River card
        bit_index=0,  # Bit 0 of rank: ±1 rank variation
    )

    # Show circuit diagram
    print("\n=== Quantum Circuit ===")
    print(game.get_circuit_diagram())

    # Showdown
    showdown_results = game.showdown()

    # Show game state
    print("\n=== Final Game State ===")
    import json

    print(json.dumps(game.get_game_state(), indent=2))


if __name__ == "__main__":
    example_game()


#https://live.codetogether.io/#/1d27bce9-9de3-4645-b11d-20b2105e1810/9TpwgABrofxO87Hz5acuLZ