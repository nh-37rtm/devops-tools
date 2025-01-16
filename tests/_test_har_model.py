
import pydantic.parse

from models.har_models import deep_map_from_raw


from pytest import fixture
import logging
import subprocess
import json
from dataclasses import dataclass, is_dataclass

import typing as t


from pydantic_core import from_json
import pydantic

import aiohttp
import asyncio

from jsonpath_ng import parse

from tests.resources.sii.models import SiiExperience, SiiCv

from models import controler as JinjaCvControler

from models.har_models import IHarFileRequest

@fixture(name="async_loop")
def fix1() -> asyncio.AbstractEventLoop:
    asyncio.set_event_loop(asyncio.new_event_loop())
    return asyncio.get_event_loop()

@fixture(name="logger")
def fix0() -> logging.Logger:
    return  logging.getLogger()


def test_har_jq(logger: logging.Logger, async_loop: asyncio.AbstractEventLoop):


    async def get_out(child: subprocess.Popen):


        lines = child.stdout.readlines()
        text = ''.join([line.decode("utf-8") for line in lines])
        json_objs = json.loads(text)  
        pydantic_data = deep_map_from_raw(json_objs, IHarFileRequest)


        async with aiohttp.ClientSession() as session:
            
            
            for header in pydantic_data.headers:             
                
                if header.name == "Content-Length":
                    continue
                
                session.headers.add(header.name, header.value)
                
                
            session.headers.add("Content-Length", f'{len(pydantic_data.postData["text"])}')
                     
            
            async with session.put(pydantic_data.url, data=pydantic_data.postData['text']) as resp:                                               
                           
                
                print(resp.status)
                print(await resp.text())

        child.wait()
        
    asyncio.set_event_loop(async_loop)
    
    child = subprocess.Popen(
        args=[
            '/usr/bin/jq', 
            '''[ .log.entries[] | select ( .request.method == "PUT" ) | .request] | first''',
            'tests/resources/sii/galaxsii.siinergy_.net.har'],
        shell=False, stdout= subprocess.PIPE)
    
    
    task = async_loop.create_task(get_out(child))
    async_loop.run_until_complete(task)
    
    pass

    

def test_controller1(logger : logging.Logger):

    
    with open('jinja_cv/data/cv.json') as json_file:
        full_test= ''.join(json_file.readlines())
        json_data = json.loads(full_test)

        jsonpath_expression = parse('$.curriculum.experiences[0].*')
        match = jsonpath_expression.find(json_data)
        res = [ v.value for v in match ]
        pass


def test_random_object_dict(logger : logging.Logger):
    
    
    
    @dataclass
    class ClassB():
        
        def __init__(self):
            pass
        
        b_a: str
        b_b: str

    @dataclass
    class ClassC():
        
        def __init__(self):
            pass
        
        c_a: str
        c_b: str
    
    
    @dataclass
    class ClassA():
        
        def __init__(self):
            pass

        a: str
        b: str
        
        ab: t.List[ClassB]
        ac: ClassC
        
        

    data_reference = { "a": "a value", "b": "b value", "c": "c value", 
                      "ab": [ { "b_a": "a string 0", "b_b": "another string 0"}, { "b_a": "a string 1", "b_b": "another string 1"}],
                      "ac": { "c_a": "a c string", "c_b": "another c string"}
                      }

    a = deep_map_from_raw(data_reference, dict)

    pass
    