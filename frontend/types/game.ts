// Type definitions for the Quantum Poker game

export interface Card {
  suit: string;
  rank: string;
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
}

export interface CreateGameRequest {
  num_players: number;
  max_players: number;
}

export interface WebSocketMessage {
  type: 'connected' | 'game_update' | 'pong' | 'error';
  state?: GameState;
  message?: string;
}
