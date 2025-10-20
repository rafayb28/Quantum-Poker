import { useState, useEffect } from 'react'
import { game } from '../api'
import './GameScreen.css'

function GameScreen({ gameId, playerNumber, username, onLeaveGame }) {
  const [gameState, setGameState] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [actionInProgress, setActionInProgress] = useState(false)
  const [copied, setCopied] = useState(false)
  const [raiseAmount, setRaiseAmount] = useState('')
  const [showWinnerModal, setShowWinnerModal] = useState(false)
  const [winnerInfo, setWinnerInfo] = useState(null)

  // Fetch game state from API
  const fetchGameState = async () => {
    try {
      const response = await game.getState(gameId)
      setGameState(response.data)
      setError('')
      setLoading(false)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch game state')
      setLoading(false)
    }
  }

  // Initial fetch and polling for updates
  useEffect(() => {
    fetchGameState()
    
    // Poll every 2 seconds for game updates
    const interval = setInterval(fetchGameState, 2000)
    
    return () => clearInterval(interval)
  }, [gameId])
  
  // Detect showdown and extract winner info
  useEffect(() => {
    if (gameState && gameState.round === 'showdown') {
      // Check if we have winner info in the most recent response
      // This would come from the auto_progress_round response
      if (gameState.winner_info) {
        setWinnerInfo(gameState.winner_info)
        setShowWinnerModal(true)
      }
    }
  }, [gameState])

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
            <h3>Waiting Room</h3>
            
            {/* Only show Game ID box to host */}
            {playerNumber === 1 && (
              <div className="game-id-box">
                <p className="share-label">Share this Game ID with other players:</p>
                <div className="game-id-display">
                  <code>{gameId}</code>
                  <button 
                    className={`copy-btn ${copied ? 'copied' : ''}`}
                    onClick={() => {
                      navigator.clipboard.writeText(gameId)
                      setCopied(true)
                      setTimeout(() => setCopied(false), 2000)
                    }}
                  >
                    {copied ? 'Copied!' : 'Copy'}
                  </button>
                </div>
              </div>
            )}

            {/* Players List */}
            <div className="waiting-players">
              <h4>Players ({gameState.players_joined || 1} of {gameState.num_players})</h4>
              <div className="player-list">
                {gameState.joined_player_names?.map((name, idx) => (
                  <div key={idx} className="waiting-player">
                    <span className="player-icon">👤</span>
                    <span className="player-name">{name}</span>
                    {idx === 0 && <span className="host-badge">Host</span>}
                  </div>
                ))}
              </div>
            </div>

            {canStart && (
              <button 
                className="start-btn"
                onClick={handleStartGame}
                disabled={actionInProgress || (gameState.players_joined || 1) < 2}
              >
                {(gameState.players_joined || 1) < 2 ? 'Waiting for more players...' : 'Start Game'}
              </button>
            )}
            {!canStart && <p className="waiting-message">Waiting for host to start the game...</p>}
          </div>
        )}

        {/* Main game area */}
        {gameState.round !== 'waiting' && (
          <>
            {/* Community Cards */}
            <div className="community-area">
              <h3>Community Cards</h3>
              <div className="cards">
                {(() => {
                  const cards = []
                  // Flop cards
                  if (gameState.community_cards?.flop) {
                    gameState.community_cards.flop.forEach((card, idx) => {
                      if (card) {
                        cards.push(
                          <div key={`flop-${idx}`} className="card">
                            {card.rank} of {card.suit}
                          </div>
                        )
                      }
                    })
                  }
                  // Turn card
                  if (gameState.community_cards?.turn) {
                    cards.push(
                      <div key="turn" className="card">
                        {gameState.community_cards.turn.rank} of {gameState.community_cards.turn.suit}
                      </div>
                    )
                  }
                  // River card
                  if (gameState.community_cards?.river) {
                    cards.push(
                      <div key="river" className="card">
                        {gameState.community_cards.river.rank} of {gameState.community_cards.river.suit}
                      </div>
                    )
                  }
                  
                  return cards.length > 0 ? cards : <p className="no-cards">No community cards yet</p>
                })()}
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
                {currentPlayer?.hand && currentPlayer.hand.length > 0 ? (
                  currentPlayer.hand.map((card, idx) => (
                    <div key={idx} className="card">
                      {card.rank} of {card.suit}
                    </div>
                  ))
                ) : (
                  <div className="card-placeholder">Waiting for game to start...</div>
                )}
              </div>
            </div>

            {/* Actions */}
            {!currentPlayer?.folded && gameState.round !== 'showdown' && (
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
                    
                    {/* Only show Check if no bet to call */}
                    {gameState.current_bet === currentPlayer.current_bet ? (
                      <button 
                        onClick={() => handleAction('check')}
                        disabled={actionInProgress}
                        className="action-btn check-btn"
                      >
                        Check
                      </button>
                    ) : (
                      <button 
                        onClick={() => handleAction('call')}
                        disabled={actionInProgress}
                        className="action-btn call-btn"
                      >
                        Call ${gameState.current_bet - currentPlayer.current_bet}
                      </button>
                    )}
                    
                    {/* Raise controls */}
                    <div className="raise-controls">
                      <input
                        type="number"
                        value={raiseAmount}
                        onChange={(e) => setRaiseAmount(e.target.value)}
                        placeholder="Raise amount"
                        min={gameState.current_bet + 1}
                        max={currentPlayer.chips}
                        disabled={actionInProgress}
                        className="raise-input"
                      />
                      <button 
                        onClick={() => {
                          const amount = parseInt(raiseAmount)
                          if (amount && amount > gameState.current_bet) {
                            handleAction('raise', amount)
                            setRaiseAmount('')
                          }
                        }}
                        disabled={actionInProgress || !raiseAmount || parseInt(raiseAmount) <= gameState.current_bet}
                        className="action-btn raise-btn"
                      >
                        Raise
                      </button>
                    </div>
                    
                    <button 
                      onClick={() => handleAction('all_in')}
                      disabled={actionInProgress}
                      className="action-btn all-in-btn"
                    >
                      All In (${currentPlayer.chips})
                    </button>
                  </div>
                ) : (
                  <p className="waiting-turn">Waiting for other players...</p>
                )}
              </div>
            )}
            
            {/* Winner Modal */}
            {showWinnerModal && winnerInfo && (
              <div className="modal-overlay" onClick={() => setShowWinnerModal(false)}>
                <div className="winner-modal" onClick={(e) => e.stopPropagation()}>
                  <h2>🎉 Hand Complete! 🎉</h2>
                  
                  {winnerInfo.winners && winnerInfo.winners.length === 1 ? (
                    <>
                      <div className="winner-announcement">
                        <h3>{winnerInfo.winners[0].player_name} Wins!</h3>
                        <p className="winning-hand">{winnerInfo.winners[0].hand_name}</p>
                        <p className="pot-won">Won ${gameState.pot} pot</p>
                      </div>
                      
                      {winnerInfo.winners[0].best_cards && (
                        <div className="winning-cards">
                          <h4>Winning Hand:</h4>
                          <div className="cards">
                            {winnerInfo.winners[0].best_cards.map((card, idx) => (
                              <div key={idx} className="card small">
                                {card.rank} of {card.suit}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </>
                  ) : winnerInfo.winners && winnerInfo.winners.length > 1 ? (
                    <>
                      <div className="winner-announcement">
                        <h3>Split Pot!</h3>
                        <p>{winnerInfo.winners.map(w => w.player_name).join(' & ')}</p>
                        <p className="winning-hand">{winnerInfo.winners[0].hand_name}</p>
                        <p className="pot-won">Each wins ${Math.floor(gameState.pot / winnerInfo.winners.length)}</p>
                      </div>
                    </>
                  ) : null}
                  
                  {winnerInfo.all_hands && (
                    <div className="all-hands">
                      <h4>All Hands:</h4>
                      {Object.entries(winnerInfo.all_hands).map(([playerNum, handInfo]) => (
                        <div key={playerNum} className="hand-result">
                          <strong>Player {playerNum}:</strong> {handInfo.hand_name}
                        </div>
                      ))}
                    </div>
                  )}
                  
                  <button 
                    className="close-modal-btn"
                    onClick={() => setShowWinnerModal(false)}
                  >
                    Close
                  </button>
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
