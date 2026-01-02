import { NextRequest, NextResponse } from 'next/server';

import { streams } from '../../../../lib/store';

export const dynamic = 'force-dynamic';

export async function GET(

  req: NextRequest,

  { params }: { params: { project_id: string } }

) {

  const projectId = params.project_id;

  const encoder = new TextEncoder();

  console.log(`[STREAM] Connection requested: ${projectId}`);

  let interval: NodeJS.Timeout;

  // Create the ReadableStream
  const stream = new ReadableStream({

    start(controller) {

      streams.set(projectId, controller);

      console.log(`[STREAM] Registered: ${projectId} (Total: ${streams.size})`);

      // 1. Initial Handshake
      try {
        controller.enqueue(encoder.encode(`event: connected\ndata: ${JSON.stringify({ status: "ready" })}\n\n`));
        console.log(`[STREAM] Sent handshake for ${projectId}`);
      } catch (e) {
        console.error(`[STREAM] Failed to send handshake: ${e}`);
        return;
      }

      // 2. Heartbeat (Every 10s)
      interval = setInterval(() => {
        try {
          controller.enqueue(encoder.encode(`event: heartbeat\ndata: ${JSON.stringify({ timestamp: Date.now() })}\n\n`));
          console.log(`[STREAM] Sent heartbeat for ${projectId}`);
        } catch (e) {
          console.log(`[STREAM] Heartbeat failed for ${projectId}, cleaning up: ${e}`);
          clearInterval(interval);
          streams.delete(projectId);
        }
      }, 10000);

      // 3. Return a Promise that never resolves - this keeps the stream alive
      return new Promise(() => {
        // This promise never resolves, keeping the stream open
        req.signal.addEventListener('abort', () => {
          console.log(`[STREAM] Client disconnected: ${projectId}`);
          clearInterval(interval);
          streams.delete(projectId);
          try {
            controller.close();
          } catch (e) {
            console.error(`[STREAM] Error closing controller: ${e}`);
          }
        });
      });
    },

    cancel() {
      console.log(`[STREAM] Stream cancelled: ${projectId}`);
      clearInterval(interval);
      streams.delete(projectId);
    }

  });

  return new NextResponse(stream, {

    headers: {

      'Content-Type': 'text/event-stream',

      'Cache-Control': 'no-cache',

      'Connection': 'keep-alive',

    },

  });

}
