'use client';

import { useState, useEffect } from 'react';
import { Card as CardType, Player } from '@/types/game';
import Card from '@/components/shared/Card';
import ChipStack from '@/components/shared/ChipStack';
import { Zap, User, ChevronDown, ChevronUp, TrendingUp } from 'lucide-react';
import { api } from '@/lib/api';
import { useParams } from 'next/navigation';

interface CommunityCardWithId {
  card: CardType;
  id: string;
}

interface QuantumEntangleProps {
  myCards: CardType[];
  communityCards: CommunityCardWithId[];
  opponents: Player[];
  myPlayerNumber: number;
  availableQuantumChips: number;
  onEntangle: (
    sourceCardIndex: number,
    targetCardId: string,
    bitIndex: number,
    angle?: number
  ) => void;
  onCancel: () => void;
}

interface ProbabilityOutcome {
  card: string;
  probability: number;
}

interface PreviewData {
  source_card: string;
  operation: string;
  bit_index: number;
  angle?: number;
  outcomes: ProbabilityOutcome[];
}

export default function QuantumEntangle({
  myCards,
  communityCards,
  opponents,
  myPlayerNumber,
  availableQuantumChips,
  onEntangle,
  onCancel
}: QuantumEntangleProps) {
  const params = useParams();
  const gameId = params.gameId as string;
  
  const [sourceCard, setSourceCard] = useState<number | null>(null);
  const [targetCardId, setTargetCardId] = useState<string | null>(null);
  const [bitIndex, setBitIndex] = useState<number>(0);
  const [expandedOpponents, setExpandedOpponents] = useState<Set<number>>(new Set());
  const [angleDeg, setAngleDeg] = useState<number>(180); // slider degrees (0-360)
  const [preview, setPreview] = useState<PreviewData | null>(null);
  const [loadingPreview, setLoadingPreview] = useState(false);

  // Calculate cost based on target
  const isSelfSuperposition = targetCardId === 'SELF';
  const isPhaseInterference = targetCardId === 'PHASE';
  const isOpponentCard = targetCardId?.startsWith('P') && !targetCardId.startsWith(`P${myPlayerNumber}H`) && targetCardId !== 'PHASE';
  const chipCost = isOpponentCard ? 2 : 1;
  const hasEnoughChips = availableQuantumChips >= chipCost;

  // Fetch probability preview when operation parameters change
  useEffect(() => {
    if (sourceCard !== null && targetCardId !== null) {
      const fetchPreview = async () => {
        setLoadingPreview(true);
        try {
          const angleRad = targetCardId === 'PHASE' ? (angleDeg * Math.PI) / 180 : undefined;
          const data = await api.previewQuantumOperation(
            gameId,
            sourceCard,
            targetCardId,
            bitIndex,
            angleRad
          );
          setPreview(data);
        } catch (error) {
          console.error('Failed to fetch preview:', error);
          setPreview(null);
        } finally {
          setLoadingPreview(false);
        }
      };

      // Debounce the API call slightly for angle slider
      const timeoutId = setTimeout(fetchPreview, 300);
      return () => clearTimeout(timeoutId);
    } else {
      setPreview(null);
    }
  }, [sourceCard, targetCardId, bitIndex, angleDeg, gameId]);

  const handleSourceSelect = (index: number) => {
    setSourceCard(index);
    // Clear target if it was the same card
    if (targetCardId === `P${myPlayerNumber}H${index + 1}`) {
      setTargetCardId(null);
    }
  };

  const handleTargetSelect = (cardId: string) => {
    // Can't select the same card as source
    if (sourceCard !== null && `P${myPlayerNumber}H${sourceCard + 1}` === cardId) {
      return;
    }
    setTargetCardId(cardId);
  };

  const toggleOpponent = (opponentNumber: number) => {
    setExpandedOpponents(prev => {
      const newSet = new Set(prev);
      if (newSet.has(opponentNumber)) {
        newSet.delete(opponentNumber);
      } else {
        newSet.add(opponentNumber);
      }
      return newSet;
    });
  };

  const handleConfirm = () => {
    if (sourceCard !== null && targetCardId !== null) {
      if (targetCardId === 'PHASE') {
        // Convert degrees to radians for backend (Qiskit expects radians)
        const angleRad = (angleDeg * Math.PI) / 180;
        onEntangle(sourceCard, targetCardId, bitIndex, angleRad);
      } else {
        onEntangle(sourceCard, targetCardId, bitIndex);
      }
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 rounded-xl p-8 max-w-6xl w-full max-h-[90vh] overflow-y-auto shadow-2xl border-2 border-purple-500">
        <div className="text-center mb-6">
          <div className="flex items-center justify-center mb-4 gap-2">
            <Zap className="text-purple-400" size={32} />
            <h2 className="text-3xl font-bold text-white">Quantum Operations</h2>
            <span className="text-xs bg-purple-600 text-white px-2 py-1 rounded-full">
              Superposition • Phase • Entanglement
            </span>
          </div>
          <p className="text-gray-400 mb-2">
            Select one of your cards, then choose an operation
          </p>
          <p className="text-sm text-gray-500">
            Manipulate quantum states to change your cards at showdown
          </p>
        </div>

        {/* Available Quantum Chips */}
        <div className="bg-gray-800 rounded-lg p-4 mb-6 flex items-center justify-between">
          <span className="text-gray-400">Available Quantum Chips:</span>
          <ChipStack amount={availableQuantumChips} size="lg" className="text-purple-400" />
        </div>

        {/* Select Your Card */}
        <div className="mb-8">
          <h3 className="text-white font-semibold mb-4">
            Select Your Card & Bit
          </h3>
          <div className="flex justify-center gap-6">
            {myCards.map((card, index) => {
              const cardId = `P${myPlayerNumber}H${index + 1}`;
              return (
                <button
                  key={index}
                  onClick={() => handleSourceSelect(index)}
                  className={`transform transition-all duration-200 hover:scale-105 ${
                    sourceCard === index
                      ? 'ring-4 ring-purple-500 scale-110'
                      : 'hover:ring-2 hover:ring-purple-300'
                  }`}
                >
                  <div className="scale-125">
                    <Card card={card} />
                  </div>
                </button>
              );
            })}
          </div>
          
          {/* Bit Selection for Source Card */}
          {sourceCard !== null && (
            <div className="mt-4">
              <h4 className="text-gray-400 text-sm mb-3 text-center">Select which bit to manipulate:</h4>
              <div className="grid grid-cols-3 gap-3 max-w-2xl mx-auto">
                <button
                  onClick={() => setBitIndex(0)}
                  className={`p-3 rounded-lg border-2 transition-all ${
                    bitIndex === 0
                      ? 'border-purple-500 bg-purple-600/30 ring-2 ring-purple-400'
                      : 'border-gray-700 bg-gray-800/50 hover:border-purple-400'
                  }`}
                >
                  <div className="text-white font-bold mb-1">Bit 0</div>
                  <div className="text-purple-400 text-sm">±1 rank</div>
                  <div className="text-gray-500 text-xs mt-1">Small</div>
                </button>
                <button
                  onClick={() => setBitIndex(1)}
                  className={`p-3 rounded-lg border-2 transition-all ${
                    bitIndex === 1
                      ? 'border-purple-500 bg-purple-600/30 ring-2 ring-purple-400'
                      : 'border-gray-700 bg-gray-800/50 hover:border-purple-400'
                  }`}
                >
                  <div className="text-white font-bold mb-1">Bit 1</div>
                  <div className="text-purple-400 text-sm">±2 rank</div>
                  <div className="text-gray-500 text-xs mt-1">Medium</div>
                </button>
                <button
                  onClick={() => setBitIndex(2)}
                  className={`p-3 rounded-lg border-2 transition-all ${
                    bitIndex === 2
                      ? 'border-purple-500 bg-purple-600/30 ring-2 ring-purple-400'
                      : 'border-gray-700 bg-gray-800/50 hover:border-purple-400'
                  }`}
                >
                  <div className="text-white font-bold mb-1">Bit 2</div>
                  <div className="text-purple-400 text-sm">±4 rank</div>
                  <div className="text-gray-500 text-xs mt-1">Large</div>
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Select Operation */}
        <div className="mb-8">
          <h3 className="text-white font-semibold mb-4">
            Select Operation
          </h3>
          
          {/* Self-Superposition Option */}
          <div className="mb-6">
            <h4 className="text-gray-400 text-sm mb-3">Your Cards</h4>
            <button
              onClick={() => handleTargetSelect('SELF')}
              className={`w-full p-4 rounded-lg border-2 transition-all ${
                targetCardId === 'SELF'
                  ? 'border-blue-500 bg-blue-600/30'
                  : 'border-gray-700 bg-gray-800/50 hover:border-blue-400'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="text-3xl">⚛️</span>
                  <div className="text-left">
                    <div className="text-white font-bold">Self (Superposition)</div>
                    <div className="text-gray-400 text-xs">Put your card in superposition - costs 1 chip</div>
                  </div>
                </div>
                {targetCardId === 'SELF' && (
                  <span className="text-xs bg-blue-600 text-white px-2 py-0.5 rounded">
                    Selected
                  </span>
                )}
              </div>
            </button>
            
            {/* Phase Interference Option */}
            <button
              onClick={() => handleTargetSelect('PHASE')}
              className={`w-full p-4 rounded-lg border-2 transition-all mt-3 ${
                targetCardId === 'PHASE'
                  ? 'border-blue-500 bg-blue-600/30'
                  : 'border-gray-700 bg-gray-800/50 hover:border-blue-400'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="text-3xl">〰️</span>
                  <div className="text-left">
                    <div className="text-white font-bold">Phase (Interference)</div>
                    <div className="text-gray-400 text-xs">Apply phase shift to create interference - costs 1 chip</div>
                  </div>
                </div>
                {targetCardId === 'PHASE' && (
                  <span className="text-xs bg-blue-600 text-white px-2 py-0.5 rounded">
                    Selected
                  </span>
                )}
              </div>
            </button>
            {/* Angle slider shown when PHASE selected */}
            {targetCardId === 'PHASE' && (
              <div className="mt-3 px-2">
                <label className="text-sm text-gray-400">Phase Angle: {angleDeg}°</label>
                <input
                  type="range"
                  min={0}
                  max={360}
                  step={1}
                  value={angleDeg}
                  onChange={(e) => setAngleDeg(parseInt(e.target.value, 10))}
                  className="w-full mt-2"
                />
                <div className="text-xs text-gray-500 mt-1">(0° = no-op, 180° ≈ Z gate)</div>
              </div>
            )}
          </div>
          
          {/* Community Cards */}
          {communityCards.length > 0 && (
            <div className="mb-6">
              <h4 className="text-gray-400 text-sm mb-3">Community Cards</h4>
              <div className="flex justify-center gap-4">
                {communityCards.map((cardWithId, index) => {
                  const cardId = cardWithId.id;
                  const isSourceCard = sourceCard !== null && `P${myPlayerNumber}H${sourceCard + 1}` === cardId;
                  return (
                    <button
                      key={`community-${cardId}`}
                      onClick={() => handleTargetSelect(cardId)}
                      disabled={isSourceCard}
                      className={`transform transition-all duration-200 hover:scale-105 ${
                        targetCardId === cardId
                          ? 'ring-4 ring-green-500 scale-110'
                          : 'hover:ring-2 hover:ring-green-300'
                      } ${
                        isSourceCard
                          ? 'opacity-50 cursor-not-allowed'
                          : ''
                      }`}
                    >
                      <Card card={cardWithId.card} />
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* Opponent Cards (Face Down) - Collapsible */}
          {opponents.map((opponent) => {
            const isExpanded = expandedOpponents.has(opponent.number);
            const hasSelectedCard = [0, 1].some(idx => 
              targetCardId === `P${opponent.number}H${idx + 1}`
            );
            
            return (
              <div key={opponent.number} className="mb-3">
                <button
                  onClick={() => toggleOpponent(opponent.number)}
                  className={`w-full flex items-center justify-between p-3 rounded-lg border-2 transition-all ${
                    hasSelectedCard
                      ? 'border-green-500 bg-green-900/20'
                      : 'border-gray-700 bg-gray-800/50 hover:border-gray-600'
                  }`}
                >
                  <div className="flex items-center text-gray-300">
                    <User className="mr-2" size={16} />
                    <span className="font-medium">
                      {opponent.name || `Player ${opponent.number}`}'s Cards
                    </span>
                    <span className="ml-2 text-xs bg-orange-600 text-white px-2 py-0.5 rounded">
                      Costs 2 chips
                    </span>
                    {hasSelectedCard && (
                      <span className="ml-2 text-xs bg-green-600 text-white px-2 py-0.5 rounded">
                        Selected
                      </span>
                    )}
                  </div>
                  {isExpanded ? (
                    <ChevronUp className="text-gray-400" size={20} />
                  ) : (
                    <ChevronDown className="text-gray-400" size={20} />
                  )}
                </button>
                
                {isExpanded && (
                  <div className="flex justify-center gap-4 mt-3 px-4">
                    {[0, 1].map((cardIndex) => {
                      const cardId = `P${opponent.number}H${cardIndex + 1}`;
                      const isSourceCard = sourceCard !== null && `P${myPlayerNumber}H${sourceCard + 1}` === cardId;
                      
                      return (
                        <button
                          key={`opponent-${opponent.number}-${cardIndex}`}
                          onClick={() => handleTargetSelect(cardId)}
                          disabled={isSourceCard}
                          className={`transform transition-all duration-200 hover:scale-105 ${
                            targetCardId === cardId
                              ? 'ring-4 ring-green-500 scale-110'
                              : 'hover:ring-2 hover:ring-green-300'
                          } ${
                            isSourceCard
                              ? 'opacity-50 cursor-not-allowed'
                              : ''
                          }`}
                        >
                          {/* Show face-down card for opponents */}
                          <div className="relative">
                            <Card card={{ rank: '?', suit: '?' }} />
                            <div className="absolute inset-0 bg-gradient-to-br from-blue-500/20 to-purple-500/20 rounded-lg pointer-events-none" />
                          </div>
                        </button>
                      );
                    })}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Probability Preview */}
        {preview && (
          <div className="bg-gradient-to-br from-purple-900/40 to-blue-900/40 border-2 border-purple-400 rounded-lg p-4 mb-6">
            <div className="flex items-center gap-2 mb-3">
              <TrendingUp className="text-purple-400" size={20} />
              <h3 className="text-white font-semibold">Probability Preview</h3>
              {loadingPreview && (
                <span className="text-xs text-gray-400">(updating...)</span>
              )}
            </div>
            
            <div className="text-sm text-gray-300 mb-3">
              <p>Source: <span className="text-white font-medium">{preview.source_card}</span></p>
              <p className="text-xs text-gray-400 mt-1">
                Most likely outcomes at showdown:
              </p>
            </div>

            <div className="space-y-2">
              {preview.outcomes.map((outcome, idx) => (
                <div key={idx} className="flex items-center gap-3">
                  <div className="flex-1 bg-gray-800/50 rounded-full h-6 relative overflow-hidden">
                    <div 
                      className="absolute inset-y-0 left-0 bg-gradient-to-r from-purple-500 to-blue-500 transition-all duration-300"
                      style={{ width: `${outcome.probability}%` }}
                    />
                    <div className="absolute inset-0 flex items-center justify-between px-3">
                      <span className="text-xs font-medium text-white drop-shadow">
                        {outcome.card}
                      </span>
                      <span className="text-xs font-bold text-white drop-shadow">
                        {outcome.probability}%
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {targetCardId === 'PHASE' && (
              <p className="text-xs text-gray-400 mt-3 italic">
                💡 Tip: Adjust the angle slider to see how phase changes probabilities
              </p>
            )}
          </div>
        )}

        {/* Info Box */}
        <div className="bg-purple-900 bg-opacity-30 border border-purple-500 rounded-lg p-4 mb-6">
          <div className="flex items-start">
            <Zap className="text-purple-400 mr-3 mt-1 flex-shrink-0" size={20} />
            <div className="text-sm text-gray-300">
              <p className="mb-2">
                <strong>How it works:</strong>
              </p>
              <ul className="list-disc list-inside space-y-1 text-gray-400">
                <li>Select one of your cards and which bit to manipulate (0-2)</li>
                <li>Choose an operation: Superposition, Phase, or Entangle with another card</li>
                <li>Affected cards collapse to quantum measurement at showdown</li>
                <li><strong className="text-blue-400">Superposition/Phase: 1 chip</strong></li>
                <li><strong className="text-purple-400">Entangle own/community: 1 chip</strong></li>
                <li><strong className="text-orange-400">Entangle opponent: 2 chips</strong></li>
              </ul>
            </div>
          </div>
        </div>

        {/* Cost Display */}
        {targetCardId && (
          <div className={`mb-4 p-3 rounded-lg text-center font-semibold ${
            isOpponentCard 
              ? 'bg-orange-900/30 border border-orange-500 text-orange-300'
              : 'bg-purple-900/30 border border-purple-500 text-purple-300'
          }`}>
            Cost: {chipCost} Quantum Chip{chipCost > 1 ? 's' : ''}
            {!hasEnoughChips && (
              <span className="ml-2 text-red-400 text-sm">
                (Not enough chips!)
              </span>
            )}
          </div>
        )}

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
            disabled={sourceCard === null || targetCardId === null || !hasEnoughChips}
            className={`flex-1 px-6 py-3 font-semibold rounded-lg transition-all flex items-center justify-center ${
              sourceCard !== null && targetCardId !== null && hasEnoughChips
                ? 'bg-purple-600 hover:bg-purple-500 text-white hover:shadow-lg hover:shadow-purple-500/50'
                : 'bg-gray-600 text-gray-400 cursor-not-allowed'
            }`}
          >
            <Zap className="mr-2" size={20} />
            Apply Operation ({chipCost} chip{chipCost > 1 ? 's' : ''})
          </button>
        </div>
      </div>
    </div>
  );
}


