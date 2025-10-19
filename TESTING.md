# Testing Checklist

## Setup
- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] No console errors in browser

## Authentication
- [ ] Can enter username and create session
- [ ] Token saved in localStorage
- [ ] Can logout and login again
- [ ] Auto-login works on page refresh

## Lobby
- [ ] Create game button works
- [ ] Game ID is displayed/copyable
- [ ] Can enter Game ID in join field
- [ ] Join game button works
- [ ] Error shown for invalid Game ID

## Game Start
- [ ] Waiting room shows player count
- [ ] Start button only visible to creator (Player 1)
- [ ] Start button disabled until 2+ players
- [ ] Start button creates game successfully
- [ ] Hole cards dealt after start

## Game Play
- [ ] Community cards area exists (empty initially)
- [ ] Player grid shows all players
- [ ] Current player highlighted
- [ ] Your turn indicator shows correctly
- [ ] Can fold when it's your turn
- [ ] Can check when appropriate
- [ ] Can call with correct amount
- [ ] Turn passes to next player after action
- [ ] Folded players shown as folded

## Round Progression
- [ ] "Deal Flop" button appears in pre-flop
- [ ] Flop deals 3 community cards
- [ ] "Deal Turn" button appears after flop
- [ ] Turn deals 4th community card
- [ ] "Deal River" button appears after turn
- [ ] River deals 5th community card
- [ ] "Showdown" button appears after river
- [ ] Showdown determines winner

## Game State
- [ ] Pot updates correctly
- [ ] Player chips update after bets
- [ ] Current bet shows correctly
- [ ] Quantum chips displayed
- [ ] Game state refreshes every ~2 seconds
- [ ] Round indicator updates

## Error Handling
- [ ] Errors displayed in red banner
- [ ] Can dismiss error messages
- [ ] Invalid actions show error
- [ ] Network errors handled

## Edge Cases
- [ ] Can't start game with 1 player
- [ ] Can't act when not your turn
- [ ] Can't check when bet is required
- [ ] Folded players can't take actions
- [ ] Game continues with remaining players

## Notes
Write any bugs or issues found:
