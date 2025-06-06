import re
import time
from html import escape
from cachetools import TTLCache
from telegram import Update, InlineQueryResultPhoto, InlineQueryResultVideo
from telegram.ext import InlineQueryHandler, CallbackContext
from TEAMZYRO import application
from TEAMZYRO.unit.zyro_inline import *

# Cache instances (shared with zyro_inline.py)
all_characters_cache = TTLCache(maxsize=10000, ttl=300)
user_collection_cache = TTLCache(maxsize=10000, ttl=30)

async def inlinequery(update: Update, context: CallbackContext) -> None:
    query = update.inline_query.query.strip()
    offset = int(update.inline_query.offset) if update.inline_query.offset else 0
    
    # Force refresh if query contains !refresh (admin feature)
    force_refresh = '!refresh' in query
    if force_refresh:
        query = query.replace('!refresh', '').strip()
        await refresh_character_caches()

    try:
        # Check if query is for a user's collection
        if query.startswith('collection.'):
            parts = query.split(' ')
            user_id = parts[0].split('.')[1]
            search_terms = ' '.join(parts[1:]) if len(parts) > 1 else ''
            
            if user_id.isdigit():
                user = await get_user_collection(user_id)
                if user:
                    # Deduplicate and filter characters
                    all_characters = list({char['id']: char for char in user.get('characters', []) if 'id' in char}.values())
                    
                    if search_terms:
                        regex = re.compile(search_terms, re.IGNORECASE)
                        all_characters = [
                            char for char in all_characters 
                            if (regex.search(char.get('name', '')) or 
                                regex.search(char.get('anime', '')) or
                                regex.search(' '.join(char.get('aliases', []))))
                        ]
                else:
                    all_characters = []
            else:
                all_characters = []
        else:
            # General character search
            if query:
                all_characters = await search_characters(query, force_refresh)
            else:
                all_characters = await get_all_characters(force_refresh)

        # Filter by media type
        if '.AMV' in query:
            all_characters = [char for char in all_characters if char.get('vid_url')]
        else:
            all_characters = [char for char in all_characters if char.get('img_url')]

        # Pagination
        characters = all_characters[offset:offset + 50]
        next_offset = str(offset + len(characters)) if len(characters) == 50 else None

        # Build results
        results = []
        for character in characters:
            # Skip if missing essential fields
            if not all(k in character for k in ['id', 'name', 'anime', 'rarity']):
                continue
                
            # Generate caption
            if 'user' in locals():
                user_character_count = sum(1 for char in user.get('characters', []) 
                                      if char.get('id') == character['id'])
                caption = (
                    f"<b>👤 Look At {escape(user.get('first_name', 'User'))}'s Collection:</b>\n"
                    f"🌸 <b>{escape(character['name'])} (x{user_character_count})</b>\n"
                    f"<b>🏖️ From: {escape(character['anime'])}</b>\n"
                    f"<b>🔮 Rarity: {escape(character['rarity'])}</b>\n"
                    f"<b>🆔 <code>{escape(str(character['id']))}</code></b>\n"
                )
            else:
                caption = (
                    f"<b>Character Details:</b>\n\n"
                    f"🌸 <b>{escape(character['name'])}</b>\n"
                    f"<b>🏖️ From: {escape(character['anime'])}</b>\n"
                    f"<b>🔮 Rarity: {escape(character['rarity'])}</b>\n"
                    f"<b>🆔 <code>{escape(str(character['id']))}</code></b>\n"
                    
                )

            # Add result based on media type
            if character.get('vid_url'):
                results.append(InlineQueryResultVideo(
                    id=f"{character['id']}_{time.time()}",
                    video_url=character['vid_url'],
                    mime_type="video/mp4",
                    thumbnail_url=character.get('thum_url', 'https://example.com/default.jpg'),
                    title=character['name'],
                    description=f"{character['anime']} | {character['rarity']}",
                    caption=caption,
                    parse_mode='HTML'
                ))
            elif character.get('img_url'):
                results.append(InlineQueryResultPhoto(
                    id=f"{character['id']}_{time.time()}",
                    photo_url=character['img_url'],
                    thumbnail_url=character['img_url'],
                    caption=caption,
                    parse_mode='HTML'
                ))

        await update.inline_query.answer(results, next_offset=next_offset, cache_time=1)
        
    except Exception as e:
        print(f"Error in inlinequery: {e}")
        await update.inline_query.answer([], cache_time=1)

# Register handler
application.add_handler(InlineQueryHandler(inlinequery, block=False))
