import os
from pyrogram import Client, filters
from pyrogram.types import Message
from io import BytesIO

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]

app = Client("fast-rename-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

user_files = {}
user_thumbs = {}
user_stage = {}

# Step 1: Receive file
@app.on_message(filters.document)
async def receive_file(client, message: Message):
    user_id = message.from_user.id
    user_files[user_id] = message
    user_stage[user_id] = "thumb"
    await message.reply("🖼 Send thumbnail (optional) or type /skip")

# Step 2: Receive thumbnail
@app.on_message(filters.photo)
async def receive_thumb(client, message: Message):
    user_id = message.from_user.id
    if user_stage.get(user_id) == "thumb":
        thumb_path = await message.download()
        user_thumbs[user_id] = thumb_path
        user_stage[user_id] = "rename"
        await message.reply("✏️ Send new file name (without extension)")

# Step 2b: Skip thumbnail
@app.on_message(filters.command("skip"))
async def skip_thumb(client, message: Message):
    user_id = message.from_user.id
    if user_stage.get(user_id) == "thumb":
        user_stage[user_id] = "rename"
        await message.reply("✏️ Send new file name (without extension)")

# Step 3: Receive new name and upload
@app.on_message(filters.text & ~filters.command("skip"))
async def receive_new_name(client, message: Message):
    user_id = message.from_user.id
    if user_stage.get(user_id) != "rename":
        return

    original_msg = user_files[user_id]
    new_name = message.text.strip()
    thumb_path = user_thumbs.get(user_id)

    ext = os.path.splitext(original_msg.document.file_name)[1]
    final_name = new_name + ext

    status = await message.reply("⚡ Uploading...")

    # Download file into memory
    file_bytes = BytesIO()
    await original_msg.download(file_bytes)
    file_bytes.seek(0)

    # Upload from memory with renamed file
    await message.reply_document(
        document=file_bytes,
        file_name=final_name,
        thumb=thumb_path,
        caption=f"✅ Renamed to {final_name}"
    )

    # Cleanup
    if thumb_path and os.path.exists(thumb_path):
        os.remove(thumb_path)
    user_files.pop(user_id, None)
    user_thumbs.pop(user_id, None)
    user_stage.pop(user_id, None)
    await status.delete()
