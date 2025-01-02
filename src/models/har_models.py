from dataclasses import dataclass

from pydantic.alias_generators import to_snake, to_camel
from pydantic import BaseModel, ConfigDict

from pydantic.functional_validators import WrapValidator
from pydantic.alias_generators import to_snake, to_camel

from typing_extensions import Annotated

from datetime import datetime

import typing as t

class PydanticBaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel, 
        arbitrary_types_allowed=True)

def validate_datetime(
        v: t.Any,
        handler: ValidatorFunctionWrapHandler,
        info: ValidationInfo
    ) -> datetime:
    
    pass

CustomDateTime = Annotated[
    datetime, 
    WrapValidator(validate_datetime)]

from pydantic import (
    BaseModel,
    ValidationError,
    ValidationInfo,
    ValidatorFunctionWrapHandler,
    ConfigDict,
)
    
def validate_datetime(
        v: t.Any,
        handler: ValidatorFunctionWrapHandler,
        info: ValidationInfo
    ) -> datetime:
    
    if info.mode == 'json':
        assert isinstance(v, str), 'In JSON mode the input must be a string!'
        try:
            return handler(datetime.strptime(v,'%Y-%m-%d').date())
        except ValidationError as e:
            raise e
    
    if info.mode == 'python':
        if isinstance(v, str):
            return handler(datetime.strptime(v,'%Y-%m-%d').date())
        assert isinstance(v, datetime), 'In JSON mode the input must be a datetime!'
    
    return v


@dataclass
class IHarHttpHeader():
    name: str
    value: str    

@dataclass
class IHarFileRequest():
    method: str
    url: str
    headers: t.List[IHarHttpHeader]
    postData: dict

@dataclass
class IHarFileResponse:
    pass

@dataclass
class IHarFileEntry:
    request: IHarFileRequest
    response: IHarFileResponse

@dataclass
class IHarFileStructure:
    log: IHarFileEntry
    

class HarHttpHeaderPydanticModel(IHarHttpHeader, PydanticBaseModel):
    pass
class HarFileRequestPydanticModel(IHarFileRequest, PydanticBaseModel):
    headers: t.List[HarHttpHeaderPydanticModel]
    pass
    
    