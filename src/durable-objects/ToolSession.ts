export class ToolSession implements DurableObject {
  private state: DurableObjectState;
  private env: any;

  constructor(state: DurableObjectState, env: any) {
    this.state = state;
    this.env = env;
  }

  async fetch(request: Request): Promise<Response> {
    const url = new URL(request.url);
    const sessionId = url.pathname.split('/')[1];

    switch (request.method) {
      case 'GET':
        return this.getSession(sessionId);
      case 'POST':
        return this.createSession(sessionId, request);
      case 'PUT':
        return this.updateSession(sessionId, request);
      case 'DELETE':
        return this.deleteSession(sessionId);
      default:
        return new Response('Method not allowed', { status: 405 });
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

  private async createSession(sessionId: string, request: Request): Promise<Response> {
    try {
      const sessionData = await request.json() as any;
      const session = Object.assign({
        id: sessionId,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
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

  private async updateSession(sessionId: string, request: Request): Promise<Response> {
    try {
      const existingSession = await this.state.storage.get(`session:${sessionId}`) as any;
      if (!existingSession) {
        return new Response('Session not found', { status: 404 });
      }

      const updateData = await request.json() as any;
      const updatedSession = Object.assign({}, existingSession, updateData, {
        updatedAt: new Date().toISOString()
      });

      await this.state.storage.put(`session:${sessionId}`, updatedSession);
      
      return new Response(JSON.stringify(updatedSession), {
        headers: { 'Content-Type': 'application/json' }
      });
    } catch (error) {
      return new Response('Update failed', { status: 500 });
    }
  }

  private async deleteSession(sessionId: string): Promise<Response> {
    try {
      const deleted = await this.state.storage.delete(`session:${sessionId}`);
      if (!deleted) {
        return new Response('Session not found', { status: 404 });
      }
      return new Response('Session deleted', { status: 200 });
    } catch (error) {
      return new Response('Delete failed', { status: 500 });
    }
  }
}
