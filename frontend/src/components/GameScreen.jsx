import { useState, useEffect } from 'react'
import { game } from '../api'
import './GameScreen.css'

function GameScreen({ gameId, playerNumber, username, onLeaveGame }) {
  const [gameState, setGameState] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [actionInProgress, setActionInProgress] = useState(false)

  const fetchGameState = async () => {
    try {
      const response = await game.getState(gameId)
      setGameState(response.data)
      setError('')
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch game state')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchGameState()
    // Poll for updates every 2 seconds
    const interval = setInterval(fetchGameState, 2000)
    return () => clearInterval(interval)
  }, [gameId])

  const handleStartGame = async () => {
    setActionInProgress(true)
    try {
      await game.start(gameId)
      await fetchGameState()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to start game')
    } finally {
      setActionInProgress(false)
    }
  }

  const handleAction = async (action, amount = null) => {
    setActionInProgress(true)
    try {
      await game.performAction(gameId, action, amount)
      await fetchGameState()
    } catch (err) {
      setError(err.response?.data?.detail || 'Action failed')
    } finally {
      setActionInProgress(false)
    }
  }

  const handleNextRound = async () => {
    setActionInProgress(true)
    try {
      await game.nextRound(gameId)
      await fetchGameState()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to advance round')
    } finally {
      setActionInProgress(false)
    }
  }

  const handleShowdown = async () => {
    setActionInProgress(true)
    try {
      await game.showdown(gameId)
      await fetchGameState()
    } catch (err) {
      setError(err.response?.data?.detail || 'Showdown failed')
    } finally {
      setActionInProgress(false)
    }
  }

  if (loading) {
    return (
      <div className="game-screen">
        <div className="loading">Loading game...</div>
      </div>
    )
  }

  if (!gameState) {
    return (
      <div className="game-screen">
        <div className="error-box">
          <p>Failed to load game</p>
          <button onClick={onLeaveGame}>Back to Lobby</button>
        </div>
      </div>
    )
  }

  const currentPlayer = gameState.players.find(p => p.number === playerNumber)
  const isMyTurn = gameState.current_player === playerNumber
  const canStart = playerNumber === 1 && gameState.round === 'waiting'

  return (
    <div className="game-screen">
      <div className="game-container">
        {/* Header */}
        <div className="game-header">
          <div className="game-info">
            <span className="game-id">Game: {gameId.slice(0, 8)}...</span>
            <span className="round-info">Round: {gameState.round}</span>
            <span className="pot-info">Pot: ${gameState.pot}</span>
          </div>
          <button className="leave-btn" onClick={onLeaveGame}>
            Leave Game
          </button>
        </div>

        {/* Waiting for game to start */}
        {gameState.round === 'waiting' && (
          <div className="waiting-area">
            <h3>Waiting for players...</h3>
            <p>{gameState.players.length} / {gameState.num_players} players joined</p>
            {canStart && (
              <button 
                className="start-btn"
                onClick={handleStartGame}
                disabled={actionInProgress || gameState.players.length < 2}
              >
                Start Game
              </button>
            )}
          </div>
        )}

        {/* Main game area */}
        {gameState.round !== 'waiting' && (
          <>
            {/* Community Cards */}
            <div className="community-area">
              <h3>Community Cards</h3>
              <div className="cards">
                {gameState.community_cards && Object.keys(gameState.community_cards).length > 0 ? (
                  Object.entries(gameState.community_cards).map(([id, card]) => (
                    <div key={id} className="card">
                      {card.rank} {card.suit}
                    </div>
                  ))
                ) : (
                  <p className="no-cards">No community cards yet</p>
                )}
              </div>
            </div>

            {/* Players */}
            <div className="players-area">
              <h3>Players</h3>
              <div className="players-grid">
                {gameState.players.map(player => (
                  <div 
                    key={player.number}
                    className={`player-card ${player.number === playerNumber ? 'current-player' : ''} ${player.folded ? 'folded' : ''}`}
                  >
                    <div className="player-name">
                      {player.name}
                      {player.number === playerNumber && ' (You)'}
                      {isMyTurn && player.number === playerNumber && ' - YOUR TURN'}
                    </div>
                    <div className="player-stats">
                      <span>Chips: ${player.chips}</span>
                      <span>Bet: ${player.current_bet}</span>
                      <span>Q-Chips: {player.quantum_chips}</span>
                    </div>
                    {player.folded && <div className="folded-badge">FOLDED</div>}
                  </div>
                ))}
              </div>
            </div>

            {/* Your Hand */}
            <div className="hand-area">
              <h3>Your Hand</h3>
              <div className="cards">
                {currentPlayer?.hand_identifiers && gameState.player_hands ? (
                  currentPlayer.hand_identifiers.map((cardId, idx) => {
                    const card = gameState.player_hands[playerNumber]?.[idx]
                    return (
                      <div key={cardId} className="card">
                        {card ? `${card.rank} ${card.suit}` : '???'}
                      </div>
                    )
                  })
                ) : (
                  <div className="card-placeholder">Waiting for game to start...</div>
                )}
              </div>
            </div>

            {/* Actions */}
            {!currentPlayer?.folded && (
              <div className="actions-area">
                {isMyTurn ? (
                  <div className="action-buttons">
                    <button 
                      onClick={() => handleAction('fold')}
                      disabled={actionInProgress}
                      className="action-btn fold-btn"
                    >
                      Fold
                    </button>
                    <button 
                      onClick={() => handleAction('check')}
                      disabled={actionInProgress}
                      className="action-btn check-btn"
                    >
                      Check
                    </button>
                    <button 
                      onClick={() => handleAction('call')}
                      disabled={actionInProgress}
                      className="action-btn call-btn"
                    >
                      Call ${gameState.current_bet - currentPlayer.current_bet}
                    </button>
                  </div>
                ) : (
                  <p className="waiting-turn">Waiting for other players...</p>
                )}

                {/* Round controls */}
                <div className="round-controls">
                  {gameState.round === 'pre-flop' && (
                    <button onClick={handleNextRound} disabled={actionInProgress}>
                      Deal Flop
                    </button>
                  )}
                  {gameState.round === 'flop' && (
                    <button onClick={handleNextRound} disabled={actionInProgress}>
                      Deal Turn
                    </button>
                  )}
                  {gameState.round === 'turn' && (
                    <button onClick={handleNextRound} disabled={actionInProgress}>
                      Deal River
                    </button>
                  )}
                  {gameState.round === 'river' && (
                    <button onClick={handleShowdown} disabled={actionInProgress}>
                      Showdown
                    </button>
                  )}
                </div>
              </div>
            )}
          </>
        )}

        {/* Error display */}
        {error && (
          <div className="error-banner">
            {error}
            <button onClick={() => setError('')}>✕</button>
          </div>
        )}
      </div>
    </div>
  )
}

export default GameScreen
