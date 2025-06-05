import os
import importlib.util
import random
import time
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from TEAMZYRO import *
from TEAMZYRO.unit.zyro_help import HELP_DATA  

NEXI_VID = [
    "https://telegra.ph/file/1a3c152717eb9d2e94dc2.mp4",
    "https://graph.org/file/ba7699c28dab379b518ca.mp4",
    "https://graph.org/file/83ebf52e8bbf138620de7.mp4",
    "https://graph.org/file/82fd67aa56eb1b299e08d.mp4",
    "https://graph.org/file/318eac81e3d4667edcb77.mp4",
    "https://graph.org/file/7c1aa59649fbf3ab422da.mp4",
    "https://graph.org/file/2a7f857f31b32766ac6fc.mp4",
]

# 🔹 Function to Calculate Uptime
START_TIME = time.time()

def get_uptime():
    uptime_seconds = int(time.time() - START_TIME)
    hours, remainder = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}h {minutes}m {seconds}s"

# 🔹 Function to Generate Start Message & Buttons
async def generate_start_message(client, message, is_group=False):
    bot_user = await client.get_me()
    bot_name = bot_user.first_name
    ping = round(time.time() - message.date.timestamp(), 2)
    uptime = get_uptime()
    
    if is_group:
        caption = f"""🍃 I'm {bot_name} 🫧
I spawn waifus in your group for users to grab.
Tap Help for details."""
        buttons = [
            [
                InlineKeyboardButton("ADD ME", url=f"https://t.me/{bot_user.username}?startgroup=true"),
                InlineKeyboardButton("SUPPORT", url=SUPPORT_CHAT)
            ]
        ]
    else:
        caption = f"""🍃 ɢʀᴇᴇᴛɪɴɢs, ɪ'ᴍ {bot_name} 🫧, ɴɪᴄᴇ ᴛᴏ ᴍᴇᴇᴛ ʏᴏᴜ!
━━━━━━━▧▣▧━━━━━━━
⦾ ᴡʜᴀᴛ ɪ ᴅᴏ: ɪ sᴘᴀᴡɴ   
     ᴡᴀɪғᴜs ɪɴ ʏᴏᴜʀ ᴄʜᴀᴛ ғᴏʀ
     ᴜsᴇʀs ᴛᴏ ɢʀᴀʙ.
⦾ ᴛᴏ ᴜsᴇ ᴍᴇ: ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ
     ɢʀᴏᴜᴘ ᴀɴᴅ ᴛᴀᴘ ᴛʜᴇ ʜᴇʟᴘ
     ʙᴜᴛᴛᴏɴ ғᴏʀ ᴅᴇᴛᴀɪʟs.
━━━━━━━▧▣▧━━━━━━━
➺ ᴘɪɴɢ: {ping} ms
➺ ᴜᴘᴛɪᴍᴇ: {uptime}"""
        buttons = [
            [InlineKeyboardButton("Add to Your Group", url=f"https://t.me/{bot_user.username}?startgroup=true")],
            [InlineKeyboardButton("Support", url=SUPPORT_CHAT), 
             InlineKeyboardButton("Channel", url=UPDATE_CHAT)],
            [InlineKeyboardButton("Help", callback_data="open_help")],
            [InlineKeyboardButton("GitHub", url="https://github.com/MrZyro/ZyroWaifu")]
        ]
    
    return caption, InlineKeyboardMarkup(buttons)

# 🔹 Start Command Handler
@app.on_message(filters.command("start"))
async def start_command(client, message):
    is_group = message.chat.type in ["group", "supergroup"]
    caption, buttons = await generate_start_message(client, message, is_group)
    
    if not is_group:
        await app.send_message(
            chat_id=GLOG,
            text=f"{message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ᴄʜᴇᴄᴋ <b>sᴜᴅᴏʟɪsᴛ</b>.\n\n<b>ᴜsᴇʀ ɪᴅ :</b> <code>{message.from_user.id}</code>\n<b>ᴜsᴇʀɴᴀᴍᴇ :</b> @{message.from_user.username}",
        )
        video = random.choice(NEXI_VID)
        await message.reply_video(
            video=video,
            caption=caption,
            reply_markup=buttons
        )
    else:
        await message.reply_text(
            text=caption,
            reply_markup=buttons
        )

# 🔹 Function to Find Help Modules (Optimized for Memory)
def find_help_modules():
    buttons = []
    
    for module_name, module_data in HELP_DATA.items():
        button_name = module_data.get("HELP_NAME", "Unknown")
        buttons.append(InlineKeyboardButton(button_name, callback_data=f"help_{module_name}"))

    return [buttons[i : i + 3] for i in range(0, len(buttons), 3)]

# 🔹 Help Button Click Handler
@app.on_callback_query(filters.regex("^open_help$"))
async def show_help_menu(client, query: CallbackQuery):
    time.sleep(1)
    buttons = find_help_modules()
    buttons.append([InlineKeyboardButton("⬅ Back", callback_data="back_to_home")])

    await query.message.edit_text(
        """*ᴄʜᴏᴏsᴇ ᴛʜᴇ ᴄᴀᴛᴇɢᴏʀʏ ғᴏʀ ᴡʜɪᴄʜ ʏᴏᴜ ᴡᴀɴɴᴀ ɢᴇᴛ ʜᴇʟᴩ.

ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs ᴄᴀɴ ʙᴇ ᴜsᴇᴅ ᴡɪᴛʜ : /""",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# 🔹 Individual Module Help Handler (Optimized)
@app.on_callback_query(filters.regex(r"^help_(.+)"))
async def show_help(client, query: CallbackQuery):
    time.sleep(1)
    module_name = query.data.split("_", 1)[1]
    
    try:
        module_data = HELP_DATA.get(module_name, {})
        help_text = module_data.get("HELP", "Is module ka koi help nahi hai.")
        buttons = [[InlineKeyboardButton("⬅ Back", callback_data="open_help")]]
        
        await query.message.edit_text(f"**{module_name} Help:**\n\n{help_text}", reply_markup=InlineKeyboardMarkup(buttons))
    except Exception as e:
        await query.answer("Help load karne me error aayi!")

# 🔹 Back to Home (Edit Message Instead of Sending New)
@app.on_callback_query(filters.regex("^back_to_home$"))
async def back_to_home(client, query: CallbackQuery):
    time.sleep(1)
    is_group = query.message.chat.type in ["group", "supergroup"]
    caption, buttons = await generate_start_message(client, query.message, is_group)
    await query.message.edit_text(caption, reply_markup=buttons)
