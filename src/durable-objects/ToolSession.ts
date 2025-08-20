interface SessionData {
  id: string;
  createdAt: string;
  updatedAt: string;
  status: 'active' | 'inactive' | 'streaming';
  toolExecutions: Array<{
    id: string;
    toolName: string;
    agent: string;
    status: 'running' | 'completed' | 'failed';
    startTime: string;
    endTime?: string;
    progress?: number;
  }>;
  websocketConnections: number;
  lastActivity: string;
}

interface StreamMessage {
  type: 'progress' | 'data' | 'error' | 'complete' | 'connection' | 'ping' | 'pong';
  timestamp: string;
  data: any;
  source?: string;
  sessionId?: string;
  requestId?: string;
}

export class ToolSession implements DurableObject {
  private state: DurableObjectState;
  private env: any;
  private websockets: Set<WebSocket>;
  private streamingConnections: Map<string, ReadableStreamDefaultController>;

  constructor(state: DurableObjectState, env: any) {
    this.state = state;
    this.env = env;
    this.websockets = new Set();
    this.streamingConnections = new Map();
  }

  async fetch(request: Request): Promise<Response> {
    const url = new URL(request.url);
    const sessionId = url.pathname.split('/')[1];

    // Handle WebSocket upgrades
    if (request.headers.get('Upgrade') === 'websocket') {
      return this.handleWebSocket(request, sessionId);
    }

    switch (request.method) {
      case 'GET':
        if (url.pathname.includes('/stream')) {
          return this.getSessionStream(sessionId);
        }
        return this.getSession(sessionId);
      case 'POST':
        if (url.pathname.includes('/stream')) {
          return this.createStreamingSession(sessionId, request);
        }
        return this.createSession(sessionId, request);
      case 'PUT':
        return this.updateSession(sessionId, request);
      case 'DELETE':
        return this.deleteSession(sessionId);
      default:
        return new Response('Method not allowed', { status: 405 });
    }
  }

  private async handleWebSocket(request: Request, sessionId: string): Promise<Response> {
    try {
      const webSocketPair = new WebSocketPair();
      const [client, server] = Object.values(webSocketPair);

      // Accept the WebSocket connection
      server.accept();
      this.websockets.add(server);

      // Update session with WebSocket connection
      const session = await this.getSessionData(sessionId);
      if (session) {
        session.websocketConnections += 1;
        session.status = 'streaming';
        session.lastActivity = new Date().toISOString();
        await this.state.storage.put(`session:${sessionId}`, session);
      }

      // Send welcome message
      server.send(JSON.stringify({
        type: 'connection',
        timestamp: new Date().toISOString(),
        data: {
          message: 'WebSocket connected to ToolSession',
          sessionId: sessionId,
          capabilities: ['real-time-streaming', 'tool-execution', 'progress-updates']
        },
        source: 'durable-object',
        sessionId: sessionId
      } as StreamMessage));

      // Handle WebSocket messages
      server.addEventListener('message', async (event) => {
        try {
          const messageData = JSON.parse(event.data as string);
          await this.handleWebSocketMessage(messageData, sessionId, server);
        } catch (error) {
          server.send(JSON.stringify({
            type: 'error',
            timestamp: new Date().toISOString(),
            data: { error: 'Invalid message format' },
            source: 'durable-object',
            sessionId: sessionId
          } as StreamMessage));
        }
      });

      server.addEventListener('close', async () => {
        this.websockets.delete(server);
        const session = await this.getSessionData(sessionId);
        if (session) {
          session.websocketConnections = Math.max(0, session.websocketConnections - 1);
          if (session.websocketConnections === 0) {
            session.status = 'inactive';
          }
          session.lastActivity = new Date().toISOString();
          await this.state.storage.put(`session:${sessionId}`, session);
        }
      });

      return new Response(null, {
        status: 101,
        webSocket: client
      });

    } catch (error) {
      return new Response('WebSocket setup failed', { status: 500 });
    }
  }

  private async handleWebSocketMessage(messageData: any, sessionId: string, websocket: WebSocket): Promise<void> {
    try {
      switch (messageData.type) {
        case 'ping':
          websocket.send(JSON.stringify({
            type: 'pong',
            timestamp: new Date().toISOString(),
            data: { message: 'pong' },
            source: 'durable-object',
            sessionId: sessionId
          } as StreamMessage));
          break;

        case 'tool_execution':
          await this.handleToolExecutionRequest(messageData, sessionId, websocket);
          break;

        case 'session_status':
          const session = await this.getSessionData(sessionId);
          websocket.send(JSON.stringify({
            type: 'data',
            timestamp: new Date().toISOString(),
            data: { session },
            source: 'durable-object',
            sessionId: sessionId
          } as StreamMessage));
          break;

        default:
          websocket.send(JSON.stringify({
            type: 'error',
            timestamp: new Date().toISOString(),
            data: { error: `Unknown message type: ${messageData.type}` },
            source: 'durable-object',
            sessionId: sessionId
          } as StreamMessage));
      }
    } catch (error) {
      websocket.send(JSON.stringify({
        type: 'error',
        timestamp: new Date().toISOString(),
        data: { error: error instanceof Error ? error.message : String(error) },
        source: 'durable-object',
        sessionId: sessionId
      } as StreamMessage));
    }
  }

  private async handleToolExecutionRequest(messageData: any, sessionId: string, websocket: WebSocket): Promise<void> {
    const { tool_name, agent, parameters, request_id } = messageData;
    const executionId = `exec_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    try {
      // Update session with new tool execution
      const session = await this.getSessionData(sessionId);
      if (session) {
        session.toolExecutions.push({
          id: executionId,
          toolName: tool_name,
          agent: agent,
          status: 'running',
          startTime: new Date().toISOString(),
          progress: 0
        });
        await this.state.storage.put(`session:${sessionId}`, session);
      }

      // Send acknowledgment
      websocket.send(JSON.stringify({
        type: 'progress',
        timestamp: new Date().toISOString(),
        data: {
          message: `Starting ${agent}.${tool_name} execution...`,
          progress: 5,
          executionId: executionId
        },
        source: 'durable-object',
        sessionId: sessionId,
        requestId: request_id
      } as StreamMessage));

      // Forward to backend for actual execution
      const backendResponse = await fetch(`${this.env.BACKEND_URL}/execute/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream'
        },
        body: JSON.stringify({
          tool_name,
          agent,
          parameters,
          request_id
        })
      });

      if (!backendResponse.body) {
        throw new Error('No response body from backend');
      }

      // Stream the response back through WebSocket
      const reader = backendResponse.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const eventData = line.slice(6);
            try {
              const parsedData = JSON.parse(eventData);
              
              // Update session progress
              if (parsedData.type === 'progress' && session) {
                const execution = session.toolExecutions.find(e => e.id === executionId);
                if (execution) {
                  execution.progress = parsedData.data?.progress || execution.progress;
                  await this.state.storage.put(`session:${sessionId}`, session);
                }
              }

              // Forward to WebSocket
              websocket.send(JSON.stringify({
                ...parsedData,
                executionId: executionId,
                source: parsedData.source || 'backend-via-durable-object'
              } as StreamMessage));

            } catch (parseError) {
              // Forward raw data if parsing fails
              websocket.send(JSON.stringify({
                type: 'data',
                timestamp: new Date().toISOString(),
                data: eventData,
                source: 'backend-raw',
                sessionId: sessionId,
                requestId: request_id
              } as StreamMessage));
            }
          }
        }
      }

      // Mark execution as completed
      if (session) {
        const execution = session.toolExecutions.find(e => e.id === executionId);
        if (execution) {
          execution.status = 'completed';
          execution.endTime = new Date().toISOString();
          execution.progress = 100;
          await this.state.storage.put(`session:${sessionId}`, session);
        }
      }

    } catch (error) {
      // Mark execution as failed
      const session = await this.getSessionData(sessionId);
      if (session) {
        const execution = session.toolExecutions.find(e => e.id === executionId);
        if (execution) {
          execution.status = 'failed';
          execution.endTime = new Date().toISOString();
          await this.state.storage.put(`session:${sessionId}`, session);
        }
      }

      websocket.send(JSON.stringify({
        type: 'error',
        timestamp: new Date().toISOString(),
        data: { error: error.message, executionId: executionId },
        source: 'durable-object',
        sessionId: sessionId,
        requestId: request_id
      } as StreamMessage));
    }
  }

  private async getSessionData(sessionId: string): Promise<SessionData | null> {
    try {
      return await this.state.storage.get(`session:${sessionId}`) as SessionData;
    } catch (error) {
      return null;
    }
  }

  private async getSession(sessionId: string): Promise<Response> {
    try {
      const session = await this.state.storage.get(`session:${sessionId}`);
      if (!session) {
        return new Response('Session not found', { status: 404 });
      }
      return new Response(JSON.stringify(session), {
        headers: { 'Content-Type': 'application/json' }
      });
    } catch (error) {
      return new Response('Internal error', { status: 500 });
    }
  }

  private async getSessionStream(sessionId: string): Promise<Response> {
    try {
      const session = await this.getSessionData(sessionId);
      if (!session) {
        return new Response('Session not found', { status: 404 });
      }

      // Create a streaming response for session updates
      return new Response(
        new ReadableStream({
          start(controller) {
            // Send current session state
            const message = {
              type: 'data',
              timestamp: new Date().toISOString(),
              data: { session },
              source: 'durable-object-stream',
              sessionId: sessionId
            };
            const encoder = new TextEncoder();
            controller.enqueue(encoder.encode(`data: ${JSON.stringify(message)}\n\n`));
          }
        }),
        {
          headers: {
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive'
          }
        }
      );
    } catch (error) {
      return new Response('Stream setup failed', { status: 500 });
    }
  }

  private async createSession(sessionId: string, request: Request): Promise<Response> {
    try {
      const sessionData = await request.json() as any;
      const session: SessionData = Object.assign({
        id: sessionId,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        status: 'active',
        toolExecutions: [],
        websocketConnections: 0,
        lastActivity: new Date().toISOString()
      }, sessionData);
      
      await this.state.storage.put(`session:${sessionId}`, session);
      
      return new Response(JSON.stringify(session), {
        status: 201,
        headers: { 'Content-Type': 'application/json' }
      });
    } catch (error) {
      return new Response('Invalid session data', { status: 400 });
    }
  }

  private async createStreamingSession(sessionId: string, request: Request): Promise<Response> {
    try {
      const sessionData = await request.json() as any;
      const session: SessionData = {
        id: sessionId,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        status: 'streaming',
        toolExecutions: [],
        websocketConnections: 0,
        lastActivity: new Date().toISOString(),
        ...sessionData
      };
      
      await this.state.storage.put(`session:${sessionId}`, session);

      // Return streaming response for session creation
      return new Response(
        new ReadableStream({
          start(controller) {
            const message = {
              type: 'data',
              timestamp: new Date().toISOString(),
              data: { 
                message: 'Streaming session created',
                session: session
              },
              source: 'durable-object',
              sessionId: sessionId
            };
            const encoder = new TextEncoder();
            controller.enqueue(encoder.encode(`data: ${JSON.stringify(message)}\n\n`));
            controller.close();
          }
        }),
        {
          status: 201,
          headers: {
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive'
          }
        }
      );
    } catch (error) {
      return new Response('Invalid session data', { status: 400 });
    }
  }

  private async updateSession(sessionId: string, request: Request): Promise<Response> {
    try {
      const existingSession = await this.state.storage.get(`session:${sessionId}`) as SessionData;
      if (!existingSession) {
        return new Response('Session not found', { status: 404 });
      }

      const updateData = await request.json() as any;
      const updatedSession: SessionData = Object.assign({}, existingSession, updateData, {
        updatedAt: new Date().toISOString(),
        lastActivity: new Date().toISOString()
      });

      await this.state.storage.put(`session:${sessionId}`, updatedSession);
      
      // Broadcast update to WebSocket connections
      await this.broadcastToWebSockets({
        type: 'data',
        timestamp: new Date().toISOString(),
        data: { 
          message: 'Session updated',
          session: updatedSession
        },
        source: 'durable-object',
        sessionId: sessionId
      });

      return new Response(JSON.stringify(updatedSession), {
        headers: { 'Content-Type': 'application/json' }
      });
    } catch (error) {
      return new Response('Update failed', { status: 500 });
    }
  }

  private async deleteSession(sessionId: string): Promise<Response> {
    try {
      // Close all WebSocket connections for this session
      await this.broadcastToWebSockets({
        type: 'connection',
        timestamp: new Date().toISOString(),
        data: { 
          message: 'Session being deleted, closing connections',
          sessionId: sessionId
        },
        source: 'durable-object',
        sessionId: sessionId
      });

      // Close WebSockets
      for (const ws of this.websockets) {
        ws.close();
      }
      this.websockets.clear();

      const deleted = await this.state.storage.delete(`session:${sessionId}`);
      if (!deleted) {
        return new Response('Session not found', { status: 404 });
      }
      return new Response('Session deleted', { status: 200 });
    } catch (error) {
      return new Response('Delete failed', { status: 500 });
    }
  }

  private async broadcastToWebSockets(message: StreamMessage): Promise<void> {
    const messageStr = JSON.stringify(message);
    for (const ws of this.websockets) {
      try {
        ws.send(messageStr);
      } catch (error) {
        // Remove failed connections
        this.websockets.delete(ws);
      }
    }
  }

  // Cleanup inactive sessions periodically
  async alarm(): Promise<void> {
    try {
      const sessions = await this.state.storage.list();
      const now = Date.now();
      const oneHourAgo = now - (60 * 60 * 1000);

      for (const [key, session] of sessions) {
        if (key.startsWith('session:')) {
          const sessionData = session as SessionData;
          const lastActivity = new Date(sessionData.lastActivity).getTime();
          
          if (lastActivity < oneHourAgo && sessionData.websocketConnections === 0) {
            await this.state.storage.delete(key);
            console.log(`Cleaned up inactive session: ${sessionData.id}`);
          }
        }
      }

      // Schedule next cleanup in 30 minutes
      this.state.storage.setAlarm(Date.now() + 30 * 60 * 1000);
    } catch (error) {
      console.error('Session cleanup failed:', error);
    }
  }
}
