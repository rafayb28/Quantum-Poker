import { useState, useEffect } from 'react'
import './App.css'
import LoginScreen from './components/LoginScreen'
import LobbyScreen from './components/LobbyScreen'
import GameScreen from './components/GameScreen'

function App() {
  const [screen, setScreen] = useState('login') // login, lobby, game
  const [token, setToken] = useState(null)
  const [username, setUsername] = useState('')
  const [gameId, setGameId] = useState(null)
  const [playerNumber, setPlayerNumber] = useState(null)

  useEffect(() => {
    // Check if token exists in localStorage
    const savedToken = localStorage.getItem('token')
    const savedUsername = localStorage.getItem('username')
    if (savedToken && savedUsername) {
      setToken(savedToken)
      setUsername(savedUsername)
      setScreen('lobby')
    }
  }, [])

  const handleLogin = (newToken, newUsername) => {
    setToken(newToken)
    setUsername(newUsername)
    localStorage.setItem('token', newToken)
    localStorage.setItem('username', newUsername)
    setScreen('lobby')
  }

  const handleLogout = () => {
    setToken(null)
    setUsername('')
    setGameId(null)
    setPlayerNumber(null)
    localStorage.removeItem('token')
    localStorage.removeItem('username')
    setScreen('login')
  }

  const handleJoinGame = (newGameId, newPlayerNumber) => {
    setGameId(newGameId)
    setPlayerNumber(newPlayerNumber)
    setScreen('game')
  }

  const handleLeaveGame = () => {
    setGameId(null)
    setPlayerNumber(null)
    setScreen('lobby')
  }

  return (
    <div className="app">
      {screen === 'login' && (
        <LoginScreen onLogin={handleLogin} />
      )}
      
      {screen === 'lobby' && (
        <LobbyScreen 
          username={username}
          onLogout={handleLogout}
          onJoinGame={handleJoinGame}
        />
      )}
      
      {screen === 'game' && (
        <GameScreen 
          gameId={gameId}
          playerNumber={playerNumber}
          username={username}
          onLeaveGame={handleLeaveGame}
        />
      )}
    </div>
  )
}

export default App
