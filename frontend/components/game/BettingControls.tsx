// Betting controls component

import { useState } from 'react';
import { Loader2 } from 'lucide-react';

interface BettingControlsProps {
  isMyTurn: boolean;
  currentBet: number;
  myChips: number;
  myCurrentBet: number;
  minRaise: number;
  onAction: (action: string, amount?: number) => Promise<void>;
  disabled?: boolean;
}

export default function BettingControls({
  isMyTurn,
  currentBet,
  myChips,
  myCurrentBet,
  minRaise,
  onAction,
  disabled = false
}: BettingControlsProps) {
  const [raiseAmount, setRaiseAmount] = useState(minRaise);
  const [isLoading, setIsLoading] = useState(false);

  const amountToCall = currentBet - myCurrentBet;
  const canCheck = amountToCall === 0;
  const canCall = amountToCall > 0 && amountToCall <= myChips;
  const canRaise = myChips > amountToCall;

  const handleAction = async (action: string, amount?: number) => {
    setIsLoading(true);
    try {
      await onAction(action, amount);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isMyTurn) {
    return (
      <div className="bg-gray-900/80 backdrop-blur-sm rounded-xl p-4 border-2 border-gray-700">
        <p className="text-gray-400 text-center">Waiting for your turn...</p>
      </div>
    );
  }

  return (
    <div className="bg-gray-900/90 backdrop-blur-sm rounded-xl p-4 sm:p-6 border-2 border-yellow-500">
      <h3 className="text-white font-bold text-lg mb-4">Your Action</h3>
      
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-4">
        {/* Fold */}
        <button
          onClick={() => handleAction('fold')}
          disabled={disabled || isLoading}
          className="px-4 py-3 bg-red-600 hover:bg-red-700 disabled:bg-gray-600 text-white font-bold rounded-lg transition-colors disabled:cursor-not-allowed"
        >
          {isLoading ? <Loader2 className="animate-spin mx-auto" size={20} /> : 'Fold'}
        </button>
        
        {/* Check / Call */}
        {canCheck ? (
          <button
            onClick={() => handleAction('check')}
            disabled={disabled || isLoading}
            className="px-4 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white font-bold rounded-lg transition-colors disabled:cursor-not-allowed"
          >
            Check
          </button>
        ) : canCall ? (
          <button
            onClick={() => handleAction('call')}
            disabled={disabled || isLoading}
            className="px-4 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white font-bold rounded-lg transition-colors disabled:cursor-not-allowed"
          >
            Call {amountToCall}
          </button>
        ) : null}
        
        {/* All-in */}
        <button
          onClick={() => handleAction('all_in')}
          disabled={disabled || isLoading}
          className="px-4 py-3 bg-orange-600 hover:bg-orange-700 disabled:bg-gray-600 text-white font-bold rounded-lg transition-colors disabled:cursor-not-allowed"
        >
          All-in
        </button>
      </div>
      
      {/* Raise */}
      {canRaise && (
        <div className="space-y-3">
          <div className="flex items-center gap-3">
            <input
              type="range"
              min={minRaise}
              max={myChips}
              step={10}
              value={raiseAmount}
              onChange={(e) => setRaiseAmount(Number(e.target.value))}
              disabled={disabled || isLoading}
              className="flex-1"
            />
            <input
              type="number"
              min={minRaise}
              max={myChips}
              step={10}
              value={raiseAmount}
              onChange={(e) => setRaiseAmount(Number(e.target.value))}
              disabled={disabled || isLoading}
              className="w-24 px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white text-center focus:outline-none focus:ring-2 focus:ring-yellow-500"
            />
          </div>
          
          <button
            onClick={() => handleAction('raise', raiseAmount)}
            disabled={disabled || isLoading || raiseAmount < minRaise}
            className="w-full px-4 py-3 bg-yellow-600 hover:bg-yellow-700 disabled:bg-gray-600 text-white font-bold rounded-lg transition-colors disabled:cursor-not-allowed"
          >
            Raise to {raiseAmount}
          </button>
        </div>
      )}
      
      <div className="mt-3 text-xs text-gray-400 text-center">
        Your chips: {myChips} | Min raise: {minRaise}
      </div>
    </div>
  );
}
