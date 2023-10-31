import copy
from typing import Any, Optional, Union

from bson.objectid import ObjectId
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorClientSession
from pymongo import UpdateOne
from pymongo.errors import DuplicateKeyError

from app.server.database.db import client, mongo
from app.server.models.core_data import CreateData
from app.server.utils import date_utils

# crud operations


def _prepare_update(update: dict[str, Any], timestamp: int) -> dict[str, Any]:
    """
    Prepare an update dictionary by adding a '$set' key if it doesn't exist,
    and updating the 'updated_at' field with the provided timestamp.

    Args:
        update (dict): The update dictionary.
        timestamp (int): The timestamp to update the 'updated_at' field with.

    Returns:
        dict: The modified update dictionary.
    """
    update.setdefault('$set', {})
    update['$set'].update({'updated_at': timestamp})
    return update


def _prepare_upsert(update: dict[str, Any], timestamp: int) -> dict[str, Any]:
    """
    Generate a dictionary update for upsert operations.

    Args:
        update (dict): The dictionary update.
        timestamp (str): The timestamp string.

    Returns:
        dict: The updated dictionary.
    """
    update.setdefault('$setOnInsert', {})
    update['$setOnInsert'].update({'_id': str(ObjectId()), 'created_at': timestamp})

    if 'is_deleted' not in update['$set']:
        update['$setOnInsert'].update({'is_deleted': False})

    return update


async def get_session() -> AsyncIOMotorClientSession:
    return await client.start_session()


async def create_one(collection_name: str, data: dict[str, Any], options: dict[str, Any] = None, session: AsyncIOMotorClientSession = None) -> dict[str, Any]:
    """Insert one operation on database

    Args:
        collection_name (str): collection name
        data (dict): document to be inserted

    Raises:
        CustomException: custom exception if document insertion fails

    Returns:
        dict[str, Any]: inserted document
    """
    collection = mongo.get_collection(collection_name)
    data = CreateData.parse_obj(data)
    data = jsonable_encoder(data)
    model = None
    try:
        model = await collection.insert_one(data, session=session)
    except DuplicateKeyError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f'{collection_name}: + {error.details}') from error
    if not model.inserted_id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f'{collection_name}: Failed to create')
    if session:
        return {'_id': model.inserted_id}
    model = await collection.find_one({'_id': model.inserted_id}, options)
    return model


async def create_many(collection_name: str, data: list[dict[str, Any]], session: AsyncIOMotorClientSession = None) -> dict[str, Any]:
    """Insert many operation on database

    Args:
        collection_name (str): collection name
        data (list): documents to be inserted

    Raises:
        CustomException: custom exception if documents insertion fails

    Returns:
        dict[str, Any]: dictionary with createdCount
    """
    collection = mongo.get_collection(collection_name)
    data = [CreateData.parse_obj(indi_data) for indi_data in data]
    data = jsonable_encoder(data)
    model = None
    try:
        model = await collection.insert_many(data, session=session)
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f'{collection_name}: + {str(error)}') from error
    if not model.inserted_ids:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f'{collection_name}: Failed to create')
    return {'ids': model.inserted_ids}


async def read_one(collection_name: str, data_filter: Union[dict[str, Any], str], options: dict[str, Any] = None) -> dict[str, Any]:
    """Read One operation on database

    Args:
        collection_name (str): collection name
        data_filter (dict): dictionary of fields to apply filter for
        options (dict): dictionary of fields with value 1 or 0. 1 - to select, 0 - de-select

    Raises:
        CustomException: custom exception if document not found

    Returns:
        dict[str, Any]: document
    """
    collection = mongo.get_collection(collection_name)
    if not options:
        options = None
    model = await collection.find_one(data_filter, options)
    return model or {}


# pylint: disable=too-many-arguments
async def read_many(
    collection_name: str, data_filter: dict[str, Any], options: dict[str, Any] = None, sort: dict[str, Any] = None, page: Optional[int] = None, page_size: Optional[int] = None
) -> list[dict[str, Any]]:
    """Read many operation on database

    Args:
        collection_name (str): collection name
        data_filter (dict): dictionary of fields to apply filter for
        options (dict): dictionary of fields with value 1 or 0. 1 - to select, 0 - de-select

    Returns:
        list[dict[str, Any]]: document list
    """
    collection = mongo.get_collection(collection_name)
    model_list = []

    if not options:
        options = None

    models = collection.find(data_filter, options)

    if sort:
        sort_query = list(sort.items())
        models.sort(sort_query)

    if page and page > 0:
        offset = page_size if page_size and page_size > 0 else 0
        models.skip((page - 1) * offset)

    if page_size and page_size > 0:
        models.limit(page_size)

    async for model in models:
        model_list.append(model)
    return model_list


# pylint: disable=too-many-arguments
async def update_one(
    collection_name: str,
    record_id: str = None,
    data_filter: dict[str, Any] = None,
    update: dict[str, Any] = None,
    options: dict[str, Any] = None,
    upsert: bool = False,
    session: AsyncIOMotorClientSession = None,
) -> dict[str, Any]:  # pylint: disable=too-many-arguments
    """Find one and update operation on database

    Args:
        collection_name (str): collection name
        record_id (str): document id
        filter (dict): dictionary of fields to apply filter for
        update (dict): dictionary of field data to be updated
        options (dict): dictionary of fields with value 1 or 0. 1 - to select, 0 - de-select

    Raises:
        HTTPException: custom exception if filter dict is not set
        HTTPException: custom exception if update dict is not set
        HTTPException: custom exception if update fails

    Returns:
        dict[str, Any]: document
    """
    collection = mongo.get_collection(collection_name)

    if record_id:
        data_filter = {'_id': record_id}
    if not data_filter:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f'{collection_name}: filter params cannot be empty')
    if not update:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f'{collection_name}: update params cannot be empty')

    timestamp = date_utils.get_current_timestamp()

    update_data = copy.deepcopy(update)
    update_data = _prepare_update(update_data, timestamp)

    if upsert:
        update_data = _prepare_upsert(update_data, timestamp)

    if not options:
        options = None

    try:
        model = await collection.find_one_and_update(data_filter, update_data, options, upsert=upsert, return_document=True, session=session)
    except DuplicateKeyError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f'{collection_name}: {error.details}') from error
    if not model:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f'{collection_name}: Failed to update')

    return model


async def update_many(collection_name: str, data_filter: dict[str, Any], update: dict[str, Any], upsert: bool = False, session: AsyncIOMotorClientSession = None) -> dict[str, Any]:
    """Update Many operation on database

    Args:
        collection_name (str): collection name
        data_filter (dict): dictionary of fields to apply filter for
        update (dict): dictionary of field data to be updated

    Raises:
        HTTPException: custom exception if filter dict is not set
        HTTPException: custom exception if update dict is not set
        HTTPException: custom exception if update fails

    Returns:
        dict[str, Any]: dictionary with modifiedCount
    """
    if not data_filter or not update:
        empty_param = 'update' if data_filter else 'data_filter'
        raise HTTPException(422, f'{collection_name}: {empty_param} param cannot be empty')

    collection = mongo.get_collection(collection_name)
    timestamp = date_utils.get_current_timestamp()

    # Prepare update fields
    update = _prepare_update(update, timestamp)

    if upsert:
        # Prepare upsert fields
        update = _prepare_upsert(update, timestamp)

    try:
        model = await collection.update_many(data_filter, update, upsert=upsert, session=session)
    except Exception as error:
        raise HTTPException(422, f'{collection_name}: Failed to update') from error

    return {'modified_count': model.modified_count}


async def delete_one(collection_name: str, record_id: str = None, data_filter: dict[str, Any] = None, session: AsyncIOMotorClientSession = None) -> dict[str, Any]:
    """Delete One operation on database

    Args:
        collection_name (str): collection name
        record_id (str): document id

    Raises:
        HTTPException: custom exception if filter dict is not set
        HTTPException: custom exception if deletion fails

    Returns:
        dict[str, Any]: document
    """
    collection = mongo.get_collection(collection_name)

    if record_id:
        data_filter = {'_id': record_id}

    if not data_filter:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f'{collection_name}: filter params cannot be empty')

    model = await collection.find_one_and_delete(data_filter, session=session)

    if not model:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f'{collection_name}: Failed to delete')

    return model


async def delete_many(collection_name: str, data_filter: dict[str, Any], session: AsyncIOMotorClientSession = None) -> dict[str, Any]:
    """Delete Many operation on database

    Args:
        collection_name (str): collection name
        data_filter (dict): dictionary of fields to apply filter for

    Raises:
        HTTPException: custom exception if filter dict is not set
        HTTPException: custom exception if deletion fails

    Returns:
        dict[str, Any]: dictionary with deletedCount
    """
    collection = mongo.get_collection(collection_name)
    if not data_filter:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f'{collection_name}: filter cannot be empty')

    model = await collection.delete_many(data_filter, session=session)

    return {'deleted_count': model.deleted_count}


async def count(collection_name: str, data_filter: dict[str, Any], session: AsyncIOMotorClientSession = None) -> dict[str, Any]:
    """Count operation on database

    Args:
        collection_name (str): collection name
        data_filter (dict): dictionary of fields to apply filter for

    Raises:
        HTTPException: custom exception if filter dict is not set

    Returns:
        dict[str, Any]: dictionary with count
    """
    collection = mongo.get_collection(collection_name)

    doc_count = await collection.count_documents(data_filter, session=session)
    return {'count': doc_count}


async def query_read(collection_name: str, aggregate: list[dict[str, Any]], page: Optional[int] = None, page_size: Optional[int] = None, paging_data: bool = False):
    collection = mongo.get_collection(collection_name)
    page_size = min(page_size, 100) if page_size else 10
    page = page or 1
    skip = (page - 1) * page_size

    if not aggregate:
        aggregate = []

    if paging_data:
        aggregate += [
            {'$facet': {'data': [{'$skip': skip}, {'$limit': page_size + 1}], 'total_count': [{'$count': 'total'}]}},
            {
                '$addFields': {
                    'metadata': {
                        'current_page': page,
                        'page_size': page_size,
                        'total_records': {'$ifNull': [{'$arrayElemAt': ['$total_count.total', 0]}, 0]},
                        'has_next_page': {'$gt': [{'$size': '$data'}, page_size]},
                    }
                }
            },
            {'$project': {'data': {'$slice': ['$data', page_size]}, 'metadata': 1}},  # Limit the result size to page_size
        ]
        result = await collection.aggregate(aggregate).to_list(None)
        return result[0]
    aggregate += [{'$skip': skip}, {'$limit': page_size}]

    return await collection.aggregate(aggregate).to_list(None)


async def aggregate_pipeline(collection_name: str, aggregate: list[dict[str, Any]], page: Optional[int] = None, page_size: Optional[int] = None) -> list[dict[str, Any]]:
    collection = mongo.get_collection(collection_name)
    # model_list = []
    page_size = min(page_size, 100) if page_size else 10
    page = page or 1
    skip = (page - 1) * page_size

    if not aggregate:
        aggregate = []

    aggregate += [
        {'$facet': {'data': [{'$skip': skip}, {'$limit': page_size + 1}], 'total_count': [{'$count': 'total'}]}},
        {
            '$addFields': {
                'metadata': {
                    'current_page': page,
                    'page_size': page_size,
                    'total_records': {'$ifNull': [{'$arrayElemAt': ['$total_count.total', 0]}, 0]},
                    'has_next_page': {'$gt': [{'$size': '$data'}, page_size]},
                }
            }
        },
        {'$project': {'data': {'$slice': ['$data', page_size]}, 'metadata': 1}},  # Limit the result size to page_size
    ]

    result = await collection.aggregate(aggregate).to_list(None)
    return result[0]


async def distinct(collection_name: str, field: str) -> dict[str, Any]:
    collection = mongo.get_collection(collection_name)

    return await collection.distinct(field)


def update_query(record_id: str = None, data_filter: dict[str, Any] = None, update: dict[str, Any] = None, upsert: bool = False) -> UpdateOne:
    timestamp = date_utils.get_current_timestamp()
    if record_id:
        data_filter = {'_id': record_id}

    if not data_filter:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='filter params cannot be empty')

    if not update:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='update params cannot be empty')

    update_data = copy.deepcopy(update)
    update_data = _prepare_update(update_data, timestamp)

    if upsert:
        update_data = _prepare_upsert(update_data, timestamp)

    return UpdateOne(filter=data_filter, update=update_data, upsert=upsert)


async def bulk_write(collection_name: str, operations: list[Any]) -> list[dict[str, Any]]:
    collection = mongo.get_collection(collection_name)
    return await collection.bulk_write(operations)
