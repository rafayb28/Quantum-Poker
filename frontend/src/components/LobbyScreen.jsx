import { useState } from 'react'
import { game } from '../api'
import './LobbyScreen.css'

function LobbyScreen({ username, onLogout, onJoinGame }) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [gameIdInput, setGameIdInput] = useState('')

  const handleCreateGame = async () => {
    setLoading(true)
    setError('')

    try {
      const response = await game.create(2, 6)
      const { game_id, player_number } = response.data
      onJoinGame(game_id, player_number)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create game')
    } finally {
      setLoading(false)
    }
  }

  const handleJoinGame = async (e) => {
    e.preventDefault()
    if (!gameIdInput.trim()) {
      setError('Please enter a game ID')
      return
    }

    setLoading(true)
    setError('')

    try {
      const response = await game.join(gameIdInput.trim())
      const { game_id, player_number } = response.data
      onJoinGame(game_id, player_number)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to join game')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="lobby-screen">
      <div className="lobby-card">
        <div className="lobby-header">
          <h2>Welcome, {username}</h2>
          <button className="logout-btn" onClick={onLogout}>
            Logout
          </button>
        </div>

        <div className="lobby-content">
          <div className="action-section">
            <h3>Create New Game</h3>
            <button 
              className="primary-btn"
              onClick={handleCreateGame}
              disabled={loading}
            >
              {loading ? 'Creating...' : 'Create Game'}
            </button>
          </div>

          <div className="divider">OR</div>

          <div className="action-section">
            <h3>Join Existing Game</h3>
            <form onSubmit={handleJoinGame}>
              <input
                type="text"
                placeholder="Enter Game ID"
                value={gameIdInput}
                onChange={(e) => setGameIdInput(e.target.value)}
                disabled={loading}
              />
              <button 
                type="submit"
                className="primary-btn"
                disabled={loading}
              >
                {loading ? 'Joining...' : 'Join Game'}
              </button>
            </form>
          </div>

          {error && <p className="error">{error}</p>}
        </div>

        <div className="lobby-info">
          <p>Share the Game ID with friends to play together</p>
          <p>2-6 players per game</p>
        </div>
      </div>
    </div>
  )
}

export default LobbyScreen
