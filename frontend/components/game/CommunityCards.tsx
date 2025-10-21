// Community cards display component

import Card from '@/components/shared/Card';
import CardBack from '@/components/shared/CardBack';
import { Card as CardType } from '@/types/game';

interface CommunityCardsProps {
  flop: CardType[];
  turn: CardType | null;
  river: CardType | null;
  className?: string;
}

export default function CommunityCards({ flop, turn, river, className = '' }: CommunityCardsProps) {
  return (
    <div className={`flex items-center justify-center gap-2 sm:gap-3 ${className}`}>
      {/* Flop */}
      {flop.length > 0 ? (
        flop.map((card, idx) => (
          <Card key={`flop-${idx}`} card={card} />
        ))
      ) : (
        <>
          <CardBack />
          <CardBack />
          <CardBack />
        </>
      )}
      
      {/* Turn */}
      {turn ? (
        <Card card={turn} />
      ) : (
        <CardBack />
      )}
      
      {/* River */}
      {river ? (
        <Card card={river} />
      ) : (
        <CardBack />
      )}
    </div>
  );
}
