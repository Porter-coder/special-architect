import React, { useState, useEffect, useRef, useCallback } from 'react';

export interface SSEEvent {
  type: string;
  [key: string]: any;
}

export interface SSEConnectorProps {
  url: string;
  onEvent: (event: SSEEvent) => void;
  onStatusChange?: (status: ConnectionStatus) => void;
  autoReconnect?: boolean;
  maxReconnectAttempts?: number;
  heartbeatInterval?: number;
}

export type ConnectionStatus =
  | 'disconnected'
  | 'connecting'
  | 'connected'
  | 'reconnecting'
  | 'error'
  | 'completed';

const SSEConnector: React.FC<SSEConnectorProps> = ({
  url,
  onEvent,
  onStatusChange,
  autoReconnect = true,
  maxReconnectAttempts = 3,
  heartbeatInterval = 30000 // 30 seconds
}) => {
  console.log(`[SSEConnector] COMPONENT MOUNTED with URL: ${url}`);
  console.log(`[SSEConnector] Component rendered with URL: ${url}`);

  // Cleanup function to log when component unmounts
  useEffect(() => {
    return () => {
      console.log(`[SSEConnector] COMPONENT WILL UNMOUNT for URL: ${url}`);
    };
  }, [url]);

  const [status, setStatus] = useState<ConnectionStatus>('disconnected');
  const [reconnectAttempts, setReconnectAttempts] = useState(0);
  const eventSourceRef = useRef<EventSource | null>(null);
  const heartbeatTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const connectRef = useRef<() => void>();
  const disconnectRef = useRef<() => void>();

  const updateStatus = useCallback((newStatus: ConnectionStatus) => {
    setStatus(newStatus);
    onStatusChange?.(newStatus);
  }, [onStatusChange]);

  const clearTimeouts = useCallback(() => {
    if (heartbeatTimeoutRef.current) {
      clearTimeout(heartbeatTimeoutRef.current);
      heartbeatTimeoutRef.current = null;
    }
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
  }, []);

  const disconnect = useCallback(() => {
    clearTimeouts();
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    updateStatus('disconnected');
  }, [clearTimeouts, updateStatus]);

  const startHeartbeat = useCallback(() => {
    clearTimeouts();
    heartbeatTimeoutRef.current = setTimeout(() => {
      console.warn('[SSEConnector] Heartbeat timeout - connection may be lost');
      if (autoReconnect && reconnectAttempts < maxReconnectAttempts) {
        handleReconnect();
      } else {
        updateStatus('error');
      }
    }, heartbeatInterval);
  }, [autoReconnect, maxReconnectAttempts, heartbeatInterval, updateStatus]); // Removed reconnectAttempts

  const handleReconnect = useCallback(() => {
    const attempt = reconnectAttempts + 1;
    setReconnectAttempts(attempt);
    updateStatus('reconnecting');

    console.log(`Attempting to reconnect (${attempt}/${maxReconnectAttempts})...`);

    // Exponential backoff: 1s, 2s, 4s...
    const delay = Math.min(1000 * Math.pow(2, attempt - 1), 10000);

    reconnectTimeoutRef.current = setTimeout(() => {
      connect();
    }, delay);
  }, [reconnectAttempts, maxReconnectAttempts, updateStatus]);

  const connect = useCallback(() => {
    console.log(`[SSEConnector] connect() called for URL: ${url}`);

    if (eventSourceRef.current) {
      console.log(`[SSEConnector] Closing existing EventSource`);
      eventSourceRef.current.close();
    }

    updateStatus('connecting');

    // Store current function in ref
    connectRef.current = connect;
    disconnectRef.current = disconnect;

    try {
      const eventSource = new EventSource(url);
      eventSourceRef.current = eventSource;

      eventSource.onopen = () => {
        console.log(`[SSEConnector] Connection OPEN for ${url}`);
        setReconnectAttempts(0);
        updateStatus('connected');
        startHeartbeat();
      };

      eventSource.onmessage = (event) => {
        console.log(`[SSEConnector] Raw message received: ${event.data.substring(0, 50)}...`);
        try {
          // Parse SSE data as JSON
          const data = JSON.parse(event.data);
          onEvent({ type: 'message', ...data });
          startHeartbeat(); // Reset heartbeat on any message
        } catch (error) {
          console.error('[SSEConnector] Failed to parse SSE message:', error, event.data);
        }
      };

      eventSource.onerror = (error) => {
        console.error(`[SSEConnector] Connection error for ${url}:`, error);
        clearTimeouts();

        if (autoReconnect && reconnectAttempts < maxReconnectAttempts) {
          handleReconnect();
        } else {
          updateStatus('error');
        }
      };

      // Listen for custom events
      eventSource.addEventListener('connected', (event: any) => {
        console.log('[SSEConnector] Connected event received');
        try {
          const data = JSON.parse(event.data);
          onEvent({ type: 'connected', ...data });
        } catch (error) {
          console.error('[SSEConnector] Failed to parse connected event:', error);
        }
        startHeartbeat(); // Reset heartbeat timer
      });

      eventSource.addEventListener('heartbeat', (event: any) => {
        console.log('[SSEConnector] Heartbeat event received');
        try {
          const data = JSON.parse(event.data);
          onEvent({ type: 'heartbeat', ...data });
        } catch (error) {
          console.error('[SSEConnector] Failed to parse heartbeat event:', error);
        }
        startHeartbeat(); // Reset heartbeat timer
      });

      // Listen for generation events
      eventSource.addEventListener('phase_start', (event: any) => {
        console.log('[SSEConnector] Phase start event received');
        try {
          const data = JSON.parse(event.data);
          onEvent({ type: 'phase_start', ...data });
        } catch (error) {
          console.error('[SSEConnector] Failed to parse phase_start event:', error);
        }
      });

      eventSource.addEventListener('chunk', (event: any) => {
        console.log('[SSEConnector] Chunk event received');
        try {
          const data = JSON.parse(event.data);
          onEvent({ type: 'chunk', ...data });
        } catch (error) {
          console.error('[SSEConnector] Failed to parse chunk event:', error);
        }
      });

      eventSource.addEventListener('phase_complete', (event: any) => {
        console.log('[SSEConnector] Phase complete event received');
        try {
          const data = JSON.parse(event.data);
          onEvent({ type: 'phase_complete', ...data });
        } catch (error) {
          console.error('[SSEConnector] Failed to parse phase_complete event:', error);
        }
      });

      eventSource.addEventListener('file_created', (event: any) => {
        console.log('[SSEConnector] File created event received');
        try {
          const data = JSON.parse(event.data);
          onEvent({ type: 'file_created', ...data });
        } catch (error) {
          console.error('[SSEConnector] Failed to parse file_created event:', error);
        }
      });

      eventSource.addEventListener('generation_complete', () => {
        console.log('[SSEConnector] Generation complete event received');
        updateStatus('completed');
        disconnect();
      });

      eventSource.addEventListener('error', (event: any) => {
        console.error('SSE connection error:', event);
        updateStatus('error');
      });

    } catch (error) {
      console.error('Failed to create EventSource:', error);
      updateStatus('error');
    }
  }, [url, onEvent, autoReconnect, maxReconnectAttempts, updateStatus, startHeartbeat, handleReconnect, clearTimeouts, disconnect]);

  const reconnect = useCallback(() => {
    if (status === 'error' || status === 'disconnected') {
      setReconnectAttempts(0);
      connect();
    }
  }, [status, connect]);

  useEffect(() => {
    console.log(`[SSEConnector] useEffect triggered. URL: ${url}, component mounted`);

    // Auto-connect on mount if URL is provided
    if (url) {
      console.log(`[SSEConnector] Creating new EventSource for URL: ${url}`);
      connect();
    }

    // Cleanup on unmount
    return () => {
      console.log(`[SSEConnector] COMPONENT UNMOUNTING - Cleaning up connection for URL: ${url}`);
      if (disconnectRef.current) {
        disconnectRef.current();
      }
    };
  }, [url]); // Only depend on url to prevent reconnect loops

  // Component methods are available through props/onStatusChange callback

  return null; // This is a logic-only component
};

export default SSEConnector;
