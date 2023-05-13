import asyncio

from websockets.server import serve, WebSocketServerProtocol as WebSocket
from .multiplex import Multiplexer

class Server:
    def __init__(self, root):
        self.root = root

    async def serve_ws(self, websocket: WebSocket):
        def send(message):
            asyncio.create_task(websocket.send(message))
        
        multiplexer = Multiplexer(send)
        multiplexer.set_root(self.root)

        async for message in websocket:
            multiplexer.receive(message)
        
        print('Connection closed.')
        multiplexer.cleanup()

    async def serve(self):
        async with serve(self.serve_ws, "localhost", 8080):
            await asyncio.Future()

    def run(self):
        asyncio.run(self.serve())


def main():
    #parser = argparse.ArgumentParser()
    #parser.add_argument("module", nargs='?', default="wirebind.demo")
    #args = parser.parse_args()

    #module = importlib.import_module(args.module)
    #root = ModuleRPCServer(module)
    from .demo import root
    server = Server(root)
    
    print('Listening.')
    server.run()


if __name__ == "__main__":
    main()
