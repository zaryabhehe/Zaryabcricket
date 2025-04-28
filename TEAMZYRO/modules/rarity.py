# TEAMZYRO/commands/rarity.py
from TEAMZYRO import app, collection
from pyrogram import filters, enums

@app.on_message(filters.command("rarity"))
async def rarity_count(client, message):
    try:
        # Fetch distinct rarities from the characters collection
        distinct_rarities = await collection.distinct('rarity')
        
        if not distinct_rarities:
            await message.reply_text("⚠️ No rarities found in the database.")
            return
        
        response_message = "✨ Character Count by Rarity ✨\n\n"
        
        # Loop through each rarity and count the number of characters
        for rarity in distinct_rarities:
            # Count the number of characters with the current rarity
            count = await collection.count_documents({'rarity': rarity})
            
            response_message += f"◈ {rarity} {count} character(s)\n"
        
        await message.reply_text(response_message)
    
    except Exception as e:
        await message.reply_text(f"⚠️ Error: {str(e)}")

from pyrogram import Client, filters
from pyrogram.types import Message
from TEAMZYRO import collection, app
from TEAMZYRO import require_power

@app.on_message(filters.command("raritymix"))
@require_power("update_character")
async def rarity_mix(client: Client, message: Message):
    try:
        args = message.text.split(maxsplit=2)
        if len(args) < 3:
            await message.reply_text("❌ Incorrect format. Use: /raritymix {rarity num} {rarity}")
            return

        rarity_num = args[1]  # Number input
        rarity_new = args[2]  # Direct rarity from user input

        # Pehli rarity map se milegi
        rarity_map = {
            "1": "⚪ Common",
            "2": "🟣 Rare",
            "3": "🟡 Legendary",
            "4": "🟢 Medium",
            "5": "💮 Special Edition",
            "6": "🔮 Limited Edition",
            "7": "🎐 Celestial",
            "8": "💖 Valentine",
            "9": "🎃 Halloween",
            "10": "❄️ Winter",
            "11": "🌧 Rainy",
            "12": "💸 Expensive",
            "13": "👑 V. I. P."
        }

        # Pehli rarity validate karo
        if rarity_num not in rarity_map:
            await message.reply_text("❌ Invalid rarity number. Use a valid number like 1, 2, 3...")
            return

        rarity_old = rarity_map[rarity_num]  # Number se rarity select karega

        # Database me update karo
        result = await collection.update_many({"rarity": rarity_new}, {"$set": {"rarity": rarity_old}})

        await message.reply_text(
            f"✅ Rarity updated!\n"
            f"🔄 {rarity_new} ➡ {rarity_old}\n"
            f"📌 {result.modified_count} characters updated!"
        )

    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")


from pyrogram import Client, filters
from pyrogram.types import Message
from TEAMZYRO import collection, user_collection, app, require_power

@app.on_message(filters.command("alldelete"))
@require_power("delete_character")
async def delete_by_rarity(client: Client, message: Message):
    try:
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            await message.reply_text("Incorrect format! Use: `/alldelete {rarity}`")
            return
        
        rarity = args[1].strip()

        # Find all characters with the specified rarity
        characters_to_delete = await collection.find({"rarity": rarity}).to_list(length=None)
        if not characters_to_delete:
            await message.reply_text(f"No characters found with rarity: {rarity}")
            return

        character_ids = [char["id"] for char in characters_to_delete]

        # Delete characters from the main collection
        delete_result = await collection.delete_many({"rarity": rarity})

        # Remove these characters from all users' collections
        update_result = await user_collection.update_many(
            {"characters.id": {"$in": character_ids}},
            {"$pull": {"characters": {"id": {"$in": character_ids}}}}
        )

        await message.reply_text(
            f"Deleted {delete_result.deleted_count} characters with rarity '{rarity}' "
            f"and removed them from {update_result.modified_count} user collections."
        )

    except Exception as e:
        await message.reply_text(f"Error: {str(e)}")
