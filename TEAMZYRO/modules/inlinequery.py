import re
import time
import asyncio
from html import escape
from cachetools import TTLCache
from telegram import Update, InlineQueryResultPhoto, InlineQueryResultVideo
from telegram.ext import InlineQueryHandler, CallbackContext
from TEAMZYRO import application
from TEAMZYRO.unit.zyro_inline import *

async def on_startup(app: Application):
    """Start the change stream watcher when bot starts"""
    asyncio.create_task(watch_for_changes())

async def inlinequery(update: Update, context: CallbackContext) -> None:
    query = update.inline_query.query.strip()
    offset = int(update.inline_query.offset) if update.inline_query.offset else 0
    
    # Check for refresh command
    force_refresh = 'refresh' in query.lower()
    if force_refresh:
        query = query.replace('refresh', '').strip()
    
    # Handle collection searches
    if query.startswith('collection.'):
        parts = query.split(' ')
        user_id = parts[0].split('.')[1]
        search_term = ' '.join(parts[1:]) if len(parts) > 1 else ''
        
        if user_id.isdigit():
            user = await get_user_collection(user_id, force_refresh)
            if user:
                # Deduplicate and filter characters
                all_chars = {char['id']: char for char in user.get('characters', []) if 'id' in char}
                all_characters = list(all_chars.values())
                
                if search_term:
                    regex = re.compile(search_term, re.IGNORECASE)
                    all_characters = [c for c in all_characters 
                                   if regex.search(c.get('name', '')) or 
                                   regex.search(c.get('anime', ''))]
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
    media_filter = 'vid_url' if '.AMV' in query else 'img_url'
    all_characters = [c for c in all_characters if media_filter in c]
    
    # Pagination
    characters = all_characters[offset:offset + 50]
    next_offset = str(offset + 50) if len(all_characters) > offset + 50 else None
    
    # Build results
    results = []
    for char in characters:
        # Generate caption
        if 'user' in locals():
            count = sum(1 for c in user['characters'] if c.get('id') == char['id'])
            caption = (
                f"<b>👤 {escape(user.get('first_name', 'User'))}'s collection:</b>\n\n"
                f"🌸 <b>{char['name']} (x{count})</b>\n"
                f"🏖️ From: <b>{char['anime']}</b>\n"
                f"🔮 Rarity: <b>{char['rarity']}</b>\n"
                f"🆔 <b>{char['id']}</b>"
            )
        else:
            caption = (
                f"<b>Character:</b> {char['name']}\n"
                f"<b>Anime:</b> {char['anime']}\n"
                f"<b>Rarity:</b> {char['rarity']}\n"
                f"<b>ID:</b> {char['id']}"
            )
        
        # Create result object
        if 'vid_url' in char:
            results.append(InlineQueryResultVideo(
                id=f"{char['id']}_{time.time()}",
                video_url=char['vid_url'],
                mime_type="video/mp4",
                thumbnail_url=char.get('thum_url', 'https://default-thumbnail.jpg'),
                title=char['name'],
                description=f"{char['anime']} | {char['rarity']}",
                caption=caption,
                parse_mode='HTML'
            ))
        elif 'img_url' in char:
            results.append(InlineQueryResultPhoto(
                id=f"{char['id']}_{time.time()}",
                photo_url=char['img_url'],
                thumbnail_url=char['img_url'],
                caption=caption,
                parse_mode='HTML'
            ))
    
    await update.inline_query.answer(results, next_offset=next_offset, cache_time=5)

# Register handler
application.add_handler(InlineQueryHandler(inlinequery, block=False))
application.add_handler(Application.POST_INIT, on_startup)


