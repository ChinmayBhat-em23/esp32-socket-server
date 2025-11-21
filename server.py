# import asyncio
# import websockets
# import os
# import http

# connected = set()

# async def handler(ws):
#     print("Client connected")
#     connected.add(ws)
#     try:
#         async for msg in ws:
#             # Broadcast to other clients
#             remove_list = []
#             for c in connected:
#                 if c != ws:
#                     try:
#                         await c.send(msg)
#                     except:
#                         remove_list.append(c)
#             for c in remove_list:
#                 connected.remove(c)
#     except websockets.exceptions.ConnectionClosed:
#         pass
#     finally:
#         if ws in connected:
#             connected.remove(ws)
#         print("Client disconnected")

# # This function handles the Render Health Check
# async def health_check(connection, request_path):
#     # If Render asks "Are you there?" at /healthz, say YES
#     if request_path == "/healthz":
#         return http.HTTPStatus.OK, [], b"OK\n"
#     # Otherwise, return None to let the WebSocket handshake continue
#     return None

# async def main():
#     port = int(os.environ.get("PORT", 8080))
#     print(f"Starting WebSocket relay on port {port}...")
    
#     # We add 'process_request' to handle the health check
#     async with websockets.serve(handler, "0.0.0.0", port, process_request=health_check):
#         await asyncio.Future()  # run forever

# if __name__ == "__main__":
#     asyncio.run(main())






import asyncio
import os
from aiohttp import web
import aiohttp
from aiohttp import web_ws

# Store connected WebSocket clients
connected_clients = set()

# ============================================
# WebSocket Handler (for ESP32 connections)
# ============================================
async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    connected_clients.add(ws)
    print(f"✅ New client connected! Total clients: {len(connected_clients)}")
    
    try:
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                data = msg.data
                print(f"📩 Received: {data}")
                
                # Broadcast to all other clients (optional)
                for client in connected_clients:
                    if client != ws and not client.closed:
                        try:
                            await client.send_str(f"Broadcast: {data}")
                        except:
                            pass
                            
            elif msg.type == aiohttp.WSMsgType.ERROR:
                print(f"❌ WebSocket error: {ws.exception()}")
                
    except Exception as e:
        print(f"❌ Error in websocket handler: {e}")
    finally:
        connected_clients.discard(ws)
        print(f"👋 Client disconnected. Remaining: {len(connected_clients)}")
    
    return ws

# ============================================
# Health Check Endpoint
# ============================================
async def health_check(request):
    return web.Response(text="OK - WebSocket Server Running", status=200)

# ============================================
# Root endpoint (optional info page)
# ============================================
async def root_handler(request):
    html = """
    <html>
        <head><title>ESP32 WebSocket Server</title></head>
        <body>
            <h1>WebSocket Server is Running! 🚀</h1>
            <p>Connect to: <code>wss://your-app.onrender.com/</code></p>
            <p>Active connections: <span id="count">Loading...</span></p>
            <script>
                fetch('/status').then(r=>r.json()).then(d=> {
                    document.getElementById('count').textContent = d.clients;
                });
            </script>
        </body>
    </html>
    """
    return web.Response(text=html, content_type='text/html')

# ============================================
# Status endpoint (optional)
# ============================================
async def status_handler(request):
    return web.json_response({
        'status': 'running',
        'clients': len(connected_clients)
    })

# ============================================
# Main Application Setup
# ============================================
async def create_app():
    app = web.Application()
    
    # Routes
    app.router.add_get('/', websocket_handler)  # WebSocket endpoint at root
    app.router.add_get('/ws', websocket_handler)  # Alternative WS endpoint
    app.router.add_get('/healthz', health_check)  # Health check
    app.router.add_head('/healthz', health_check)  # HEAD request support
    app.router.add_get('/status', status_handler)  # Status endpoint
    
    return app

# ============================================
# Start Server
# ============================================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))  # Render uses PORT env variable
    
    print(f"🚀 Starting WebSocket server on port {port}...")
    print(f"📡 WebSocket endpoint: ws://0.0.0.0:{port}/")
    print(f"🏥 Health check: http://0.0.0.0:{port}/healthz")
    
    app = asyncio.run(create_app())
    web.run_app(app, host='0.0.0.0', port=port)