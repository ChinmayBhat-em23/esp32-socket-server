import asyncio
import websockets
import os
import http

connected = set()

async def handler(ws):
    print("Client connected")
    connected.add(ws)
    try:
        async for msg in ws:
            # Broadcast to other clients
            remove_list = []
            for c in connected:
                if c != ws:
                    try:
                        await c.send(msg)
                    except:
                        remove_list.append(c)
            for c in remove_list:
                connected.remove(c)
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        if ws in connected:
            connected.remove(ws)
        print("Client disconnected")

# This function handles the Render Health Check
async def health_check(connection, request_path):
    # If Render asks "Are you there?" at /healthz, say YES
    if request_path == "/healthz":
        return http.HTTPStatus.OK, [], b"OK\n"
    # Otherwise, return None to let the WebSocket handshake continue
    return None

async def main():
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting WebSocket relay on port {port}...")
    
    # We add 'process_request' to handle the health check
    async with websockets.serve(handler, "0.0.0.0", port, process_request=health_check):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())