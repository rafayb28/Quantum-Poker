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
        
        await expect(player1Page.locator('text=Community Cards')).toBeVisible();
        await expect(player2Page.locator('text=Community Cards')).toBeVisible();
        
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
});
