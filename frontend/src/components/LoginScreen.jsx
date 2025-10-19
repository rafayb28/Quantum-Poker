import { useState } from 'react'
import { auth } from '../api'
import './LoginScreen.css'

function LoginScreen({ onLogin }) {
  const [username, setUsername] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!username.trim()) {
      setError('Please enter a username')
      return
    }

    setLoading(true)
    setError('')

    try {
      const response = await auth.createSession(username.trim())
      const { token } = response.data
      onLogin(token, username.trim())
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create session')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-screen">
      <div className="login-card">
        <h1>Quantum Poker</h1>
        <p className="subtitle">Enter the quantum realm</p>
        
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Enter username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            disabled={loading}
            maxLength={20}
            autoFocus
          />
          
          {error && <p className="error">{error}</p>}
          
          <button type="submit" disabled={loading}>
            {loading ? 'Connecting...' : 'Enter Game'}
          </button>
        </form>
        
        <p className="info">No registration required - just pick a name</p>
      </div>
    </div>
  )
}

export default LoginScreen
