// Type definitions for the Quantum Poker game

export interface Card {
  suit: string;
  rank: string;
}

export interface EntanglementRecord {
  source: string;
  target: string;
  bit: number;
  effect: string;
}

export interface Player {
  name: string;
  number: number;
  chips: number;
  quantum_chips: number;
  current_bet: number;
  total_bet_this_round: number;
  folded: boolean;
  all_in: boolean;
  hand: Card[] | null; // null if cards are hidden
  entanglement_history?: EntanglementRecord[];
}

export interface CommunityCards {
  flop: Card[];
  turn: Card | null;
  river: Card | null;
}

export interface Entanglement {
  card1: string;
  card2: string;
  bit: number;
}

export interface GameState {
  game_id?: string;
  round: string;
  pot: number;
  current_bet: number;
  dealer_position: number;
  current_player: number;
  players: Player[];
  community_cards: CommunityCards;
  entanglements: Record<string, Array<[string, number]>>;
  winner_info?: WinnerInfo;
  players_joined?: number;
  joined_player_names?: string[];
}

export interface WinnerInfo {
  winners: Array<{
    player_num: number;
    player_name: string;
    hand_name: string;
    kickers: number[];
    best_cards: Card[];
  }>;
  all_hands: Record<string, any>;
}

export type PokerAction = 'fold' | 'check' | 'call' | 'raise' | 'all_in';

export interface ActionRequest {
  action: PokerAction;
  amount?: number;
}

export interface QuantumActionRequest {
  action: 'entangle';
  source_card_idx: number;
  target_card_id: string;
  bit_index: number;
  angle?: number; // optional angle in radians for phase (RZ)
}

export interface CreateGameRequest {
  // No parameters needed - always creates 6-player games
}

export interface WebSocketMessage {
  type: 'connected' | 'game_update' | 'pong' | 'error' | 'game_destroyed';
  state?: GameState;
  message?: string;
}
