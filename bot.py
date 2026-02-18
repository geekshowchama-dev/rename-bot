import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.raw.functions.messages import UploadMedia
from pyrogram.types import InputMediaDocument

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]

app = Client("fast-rename-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# User states
user_files = {}
user_thumbs = {}
user_stage = {}

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

# Step 3: Receive New Name and Upload Fast
@app.on_message(filters.text)
async def receive_new_name(client, message: Message):
    user_id = message.from_user.id
    if user_stage.get(user_id) != "rename":
        return

    original_msg = user_files[user_id]
    new_name = message.text.strip()
    thumb_path = user_thumbs.get(user_id)

    status = await message.reply("⚡ Streaming upload started...")

    # Extension
    ext = os.path.splitext(original_msg.document.file_name)[1]
    final_name = new_name + ext

    # Streaming upload using Pyrogram
    file_path = await original_msg.download(file_name=f"./{final_name}", in_memory=False)

    await message.reply_document(
        document=file_path,
        thumb=thumb_path,
        caption=f"✅ Renamed to {final_name}"
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
