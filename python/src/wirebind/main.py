import argparse
import asyncio
import importlib
import importlib.util
from os.path import splitext

from websockets.server import WebSocketServerProtocol as WebSocket
from websockets.server import serve

from .multiplex import Multiplexer


class Server:
    def __init__(self, root):
        self.root = root

    async def serve_ws(self, websocket: WebSocket):
        loop = asyncio.get_event_loop()

        def send(message):
            # asyncio.create_task(websocket.send(message))
            asyncio.run_coroutine_threadsafe(websocket.send(message), loop)

        multiplexer = Multiplexer(send)
        multiplexer.set_root(self.root)

        async for message in websocket:
            multiplexer.receive(message)

        print("Connection closed.")
        multiplexer.cleanup()

    async def serve(self):
        async with serve(self.serve_ws, "localhost", 8080):
            await asyncio.Future()

    def run(self):
        asyncio.run(self.serve())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Filename of Python module to load.")
    args = parser.parse_args()

    name, _ = splitext(args.file)
    spec = importlib.util.spec_from_file_location(name, args.file)
    module = importlib.util.module_from_spec(spec)

    spec.loader.exec_module(module)
    root = module.root
    server = Server(root)

    print("Listening.")
    server.run()


if __name__ == "__main__":
    main()
