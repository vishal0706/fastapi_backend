import pymongo

from app.server.database.db import mongo
from app.server.static.collections import Collections


async def create_indexes():
    await mongo.get_collection(Collections.USERS).create_index([('first_name', pymongo.TEXT), ('last_name', pymongo.TEXT)], background=True)
