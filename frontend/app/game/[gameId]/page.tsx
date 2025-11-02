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
import { ArrowLeft, Loader2, Users, Play, Copy, Check, HelpCircle, X } from 'lucide-react';

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
  const [showQuantumHelp, setShowQuantumHelp] = useState(false);
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

  const handleQuantumEntangle = async (
    sourceCardIndex: number,
    targetCardId: string,
    bitIndex: number,
    angle?: number
  ) => {
    try {
      await performQuantumAction(sourceCardIndex, targetCardId, bitIndex, angle);
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

  // Helper function to convert card IDs to readable names
  const formatCardId = (cardId: string): string => {
    // Handle self-superposition
    if (cardId === 'SELF') {
      return 'Self (Superposition)';
    }
    
    if (cardId === 'PHASE') {
      return 'Phase (Interference)';
    }
    
    // Format: P1H1, P2H2, COM1, etc.
    if (cardId.startsWith('P') && cardId.includes('H')) {
      // Player hand card: P2H1 -> "Player 2's Card 1"
      const playerNum = cardId.match(/P(\d+)/)?.[1];
      const cardNum = cardId.match(/H(\d+)/)?.[1];
      const player = players?.find(p => p.number === parseInt(playerNum || '0'));
      const playerName = player?.name || `Player ${playerNum}`;
      return `${playerName}'s Card ${cardNum}`;
    } else if (cardId.startsWith('COM')) {
      // Community card: COM1 -> "Community Card 1"
      const cardNum = cardId.match(/COM(\d+)/)?.[1];
      return `Community Card ${cardNum}`;
    }
    return cardId; // Fallback to original ID
  };

  // Debug logging
  console.log('Debug - myPlayerNumber:', myPlayerNumber, 'isHost:', isHost, 'playersJoined:', playersJoined, 'round:', round);
  console.log('Debug - myPlayer entanglement_history:', myPlayer?.entanglement_history);

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
                currentRound={round || ''}
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
                  
                  {/* Quantum Operations Button */}
                  {myPlayer.quantum_chips > 0 && myPlayer.hand && myPlayer.hand.length === 2 && (
                    <div className="flex gap-2">
                      <button
                        onClick={() => setShowQuantumModal(true)}
                        disabled={!isConnected}
                        className="flex-1 px-4 py-3 bg-purple-600 hover:bg-purple-500 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-semibold rounded-lg transition-colors flex items-center justify-center gap-2"
                      >
                        <span className="text-xl">⚛️</span>
                        <span>Quantum Operations</span>
                        <span className="ml-2 text-xs bg-purple-500 px-2 py-0.5 rounded-full">
                          {myPlayer.quantum_chips} available
                        </span>
                      </button>
                      <button
                        onClick={() => setShowQuantumHelp(true)}
                        className="px-3 py-3 bg-purple-700 hover:bg-purple-600 text-white rounded-lg transition-colors flex items-center justify-center"
                        title="How Quantum Operations Work"
                      >
                        <HelpCircle size={20} />
                      </button>
                    </div>
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
              
              {/* Quantum Operations History */}
              {myPlayer && myPlayer.entanglement_history && myPlayer.entanglement_history.length > 0 && (
                <div className="bg-gray-900 rounded-xl p-4 border-2 border-purple-700">
                  <h3 className="text-purple-400 font-bold mb-3 flex items-center gap-2">
                    <span className="text-xl">⚛️</span>
                    <span>Quantum Operations</span>
                    <span className="text-xs bg-purple-600/50 text-purple-200 px-2 py-0.5 rounded-full">
                      {myPlayer.entanglement_history.length}
                    </span>
                  </h3>
                  <div className="space-y-2">
                    {myPlayer.entanglement_history.map((ent, idx) => (
                      <div key={idx} className="bg-gray-800 rounded-lg p-3 border border-purple-900">
                        <div className="text-purple-300 font-medium mb-1 text-sm">
                          {ent.target === 'SELF' ? (
                            <>⚛️ {formatCardId(ent.source)} → Superposition</>
                          ) : ent.target === 'PHASE' ? (
                            <>〰️ {formatCardId(ent.source)} → Phase Interference</>
                          ) : (
                            <>🔗 {formatCardId(ent.source)} ↔ {formatCardId(ent.target)}</>
                          )}
                        </div>
                        <div className="text-gray-400 text-xs">
                          {ent.effect} rank change (Bit {ent.bit})
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
            ...(community_cards?.flop || []).map((card, idx) => ({ card, id: `F${idx}` })),
            ...(community_cards?.turn ? [{ card: community_cards.turn, id: 'T' }] : []),
            ...(community_cards?.river ? [{ card: community_cards.river, id: 'R' }] : [])
          ]}
          opponents={players?.filter(p => p.number !== myPlayerNumber && p.name) || []}
          myPlayerNumber={myPlayerNumber || 0}
          availableQuantumChips={myPlayer.quantum_chips}
          onEntangle={handleQuantumEntangle}
          onCancel={() => setShowQuantumModal(false)}
        />
      )}

      {/* Quantum Help Modal */}
      {showQuantumHelp && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-900 rounded-xl p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto shadow-2xl border-2 border-purple-500">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-3xl font-bold text-white flex items-center gap-2">
                <span className="text-3xl">⚛️</span>
                How Quantum Operations Work
              </h2>
              <button
                onClick={() => setShowQuantumHelp(false)}
                className="text-gray-400 hover:text-white transition-colors"
              >
                <X size={24} />
              </button>
            </div>

            <div className="space-y-6 text-white">
              {/* Bitwise Explanation */}
              <div className="bg-gray-800 rounded-lg p-4 border border-purple-700">
                <h3 className="text-xl font-bold text-purple-400 mb-3">Card Encoding (6 Qubits)</h3>
                <p className="text-gray-300 mb-3">Each card is encoded as 6 quantum bits:</p>
                <div className="bg-gray-900 rounded p-3 font-mono text-sm">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="text-purple-400 mb-2">Rank (4 bits):</div>
                      <div className="space-y-1 text-gray-300">
                        <div>Bit 0: ±1 rank</div>
                        <div>Bit 1: ±2 rank</div>
                        <div>Bit 2: ±4 rank</div>
                        <div>Bit 3: ±8 rank</div>
                      </div>
                    </div>
                    <div>
                      <div className="text-blue-400 mb-2">Suit (2 bits):</div>
                      <div className="space-y-1 text-gray-300">
                        <div>00 = Spades ♠</div>
                        <div>01 = Diamonds ♦</div>
                        <div>10 = Clubs ♣</div>
                        <div>11 = Hearts ♥</div>
                      </div>
                    </div>
                  </div>
                </div>
                <p className="text-gray-400 text-sm mt-3">
                  <strong>Note:</strong> Only rank bits 0-2 can be manipulated (suit is locked)
                </p>
              </div>

              {/* Superposition */}
              <div className="bg-gray-800 rounded-lg p-4 border border-blue-700">
                <h3 className="text-xl font-bold text-blue-400 mb-3 flex items-center gap-2">
                  <span className="text-2xl">⚛️</span>
                  Superposition (H Gate)
                </h3>
                <p className="text-gray-300 mb-3">Puts a single bit of your card into quantum superposition - 50/50 chance to flip.</p>
                <div className="bg-gray-900 rounded p-3 space-y-2">
                  <div className="font-bold text-blue-300">Example: 7♠ → Bit 0 (±1)</div>
                  <div className="font-mono text-sm space-y-1">
                    <div>Before: 7 = 0111 (binary)</div>
                    <div className="text-yellow-400">Operation: H gate on bit 0</div>
                    <div>After measurement:</div>
                    <div className="ml-4">• 50% → 0110 = 6♠</div>
                    <div className="ml-4">• 50% → 1000 = 8♠</div>
                  </div>
                </div>
                <div className="mt-3 text-sm text-gray-400">
                  <strong>Cost:</strong> 1 quantum chip | <strong>Risk:</strong> Your card might get worse!
                </div>
              </div>

              {/* Phase Interference */}
              <div className="bg-gray-800 rounded-lg p-4 border border-indigo-700">
                <h3 className="text-xl font-bold text-indigo-400 mb-3 flex items-center gap-2">
                  <span className="text-2xl">〰️</span>
                  Phase Interference (RZ Gate)
                </h3>
                <p className="text-gray-300 mb-3">Apply phase rotation with adjustable angle (0-360°) to control interference patterns and bias probabilities.</p>
                <div className="bg-gray-900 rounded p-3 space-y-2">
                  <div className="font-bold text-indigo-300">Example: 7♠ → Bit 0 with Phase</div>
                  <div className="text-sm text-gray-300 space-y-1">
                    <div>• Put bit into superposition (H gate)</div>
                    <div>• Apply phase rotation at chosen angle (RZ)</div>
                    <div>• Apply superposition again (H gate)</div>
                    <div className="mt-2 text-yellow-400">Results:</div>
                    <div className="ml-4">• 180°: Guarantees bit flip (7→6 or 8)</div>
                    <div className="ml-4">• Other angles: Bias toward specific outcomes</div>
                    <div className="ml-4">• 0°/360°: No effect (50/50)</div>
                  </div>
                </div>
                <div className="mt-3 text-sm text-gray-400">
                  <strong>Cost:</strong> 1 quantum chip | <strong>Use:</strong> Strategic probability control
                </div>
              </div>

              {/* Entanglement */}
              <div className="bg-gray-800 rounded-lg p-4 border border-green-700">
                <h3 className="text-xl font-bold text-green-400 mb-3 flex items-center gap-2">
                  <span className="text-2xl">🔗</span>
                  Entanglement (H + CNOT Gates)
                </h3>
                <p className="text-gray-300 mb-3">Links two cards together - when one changes, the other changes in a correlated way.</p>
                <div className="bg-gray-900 rounded p-3 space-y-2">
                  <div className="font-bold text-green-300">Example: Entangle 7♠ with K♥ (Bit 1 = ±2)</div>
                  <div className="font-mono text-sm space-y-1">
                    <div>Card A: 7♠ = 0111</div>
                    <div>Card B: K♥ = 1101</div>
                    <div className="text-yellow-400">Operation: H on A + CNOT(A→B) on bit 1</div>
                    <div>Possible outcomes:</div>
                    <div className="ml-4">• 50% → 7♠ (0111) & K♥ (1101) - both stay same</div>
                    <div className="ml-4">• 50% → 5♠ (0101) & J♥ (1011) - both change ±2</div>
                  </div>
                </div>
                <div className="mt-3 text-sm text-gray-400 space-y-1">
                  <div><strong>Cost:</strong> 1 chip (your/community) or 2 chips (opponent)</div>
                  <div><strong>Strategy:</strong> Great for hedging - if your card gets worse, theirs does too!</div>
                </div>
              </div>

              {/* Important Notes */}
              <div className="bg-gray-800 rounded-lg p-4 border border-yellow-700">
                <h3 className="text-xl font-bold text-yellow-400 mb-3">⚠️ Important Rules</h3>
                <ul className="space-y-2 text-gray-300">
                  <li className="flex items-start gap-2">
                    <span className="text-yellow-400 mt-1">•</span>
                    <span>Only cards affected by operations change at showdown</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-yellow-400 mt-1">•</span>
                    <span>Untouched cards remain exactly as dealt</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-yellow-400 mt-1">•</span>
                    <span>You get 2 quantum chips per hand</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-yellow-400 mt-1">•</span>
                    <span>Card suits never change (only ranks)</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-yellow-400 mt-1">•</span>
                    <span>Measurements are random but follow quantum probabilities</span>
                  </li>
                </ul>
              </div>
            </div>

            <button
              onClick={() => setShowQuantumHelp(false)}
              className="mt-6 w-full px-6 py-3 bg-purple-600 hover:bg-purple-500 text-white font-semibold rounded-lg transition-colors"
            >
              Got it!
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
