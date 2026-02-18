import os
from pyrogram import Client, filters

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]

app = Client("rename-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.document)
async def rename_file(client, message):
    try:
        original_name = message.document.file_name
        file_path = await message.download()

        new_name = "Renamed_" + original_name

        os.rename(file_path, new_name)

        await message.reply_document(
            document=new_name,
            caption=f"✅ Renamed: {new_name}"
        )

        os.remove(new_name)

    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")

app.run()
