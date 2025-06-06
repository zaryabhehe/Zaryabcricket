import re
from cachetools import TTLCache
from pymongo import MongoClient
from TEAMZYRO import user_collection, collection

# Caching with shorter TTL for better freshness
all_characters_cache = TTLCache(maxsize=10000, ttl=300)  # 5 minutes
user_collection_cache = TTLCache(maxsize=10000, ttl=30)   # 30 seconds

async def get_user_collection(user_id, force_refresh=False):
    """Get user collection with cache control"""
    if not force_refresh and user_id in user_collection_cache:
        return user_collection_cache[user_id]
    
    user = await user_collection.find_one({'id': int(user_id)})
    if user:
        user_collection_cache[user_id] = user
    return user

async def search_characters(query, force_refresh=False):
    """Search characters with cache control"""
    if not force_refresh and f"search_{query}" in all_characters_cache:
        return all_characters_cache[f"search_{query}"]
    
    regex = re.compile(query, re.IGNORECASE)
    results = await collection.find({"$or": [
        {"name": regex},
        {"anime": regex}
    ]}).to_list(length=None)
    
    all_characters_cache[f"search_{query}"] = results
    return results

async def get_all_characters(force_refresh=False):
    """Get all characters with cache control"""
    if not force_refresh and 'all_characters' in all_characters_cache:
        return all_characters_cache['all_characters']
    
    characters = await collection.find({}).to_list(length=None)
    all_characters_cache['all_characters'] = characters
    return characters

async def watch_for_changes():
    """MongoDB change stream for real-time updates"""
    client = MongoClient('your_mongo_connection_string')
    pipeline = [{'$match': {'operationType': {'$in': ['insert', 'update', 'delete']}}}]
    
    try:
        with client.watch(pipeline) as stream:
            for change in stream:
                # Clear relevant caches when changes occur
                if 'all_characters' in all_characters_cache:
                    del all_characters_cache['all_characters']
                
                # Clear search caches if document was modified
                if 'documentKey' in change:
                    doc_id = str(change['documentKey']['_id'])
                    for key in list(all_characters_cache.keys()):
                        if key.startswith('search_'):
                            del all_characters_cache[key]
                
                print(f"Database change detected - caches cleared: {change['operationType']}")
    except Exception as e:
        print(f"Change stream error: {e}")
