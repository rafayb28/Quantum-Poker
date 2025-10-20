/**
 * Comprehensive Poker Game Tests
 * Tests actual poker mechanics, not just UI elements
 */
import { test, expect } from '@playwright/test'

test.describe('Poker Game Mechanics', () => {
  let player1Context, player2Context
  let player1Page, player2Page
  let gameId

  test.beforeEach(async ({ browser }) => {
    // Create two separate browser contexts (like two different players)
    player1Context = await browser.newContext()
    player2Context = await browser.newContext()

    player1Page = await player1Context.newPage()
    player2Page = await player2Context.newPage()

    // Player 1 creates game
    await player1Page.goto('http://localhost:3000')
    await player1Page.fill('input[type="text"]', 'Alice')
    await player1Page.click('button:has-text("Create Game")')

    // Get game ID
    await player1Page.waitForSelector('.game-id-display strong', { timeout: 5000 })
    gameId = await player1Page.locator('.game-id-display strong').textContent()

    // Player 2 joins
    await player2Page.goto('http://localhost:3000')
    await player2Page.fill('input[placeholder="Enter your name"]', 'Bob')
    await player2Page.fill('input[placeholder="Enter Game ID"]', gameId)
    await player2Page.click('button:has-text("Join Game")')

    // Wait for both to be in waiting room
    await expect(player1Page.locator('text=Players (2 of')).toBeVisible({ timeout: 5000 })

    // Start game
    await player1Page.click('button:has-text("Start Game")')
    await expect(player1Page.locator('text=Round: pre-flop')).toBeVisible({ timeout: 5000 })
  })

  test.afterEach(async () => {
    await player1Context.close()
    await player2Context.close()
  })

  test('should deal cards to both players', async () => {
    // Player 1 should see their cards (not "Waiting for game")
    const p1HandArea = player1Page.locator('.hand-area')
    await expect(p1HandArea.locator('.card')).toHaveCount(2, { timeout: 5000 })
    
    // Verify cards show rank and suit (not undefined)
    const p1Card1Text = await p1HandArea.locator('.card').first().textContent()
    expect(p1Card1Text).toMatch(/.+ of .+/) // e.g., "Jack of Diamonds"
    expect(p1Card1Text).not.toContain('undefined')
    expect(p1Card1Text).not.toContain('???')

    // Player 2 should also see their cards
    const p2HandArea = player2Page.locator('.hand-area')
    await expect(p2HandArea.locator('.card')).toHaveCount(2, { timeout: 5000 })
    
    const p2Card1Text = await p2HandArea.locator('.card').first().textContent()
    expect(p2Card1Text).toMatch(/.+ of .+/)
    expect(p2Card1Text).not.toContain('undefined')
    
    console.log(`✅ Player 1 cards: ${p1Card1Text}`)
    console.log(`✅ Player 2 cards: ${p2Card1Text}`)
  })

  test('should post blinds correctly', async () => {
    // Check initial chip counts after blinds
    const p1Stats = await player1Page.locator('.player-card:has-text("Alice (You)")').textContent()
    const p2Stats = await player2Page.locator('.player-card:has-text("Bob (You)")').textContent()

    // Player 1 (big blind) should have posted $20
    expect(p1Stats).toContain('Chips: $980')
    expect(p1Stats).toContain('Bet: $20')

    // Player 2 (small blind) should have posted $10  
    expect(p2Stats).toContain('Chips: $990')
    expect(p2Stats).toContain('Bet: $10')

    // Pot should be $30
    await expect(player1Page.locator('text=Pot: $30')).toBeVisible()
    await expect(player2Page.locator('text=Pot: $30')).toBeVisible()

    console.log('✅ Blinds posted correctly: SB=$10, BB=$20, Pot=$30')
  })

  test('should progress through betting rounds', async () => {
    // Pre-flop: Player 1's turn (after big blind)
    await expect(player1Page.locator('text=YOUR TURN')).toBeVisible()
    
    // Player 1 calls
    await player1Page.click('button:has-text("Call")')
    await player1Page.waitForTimeout(500) // Wait for action to process

    // Now Player 2's turn
    await expect(player2Page.locator('text=YOUR TURN')).toBeVisible()
    
    // Player 2 checks
    await player2Page.click('button:has-text("Check")')
    await player2Page.waitForTimeout(500)

    // Should now be in flop
    await expect(player1Page.locator('text=Round: flop')).toBeVisible({ timeout: 5000 })
    await expect(player2Page.locator('text=Round: flop')).toBeVisible({ timeout: 5000 })

    // Should have 3 community cards
    const flopCards = await player1Page.locator('.community-area .card').count()
    expect(flopCards).toBe(3)

    // Verify cards are not undefined
    const card1 = await player1Page.locator('.community-area .card').first().textContent()
    expect(card1).toMatch(/.+ of .+/)
    expect(card1).not.toContain('undefined')

    console.log('✅ Betting round completed, flop dealt')
    console.log(`✅ First flop card: ${card1}`)
  })

  test('should handle folding correctly', async () => {
    // Player 1 folds
    await player1Page.click('button:has-text("Fold")')
    await player1Page.waitForTimeout(500)

    // Player 1 should see FOLDED badge
    await expect(player1Page.locator('.folded-badge')).toBeVisible()

    // Player 2 should win the pot
    // Check that pot increased for Player 2
    const p2StatsAfter = await player2Page.locator('.player-card:has-text("Bob (You)")').textContent()
    
    // Player 2 should have chips > $990 (won the blinds)
    expect(p2StatsAfter).toMatch(/Chips: \$1\d{3}/) // Should be > $1000

    console.log('✅ Fold action works, pot awarded correctly')
  })

  test('should handle raising correctly', async () => {
    const initialPot = 30 // After blinds

    // Player 1 raises to $100
    await player1Page.fill('input[type="number"]', '100')
    await player1Page.click('button:has-text("Raise")')
    await player1Page.waitForTimeout(500)

    // Pot should increase
    const potText = await player1Page.locator('.pot-info').textContent()
    const potAmount = parseInt(potText.match(/\$(\d+)/)[1])
    expect(potAmount).toBeGreaterThan(initialPot)

    // Player 2 should see Call button with correct amount
    const callButton = player2Page.locator('button:has-text("Call")')
    await expect(callButton).toBeVisible()
    
    const callButtonText = await callButton.textContent()
    expect(callButtonText).toContain('$') // Should show amount to call

    console.log(`✅ Raise works, pot increased to $${potAmount}`)
    console.log(`✅ Player 2 sees: ${callButtonText}`)
  })

  test('should handle all-in correctly', async () => {
    // Player 1 goes all-in
    await player1Page.click('button:has-text("All-In")')
    await player1Page.waitForTimeout(500)

    // Player 1 should have 0 chips
    const p1Stats = await player1Page.locator('.player-card:has-text("Alice (You)")').textContent()
    expect(p1Stats).toContain('Chips: $0')

    // Pot should be massive
    const potText = await player1Page.locator('.pot-info').textContent()
    const potAmount = parseInt(potText.match(/\$(\d+)/)[1])
    expect(potAmount).toBeGreaterThan(900) // Should have most of Player 1's chips

    console.log(`✅ All-in works, pot is now $${potAmount}`)
  })

  test('should progress to turn and river', async () => {
    // Complete pre-flop
    await player1Page.click('button:has-text("Call")')
    await player1Page.waitForTimeout(500)
    await player2Page.click('button:has-text("Check")')
    await player2Page.waitForTimeout(1000)

    // Should be in flop
    await expect(player1Page.locator('text=Round: flop')).toBeVisible()
    const flopCount = await player1Page.locator('.community-area .card').count()
    expect(flopCount).toBe(3)

    // Complete flop betting
    // Player 2 checks (they're first to act post-flop)
    await player2Page.click('button:has-text("Check")')
    await player2Page.waitForTimeout(500)
    await player1Page.click('button:has-text("Check")')
    await player1Page.waitForTimeout(1000)

    // Should be in turn
    await expect(player1Page.locator('text=Round: turn')).toBeVisible()
    const turnCount = await player1Page.locator('.community-area .card').count()
    expect(turnCount).toBe(4)

    // Complete turn betting
    await player2Page.click('button:has-text("Check")')
    await player2Page.waitForTimeout(500)
    await player1Page.click('button:has-text("Check")')
    await player1Page.waitForTimeout(1000)

    // Should be in river
    await expect(player1Page.locator('text=Round: river')).toBeVisible()
    const riverCount = await player1Page.locator('.community-area .card').count()
    expect(riverCount).toBe(5)

    // Get all 5 community cards
    const cards = []
    for (let i = 0; i < 5; i++) {
      const cardText = await player1Page.locator('.community-area .card').nth(i).textContent()
      cards.push(cardText)
      expect(cardText).toMatch(/.+ of .+/)
      expect(cardText).not.toContain('undefined')
    }

    console.log('✅ Full betting rounds completed')
    console.log('✅ Community cards:', cards.join(', '))
  })

  test('should show different cards to each player', async () => {
    // Get Player 1's cards
    const p1Card1 = await player1Page.locator('.hand-area .card').first().textContent()
    const p1Card2 = await player1Page.locator('.hand-area .card').last().textContent()

    // Get Player 2's cards
    const p2Card1 = await player2Page.locator('.hand-area .card').first().textContent()
    const p2Card2 = await player2Page.locator('.hand-area .card').last().textContent()

    // Cards should be different (extremely unlikely to be the same)
    const p1Hand = `${p1Card1}, ${p1Card2}`
    const p2Hand = `${p2Card1}, ${p2Card2}`
    
    expect(p1Hand).not.toBe(p2Hand)

    console.log(`✅ Player 1 hand: ${p1Hand}`)
    console.log(`✅ Player 2 hand: ${p2Hand}`)
    console.log('✅ Cards are different for each player')
  })
})
