import asyncio
from http import HTTPStatus

from websockets.server import serve
from websockets.http import Headers

async def http_handler(path, request_headers):
    """Serve os HTMLs estáticos via HTTP no mesmo socket."""
    if path == "/ui-chat":
        with open("chat.html", "rb") as f:
            body = f.read()
        headers = Headers(**{"Content-Type": "text/html; charset=utf-8"})
        return HTTPStatus.OK, headers, body

    if path == "/ui-echo":
        with open("echo.html", "rb") as f:
            body = f.read()
        headers = Headers(**{"Content-Type": "text/html; charset=utf-8"})
        return HTTPStatus.OK, headers, body

    return None  # deixa o upgrade WS ocorrer

async def echo(websocket):
    """Echo WebSocket handler"""
    async for message in websocket:
        await websocket.send(message)

async def web_socket_router(websocket):
    """Roteia usando websocket.path (websockets >= 11)."""
    path = getattr(websocket, "path", "/")
    if path == "/":
        await websocket.close(reason="needs a path")
    elif path == "/echo":
        await echo(websocket)
    elif path == "/chat":
        # (adicione seu handler de chat aqui quando quiser)
        await echo(websocket)  # provisório
    else:
        await websocket.close(reason=f"path not found: {path}")

async def main():
    async with serve(web_socket_router, "localhost", 8080, process_request=http_handler):
        await asyncio.Future()  # roda para sempre

if __name__ == "__main__":
    asyncio.run(main())
