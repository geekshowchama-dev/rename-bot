from pyrogram import Client, filters
import os

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]

app = Client("rename-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

rename_users = set()

@app.on_message(filters.command("rename"))
async def start_rename(client, message):
    rename_users.add(message.from_user.id)
    await message.reply("📁 Now send me the file to rename.")

@app.on_message(filters.document)
async def rename_file(client, message):
    if message.from_user.id in rename_users:
        rename_users.remove(message.from_user.id)

        file_path = await message.download()
        new_name = "Renamed_" + message.document.file_name
        os.rename(file_path, new_name)

        await message.reply_document(new_name)
        os.remove(new_name)

app.run()
