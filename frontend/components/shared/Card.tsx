// Playing card component

import { Card as CardType } from '@/types/game';

interface CardProps {
  card: CardType;
  className?: string;
  isEntangled?: boolean;
}

const getSuitSymbol = (suit: string): string => {
  const suitMap: Record<string, string> = {
    'Spades': '♠',
    'Hearts': '♥',
    'Diamonds': '♦',
    'Clubs': '♣',
  };
  return suitMap[suit] || suit;
};

const getSuitColor = (suit: string): string => {
  return suit === 'Hearts' || suit === 'Diamonds' ? 'text-red-600' : 'text-gray-900';
};

const getRankDisplay = (rank: string): string => {
  const rankMap: Record<string, string> = {
    'Ace': 'A',
    'Jack': 'J',
    'Queen': 'Q',
    'King': 'K',
  };
  return rankMap[rank] || rank;
};

export default function Card({ card, className = '', isEntangled = false }: CardProps) {
  const suitSymbol = getSuitSymbol(card.suit);
  const suitColor = getSuitColor(card.suit);
  const rankDisplay = getRankDisplay(card.rank);
  
  return (
    <div 
      className={`
        relative bg-white rounded-lg shadow-lg
        flex flex-col items-center justify-center
        border-2 border-gray-300
        transition-all duration-200
        hover:scale-105 hover:shadow-xl
        ${isEntangled ? 'ring-2 ring-purple-500 ring-offset-2 animate-pulse' : ''}
        ${className || 'w-16 h-24 sm:w-20 sm:h-32'}
      `}
    >
      {/* Top corner */}
      <div className={`absolute top-0.5 left-0.5 flex flex-col items-center ${suitColor}`}>
        <span className="text-[10px] sm:text-xs font-bold leading-tight">{rankDisplay}</span>
        <span className="text-[8px] sm:text-[10px] leading-tight">{suitSymbol}</span>
      </div>
      
      {/* Center symbol */}
      <div className={`text-xl sm:text-2xl lg:text-3xl ${suitColor}`}>
        {suitSymbol}
      </div>
      
      {/* Bottom corner (inverted) */}
      <div className={`absolute bottom-0.5 right-0.5 flex flex-col items-center rotate-180 ${suitColor}`}>
        <span className="text-[10px] sm:text-xs font-bold leading-tight">{rankDisplay}</span>
        <span className="text-[8px] sm:text-[10px] leading-tight">{suitSymbol}</span>
      </div>
      
      {/* Quantum entanglement effect */}
      {isEntangled && (
        <div className="absolute inset-0 rounded-lg bg-purple-500/10 pointer-events-none" />
      )}
    </div>
  );
}
