
import pydantic.parse
from jinja_cv.models.base_models import (
    Experience, 
    JExperience, 
    JsonObject, 
    JExperienceList, 
    VExperience,
    deep_map_from_raw)

from jinja_cv.models.har_models import IHarFileRequest

from pytest import fixture
import logging
import subprocess
import json
from dataclasses import dataclass, is_dataclass, asdict

from datetime import datetime, timezone, timedelta

from pydantic_core import from_json
import pydantic

import aiohttp
import asyncio

from jsonpath_ng import parse

from tests.resources.sii.models import SiiExperience, SiiCv

from jinja_cv.controler import controler as JinjaCvControler

from jinja_cv.generate import RenderContext

import typing as t

@fixture(name="logger")
def fix0() -> logging.Logger:
    return  logging.getLogger()

def test_controller1(logger : logging.Logger):

    
    with open('jinja_cv/data/cv.json') as json_file:
        full_test= ''.join(json_file.readlines())
        json_data = json.loads(full_test)

        jsonpath_expression = parse('$.curriculum.experiences[0].*')
        match = jsonpath_expression.find(json_data)
        res = [ v.value for v in match ]
        pass


def SiiExperienceMapper(source: JinjaCvControler.Experience) -> SiiExperience:
    
    experience = SiiExperience()
    experience.client = source.client
    experience.clientService = source.intitule
    experience.projectTitle = source.intitule
    experience.shortDescription = source.presentation
    experience.stack = source.environnementTechnique
    experience.startDate = source.dateDebut
    experience.endDate = source.dateFin
    
    return experience

def SiiRealisationMapper(source: JinjaCvControler.Realisation):
    
    if len(source.realisations) > 0:
        for realisation in source.realisations:
            description = f"{description}\n- {realisation}"
            


async def get_har_data(child: subprocess.Popen) -> IHarFileRequest:

    lines = child.stdout.readlines()
    text = ''.join([line.decode("utf-8") for line in lines])
    json_objs = json.loads(text)  
    child.wait()
    
    return deep_map_from_raw(json_objs, IHarFileRequest)


def format_date(date: datetime) -> str:
    
    date = date.replace(tzinfo=datetime.now().astimezone().tzinfo)
    formatted_date = datetime.isoformat(date, timespec='microseconds')
    return formatted_date
    


class EnhancedJSONEncoder(json.JSONEncoder):
        def default(self, o):
            if is_dataclass(o):
                return asdict(o)
            if isinstance(o, datetime):
                return format_date(o)
            if isinstance(o, str):
                return o.replace('\n', '')
            return super().default(o)



async def put_to_sii(experiences: t.List[SiiExperience] ):

    child = subprocess.Popen(
        args=[
            '/usr/bin/jq', 
            '''[ .log.entries[] | select ( .request.method == "PUT" ) | .request] | first''',
            'tests/resources/sii/galaxsii.siinergy_.net.har'],
        shell=False, stdout= subprocess.PIPE)

    # task = asyncio.create_task(get_har_data(child))
    
    har_data: IHarFileRequest = await get_har_data(child)

    async with aiohttp.ClientSession() as session:
        
        
        for header in har_data.headers:             
            
            if header.name == "Content-Length":
                continue
            
            session.headers.add(header.name, header.value)
            
        # SiiCv.model_validate_json(har_data.postData["text"])
        # SiiCv.model_construct(har_data.postData["text"])
        json_cv = json.loads(har_data.postData["text"])
        cv = deep_map_from_raw(json_cv, SiiCv)
        #SiiExperience.model_construct(har_data.postData["text"])
        experiences[0].description = experiences[0].description.replace('\n', '')
        cv.experiences.append(experiences[0])
        json_cv['experiences'] = cv.experiences
        
        
        # cv.experiences = experiences
        json_data = json.dumps(json_cv, cls=EnhancedJSONEncoder)
        # json_data = har_data.postData["text"]
            
        session.headers.add("Content-Length", f'{len(json_data)}')
        
        
        async with session.put(har_data.url, data=json_data) as resp:
            
            print(resp.status)
            print(await resp.text())
           


def test_sii(logger : logging.Logger):
    
    logger.info("this is the test begin")

    sii_experiences_list: t.List[SiiExperience] = []

    #with open('tests/resources/sii/service_payload.json', 'r', encoding='utf-8') as file:
    with open('jinja_cv/data/cv.json', 'r', encoding='utf-8') as file:
        jsonCv = json.load(file)
        
        experience_list = JinjaCvControler.controlFlatenExperience(jsonCv['curriculum']['experiences'])

        render_context = RenderContext()
        render_context.templateDir = 'tests/resources/sii/'
        
        for experience in experience_list:
            
            realisation_list = JinjaCvControler.controlRealisation(experience.realisations)
            realisations_as_html: str = ""
            for realisation in realisation_list:
                realisation_render = render_context.renderTemplate("rea.j2.html", data = realisation)
                realisations_as_html = f"{realisations_as_html}{realisation_render}"
            
            realisations_as_html = f"<ul>{realisations_as_html}</ul>"
            
            sii_experience = SiiExperienceMapper(experience)
            sii_experience.description = realisations_as_html
            
            sii_experiences_list.append(sii_experience)

        pass
    
    
    # cv = SiiCv.model_construct(experiences=sii_experiences_list)
    # put_data = cv.experiences[0].model_dump_json()
    
    
    test_value = '''{
  "job": null,
  "experience": null,
  "availability": null,
  "introduction": null,
  "technicalSkills": [],
  "functionalSkills": [],
  "experiences": [
    {
      "id": "2a6eb87a-a421-49ed-8cda-54213d14846a",
      "favorite": false,
      "clientService": "service",
      "city": "Belfort",
      "projectTitle": "allo",
      "job": "poste2",
      "endDate": "2024-11-23T00:00:00.000+01:00",
      "description": "<p>description longue </p>",
      "shortDescription": "description courte",
      "task": null,
      "stack": "dsfs, sdfsdf, sdfsdf, sdfsdf",
      "client": "client1",
      "startDate": "2024-11-23T00:00:00.000+01:00",
      "rank": 0,
      "significant": false
    },
    {
      "id": "e99fbae4-3161-4b88-8ff8-525132e2d1ca",
      "favorite": false,
      "clientService": null,
      "city": null,
      "projectTitle": "ytytyt",
      "job": "ytytytyt",
      "endDate": null,
      "description": "",
      "shortDescription": "aa",
      "task": null,
      "stack": null,
      "client": null,
      "startDate": null,
      "rank": 1,
      "significant": false
    },
    {
      "id": "df1d9332-8a11-4c64-9035-b9a8a1a62d0e",
      "favorite": false,
      "clientService": null,
      "city": null,
      "projectTitle": null,
      "job": null,
      "endDate": null,
      "description": "",
      "shortDescription": null,
      "task": null,
      "stack": null,
      "client": null,
      "startDate": null,
      "rank": 2,
      "significant": false
    }
  ],
  "diplomas": [],
  "languages": [],
  "submitted": false,
  "id": null,
  "ref": null,
  "schools": [],
  "formations": [],
  "technology": null,
  "significant": null
}'''
    
    asyncio.run(put_to_sii(sii_experiences_list))