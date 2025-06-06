from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus
from TEAMZYRO import group_user_totals_collection, app

async def is_admin(client: Client, chat_id: int, user_id: int) -> bool:
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except Exception as e:
        print(f"[is_admin error] {e}")
        return False

@app.on_message(filters.command("changetime") & filters.group)
async def change_time(client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if not await is_admin(client, chat_id, user_id):
        await message.reply("⚠️ Only group admins can use this command.")
        return

    try:
        new_freq = int(message.command[1])
    except (IndexError, ValueError):
        await message.reply("⚠️ Please provide a valid number.\nExample: /changetime 150")
        return

    if not 80 <= new_freq <= 200:
        await message.reply("⚠️ Frequency must be between 80 and 200.")
        return

    try:
        await group_user_totals_collection.update_one(
            {"group_id": str(chat_id)},
            {"$set": {"message_frequency": new_freq}},
            upsert=True
        )
        await message.reply(f"✅ Message frequency successfully set to {new_freq}.")
    except Exception as e:
        await message.reply(f"❌ Failed to update: {e}")
