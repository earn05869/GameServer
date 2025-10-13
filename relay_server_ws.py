# relay_server_ws.py
import asyncio
import websockets
import json

clients = []

async def relay(websocket):
    global clients
    clients.append(websocket)
    player_id = len(clients)
    print(f"[*] Player {player_id} connected.")

    # รอจนมีครบ 2 คน
    while len(clients) < 2:
        await asyncio.sleep(0.1)

    peer = clients[1] if clients[0] == websocket else clients[0]

    try:
        # แจ้งว่าเกมเริ่ม
        await websocket.send(json.dumps({"type": "status", "msg": "READY"}))
        await peer.send(json.dumps({"type": "status", "msg": "READY"}))

        # รอรับข้อความแล้วส่งต่อ
        async for message in websocket:
            try:
                await peer.send(message)
            except websockets.exceptions.ConnectionClosed:
                break
    except:
        print(f"[!] Player {player_id} disconnected")
    finally:
        if websocket in clients:
            clients.remove(websocket)
        if peer in clients:
            try:
                await peer.send(json.dumps({"type": "status", "msg": "PEER_DISCONNECTED"}))
            except:
                pass
        print(f"[*] Player {player_id} cleaned up.")


async def main():
    print("[*] Starting WebSocket relay server on port 10000")
    async with websockets.serve(relay, "0.0.0.0", 10000):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
