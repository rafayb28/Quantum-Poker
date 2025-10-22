// Player seat component

import Card from '@/components/shared/Card';
import CardBack from '@/components/shared/CardBack';
import ChipStack from '@/components/shared/ChipStack';
import { Player } from '@/types/game';
import { Zap } from 'lucide-react';

interface PlayerSeatProps {
  player: Player;
  position: number;
  isCurrentPlayer: boolean;
  isMe: boolean;
  className?: string;
}

export default function PlayerSeat({
  player,
  position,
  isCurrentPlayer,
  isMe,
  className = ''
}: PlayerSeatProps) {
  const getPositionClasses = () => {
    // Position around the table (0-9 for up to 10 players)
    const positions: Record<number, string> = {
      0: 'top-0 left-1/2 -translate-x-1/2',
      1: 'top-8 right-8',
      2: 'top-1/2 right-0 -translate-y-1/2',
      3: 'bottom-8 right-8',
      4: 'bottom-0 right-1/3',
      5: 'bottom-0 left-1/3',
      6: 'bottom-8 left-8',
      7: 'top-1/2 left-0 -translate-y-1/2',
      8: 'top-8 left-8',
    };
    return positions[position] || '';
  };

  return (
    <div 
      className={`
        absolute ${getPositionClasses()}
        transition-all duration-300
        ${className}
      `}
    >
      <div 
        className={`
          bg-gray-900 rounded-xl p-2 sm:p-3 w-[110px] sm:w-[130px]
          border-2 transition-all duration-300
          ${isCurrentPlayer ? 'border-yellow-500 ring-4 ring-yellow-500/50 scale-105' : 'border-gray-700'}
          ${player.folded ? 'opacity-50 grayscale' : ''}
          ${isMe ? 'border-blue-500' : ''}
        `}
      >
        {/* Player Info */}
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-1">
            <p className="text-white font-semibold text-xs truncate max-w-[70px]">
              {player.name}
              {isMe && <span className="text-blue-400 ml-1">(You)</span>}
            </p>
          </div>
          
          {player.quantum_chips > 0 && (
            <div className="flex items-center gap-1 text-purple-400 text-xs flex-shrink-0">
              <Zap size={12} />
              <span>{player.quantum_chips}</span>
            </div>
          )}
        </div>
        
        {/* Chip Stack */}
        <ChipStack amount={player.chips} size="sm" className="mb-2" />
        
        {/* Current Bet */}
        {player.current_bet > 0 && (
          <div className="text-xs text-yellow-500 mb-2">
            Bet: {player.current_bet}
          </div>
        )}
        
        {/* Status */}
        {player.folded && (
          <div className="text-xs text-red-400">Folded</div>
        )}
        {player.all_in && (
          <div className="text-xs text-orange-400 font-bold">ALL IN!</div>
        )}
        
        {/* Cards */}
        <div className="flex gap-1 mt-2 justify-center">
          {player.hand && player.hand.length > 0 ? (
            player.hand.map((card, idx) => (
              <div key={idx} className="w-12 h-16 text-[8px]">
                <Card card={card} className="w-12 h-16 text-[8px]" />
              </div>
            ))
          ) : isMe ? (
            <>
              <CardBack className="w-12 h-16" />
              <CardBack className="w-12 h-16" />
            </>
          ) : (
            <>
              <CardBack className="w-12 h-16" />
              <CardBack className="w-12 h-16" />
            </>
          )}
        </div>
      </div>
    </div>
  );
}
