import asyncio
import websockets
import os

connected = set()

async def handler(ws):
    print("Client connected")
    connected.add(ws)
    try:
        async for msg in ws:
            # We don't print "RECV" to logs to save cloud memory, 
            # but it is still forwarding the data.
            
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

async def main():
    # This reads the port Render assigns to us
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting WebSocket relay on port {port}...")
    
    # "0.0.0.0" means "Listen to the whole internet"
    async with websockets.serve(handler, "0.0.0.0", port):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())