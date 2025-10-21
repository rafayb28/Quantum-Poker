// Chip stack display component

import { Coins } from 'lucide-react';

interface ChipStackProps {
  amount: number;
  label?: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export default function ChipStack({ 
  amount, 
  label, 
  size = 'md',
  className = '' 
}: ChipStackProps) {
  const sizeClasses = {
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-lg'
  };
  
  const iconSizes = {
    sm: 16,
    md: 20,
    lg: 24
  };
  
  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <Coins className="text-yellow-500" size={iconSizes[size]} />
      <div className={`${sizeClasses[size]}`}>
        <span className="font-bold text-yellow-500">{amount.toLocaleString()}</span>
        {label && <span className="text-gray-400 ml-1">{label}</span>}
      </div>
    </div>
  );
}
