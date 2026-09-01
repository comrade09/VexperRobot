import time
import json
import base64
import hmac
import hashlib
import re
from aiohttp import web

# Must match the SECRET_KEY in search.py and DUMP_CHANNEL_ID in save_video.py
SECRET_KEY = b"84b6f10c7931c890e0e1a967f6515f40192ea62f25608d0f7a75932598be6f2d"
DUMP_CHANNEL_ID = -1003946902565

routes = web.RouteTableDef()

@routes.get('/watch')
async def stream_video(request):
    data = request.query.get('data')
    sig = request.query.get('sig')
    
    if not data or not sig:
        return web.Response(text="Missing parameters", status=400)
        
    expected_sig = hmac.new(SECRET_KEY, data.encode('utf-8'), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected_sig, sig):
        return web.Response(text="Invalid or forged signature", status=403)
        
    try:
        padding = '=' * (4 - len(data) % 4)
        decoded_json = base64.urlsafe_b64decode(data + padding).decode('utf-8')
        payload = json.loads(decoded_json)
        
        if int(time.time()) > payload['exp']:
            return web.Response(text="Link expired. Send /search to the bot again.", status=403)
            
        message_id = payload['mid']
    except Exception:
        return web.Response(text="Malformed token", status=400)
        
    # Retrieves your active Pyrogram bot client injected into the web app
    bot = request.app['bot'] 
    
    try:
        message = await bot.get_messages(DUMP_CHANNEL_ID, message_id)
        if not message or not message.video:
            return web.Response(text="Video not found in channel", status=404)
            
        file_size = message.video.file_size
        mime_type = message.video.mime_type or 'video/mp4'
        
        # Enables seeking/skipping forward and backward in the video player
        range_header = request.headers.get('Range', '')
        offset = 0
        limit = file_size
        
        if range_header:
            match = re.search(r'bytes=(\d+)-(\d*)', range_header)
            if match:
                offset = int(match.group(1))
                end = match.group(2)
                limit = (int(end) + 1) if end else file_size
        
        chunk_size = limit - offset
        
        response = web.StreamResponse(
            status=206 if range_header else 200,
            headers={
                'Content-Type': mime_type,
                'Content-Range': f'bytes {offset}-{limit-1}/{file_size}',
                'Accept-Ranges': 'bytes',
                'Content-Length': str(chunk_size),
                'Content-Disposition': f'inline; filename="video_{message_id}.mp4"'
            }
        )
        
        await response.prepare(request)
        
        async for chunk in bot.stream_media(message, offset=offset, limit=limit):
            await response.write(chunk)
            
        return response
        
    except Exception as e:
        print("Stream Error:", e)
        return web.Response(text="Error streaming video from Telegram", status=500)
