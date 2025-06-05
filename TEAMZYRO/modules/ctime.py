from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus
from TEAMZYRO import group_user_totals_collection, app, OWNER_ID

@app.on_message(filters.command("ctime") & filters.group)
async def set_ctime(client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    is_admin = False
    
    try:
        member = await client.get_chat_member(chat_id, user_id)
        is_admin = member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]
    except Exception:
        pass

    is_owner = user_id == OWNER_ID

    if not (is_admin or is_owner):
        await message.reply("⚠️ Only group admins can use this command!")
        return

    try:
        ctime = int(message.command[1])
    except (IndexError, ValueError):
        await message.reply("⚠️ Please provide a number (e.g., /ctime 80).")
        return

    if is_owner:
        if not 1 <= ctime <= 200:
            await message.reply("⚠️ Bot owner can set ctime between 1 and 200.")
            return
    else:
        if not 80 <= ctime <= 200:
            await message.reply("⚠️ Admins can set ctime between 80 and 200.")
            return

    await group_user_totals_collection.update_one(
        {"group_id": str(chat_id)},
        {"$set": {"ctime": ctime}},
        upsert=True
    )

    await message.reply(f"✅ Message count threshold set to {ctime} for this group.")
