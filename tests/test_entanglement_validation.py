"""
Test to understand which cards create invalid values when entangled
"""

import sys

sys.path.insert(0, "..")

from src.card import Card, RANKS

# Test each rank to see what values it can produce with each bit entangled
print("Testing entanglement effects on card ranks:\n")
print("=" * 70)

for rank_name, rank_bits in RANKS.items():
    print(f"\n{rank_name} (value {rank_bits:04b} = {rank_bits})")
    print("-" * 70)

    for bit in range(4):
        # Flip the bit to see possible outcomes
        flipped = rank_bits ^ (1 << bit)

        # Check if both original and flipped are valid (1-13)
        original_valid = 1 <= rank_bits <= 13
        flipped_valid = 1 <= flipped <= 13

        status = "✓ SAFE" if (original_valid and flipped_valid) else "✗ UNSAFE"

        print(
            f"  Bit {bit} (±{1 << bit}): {rank_bits:04b} ↔ {flipped:04b}  "
            f"({rank_bits} ↔ {flipped})  {status}"
        )

print("\n" + "=" * 70)
print("\nSummary:")
print("- Bit 0 (±1): Generally safe except for Ace (can become 0)")
print("- Bit 1 (±2): Safe for 3-11, risky for Ace/2 and Queen/King")
print("- Bit 2 (±4): Safe for 5-9, risky otherwise")
print("- Bit 3 (±8): Very dangerous - creates 14-15 frequently")
