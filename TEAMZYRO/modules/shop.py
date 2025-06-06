import urllib.request
import uuid
import requests
import random
import html
import logging
from pymongo import ReturnDocument
from typing import List
from bson import ObjectId
from datetime import datetime, timedelta
import asyncio
import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from TEAMZYRO import *

shops_collection = db["shops"]

# Global dictionary to store user-specific states
user_data = {}

async def get_user_data(user_id):
    return await user_collection.find_one({"id": user_id})


logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    level=logging.INFO,
)
LOGGER = logging.getLogger(__name__)

@app.on_message(filters.command(["shop", "hshopmenu", "hshop"]))
async def show_shop(client, message):
    user_id = message.from_user.id
    message_id = message.id  # Corrected from message.message_id

    # Retrieve characters/items from the database
    characters_cursor = shops_collection.find()
    characters = await characters_cursor.to_list(length=None)

    if not characters:
        await message.reply("No characters found in the shop")
        return

    # Store the user's state
    current_index = 0
    character = characters[current_index]

    caption_message = (
        f"Welcome to the Luxury Shop \n\n"
        f"**Character:** {character['name']}\n"
        f"**Anime:** {character['anime']}\n"
        f"**Rarity:** {character['rarity']}\n"
        f"**Price:** {character['price']} coins\n"
        f"**ID:** {character['id']}\n"
        f"Unlock New characters"
    )

    keyboard = [
        [InlineKeyboardButton("Buy", callback_data=f"buy_{current_index}"),
         InlineKeyboardButton("Next", callback_data="next")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await message.reply_photo(
        photo=character['img_url'],
        caption=caption_message,
        reply_markup=reply_markup
    )

    # Store current index in the global user_data dictionary
    user_data[user_id] = {"current_index": current_index, "shop_message_id": message_id}


@app.on_callback_query(filters.regex(r"^buy_\d+$"))
async def buy_character(client, callback_query):
    user_id = callback_query.from_user.id
    current_index = int(callback_query.data.split("_")[1])

    # Retrieve all characters from the shop
    characters_cursor = shops_collection.find()
    characters = await characters_cursor.to_list(length=None)

    if current_index >= len(characters):
        await callback_query.answer("Character not found.", show_alert=True)
        return

    character = characters[current_index]


    user = await user_collection.find_one({"id": user_id})
    if not user:
        await callback_query.answer("User not found.", show_alert=True)
        return

    price = character['price']
    current_balance = user.get("balance", 0)

    if current_balance < price:
        await callback_query.answer(
            f"You need {price - current_balance}.",
            show_alert=True
        )
        return

    # Deduct coins and add the character to user's collection
    new_balance = current_balance - price
    character_data = {
        "_id": ObjectId(),
        "img_url": character["img_url"],
        "name": character["name"],
        "anime": character["anime"],
        "rarity": character["rarity"],
        "id": character["id"]
    }

    # Update user's data in the database
    user["characters"].append(character_data)
    await user_collection.update_one(
        {"id": user_id},
        {"$set": {"balance": new_balance, "characters": user["characters"]}}
    )

    await callback_query.answer("Character purchased successfully!")


@app.on_callback_query(filters.regex("^next$"))
async def next_item(client, callback_query):
    user_id = callback_query.from_user.id

    # Access the user's state from the global dictionary
    user_state = user_data.get(user_id, {})
    current_index = user_state.get("current_index", 0)

    characters_cursor = shops_collection.find()
    characters = await characters_cursor.to_list(length=None)

    if not characters:
        await callback_query.answer("No characters found in the shop.", show_alert=True)
        return

    next_index = (current_index + 1) % len(characters)
    character = characters[next_index]

    caption_message = (
        f"**Welcome to the Luxury Shop!**\n\n"
        f"**Character:** {character['name']}\n"
        f"**Anime:** {character['anime']}\n"
        f"**Rarity:** {character['rarity']}\n"
        f"**Price:** {character['price']} coins\n"
        f"**ID:** {character['id']}\n"
        f"Unlock New characters"
    )

    keyboard = [
        [InlineKeyboardButton("Buy", callback_data=f"buy_{next_index}"),
         InlineKeyboardButton("Next", callback_data="next")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await callback_query.message.edit_media(
        media=InputMediaPhoto(media=character['img_url'], caption=caption_message),
        reply_markup=reply_markup
    )

    # Update the user's state in the global dictionary
    user_data[user_id]["current_index"] = next_index
    await callback_query.answer()

@app.on_message(filters.command("addshop"))
@require_power("add_character")
async def add_to_shop(client, message):
    args = message.text.split()[1:]

    if len(args) != 2:
        await message.reply("Usage: /addshop <id> <price>")
        return

    character_id, price = args

    try:
        price = int(price)
    except ValueError:
        await message.reply("Price must be a valid number.")
        return

    character = await collection.find_one({"id": character_id})
    if not character:
        await message.reply("Character not found.")
        return

    character["price"] = price
    await shops_collection.insert_one(character)

    await message.reply(f"Character {character['name']} added to shop for {price} coins.")
