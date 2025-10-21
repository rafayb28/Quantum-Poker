// Game state store using Zustand

import { create } from 'zustand';
import { GameState, Player } from '@/types/game';
import { api } from '@/lib/api';

interface GameStore extends Partial<GameState> {
  gameId: string | null;
  myPlayerNumber: number | null;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  setGameState: (state: Partial<GameState>) => void;
  setGameId: (gameId: string, playerNumber: number) => void;
  clearGame: () => void;
  performAction: (action: string, amount?: number) => Promise<void>;
  performQuantumAction: (source: number, target: string, bit: number) => Promise<void>;
  loadGameState: () => Promise<void>;
  clearError: () => void;
}

const initialState = {
  gameId: null,
  myPlayerNumber: null,
  round: 'waiting',
  pot: 0,
  current_bet: 0,
  dealer_position: 0,
  current_player: 0,
  players: [],
  community_cards: { flop: [], turn: null, river: null },
  entanglements: {},
  isLoading: false,
  error: null,
};

export const useGameStore = create<GameStore>((set, get) => ({
  ...initialState,
  
  setGameState: (state: Partial<GameState>) => {
    set({ ...state, error: null });
  },
  
  setGameId: (gameId: string, playerNumber: number) => {
    set({ gameId, myPlayerNumber: playerNumber });
  },
  
  clearGame: () => {
    set(initialState);
  },
  
  performAction: async (action: string, amount?: number) => {
    const { gameId } = get();
    if (!gameId) return;
    
    set({ isLoading: true, error: null });
    try {
      const response = await api.performAction(gameId, action, amount);
      // WebSocket will update state, but we can optimistically update here
      set({ isLoading: false });
    } catch (error: any) {
      set({
        error: error.message || 'Action failed',
        isLoading: false,
      });
      throw error;
    }
  },
  
  performQuantumAction: async (source: number, target: string, bit: number) => {
    const { gameId } = get();
    if (!gameId) return;
    
    set({ isLoading: true, error: null });
    try {
      await api.performQuantumAction(gameId, source, target, bit);
      set({ isLoading: false });
    } catch (error: any) {
      set({
        error: error.message || 'Quantum action failed',
        isLoading: false,
      });
      throw error;
    }
  },
  
  loadGameState: async () => {
    const { gameId } = get();
    if (!gameId) return;
    
    set({ isLoading: true, error: null });
    try {
      const state = await api.getGameState(gameId);
      set({ ...state, isLoading: false });
    } catch (error: any) {
      set({
        error: error.message || 'Failed to load game state',
        isLoading: false,
      });
    }
  },
  
  clearError: () => set({ error: null }),
}));
