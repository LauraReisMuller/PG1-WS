import asyncio
from http import HTTPStatus
from functools import partial

from websockets.server import serve
from websockets.http import Headers

# Dicionário compartilhado para armazenar as sessões ativas do chat
SESSIONS = {}

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

# 3: Implementação do novo handler para o serviço de chat
# 4: Assinatura do método estendida para receber o dicionário de sessões
async def chat(websocket, sessions):
    """Chat WebSocket handler com suporte a sessões, logs e broadcast."""
    # 4: Recupera o endereço remoto para usar como chave da sessão
    remote = websocket.remote_address
    # 4: Armazena o websocket do cliente no dicionário de sessões
    sessions[remote] = websocket
   # 11: Log de conexão do cliente. 
    print(f"[CONEXÃO] Cliente conectado: {remote}. Total de clientes: {len(sessions)}.")
    
    # 6: Início do bloco try para lidar com a desconexão do cliente
    try:
        # 5: Itera sobre as mensagens recebidas do websocket
        async for message in websocket:
           # 11: Log de mensagem recebida. 
            print(f"[MENSAGEM] De {remote}: '{message}'. Transmitindo para {len(sessions)} clientes.")
            
            # Formata a mensagem para incluir o remetente
            outgoing = f"({remote[0]}:{remote[1]}): {message}"

            # 5: Envia a mensagem recuperada para cada um dos clientes ativos
            for socket in sessions.values():
                await socket.send(outgoing)
    finally:
        # 6: Bloco para garantir a remoção do cliente ao desconectar 
        del sessions[remote]
        # 11: Log de desconexão do cliente
        print(f"[DESCONEXÃO] Cliente desconectado: {remote}. Total de clientes: {len(sessions)}.")

async def web_socket_router(websocket, sessions):
    """Roteia usando websocket.path e passa o dicionário de sessões."""
    path = getattr(websocket, "path", "/")
    if path == "/":
        await websocket.close(reason="needs a path")
    elif path == "/echo":
        await echo(websocket)
    # 7: Definição da nova URL /chat no roteador para invocar o handler 'chat'
    elif path == "/chat":
        await chat(websocket, sessions=sessions)
    else:
        await websocket.close(reason=f"path not found: {path}")

async def main():
    handler = partial(web_socket_router, sessions=SESSIONS)
    async with serve(handler, "localhost", 8080, process_request=http_handler):
        await asyncio.Future()  # roda para sempre

if __name__ == "__main__":
    asyncio.run(main())