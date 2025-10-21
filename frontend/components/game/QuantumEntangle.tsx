'use client';

import { useState } from 'react';
import { Card as CardType } from '@/types/game';
import Card from '@/components/shared/Card';
import ChipStack from '@/components/shared/ChipStack';
import { Zap } from 'lucide-react';

interface QuantumEntangleProps {
  myCards: CardType[];
  availableQuantumChips: number;
  onEntangle: (cardIndex: number) => void;
  onCancel: () => void;
}

export default function QuantumEntangle({
  myCards,
  availableQuantumChips,
  onEntangle,
  onCancel
}: QuantumEntangleProps) {
  const [selectedCard, setSelectedCard] = useState<number | null>(null);

  const handleCardSelect = (index: number) => {
    setSelectedCard(index);
  };

  const handleConfirm = () => {
    if (selectedCard !== null) {
      onEntangle(selectedCard);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 rounded-xl p-8 max-w-2xl w-full shadow-2xl border-2 border-purple-500">
        <div className="text-center mb-6">
          <div className="flex items-center justify-center mb-4">
            <Zap className="text-purple-400 mr-2" size={32} />
            <h2 className="text-3xl font-bold text-white">Quantum Entanglement</h2>
          </div>
          <p className="text-gray-400 mb-2">
            Select a card to entangle with an opponent's card
          </p>
          <p className="text-sm text-gray-500">
            Entangling creates quantum superposition between rank bits
          </p>
        </div>

        {/* Available Quantum Chips */}
        <div className="bg-gray-800 rounded-lg p-4 mb-6 flex items-center justify-between">
          <span className="text-gray-400">Available Quantum Chips:</span>
          <ChipStack amount={availableQuantumChips} size="lg" className="text-purple-400" />
        </div>

        {/* Card Selection */}
        <div className="mb-8">
          <h3 className="text-white font-semibold mb-4 text-center">Your Cards</h3>
          <div className="flex justify-center gap-6">
            {myCards.map((card, index) => (
              <button
                key={index}
                onClick={() => handleCardSelect(index)}
                className={`transform transition-all duration-200 hover:scale-105 ${
                  selectedCard === index
                    ? 'ring-4 ring-purple-500 scale-110'
                    : 'hover:ring-2 hover:ring-purple-300'
                }`}
              >
                <div className="scale-150">
                  <Card card={card} />
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Info Box */}
        <div className="bg-purple-900 bg-opacity-30 border border-purple-500 rounded-lg p-4 mb-6">
          <div className="flex items-start">
            <Zap className="text-purple-400 mr-3 mt-1 flex-shrink-0" size={20} />
            <div className="text-sm text-gray-300">
              <p className="mb-2">
                <strong>How it works:</strong>
              </p>
              <ul className="list-disc list-inside space-y-1 text-gray-400">
                <li>Your selected card will be entangled with a random opponent card</li>
                <li>Only rank bits 0-2 are affected (quantum superposition)</li>
                <li>Both cards' actual values remain unknown until showdown</li>
                <li>Costs 1 quantum chip per entanglement</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-4">
          <button
            onClick={onCancel}
            className="flex-1 px-6 py-3 bg-gray-700 hover:bg-gray-600 text-white font-semibold rounded-lg transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleConfirm}
            disabled={selectedCard === null || availableQuantumChips === 0}
            className={`flex-1 px-6 py-3 font-semibold rounded-lg transition-all flex items-center justify-center ${
              selectedCard !== null && availableQuantumChips > 0
                ? 'bg-purple-600 hover:bg-purple-500 text-white hover:shadow-lg hover:shadow-purple-500/50'
                : 'bg-gray-600 text-gray-400 cursor-not-allowed'
            }`}
          >
            <Zap className="mr-2" size={20} />
            Entangle Card
          </button>
        </div>
      </div>
    </div>
  );
}
