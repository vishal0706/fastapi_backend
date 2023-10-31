from typing import Any, Optional, Union

from bson.objectid import ObjectId
from pydantic import BaseModel as PydanticBaseModel
from pydantic.class_validators import validator
from pydantic.fields import Field

from app.server.utils import date_utils

ListOrDictType = Union[Optional[list[dict[str, Any]]], Optional[dict[str, Any]]]
DictType = dict[str, Any]


class PyObjectId(ObjectId):
    """Extension of mongo ObjectId class"""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        if not ObjectId.is_valid(value):
            raise ValueError('Invalid objectid')
        return ObjectId(value)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type='string')


class BaseModel(PydanticBaseModel):
    """Base class for model with predefined Config"""

    class Config:
        arbitrary_types_allowed = True
        anystr_strip_whitespace = True
        extra = 'forbid'


class DictWithObjectIdStr(BaseModel):
    """Base class for model that needs auto mongo ObjectId creation to be inserted in database"""

    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class DateTimeModelMixin(BaseModel):
    created_at: int = None
    updated_at: int = created_at

    # pylint: disable=no-self-argument
    @validator('created_at', 'updated_at', pre=True, always=True)
    def default_datetime(cls, value: int) -> int:
        return value or date_utils.get_current_timestamp()
