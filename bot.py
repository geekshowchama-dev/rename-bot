import os
from pyrogram import Client, filters

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client(
    "rename-bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@app.on_message(filters.document)
async def rename_file(client, message):
    file = await message.download()
    
    new_name = "Renamed_" + message.document.file_name
    os.rename(file, new_name)

    await message.reply_document(new_name)
    os.remove(new_name)

app.run()
