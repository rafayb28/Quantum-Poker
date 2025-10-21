// Pot display component

import ChipStack from '@/components/shared/ChipStack';

interface PotDisplayProps {
  amount: number;
  className?: string;
}

export default function PotDisplay({ amount, className = '' }: PotDisplayProps) {
  return (
    <div className={`bg-gray-900/80 backdrop-blur-sm rounded-xl px-6 py-4 border-2 border-yellow-500 ${className}`}>
      <div className="text-center">
        <p className="text-gray-400 text-sm mb-1">Pot</p>
        <ChipStack amount={amount} size="lg" />
      </div>
    </div>
  );
}
