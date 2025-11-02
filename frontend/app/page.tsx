'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import { LogIn, Loader2 } from 'lucide-react';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();
  const { login, validateToken, error, clearError } = useAuthStore();

  useEffect(() => {
    validateToken().then((isValid) => {
      if (isValid) {
        router.push('/lobby');
      } else {
        setIsLoading(false);
      }
    });
  }, [validateToken, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username.trim()) return;

    setIsLoading(true);
    clearError();
    
    try {
      await login(username.trim());
      router.push('/lobby');
    } catch (error) {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 flex items-center justify-center">
        <Loader2 className="animate-spin text-purple-500" size={48} />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 flex items-center justify-center p-4">
      <div className="bg-gray-800 rounded-2xl shadow-2xl p-8 w-full max-w-md border-2 border-purple-500">
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <span className="text-6xl">⚛️</span>
          </div>
          <h1 className="text-4xl font-bold text-white mb-2">Quantum Poker</h1>
          <p className="text-gray-400">Experience poker with quantum mechanics</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-gray-300 mb-2">
              Username
            </label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="Enter your username"
              disabled={isLoading}
              autoFocus
            />
          </div>

          {error && (
            <div className="bg-red-900 bg-opacity-50 border border-red-500 text-red-200 px-4 py-3 rounded-lg text-sm">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading || !username.trim()}
            className="w-full bg-purple-600 hover:bg-purple-500 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-bold py-3 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
          >
            {isLoading ? (
              <>
                <Loader2 className="animate-spin" size={20} />
                <span>Logging in...</span>
              </>
            ) : (
              <>
                <LogIn size={20} />
                <span>Enter Game</span>
              </>
            )}
          </button>
        </form>

        <div className="mt-8 pt-6 border-t border-gray-700">
          <h3 className="text-white font-semibold mb-3 text-center">How to Play</h3>
          <ul className="text-gray-400 text-sm space-y-2">
            <li className="flex items-start">
              <span className="text-purple-400 mr-2">1.</span>
              <span>Enter a username to create your session</span>
            </li>
            <li className="flex items-start">
              <span className="text-purple-400 mr-2">2.</span>
              <span>Create a new game or join an existing one</span>
            </li>
            <li className="flex items-start">
              <span className="text-purple-400 mr-2">3.</span>
              <span>Use quantum chips to entangle cards</span>
            </li>
            <li className="flex items-start">
              <span className="text-purple-400 mr-2">4.</span>
              <span>Win chips with the best poker hand</span>
            </li>
          </ul>
        </div>

        <div className="mt-6 text-center text-xs text-gray-500">
          Powered by Qiskit quantum computing
        </div>
      </div>
    </div>
  );
}
