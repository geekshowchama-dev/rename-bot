import os
import time
from pyrogram import Client, filters
from pyrogram.types import Message

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]

app = Client("fast-rename-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# User states
user_files = {}
user_thumbs = {}
user_stage = {}

# Progress bar function (20s update)
async def progress(current, total, message, start, text):
    now = time.time()
    diff = now - start
    if diff < 20:
        return  # update only every 20s

    percentage = current * 100 / total
    bar = "█" * int(percentage // 5) + "░" * (20 - int(percentage // 5))
    speed = current / diff

    try:
        await message.edit_text(
            f"{text}\n\n"
            f"[{bar}] {percentage:.2f}%\n"
            f"⚡ Speed: {speed/1024/1024:.2f} MB/s"
        )
    except:
        pass

# Step 1: Receive File
@app.on_message(filters.document)
async def receive_file(client, message: Message):
    user_id = message.from_user.id
    user_files[user_id] = message
    user_stage[user_id] = "thumb"
    await message.reply("🖼 **Send your custom thumbnail now (optional)**")

# Step 2: Receive Thumbnail
@app.on_message(filters.photo)
async def receive_thumb(client, message: Message):
    user_id = message.from_user.id
    if user_stage.get(user_id) == "thumb":
        path = await message.download()
        user_thumbs[user_id] = path
        user_stage[user_id] = "rename"
        await message.reply("✏️ **Now send your new file name**")

# Step 3: Receive New Name and Upload
@app.on_message(filters.text)
async def receive_new_name(client, message: Message):
    user_id = message.from_user.id
    if user_stage.get(user_id) != "rename":
        return

    original_msg = user_files[user_id]
    new_name = message.text.strip()
    thumb_path = user_thumbs.get(user_id)

    status = await message.reply("⚡ Downloading & Uploading started...")

    start_download = time.time()

    # Download with progress (20s interval)
    file_path = await original_msg.download(
        file_name=f"./{new_name}{os.path.splitext(original_msg.document.file_name)[1]}",
        in_memory=False,
        progress=progress,
        progress_args=(status, start_download, "📥 Downloading")
    )

    start_upload = time.time()
    await status.edit_text("⚡ Uploading started...")

    # Upload with progress (20s interval)
    await message.reply_document(
        document=file_path,
        thumb=thumb_path,
        caption=f"✅ Renamed to {new_name}",
        progress=progress,
        progress_args=(status, start_upload, "📤 Uploading")
    )

    # Cleanup
    if os.path.exists(file_path):
        os.remove(file_path)
    if thumb_path and os.path.exists(thumb_path):
        os.remove(thumb_path)
    user_files.pop(user_id)
    user_thumbs.pop(user_id, None)
    user_stage.pop(user_id)
    await status.delete()

app.run()
