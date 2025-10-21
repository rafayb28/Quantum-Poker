'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import { api } from '@/lib/api';
import { PlusCircle, LogOut } from 'lucide-react';

export default function LobbyPage() {
  const [isCreating, setIsCreating] = useState(false);
  const [joinGameId, setJoinGameId] = useState('');
  const [numPlayers, setNumPlayers] = useState(2);
  const router = useRouter();
  const { username, logout, validateToken } = useAuthStore();
  
  useEffect(() => {
    // Validate authentication
    validateToken().then((isValid) => {
      if (!isValid) {
        router.push('/');
      }
    });
  }, [validateToken, router]);
  
  const handleCreateGame = async () => {
    setIsCreating(true);
    try {
      const response = await api.createGame(numPlayers, 6);
      router.push(`/game/${response.game_id}`);
    } catch (error: any) {
      alert(error.message || 'Failed to create game');
      setIsCreating(false);
    }
  };
  
  const handleJoinByCode = async () => {
    if (!joinGameId.trim()) {
      alert('Please enter a game code');
      return;
    }
    try {
      await api.joinGame(joinGameId.trim());
      router.push(`/game/${joinGameId.trim()}`);
    } catch (error: any) {
      alert(error.message || 'Failed to join game');
    }
  };
  
  const handleLogout = () => {
    logout();
    router.push('/');
  };
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 p-8">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="bg-gray-800 rounded-2xl p-6 mb-6 border-2 border-purple-500">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-white mb-1">
                ⚛️ Quantum Poker
              </h1>
              <p className="text-gray-400">Welcome, {username}!</p>
            </div>
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-500 text-white rounded-lg transition-colors"
            >
              <LogOut size={20} />
              Logout
            </button>
          </div>
        </div>

        {/* Create Game Card */}
        <div className="bg-gray-800 rounded-2xl p-8 mb-6 border-2 border-purple-500">
          <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
            <PlusCircle className="text-purple-400" />
            Create New Game
          </h2>
          
          {/* Player Count Selector */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-300 mb-3">
              Number of Players
            </label>
            <div className="flex gap-2">
              {[2, 3, 4, 5, 6].map((num) => (
                <button
                  key={num}
                  onClick={() => setNumPlayers(num)}
                  className={`flex-1 py-3 rounded-lg font-semibold transition-all ${
                    numPlayers === num
                      ? 'bg-purple-600 text-white shadow-lg shadow-purple-500/50'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  {num}
                </button>
              ))}
            </div>
          </div>

          <button
            onClick={handleCreateGame}
            disabled={isCreating}
            className="w-full bg-purple-600 hover:bg-purple-500 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-bold py-4 px-6 rounded-lg transition-all flex items-center justify-center gap-2"
          >
            {isCreating ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white" />
                Creating...
              </>
            ) : (
              <>
                <PlusCircle size={24} />
                Create Game
              </>
            )}
          </button>
        </div>

        {/* Join Game Card */}
        <div className="bg-gray-800 rounded-2xl p-8 border-2 border-purple-500">
          <h2 className="text-2xl font-bold text-white mb-6">Join Game</h2>
          
          <div className="space-y-4">
            <div>
              <label htmlFor="gameCode" className="block text-sm font-medium text-gray-300 mb-2">
                Enter Game Code
              </label>
              <input
                id="gameCode"
                type="text"
                value={joinGameId}
                onChange={(e) => setJoinGameId(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleJoinByCode()}
                placeholder="Paste game code here..."
                className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 font-mono text-sm"
              />
            </div>

            <button
              onClick={handleJoinByCode}
              disabled={!joinGameId.trim()}
              className="w-full bg-green-600 hover:bg-green-500 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-bold py-4 px-6 rounded-lg transition-all"
            >
              Join Game
            </button>
          </div>
        </div>

        {/* Info Box */}
        <div className="mt-6 bg-gray-800 border border-gray-700 rounded-lg p-4">
          <p className="text-gray-400 text-sm">
            <strong className="text-white">How to play:</strong> Create a game and share the code with friends, or enter a code to join an existing game. Only the host can start the game once all players have joined.
          </p>
        </div>
      </div>
    </div>
  );
}
