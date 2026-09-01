import time
import json
import base64
import hmac
import hashlib
import re
from aiohttp import web

SECRET_KEY = b"84b6f10c7931c890e0e1a967f6515f40192ea62f25608d0f7a75932598be6f2d"
DUMP_CHANNEL_ID = -1003946902565

routes = web.RouteTableDef()

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.json_response({"status": "running", "service": "Telegram Video Stream Server"})

@routes.get("/watch")
async def stream_video(request):
    data = request.query.get("data")
    sig = request.query.get("sig")

    if not data or not sig:
        return web.Response(text="Missing required parameters.", status=400)

    expected_sig = hmac.new(SECRET_KEY, data.encode("utf-8"), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected_sig, sig):
        return web.Response(text="Invalid or tampered link signature.", status=403)

    try:
        padding = "=" * (4 - len(data) % 4)
        decoded_json = base64.urlsafe_b64decode(data + padding).decode("utf-8")
        payload = json.loads(decoded_json)

        if int(time.time()) > payload["exp"]:
            return web.Response(text="⚠️ This link expired. Please search again in the bot.", status=403)

        message_id = int(payload["mid"])
    except Exception:
        return web.Response(text="Malformed token.", status=400)

    bot = request.app["bot"]

    try:
        message = await bot.get_messages(DUMP_CHANNEL_ID, message_id)
        if not message or not (message.video or message.document):
            return web.Response(text="Video file not found in database channel.", status=404)

        media = message.video or message.document
        file_size = media.file_size
        mime_type = media.mime_type or "video/mp4"

        range_header = request.headers.get("Range", "")
        offset = 0
        limit = file_size

        if range_header:
            match = re.search(r"bytes=(\d+)-(\d*)", range_header)
            if match:
                offset = int(match.group(1))
                end = match.group(2)
                limit = (int(end) + 1) if end else file_size

        chunk_size = limit - offset
        response = web.StreamResponse(
            status=206 if range_header else 200,
            headers={
                "Content-Type": mime_type,
                "Content-Range": f"bytes {offset}-{limit-1}/{file_size}",
                "Accept-Ranges": "bytes",
                "Content-Length": str(chunk_size),
                "Content-Disposition": f'inline; filename="video_{message_id}.mp4"',
                "Access-Control-Allow-Origin": "*"
            }
        )

        await response.prepare(request)
        async for chunk in bot.stream_media(message, offset=offset, limit=limit):
            await response.write(chunk)

        return response
    except Exception as e:
        print(f"Streaming Error: {e}")
        return web.Response(text="Error streaming from Telegram.", status=500)

async def web_server(bot_client):
    web_app = web.Application(client_max_size=30000000)
    web_app["bot"] = bot_client
    web_app.add_routes(routes)
    return web_app
