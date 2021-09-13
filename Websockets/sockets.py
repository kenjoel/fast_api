from typing import Optional

from fastapi import FastAPI, WebSocket, Cookie, Query, Depends

from fastapi.responses import HTMLResponse
from starlette import status
from starlette.websockets import WebSocketDisconnect

app = FastAPI()

html = """

<!DOCTYPE html>

<html>

    <head>

        <title>Chat</title>

    </head>

    <body>

        <h1>WebSocket Chat</h1>

        <form action="" onsubmit="sendMessage(event)">

            <input type="text" id="messageText" autocomplete="off"/>

            <button>Send</button>

        </form>

        <ul id='messages'>

        </ul>

        <script>

            var ws = new WebSocket("ws://localhost:8000/ws");

            ws.onmessage = function(event) {

                var messages = document.getElementById('messages')

                var message = document.createElement('li')

                var content = document.createTextNode(event.data)

                message.appendChild(content)

                messages.appendChild(message)

            };

            function sendMessage(event) {

                var input = document.getElementById("messageText")

                ws.send(input.value)

                input.value = ''

                event.preventDefault()

            }

        </script>

    </body>

</html>

"""


async def get_cookie_or_token(
        websocket: WebSocket,
        session: Optional[str] = Cookie(None),
        token: Optional[str] = Query(None),
):
    if session is None and token is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    return session or token


@app.get("/")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws")
async def websocket_endpoint(
        websocket: WebSocket,
        item_id: str,
        q: Optional[int] = None,
        cookie_or_token: str = Depends(get_cookie_or_token),
):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text( f"Session cookie or query token value is: {cookie_or_token}"
        )
        if q is not None:
            await websocket.send_text(f"Query parameter q is: {q}")
        await websocket.send_text(f"Message text was: {data}, for item ID: {item_id}")


'''Handling Multiple Disconnections and Multiple CLients'''


html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <h2>Your ID: <span id="ws-id"></span></h2>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var client_id = Date.now()
            document.querySelector("#ws-id").textContent = client_id;
            var ws = new WebSocket(`ws://localhost:8000/ws/${client_id}`);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.get("/smh")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}")

    except WebSocketDisconnect:

        manager.disconnect(websocket)

        await manager.broadcast(f"Client #{client_id} left the chat")
