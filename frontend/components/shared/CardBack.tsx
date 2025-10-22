// Face-down card component

interface CardBackProps {
  className?: string;
}

export default function CardBack({ className = '' }: CardBackProps) {
  return (
    <div 
      className={`
        relative bg-gradient-to-br from-blue-600 to-blue-800
        rounded-lg shadow-lg
        flex items-center justify-center
        border-2 border-blue-900
        transition-all duration-200
        ${className || 'w-16 h-24 sm:w-20 sm:h-32'}
      `}
    >
      {/* Card back pattern */}
      <div className="absolute inset-2 border-4 border-white/30 rounded-md" />
      <div className="text-4xl text-white/40">⚛️</div>
    </div>
  );
}
