'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useParams } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import { useGameStore } from '@/store/gameStore';
import { useGameWebSocket } from '@/hooks/useGameWebSocket';
import PokerTable from '@/components/game/PokerTable';
import BettingControls from '@/components/game/BettingControls';
import QuantumEntangle from '@/components/game/QuantumEntangle';
import { api } from '@/lib/api';
import { ArrowLeft, Loader2, Users, Play, Copy, Check } from 'lucide-react';

export default function GamePage() {
  const params = useParams();
  const router = useRouter();
  const gameId = params.gameId as string;
  
  const { validateToken } = useAuthStore();
  const {
    players,
    round,
    pot,
    current_bet,
    current_player,
    community_cards,
    myPlayerNumber,
    setGameId,
    loadGameState,
    performAction,
    performQuantumAction,
    clearGame,
    isLoading,
    error
  } = useGameStore();
  
  const { isConnected, reconnect } = useGameWebSocket(gameId);
  const [isStarting, setIsStarting] = useState(false);
  const [showQuantumModal, setShowQuantumModal] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    validateToken().then(async (isValid) => {
      if (!isValid) {
        router.push('/');
        return;
      }
      
      // Get player number from sessionStorage (set when creating/joining)
      const storedPlayerNumber = sessionStorage.getItem(`game_${gameId}_playerNumber`);
      const playerNumber = storedPlayerNumber ? parseInt(storedPlayerNumber, 10) : 1;
      
      // Load initial game state
      try {
        const state = await api.getGameState(gameId);
        setGameId(gameId, playerNumber);
      } catch (error) {
        console.error('Failed to load game state:', error);
      }
    });
    
    return () => {
      clearGame();
    };
  }, [gameId, validateToken, router, setGameId, clearGame]);

  const handleLeaveGame = async () => {
    try {
      await api.leaveGame(gameId);
      router.push('/lobby');
    } catch (error) {
      console.error('Failed to leave game:', error);
    }
  };

  const handleStartGame = async () => {
    setIsStarting(true);
    try {
      await api.startGame(gameId);
    } catch (error: any) {
      alert(error.message || 'Failed to start game');
    } finally {
      setIsStarting(false);
    }
  };

  const handleAction = async (action: string, amount?: number) => {
    try {
      await performAction(action, amount);
    } catch (error: any) {
      alert(error.message || 'Action failed');
    }
  };

  const handleQuantumEntangle = async (sourceCardIndex: number, targetCardId: string, bitIndex: number) => {
    try {
      await performQuantumAction(sourceCardIndex, targetCardId, bitIndex);
      setShowQuantumModal(false);
      await loadGameState();
    } catch (error: any) {
      alert(error.message || 'Quantum entanglement failed');
    }
  };

  const handleNextHand = async () => {
    try {
      await api.startNextHand(gameId);
    } catch (error: any) {
      alert(error.message || 'Failed to start next hand');
    }
  };

  if (isLoading && (!players || players.length === 0)) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-900 via-green-800 to-emerald-900 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="animate-spin mx-auto mb-4 text-yellow-500" size={48} />
          <p className="text-white text-xl">Loading game...</p>
        </div>
      </div>
    );
  }

  const myPlayer = players?.find(p => p.number === myPlayerNumber);
  const isMyTurn = current_player === myPlayerNumber;
  const isHost = myPlayerNumber === 1; // Player 1 is always the host/creator
  
  // Count players who have actually joined (have a name)
  const playersJoined = players?.filter(p => p.name && p.name.trim() !== '').length || 0;

  // Debug logging
  console.log('Debug - myPlayerNumber:', myPlayerNumber, 'isHost:', isHost, 'playersJoined:', playersJoined, 'round:', round);

  const copyGameCode = () => {
    navigator.clipboard.writeText(gameId);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-4 sm:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <button
            onClick={handleLeaveGame}
            className="flex items-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded-lg transition-colors"
          >
            <ArrowLeft size={20} />
            Leave Game
          </button>
          
          <div className="flex items-center gap-4">
            <div className={`flex items-center gap-2 px-4 py-2 rounded-lg ${
              isConnected ? 'bg-green-900 text-green-400' : 'bg-red-900 text-red-400'
            }`}>
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'} animate-pulse`} />
              {isConnected ? 'Connected' : 'Reconnecting...'}
            </div>
            
            <div className="bg-gray-800 px-4 py-2 rounded-lg text-white">
              Round: <span className="font-bold capitalize">{round}</span>
            </div>
          </div>
        </div>

        {error && (
          <div className="bg-red-900/50 border border-red-500 text-red-200 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* Waiting Room */}
        {round === 'waiting' && (
          <div className="bg-gray-900 rounded-xl p-8 mb-6 text-center border-2 border-gray-700">
            <Users className="mx-auto mb-4 text-yellow-500" size={48} />
            <h2 className="text-2xl font-bold text-white mb-2">Waiting for Players</h2>
            <p className="text-gray-400 mb-4">
              {playersJoined} player{playersJoined !== 1 ? 's' : ''} joined (max 6)
            </p>
            
            {/* Player List */}
            <div className="bg-gray-800 rounded-lg p-4 mb-6 max-w-md mx-auto">
              <h3 className="text-sm font-semibold text-gray-400 mb-3">Players in Lobby</h3>
              <div className="space-y-2">
                {players?.map((player) => (
                  <div
                    key={player.number}
                    className={`flex items-center gap-3 p-2 rounded-lg ${
                      player.name && player.name.trim() !== ''
                        ? 'bg-green-900/30 text-green-400'
                        : 'bg-gray-700/50 text-gray-500'
                    }`}
                  >
                    <div className={`w-2 h-2 rounded-full ${
                      player.name && player.name.trim() !== ''
                        ? 'bg-green-400'
                        : 'bg-gray-600'
                    }`} />
                    <span className="text-sm font-medium">
                      {player.name && player.name.trim() !== ''
                        ? `${player.name}${player.number === 1 ? ' (Host)' : ''}`
                        : `Waiting for player ${player.number}...`
                      }
                    </span>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="flex items-center justify-center gap-3 text-gray-500 text-sm mb-6">
              <span>Game Code: <span className="font-mono text-white">{gameId}</span></span>
              <button
                onClick={copyGameCode}
                className="p-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors text-white"
                title="Copy game code"
              >
                {copied ? <Check size={16} className="text-green-400" /> : <Copy size={16} />}
              </button>
            </div>
            
            {/* Debug Info */}
            <div className="text-xs text-gray-600 mb-4 text-center">
              Debug: Player #{myPlayerNumber} | Host: {isHost ? 'Yes' : 'No'} | Joined: {playersJoined}/{players?.length ?? 0}
            </div>
            
            {isHost && playersJoined >= 2 && (
              <button
                onClick={handleStartGame}
                disabled={isStarting}
                className="px-8 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white font-bold rounded-lg transition-colors disabled:cursor-not-allowed flex items-center gap-2 mx-auto"
              >
                {isStarting ? (
                  <>
                    <Loader2 className="animate-spin" size={20} />
                    Starting...
                  </>
                ) : (
                  <>
                    <Play size={20} />
                    Start Game
                  </>
                )}
              </button>
            )}
            
            {isHost && playersJoined < 2 && (
              <p className="text-yellow-500 text-sm">Waiting for at least one more player to join...</p>
            )}
            
            {!isHost && (
              <p className="text-gray-500 text-sm">Waiting for host to start the game...</p>
            )}
          </div>
        )}

        {/* Game Table */}
        {round !== 'waiting' && players && players.length > 0 && (
          <div className="grid lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <PokerTable
                players={players}
                communityCards={community_cards || { flop: [], turn: null, river: null }}
                pot={pot || 0}
                currentPlayer={current_player || 0}
                myPlayerNumber={myPlayerNumber || 1}
              />
            </div>
            
            <div className="space-y-6">
              {/* Betting Controls */}
              {myPlayer && round !== 'showdown' && round !== 'complete' && (
                <>
                  <BettingControls
                    isMyTurn={isMyTurn}
                    currentBet={current_bet || 0}
                    myChips={myPlayer.chips}
                    myCurrentBet={myPlayer.current_bet}
                    minRaise={(current_bet || 0) + 10}
                    onAction={handleAction}
                    disabled={!isConnected}
                  />
                  
                  {/* Quantum Entangle Button */}
                  {myPlayer.quantum_chips > 0 && myPlayer.hand && myPlayer.hand.length === 2 && (
                    <button
                      onClick={() => setShowQuantumModal(true)}
                      disabled={!isConnected}
                      className="w-full px-4 py-3 bg-purple-600 hover:bg-purple-500 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-semibold rounded-lg transition-colors flex items-center justify-center gap-2"
                    >
                      <span className="text-xl">⚛️</span>
                      <span>Quantum Entangle ({myPlayer.quantum_chips} chips)</span>
                    </button>
                  )}
                </>
              )}
              
              {/* Next Hand Button (Showdown or Complete) */}
              {(round === 'showdown' || round === 'complete') && isHost && (
                <button
                  onClick={handleNextHand}
                  disabled={!isConnected}
                  className="w-full px-6 py-4 bg-green-600 hover:bg-green-500 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-bold text-lg rounded-lg transition-colors flex items-center justify-center gap-2"
                >
                  <span className="text-2xl">🃏</span>
                  <span>Deal Next Hand</span>
                </button>
              )}
              
              {/* Player Info */}
              <div className="bg-gray-900 rounded-xl p-4 border-2 border-gray-700">
                <h3 className="text-white font-bold mb-3">Your Info</h3>
                {myPlayer && (
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-400">Chips:</span>
                      <span className="text-yellow-500 font-bold">{myPlayer.chips}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Quantum Chips:</span>
                      <span className="text-purple-400 font-bold">{myPlayer.quantum_chips}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Current Bet:</span>
                      <span className="text-white font-bold">{myPlayer.current_bet}</span>
                    </div>
                  </div>
                )}
              </div>
              
              {/* Game Info */}
              <div className="bg-gray-900 rounded-xl p-4 border-2 border-gray-700">
                <h3 className="text-white font-bold mb-3">Game Info</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Active Players:</span>
                    <span className="text-white">{playersJoined}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Pot:</span>
                    <span className="text-yellow-500 font-bold">{pot || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Current Bet:</span>
                    <span className="text-white">{current_bet || 0}</span>
                  </div>
                </div>
              </div>
              
              {/* Entanglement History */}
              {myPlayer && myPlayer.entanglement_history && myPlayer.entanglement_history.length > 0 && (
                <div className="bg-gray-900 rounded-xl p-4 border-2 border-purple-700">
                  <h3 className="text-purple-400 font-bold mb-3 flex items-center gap-2">
                    <span className="text-xl">⚛️</span>
                    <span>Your Entanglements</span>
                  </h3>
                  <div className="space-y-2">
                    {myPlayer.entanglement_history.map((ent, idx) => (
                      <div key={idx} className="bg-gray-800 rounded-lg p-3 border border-purple-900">
                        <div className="text-purple-300 font-medium mb-1">
                          {ent.source} ↔ {ent.target}
                        </div>
                        <div className="text-gray-400 text-xs">
                          Bit {ent.bit}: {ent.effect} rank change
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
      
      {/* Quantum Entangle Modal */}
      {showQuantumModal && myPlayer && myPlayer.hand && (
        <QuantumEntangle
          myCards={myPlayer.hand}
          communityCards={[
            ...(community_cards?.flop || []),
            ...(community_cards?.turn ? [community_cards.turn] : []),
            ...(community_cards?.river ? [community_cards.river] : [])
          ]}
          opponents={players?.filter(p => p.number !== myPlayerNumber && p.name) || []}
          myPlayerNumber={myPlayerNumber || 0}
          availableQuantumChips={myPlayer.quantum_chips}
          onEntangle={handleQuantumEntangle}
          onCancel={() => setShowQuantumModal(false)}
        />
      )}
    </div>
  );
}
