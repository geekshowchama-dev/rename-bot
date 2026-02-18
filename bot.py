import os
import time
from pyrogram import Client, filters
from pyrogram.types import Message

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"])
BOT_TOKEN = os.environ["BOT_TOKEN"]

app = Client("rename-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Store user states
user_files = {}
user_thumbs = {}
user_stage = {}

# Progress Bar
async def progress(current, total, message, start, text):
    now = time.time()
    diff = now - start

    if diff == 0:
        return

    percentage = current * 100 / total
    speed = current / diff
    bar = "█" * int(percentage // 5) + "░" * (20 - int(percentage // 5))

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
    await message.reply("🖼 **Send your custom thumbnail now**")

# Step 2: Receive Thumbnail
@app.on_message(filters.photo)
async def receive_thumb(client, message: Message):
    user_id = message.from_user.id

    if user_stage.get(user_id) == "thumb":
        path = await message.download()
        user_thumbs[user_id] = path
        user_stage[user_id] = "rename"
        await message.reply("✏️ **Now send your new file name**")

# Step 3: Receive Rename Text
@app.on_message(filters.text)
async def receive_new_name(client, message: Message):
    user_id = message.from_user.id

    if user_stage.get(user_id) == "rename":

        original_msg = user_files[user_id]
        new_name = message.text.strip()

        status = await message.reply("📥 Downloading...")

        start = time.time()

        file_path = await original_msg.download(
            progress=progress,
            progress_args=(status, start, "📥 Downloading")
        )

        ext = os.path.splitext(original_msg.document.file_name)[1]
        final_name = new_name + ext
        os.rename(file_path, final_name)

        start = time.time()

        await message.reply_document(
            document=final_name,
            thumb=user_thumbs.get(user_id),
            progress=progress,
            progress_args=(status, start, "📤 Uploading")
        )

        os.remove(final_name)
        await status.delete()

        # Cleanup
        user_stage.pop(user_id)
        user_files.pop(user_id)
        user_thumbs.pop(user_id, None)

app.run()
