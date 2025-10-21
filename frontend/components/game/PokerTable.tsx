// Main poker table component

import { Player } from '@/types/game';
import PlayerSeat from './PlayerSeat';
import CommunityCards from './CommunityCards';
import PotDisplay from './PotDisplay';
import { Card as CardType, CommunityCards as CommunityCardsType } from '@/types/game';

interface PokerTableProps {
  players: Player[];
  communityCards: CommunityCardsType;
  pot: number;
  currentPlayer: number;
  myPlayerNumber: number;
}

export default function PokerTable({
  players,
  communityCards,
  pot,
  currentPlayer,
  myPlayerNumber
}: PokerTableProps) {
  return (
    <div className="relative w-full h-full min-h-[600px] bg-gradient-to-br from-green-900 via-green-800 to-emerald-900 rounded-3xl border-8 border-amber-900 shadow-2xl p-8">
      {/* Felt texture overlay */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-transparent via-green-900/20 to-green-900/40 rounded-2xl pointer-events-none" />
      
      {/* Center area */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 flex flex-col items-center gap-6">
        {/* Pot */}
        <PotDisplay amount={pot} />
        
        {/* Community Cards */}
        <CommunityCards
          flop={communityCards.flop}
          turn={communityCards.turn}
          river={communityCards.river}
        />
      </div>
      
      {/* Player Seats - only show players who have joined */}
      {players
        .filter(player => player.name && player.name.trim() !== '')
        .map((player, idx) => (
          <PlayerSeat
            key={player.number}
            player={player}
            position={idx}
            isCurrentPlayer={currentPlayer - 1 === (player.number - 1)}
            isMe={player.number === myPlayerNumber}
          />
        ))}
    </div>
  );
}
