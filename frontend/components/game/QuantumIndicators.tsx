'use client';

import { Player } from '@/types/game';

interface QuantumOperation {
  type: 'ENTANGLE' | 'SELF' | 'PHASE';
  sourceCardId: string;
  targetCardId?: string;
  playerName: string;
  playerNumber: number;
  bitIndex: number;
}

interface QuantumIndicatorsProps {
  players: Player[];
  myPlayerNumber: number;
}

// Helper to parse entanglement history into visual operations
function parseQuantumOperations(players: Player[]): QuantumOperation[] {
  const operations: QuantumOperation[] = [];

  players.forEach(player => {
    if (!player.entanglement_history) return;

    player.entanglement_history.forEach(record => {
      // Determine operation type based on target
      if (record.target === 'SELF') {
        operations.push({
          type: 'SELF',
          sourceCardId: record.source,
          playerName: player.name,
          playerNumber: player.number,
          bitIndex: record.bit
        });
      } else if (record.target === 'PHASE') {
        operations.push({
          type: 'PHASE',
          sourceCardId: record.source,
          playerName: player.name,
          playerNumber: player.number,
          bitIndex: record.bit
        });
      } else {
        operations.push({
          type: 'ENTANGLE',
          sourceCardId: record.source,
          targetCardId: record.target,
          playerName: player.name,
          playerNumber: player.number,
          bitIndex: record.bit
        });
      }
    });
  });

  return operations;
}

// Helper to get card display name with player names
function getCardDisplayName(cardId: string, players: Player[]): string {
  if (cardId.startsWith('P')) {
    const playerNum = parseInt(cardId[1]);
    const cardNum = cardId[3];
    const player = players.find(p => p.number === playerNum);
    const playerName = player?.name || `P${playerNum}`;
    return `${playerName}'s card ${cardNum}`;
  }
  if (cardId === 'F0') return 'flop card 1';
  if (cardId === 'F1') return 'flop card 2';
  if (cardId === 'F2') return 'flop card 3';
  if (cardId === 'T') return 'turn';
  if (cardId === 'R') return 'river';
  return cardId;
}

export default function QuantumIndicators({ players, myPlayerNumber }: QuantumIndicatorsProps) {
  const operations = parseQuantumOperations(players);

  if (operations.length === 0) {
    return null;
  }

  return (
    <div className="bg-gray-800/50 border border-purple-500/30 rounded-lg p-3">
      <h3 className="text-sm font-semibold text-purple-400 mb-2 flex items-center gap-2">
        <span className="text-lg">⚛️</span>
        Quantum Operations
      </h3>
      
      <div className="space-y-1.5 max-h-32 overflow-y-auto">
        {operations.map((op, idx) => {
          const isMyOp = op.playerNumber === myPlayerNumber;
          
          return (
            <div 
              key={idx}
              className={`text-xs px-2 py-1.5 rounded ${
                isMyOp 
                  ? 'bg-purple-600/20 border border-purple-500/40' 
                  : 'bg-gray-700/40 border border-gray-600/40'
              }`}
            >
              {op.type === 'ENTANGLE' && (
                <div className="flex items-center gap-1.5">
                  <span className="text-blue-400 font-mono">🔗</span>
                  <span className="text-gray-300">
                    <span className="font-semibold text-white">{op.playerName}</span>
                    {' '}entangled{' '}
                    <span className="text-blue-300">{getCardDisplayName(op.sourceCardId, players)}</span>
                    {' '}↔{' '}
                    <span className="text-blue-300">{getCardDisplayName(op.targetCardId!, players)}</span>
                    {' '}(bit {op.bitIndex})
                  </span>
                </div>
              )}
              
              {op.type === 'SELF' && (
                <div className="flex items-center gap-1.5">
                  <span className="text-green-400 font-mono">⚛️</span>
                  <span className="text-gray-300">
                    <span className="font-semibold text-white">{op.playerName}</span>
                    {' '}→{' '}
                    <span className="text-green-300">{getCardDisplayName(op.sourceCardId, players)}</span>
                    {' '}→ superposition (bit {op.bitIndex})
                  </span>
                </div>
              )}
              
              {op.type === 'PHASE' && (
                <div className="flex items-center gap-1.5">
                  <span className="text-indigo-400 font-mono">〰️</span>
                  <span className="text-gray-300">
                    <span className="font-semibold text-white">{op.playerName}</span>
                    {' '}→{' '}
                    <span className="text-indigo-300">{getCardDisplayName(op.sourceCardId, players)}</span>
                    {' '}→ phase (bit {op.bitIndex})
                  </span>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
