// WebSocket hook for real-time game updates

import { useEffect, useRef, useCallback } from 'react';
import { useGameStore } from '@/store/gameStore';
import { WebSocketMessage } from '@/types/game';

const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';

export function useGameWebSocket(gameId: string | null) {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const setGameState = useGameStore((state) => state.setGameState);
  
  const connect = useCallback(() => {
    if (!gameId) return;
    
    // Close existing connection
    if (wsRef.current) {
      wsRef.current.close();
    }
    
    // Get token for authentication
    const token = localStorage.getItem('token');
    if (!token) {
      console.error('No authentication token found');
      return;
    }
    
    console.log(`Connecting to WebSocket: ${WS_BASE_URL}/ws/${gameId}`);
    const ws = new WebSocket(`${WS_BASE_URL}/ws/${gameId}?token=${encodeURIComponent(token)}`);
    
    ws.onopen = () => {
      console.log('WebSocket connected');
      reconnectAttemptsRef.current = 0;
    };
    
    ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        
        switch (message.type) {
          case 'connected':
            console.log('WebSocket connection confirmed');
            if (message.state) {
              setGameState(message.state);
            }
            break;
            
          case 'game_update':
            console.log('Game state updated');
            if (message.state) {
              setGameState(message.state);
            }
            break;
            
          case 'game_destroyed':
            console.log('Game was destroyed by host');
            alert(message.message || 'Host left the game. Returning to lobby...');
            // Close WebSocket and redirect to lobby
            ws.close();
            window.location.href = '/lobby';
            break;
            
          case 'error':
            console.error('WebSocket error:', message.message);
            break;
        }
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    ws.onclose = () => {
      console.log('WebSocket closed');
      wsRef.current = null;
      
      // Attempt to reconnect with exponential backoff
      if (reconnectAttemptsRef.current < 5) {
        const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 10000);
        console.log(`Reconnecting in ${delay}ms...`);
        
        reconnectTimeoutRef.current = setTimeout(() => {
          reconnectAttemptsRef.current++;
          connect();
        }, delay);
      }
    };
    
    wsRef.current = ws;
    
    // Send periodic pings to keep connection alive
    const pingInterval = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'ping' }));
      }
    }, 30000); // Every 30 seconds
    
    return () => {
      clearInterval(pingInterval);
    };
  }, [gameId, setGameState]);
  
  useEffect(() => {
    const cleanup = connect();
    
    return () => {
      if (cleanup) cleanup();
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [connect]);
  
  return {
    isConnected: wsRef.current?.readyState === WebSocket.OPEN,
    reconnect: connect,
  };
}
