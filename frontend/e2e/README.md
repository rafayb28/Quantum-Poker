# E2E Tests

Automated end-to-end tests using Playwright to test real user scenarios.

## Quick Start

```bash
# Make sure backend is running
cd ..
python -m uvicorn src.api:app --reload

# In another terminal, run tests
cd frontend
npm run test:e2e
```

## Test Commands

| Command | Description |
|---------|-------------|
| `npm run test:e2e` | Run all tests in headless mode |
| `npm run test:e2e:headed` | Run with browser visible |
| `npm run test:e2e:ui` | Open Playwright UI (best for debugging) |

## What's Tested

### `game-flow.spec.js`

**Test 1: Two-Player Game Flow**
- Player 1 logs in as "Alice"
- Player 1 creates a game
- Player 2 logs in as "Bob"
- Player 2 joins using Game ID
- Both players see each other in waiting room
- Player 1 starts the game
- Both players transition to pre-flop round
- Both players see their cards and game state

**Test 2: Single Player Restriction**
- Player creates game
- Start button is disabled with only 1 player
- Shows "Waiting for more players..." message

**Test 3: Leave Game**
- Player 1 creates game
- Player 2 joins
- Player 2 leaves game
- Player 1 sees player count update to 1

## Test Structure

Each test:
1. Creates separate browser contexts (simulates different users)
2. Uses test.step() for clear organization
3. Includes proper cleanup
4. Waits for elements with timeouts
5. Verifies both player perspectives

## Tips

- Tests run sequentially to avoid race conditions
- Frontend auto-starts during tests (no need to run `npm run dev`)
- HTML report generated in `playwright-report/`
- Screenshots captured on failure in `test-results/`
- Use `--debug` flag for step-by-step debugging

## Adding New Tests

```javascript
test('my new test', async ({ browser }) => {
  const context = await browser.newContext();
  const page = await context.newPage();
  
  await test.step('describe what you're testing', async () => {
    await page.goto('/');
    // ... your test logic
  });
  
  await context.close();
});
```

## Troubleshooting

**Backend not running:**
- Tests will timeout waiting for API
- Start backend before running tests

**Frontend port conflict:**
- Tests expect frontend on port 3000
- Check `playwright.config.js` if using different port

**Flaky tests:**
- Increase timeouts in test if needed
- Check polling intervals (game state updates every 2s)
- Use `page.waitForTimeout()` for polling-dependent checks
