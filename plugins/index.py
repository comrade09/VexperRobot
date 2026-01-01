from telethon import TelegramClient
from pyrogram import filters
from bot import Bot
from config import API_ID, API_HASH, CHANNEL_ID, ADMINS
from database.videos import add_video, count

user = TelegramClient("user", API_ID, API_HASH)

@Bot.on_message(filters.command("index"),group=234776 )
async def index_cmd(_, msg):
    if msg.from_user.id not in ADMINS:
        await msg.reply("❌ You are not authorized")
        return

    status = await msg.reply("🔄 Starting index...")
    await user.start()

    scanned = 0
    added = 0

    async for m in user.iter_messages(CHANNEL_ID):
        scanned += 1

        if m.video and m.text:
            code = m.text.strip().upper()
            if add_video(code, m.video.file_id, m.id):
                added += 1

        if scanned % 50 == 0:
            await status.edit(
                f"📥 Scanned: {scanned}\n"
                f"➕ Added: {added}\n"
                f"📦 Total: {count()}"
            )

    await status.edit(
        f"✅ Done\n\n"
        f"📥 Scanned: {scanned}\n"
        f"➕ Added: {added}\n"
        f"📦 Total: {count()}"
    )
