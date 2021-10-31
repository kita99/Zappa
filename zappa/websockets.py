import os
import json

with open("/abusetotal/zappa_settings.json") as f:
    settings = json.load(f).get("production")

from mangum.backends import WebSocket

websocket = WebSocket(
    dsn=settings.get("asgi_websocket_backend"),
    api_gateway_endpoint_url=settings.get("aws_endpoint_urls").get("websockets"),
    api_gateway_region_name=os.environ.get("AWS_REGION")
)


async def group_add(key, connection_id):
    async with websocket._Backend(websocket.dsn) as backend:
        try:
            group = json.loads(await backend.retrieve(key))
        except:
            group = {"connections": []}

        group["connections"].append(connection_id)

        await backend.save(key, json_scope=json.dumps(group))


async def group_discard(key, connection_id):
    async with websocket._Backend(websocket.dsn) as backend:
        try:
            group = json.loads(await backend.retrieve(key))
            group["connections"].remove(connection_id)
        except:
            return

        await backend.save(key, json_scope=json.dumps(group))


async def group_send(key, data):
    async with websocket._Backend(websocket.dsn) as backend:
        try:
            group = json.loads(await backend.retrieve(key))
        except:
            return

    data = json.dumps(data)
    body = data.encode()
    for connection_id in group["connections"]:
        await websocket.post_to_connection(connection_id, body=body)


async def send(connection_id, data):
    data = json.dumps(data)
    body = data.encode()
    await websocket.post_to_connection(connection_id, body=body)
