import os
from pyrogram import Client, filters
from pyrogram.types import Message

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]

app = Client("rename-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

user_thumbnails = {}
rename_files = {}

# 1️⃣ Set Thumbnail Command
@app.on_message(filters.command("setthumbnail"))
async def set_thumb(client, message: Message):
    await message.reply("📸 Send me the image to set as thumbnail.")

# 2️⃣ Save Thumbnail
@app.on_message(filters.photo)
async def save_thumbnail(client, message: Message):
    if message.from_user:
        path = await message.download()
        user_thumbnails[message.from_user.id] = path
        await message.reply("✅ Thumbnail saved successfully!")

# 3️⃣ When File Forwarded / Sent
@app.on_message(filters.document)
async def ask_new_name(client, message: Message):
    if message.from_user:
        rename_files[message.from_user.id] = message
        await message.reply("✏️ Give me the new file name.")

# 4️⃣ Get New Name & Send File
@app.on_message(filters.text & ~filters.command(["setthumbnail"]))
async def rename_and_send(client, message: Message):
    user_id = message.from_user.id

    if user_id in rename_files:
        original_msg = rename_files[user_id]
        new_name = message.text

        file_path = await original_msg.download()
        ext = os.path.splitext(original_msg.document.file_name)[1]

        final_name = new_name + ext
        os.rename(file_path, final_name)

        thumb = user_thumbnails.get(user_id)

        await message.reply_document(
            document=final_name,
            thumb=thumb if thumb else None,
            caption="✅ Renamed Successfully!"
        )

        os.remove(final_name)
        rename_files.pop(user_id)

app.run()
