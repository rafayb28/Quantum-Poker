#!/usr/bin/env python3
"""
Test script to see what game state looks like
"""
import sys
sys.path.insert(0, '.')

from src.game import QuantumPoker
import json

# Create a game
game = QuantumPoker(num_players=2, starting_chips=1000, small_blind=10, big_blind=20)

# Add players
game.players[0].name = "Alice"
game.players[1].name = "Bob"

print("=== BEFORE START ===")
state = game.to_dict(viewing_player=1)
print(json.dumps(state, indent=2, default=str))

# Start the game
game.start_game()

print("\n=== AFTER START (Player 1 view) ===")
state = game.to_dict(viewing_player=1)
print(json.dumps(state, indent=2, default=str))

print("\n=== AFTER START (Player 2 view) ===")
state = game.to_dict(viewing_player=2)
print(json.dumps(state, indent=2, default=str))
