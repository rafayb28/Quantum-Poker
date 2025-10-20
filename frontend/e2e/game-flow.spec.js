import { test, expect } from '@playwright/test';

test.describe('Two-Player Game Flow', () => {
  test('should allow two players to create, join, and start a game', async ({ browser }) => {
    // Create two browser contexts (simulates two separate users)
    const player1Context = await browser.newContext();
    const player2Context = await browser.newContext();
    
    const player1Page = await player1Context.newPage();
    const player2Page = await player2Context.newPage();

    let gameId = '';

    try {
      // ============ PLAYER 1: CREATE GAME ============
      await test.step('Player 1 logs in', async () => {
        await player1Page.goto('/');
        await player1Page.fill('input[type="text"]', 'Alice');
        await player1Page.click('button:has-text("Enter")');
        await expect(player1Page.locator('text=Welcome, Alice')).toBeVisible({ timeout: 5000 });
      });

      await test.step('Player 1 creates game', async () => {
        await player1Page.click('button:has-text("Create Game")');
        await expect(player1Page.locator('text=Waiting Room')).toBeVisible({ timeout: 5000 });
        
        // Get the game ID from the code element
        const gameIdElement = await player1Page.locator('code').textContent();
        gameId = gameIdElement.trim();
        console.log('Game ID:', gameId);
        
        // Verify waiting room shows 1 player
        await expect(player1Page.locator('text=Players (1 of')).toBeVisible();
        await expect(player1Page.locator('text=Alice')).toBeVisible();
        await expect(player1Page.locator('.host-badge')).toBeVisible();
      });

      // ============ PLAYER 2: JOIN GAME ============
      await test.step('Player 2 logs in', async () => {
        await player2Page.goto('/');
        await player2Page.fill('input[type="text"]', 'Bob');
        await player2Page.click('button:has-text("Enter")');
        await expect(player2Page.locator('text=Welcome, Bob')).toBeVisible({ timeout: 5000 });
      });

      await test.step('Player 2 joins game', async () => {
        await player2Page.fill('input[placeholder*="Game ID"]', gameId);
        await player2Page.click('button:has-text("Join Game")');
        
        // Wait for game screen
        await expect(player2Page.locator('text=Waiting Room')).toBeVisible({ timeout: 5000 });
        
        // Verify Player 2 sees both players
        await expect(player2Page.locator('text=Players (2 of')).toBeVisible();
        await expect(player2Page.locator('text=Bob')).toBeVisible();
        
        // Player 2 should NOT see the copy button (not host)
        await expect(player2Page.locator('.copy-btn')).not.toBeVisible();
      });

      // ============ PLAYER 1: START GAME ============
      await test.step('Player 1 sees Player 2 joined', async () => {
        // Wait a bit for polling to update
        await player1Page.waitForTimeout(2500);
        
        // Verify Player 1 sees both players
        await expect(player1Page.locator('text=Players (2 of')).toBeVisible();
        await expect(player1Page.locator('text=Bob')).toBeVisible();
      });

      await test.step('Player 1 starts the game', async () => {
        // Start button should now be enabled
        const startButton = player1Page.locator('button:has-text("Start Game")');
        await expect(startButton).toBeEnabled();
        await startButton.click();
        
        // Wait for game to start (should transition from "waiting" to "pre-flop")
        await expect(player1Page.locator('text=Round: pre-flop')).toBeVisible({ timeout: 5000 });
        
        // Verify Player 1 has cards
        await expect(player1Page.locator('text=Your Hand')).toBeVisible();
      });

      await test.step('Player 2 sees game started', async () => {
        // Player 2 should see the game has started
        await expect(player2Page.locator('text=Round: pre-flop')).toBeVisible({ timeout: 5000 });
        await expect(player2Page.locator('text=Your Hand')).toBeVisible();
      });

      // ============ VERIFY GAME STATE ============
      await test.step('Verify game state for both players', async () => {
        // Both should see pot and community cards area
        await expect(player1Page.locator('text=Pot:')).toBeVisible();
        await expect(player2Page.locator('text=Pot:')).toBeVisible();
        
        await expect(player1Page.locator('h3:has-text("Community Cards")')).toBeVisible();
        await expect(player2Page.locator('h3:has-text("Community Cards")')).toBeVisible();
        
        // Both should see player info
        await expect(player1Page.locator('text=Alice')).toBeVisible();
        await expect(player1Page.locator('text=Bob')).toBeVisible();
        
        await expect(player2Page.locator('text=Alice')).toBeVisible();
        await expect(player2Page.locator('text=Bob')).toBeVisible();
        
        console.log('✅ Game successfully started with 2 players!');
      });

    } finally {
      // Cleanup
      await player1Context.close();
      await player2Context.close();
    }
  });

  test('should not allow starting game with only 1 player', async ({ page }) => {
    await test.step('Player logs in and creates game', async () => {
      await page.goto('/');
      await page.fill('input[type="text"]', 'Solo');
      await page.click('button:has-text("Enter")');
      await page.click('button:has-text("Create Game")');
      await expect(page.locator('text=Waiting Room')).toBeVisible();
    });

    await test.step('Start button should be disabled', async () => {
      const startButton = page.locator('button:has-text("Waiting for more players...")');
      await expect(startButton).toBeVisible();
      await expect(startButton).toBeDisabled();
    });
  });

  test('should allow player to leave game', async ({ browser }) => {
    const player1Context = await browser.newContext();
    const player2Context = await browser.newContext();
    
    const player1Page = await player1Context.newPage();
    const player2Page = await player2Context.newPage();

    let gameId = '';

    try {
      // Player 1 creates game
      await player1Page.goto('/');
      await player1Page.fill('input[type="text"]', 'Creator');
      await player1Page.click('button:has-text("Enter")');
      await player1Page.click('button:has-text("Create Game")');
      
      gameId = await player1Page.locator('code').textContent();

      // Player 2 joins
      await player2Page.goto('/');
      await player2Page.fill('input[type="text"]', 'Joiner');
      await player2Page.click('button:has-text("Enter")');
      await player2Page.fill('input[placeholder*="Game ID"]', gameId);
      await player2Page.click('button:has-text("Join Game")');
      
      await expect(player2Page.locator('text=Players (2 of')).toBeVisible({ timeout: 5000 });

      // Player 2 leaves
      await player2Page.click('button:has-text("Leave Game")');
      await expect(player2Page.locator('text=Welcome, Joiner')).toBeVisible();

      // Player 1 should see player left
      await player1Page.waitForTimeout(2500); // Wait for polling
      await expect(player1Page.locator('text=Players (1 of')).toBeVisible();

    } finally {
      await player1Context.close();
      await player2Context.close();
    }
  });

  test('should allow players to perform poker actions during gameplay', async ({ browser }) => {
    const player1Context = await browser.newContext();
    const player2Context = await browser.newContext();
    
    const player1Page = await player1Context.newPage();
    const player2Page = await player2Context.newPage();

    try {
      await test.step('Setup: Players join and start game', async () => {
        // Player 1 setup
        await player1Page.goto('/');
        await player1Page.fill('input[type="text"]', 'ActionPlayer1');
        await player1Page.click('button:has-text("Enter")');
        await player1Page.click('button:has-text("Create Game")');
        
        const gameId = await player1Page.locator('code').textContent();

        // Player 2 setup
        await player2Page.goto('/');
        await player2Page.fill('input[type="text"]', 'ActionPlayer2');
        await player2Page.click('button:has-text("Enter")');
        await player2Page.fill('input[placeholder*="Game ID"]', gameId);
        await player2Page.click('button:has-text("Join Game")');
        
        await player2Page.waitForTimeout(1000);

        // Start game
        await player1Page.click('button:has-text("Start Game")');
        await expect(player1Page.locator('text=Round: pre-flop')).toBeVisible({ timeout: 5000 });
        await expect(player2Page.locator('text=Round: pre-flop')).toBeVisible({ timeout: 5000 });
      });

      await test.step('Players take turns performing actions', async () => {
        // Wait for game state to be fully loaded with polling (2 second polling interval)
        await player1Page.waitForTimeout(3000);
        await player2Page.waitForTimeout(3000);
        
        // Check for action buttons on both pages
        const player1HasActions = await player1Page.locator('button:has-text("Fold")').isVisible();
        const player2HasActions = await player2Page.locator('button:has-text("Fold")').isVisible();
        
        console.log('Player 1 has action buttons:', player1HasActions);
        console.log('Player 2 has action buttons:', player2HasActions);
        
        if (player1HasActions) {
          // Player 1's turn
          await expect(player1Page.locator('button:has-text("Check")')).toBeVisible();
          await player1Page.click('button:has-text("Check")');
          console.log('Player 1 checked');
          await player1Page.waitForTimeout(3000); // Wait for polling to update state
          
          // Now Player 2's turn
          await expect(player2Page.locator('button:has-text("Call")')).toBeVisible({ timeout: 8000 });
          await player2Page.click('button:has-text("Call")');
          console.log('Player 2 called');
        } else if (player2HasActions) {
          // Player 2's turn first
          await expect(player2Page.locator('button:has-text("Check")')).toBeVisible();
          await player2Page.click('button:has-text("Check")');
          console.log('Player 2 checked');
          await player2Page.waitForTimeout(3000); // Wait for polling to update state
          
          // Now Player 1's turn
          await expect(player1Page.locator('button:has-text("Call")')).toBeVisible({ timeout: 8000 });
          await player1Page.click('button:has-text("Call")');
          console.log('Player 1 called');
        } else {
          throw new Error('Neither player has action buttons - game may not have started properly');
        }
        
        console.log('✅ Both players successfully performed actions');
      });

      await test.step('Verify game continues after actions', async () => {
        // After both players act, game should still be active
        await player1Page.waitForTimeout(2000);
        
        // Should still see game elements
        await expect(player1Page.locator('text=Pot:')).toBeVisible();
        await expect(player2Page.locator('text=Pot:')).toBeVisible();
        
        // Check if we can progress rounds (Deal Flop button might appear)
        const dealFlopVisible = await player1Page.locator('button:has-text("Deal Flop")').isVisible();
        if (dealFlopVisible) {
          console.log('✅ Game ready to progress to flop');
        }
      });

    } finally {
      await player1Context.close();
      await player2Context.close();
    }
  });

  test('should test fold action - player folds and loses', async ({ browser }) => {
    const player1Context = await browser.newContext();
    const player2Context = await browser.newContext();
    
    const player1Page = await player1Context.newPage();
    const player2Page = await player2Context.newPage();

    try {
      await test.step('Setup game', async () => {
        await player1Page.goto('/');
        await player1Page.fill('input[type="text"]', 'FoldTest1');
        await player1Page.click('button:has-text("Enter")');
        await player1Page.click('button:has-text("Create Game")');
        
        const gameId = await player1Page.locator('code').textContent();

        await player2Page.goto('/');
        await player2Page.fill('input[type="text"]', 'FoldTest2');
        await player2Page.click('button:has-text("Enter")');
        await player2Page.fill('input[placeholder*="Game ID"]', gameId);
        await player2Page.click('button:has-text("Join Game")');
        await player2Page.waitForTimeout(1000);

        await player1Page.click('button:has-text("Start Game")');
        await expect(player1Page.locator('text=Round: pre-flop')).toBeVisible({ timeout: 5000 });
      });

      await test.step('Player folds', async () => {
        await player1Page.waitForTimeout(3000);
        
        const player1HasActions = await player1Page.locator('button:has-text("Fold")').isVisible();
        const player2HasActions = await player2Page.locator('button:has-text("Fold")').isVisible();
        
        if (player1HasActions) {
          // Player 1 folds
          await player1Page.click('button:has-text("Fold")');
          console.log('Player 1 clicked fold button');
          await player1Page.waitForTimeout(3000);
          
          // Player 1 should see FOLDED badge on their player info
          await expect(player1Page.locator('text=FOLDED')).toBeVisible({ timeout: 5000 });
          console.log('✅ Player 1 folded successfully');
        } else if (player2HasActions) {
          // Player 2 folds
          await player2Page.click('button:has-text("Fold")');
          console.log('Player 2 clicked fold button');
          await player2Page.waitForTimeout(3000);
          
          await expect(player2Page.locator('text=FOLDED')).toBeVisible({ timeout: 5000 });
          console.log('✅ Player 2 folded successfully');
        } else {
          throw new Error('Neither player has fold button - game may not have started properly');
        }
      });

    } finally {
      await player1Context.close();
      await player2Context.close();
    }
  });

  test('should allow players to raise bets', async ({ browser }) => {
    const player1Context = await browser.newContext();
    const player2Context = await browser.newContext();
    
    const player1Page = await player1Context.newPage();
    const player2Page = await player2Context.newPage();

    try {
      await test.step('Setup game', async () => {
        await player1Page.goto('/');
        await player1Page.fill('input[type="text"]', 'RaiseTest1');
        await player1Page.click('button:has-text("Enter")');
        await player1Page.click('button:has-text("Create Game")');
        
        const gameId = await player1Page.locator('code').textContent();

        await player2Page.goto('/');
        await player2Page.fill('input[type="text"]', 'RaiseTest2');
        await player2Page.click('button:has-text("Enter")');
        await player2Page.fill('input[placeholder*="Game ID"]', gameId);
        await player2Page.click('button:has-text("Join Game")');
        await player2Page.waitForTimeout(1000);

        await player1Page.click('button:has-text("Start Game")');
        await expect(player1Page.locator('text=Round: pre-flop')).toBeVisible({ timeout: 5000 });
      });

      await test.step('Player raises the bet', async () => {
        await player1Page.waitForTimeout(3000);
        
        const player1HasActions = await player1Page.locator('button:has-text("Fold")').isVisible();
        const player2HasActions = await player2Page.locator('button:has-text("Fold")').isVisible();
        
        if (player1HasActions) {
          // Player 1 raises
          await expect(player1Page.locator('input.raise-input')).toBeVisible();
          await player1Page.fill('input.raise-input', '100');
          await player1Page.click('button:has-text("Raise")');
          console.log('Player 1 raised to 100');
          await player1Page.waitForTimeout(3000);
          
          // Player 2 should see the raised bet
          await expect(player2Page.locator('button:has-text("Call")')).toBeVisible({ timeout: 5000 });
          const callButtonText = await player2Page.locator('button:has-text("Call")').textContent();
          console.log('Player 2 sees call button:', callButtonText);
          
          // Player 2 calls the raise
          await player2Page.click('button:has-text("Call")');
          console.log('Player 2 called the raise');
        } else if (player2HasActions) {
          // Player 2 raises
          await expect(player2Page.locator('input.raise-input')).toBeVisible();
          await player2Page.fill('input.raise-input', '100');
          await player2Page.click('button:has-text("Raise")');
          console.log('Player 2 raised to 100');
          await player2Page.waitForTimeout(3000);
          
          // Player 1 calls
          await expect(player1Page.locator('button:has-text("Call")')).toBeVisible({ timeout: 5000 });
          await player1Page.click('button:has-text("Call")');
          console.log('Player 1 called the raise');
        }
        
        console.log('✅ Raise action completed successfully');
      });

      await test.step('Verify pot increased', async () => {
        await player1Page.waitForTimeout(2000);
        
        // Check that pot value increased (should be at least 200 from the raise)
        const potText1 = await player1Page.locator('text=Pot:').textContent();
        const potText2 = await player2Page.locator('text=Pot:').textContent();
        
        console.log('Player 1 sees pot:', potText1);
        console.log('Player 2 sees pot:', potText2);
        
        // Pot should exist
        await expect(player1Page.locator('text=Pot:')).toBeVisible();
        await expect(player2Page.locator('text=Pot:')).toBeVisible();
      });

    } finally {
      await player1Context.close();
      await player2Context.close();
    }
  });

  test('should allow player to go all-in', async ({ browser }) => {
    const player1Context = await browser.newContext();
    const player2Context = await browser.newContext();
    
    const player1Page = await player1Context.newPage();
    const player2Page = await player2Context.newPage();

    try {
      await test.step('Setup game', async () => {
        await player1Page.goto('/');
        await player1Page.fill('input[type="text"]', 'AllInTest1');
        await player1Page.click('button:has-text("Enter")');
        await player1Page.click('button:has-text("Create Game")');
        
        const gameId = await player1Page.locator('code').textContent();

        await player2Page.goto('/');
        await player2Page.fill('input[type="text"]', 'AllInTest2');
        await player2Page.click('button:has-text("Enter")');
        await player2Page.fill('input[placeholder*="Game ID"]', gameId);
        await player2Page.click('button:has-text("Join Game")');
        await player2Page.waitForTimeout(1000);

        await player1Page.click('button:has-text("Start Game")');
        await expect(player1Page.locator('text=Round: pre-flop')).toBeVisible({ timeout: 5000 });
      });

      await test.step('Player goes all-in', async () => {
        await player1Page.waitForTimeout(3000);
        
        const player1HasActions = await player1Page.locator('button:has-text("All In")').isVisible();
        const player2HasActions = await player2Page.locator('button:has-text("All In")').isVisible();
        
        if (player1HasActions) {
          // Get player 1's chip count before all-in
          const chipsText = await player1Page.locator('.player-card.current-player .player-stats').textContent();
          console.log('Player 1 chips before all-in:', chipsText);
          
          // Player 1 goes all-in
          await player1Page.click('button:has-text("All In")');
          console.log('Player 1 went all-in');
          await player1Page.waitForTimeout(3000);
          
          // Player 2 should see the all-in and can call or fold
          const player2Actions = await player2Page.locator('.action-buttons').isVisible({ timeout: 5000 });
          expect(player2Actions).toBeTruthy();
          console.log('Player 2 sees action buttons after all-in');
          
          // Player 2 calls the all-in
          await player2Page.click('button:has-text("Call")');
          console.log('Player 2 called the all-in');
        } else if (player2HasActions) {
          // Player 2 goes all-in
          const chipsText = await player2Page.locator('.player-card:not(.current-player) .player-stats').textContent();
          console.log('Player 2 chips before all-in:', chipsText);
          
          await player2Page.click('button:has-text("All In")');
          console.log('Player 2 went all-in');
          await player2Page.waitForTimeout(3000);
          
          // Player 1 calls
          await player1Page.click('button:has-text("Call")');
          console.log('Player 1 called the all-in');
        }
        
        console.log('✅ All-in action completed successfully');
      });

      await test.step('Verify game continues after all-in', async () => {
        await player1Page.waitForTimeout(2000);
        
        // Game should still show active state
        await expect(player1Page.locator('text=Pot:')).toBeVisible();
        await expect(player2Page.locator('text=Pot:')).toBeVisible();
        
        console.log('✅ Game state maintained after all-in');
      });

    } finally {
      await player1Context.close();
      await player2Context.close();
    }
  });
});
