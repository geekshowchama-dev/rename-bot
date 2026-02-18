import os
import time
from pyrogram import Client, filters

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]

app = Client("rename-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Progress Bar Function
async def progress(current, total, message, start, text):
    now = time.time()
    diff = now - start

    if round(diff % 3) == 0:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff)
        bar = "█" * int(percentage // 5) + "░" * (20 - int(percentage // 5))

        await message.edit_text(
            f"{text}\n\n"
            f"[{bar}] {percentage:.2f}%\n"
            f"Speed: {speed/1024/1024:.2f} MB/s\n"
            f"Downloaded: {current/1024/1024:.2f} MB"
        )

@app.on_message(filters.document)
async def rename_file(client, message):

    status = await message.reply("📥 Downloading...")

    start = time.time()

    file_path = await message.download(
        progress=progress,
        progress_args=(status, start, "📥 Downloading")
    )

    new_name = "Renamed_" + message.document.file_name
    os.rename(file_path, new_name)

    start = time.time()

    await message.reply_document(
        document=new_name,
        progress=progress,
        progress_args=(status, start, "📤 Uploading")
    )

    os.remove(new_name)
    await status.delete()

app.run()
