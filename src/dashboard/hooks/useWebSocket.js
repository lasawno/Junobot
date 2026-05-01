import { useEffect, useState, useRef } from 'react';

export function useWebSocket(url) {
  const [ws, setWs] = useState(null);
  const wsRef = useRef(null);

  useEffect(() => {
    const connect = () => {
      try {
        const socket = new WebSocket(url);

        socket.onopen = () => {
          console.log('WebSocket connected');
          setWs(socket);
        };

        socket.onerror = (err) => {
          console.error('WebSocket error:', err);
        };

        socket.onclose = () => {
          console.log('WebSocket disconnected');
          setWs(null);
          // Attempt to reconnect after 3 seconds
          setTimeout(connect, 3000);
        };

        wsRef.current = socket;
      } catch (err) {
        console.error('Failed to create WebSocket:', err);
      }
    };

    connect();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [url]);

  return ws;
}
