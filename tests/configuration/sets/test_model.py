
from pydantic import BaseModel, constr, HttpUrl

class SubModel(BaseModel):
    object_property: str

class TestModel(BaseModel):
    __test__ = False
    an_array: list[str]
    an_object: SubModel
    a_property: str


class SplunkModel(BaseModel):
    url: str
    hecurl: str

class TestEnvModel(BaseModel):
    __test__ = False
    splunk: SplunkModel

class vaultAuthModel(BaseModel):
    role_id: constr(min_length=36)
    secret_id: constr(min_length=36)
    url: HttpUrl

class TestSplunkModel(BaseModel):
    __test__ = False
    token_hec: str
    url_hec: HttpUrl

class TestvaultAuthModel(BaseModel):
    __test__ = False
    role_id: str
    secret_id: str