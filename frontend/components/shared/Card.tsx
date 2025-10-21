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
        w-16 h-24 sm:w-20 sm:h-32 lg:w-24 lg:h-36
        flex flex-col items-center justify-center
        border-2 border-gray-300
        transition-all duration-200
        hover:scale-105 hover:shadow-xl
        ${isEntangled ? 'ring-2 ring-purple-500 ring-offset-2 animate-pulse' : ''}
        ${className}
      `}
    >
      {/* Top corner */}
      <div className={`absolute top-1 left-1 flex flex-col items-center ${suitColor}`}>
        <span className="text-sm sm:text-base lg:text-lg font-bold leading-none">{rankDisplay}</span>
        <span className="text-xs sm:text-sm lg:text-base leading-none">{suitSymbol}</span>
      </div>
      
      {/* Center symbol */}
      <div className={`text-3xl sm:text-4xl lg:text-5xl ${suitColor}`}>
        {suitSymbol}
      </div>
      
      {/* Bottom corner (inverted) */}
      <div className={`absolute bottom-1 right-1 flex flex-col items-center rotate-180 ${suitColor}`}>
        <span className="text-sm sm:text-base lg:text-lg font-bold leading-none">{rankDisplay}</span>
        <span className="text-xs sm:text-sm lg:text-base leading-none">{suitSymbol}</span>
      </div>
      
      {/* Quantum entanglement effect */}
      {isEntangled && (
        <div className="absolute inset-0 rounded-lg bg-purple-500/10 pointer-events-none" />
      )}
    </div>
  );
}
