
from jinja_cv.models.base_models import (
    Experience, 
    JExperience, 
    JsonObject, 
    JExperienceList, 
    VExperience)

from pytest import fixture
import logging
import subprocess
import json
from dataclasses import dataclass
import asyncio

from jsonpath_ng import parse

@fixture(name="logger")
def fix0() -> logging.Logger:
    return  logging.getLogger()


@fixture(name="async_loop")
def fix1() -> asyncio.AbstractEventLoop:
    asyncio.set_event_loop(asyncio.new_event_loop())
    return asyncio.get_event_loop()


@fixture(name="readers_v")
def fix2() -> tuple[asyncio.StreamReaderProtocol, asyncio.StreamReader]:
    stream_reader = asyncio.StreamReader()
    return (lambda: asyncio.StreamReaderProtocol(stream_reader), stream_reader)

def test_parse(logger : logging.Logger):
    with open('tests/resources/experience.json') as json_file:
        full_test= ''.join(json_file.readlines())
        experience = VExperience.model_validate_json(full_test)
        logger.info(experience)


def test_jsonhpath():
    json_string = '{"id":1, "name":"Pankaj"}'
    json_data = json.loads(json_string)
    jsonpath_expression = parse('$.id')



def test_async_pipes(
    logger: logging.Logger, 
    async_loop: asyncio.AbstractEventLoop,
    readers_v: tuple[asyncio.StreamReaderProtocol, asyncio.StreamReader]):
    
    
    protocol_factory, stream_reader = readers_v
    
    async def produce_input(child: subprocess.Popen):
        for i in range(0, 10):
            logger.info("creating %d ..." % i)
            await asyncio.sleep(2)
            astring = '%s\n' % i

            child.stdin.writelines([astring.encode()])
            child.stdin.flush()
            
        child.stdin.close()
        
    async def consume_out(child: subprocess.Popen):

        while(child.stdout.readable):
            line = await stream_reader.readline()
            if not line:
                break 

            await asyncio.sleep(1)
            logger.info("consumed %s ..." % line)

        child.wait()
    
    async def do_work():
                
        await async_loop.connect_read_pipe(protocol_factory, pipe=child.stdout)

        async with asyncio.TaskGroup() as task_group :
                
            await asyncio.gather(
                produce_input(child), 
                consume_out(child) )
    
    child = subprocess.Popen(
        args=['/bin/cat'],
        shell=False, stdin=subprocess.PIPE, stdout= subprocess.PIPE)
    
    async_loop.run_until_complete(async_loop.create_task(do_work()))
    
    pass


def test_asyncio_2(logger: logging.Logger, async_loop: asyncio.AbstractEventLoop):
    
    async def produce_input(child: asyncio.subprocess.Process):
        for i in range(0, 10):
            logger.info("creating %d ..." % i)
            await asyncio.sleep(2)
            astring = '%s\n' % i

            child.stdin.writelines([astring.encode()])
            
        child.stdin.close()
    
    async def consume_out(child: asyncio.subprocess.Process):
        
        while(True) :
            line = await child.stdout.readline()
            logger.info("reading %s ..." % line)
            if not line:
                break
    
    async def do_work():

        proc = await asyncio.create_subprocess_exec(
            '/bin/cat', 
            stdin= asyncio.subprocess.PIPE,
            stdout= asyncio.subprocess.PIPE,
            stderr= asyncio.subprocess.PIPE
        )

        async with asyncio.TaskGroup() as task_group :
            task_group.create_task(produce_input(proc))
            task_group.create_task(consume_out(proc))


    async_loop.run_until_complete(do_work())



def test_jq(logger: logging.Logger, async_loop: asyncio.AbstractEventLoop):

    async def get_out(child: subprocess.Popen):

        lines = child.stdout.readlines()
        text = ''.join([line.decode() for line in lines])
        json_objs = json.loads(text)
      
        experience_list = JExperienceList.from_object(json_objs)

        child.wait()
        
    asyncio.set_event_loop(async_loop)
    
    child = subprocess.Popen(
        args=[
            '/usr/bin/jq', 
            '-f', './jq_queries/experiences.jq', 
            './jinja_cv/data/cv.json'],
        shell=False, stdout= subprocess.PIPE)
    task = async_loop.create_task(get_out(child))
    async_loop.run_until_complete(task)
    
    pass
   
   
def test_jq2(logger: logging.Logger, async_loop: asyncio.AbstractEventLoop):

    async def get_out(child: subprocess.Popen):

        lines = child.stdout.readlines()
        text = ''.join([line.decode() for line in lines])
        json_objs = json.loads(text)
      
        experience_list = JExperienceList.from_object(json_objs)

        child.wait()
        
    asyncio.set_event_loop(async_loop)
    
    child = subprocess.Popen(
        args=[
            '/usr/bin/jq', 
            '-f', './jq_queries/experiences2.jq', 
            './jinja_cv/data/cv.json'],
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
    
    
def test_class():
    
    class AsyncPopen():

        @dataclass
        class ConstructorParameters:
            a: str
            b: str
            
        def __init__(self, parameters: ConstructorParameters) -> 'AsyncPopen':
            pass
    
    AsyncPopen(AsyncPopen.ConstructorParameters(a="test", b="test"))
    