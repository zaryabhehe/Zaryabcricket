from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from TEAMZYRO import app

@app.on_callback_query(filters.regex("^about_sudo$"))
async def about_sudo(client, callback_query: CallbackQuery):
    # Delete the old message (if needed)
    await callback_query.message.delete()

    # Send new message with photo + caption + buttons
    await client.send_photo(
        chat_id=callback_query.message.chat.id,
        photo="https://files.catbox.moe/77m5ks.jpg",
        caption=(
            "💠 *Main Admins of Oneforall*\n\n"
            "Here you can see the core sudo members of the bot."
        ),
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Owner", url="https://t.me/IAMBILLI"),
                InlineKeyboardButton("Mister DEV", url="https://t.me/BILLICHOR")
            ],
            [
                InlineKeyboardButton("Ken rugyuji", url="https://t.me/STAY_OUT_88"),
                InlineKeyboardButton("barnali roy", url="https://t.me/Barnali_roy")
            ],
            [
                InlineKeyboardButton("𓆩𔘓⃭𓆪 | 💠", url="https://t.me/koboreta_Shinzo"),
                InlineKeyboardButton("◉𝐕𝐄𝐆𝐄𝐓𝐀 ⌯", url="https://t.me/King_of_saiyans")
            ],
            [
                InlineKeyboardButton("ᛕﺃꪖꪀ ✨", url="https://t.me/Orewa_KIAN"),
                InlineKeyboardButton("𝘿𝙍𝘼‌𝕲𝕺𝙉‌", url="https://t.me/Dante_Koryu_999")
            ],
            [
                InlineKeyboardButton("Baby Saja", url="https://t.me/Niteconosco")
            ],
            [
                InlineKeyboardButton("🔙 Back", callback_data="settings_back_helper")
            ]
        ])
    )
