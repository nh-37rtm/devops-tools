


from dataclasses import dataclass
from pydantic import BaseModel, Field
import typing as t

@dataclass
class SiiExperience():
    id: t.Optional[str] = None 
    favorite: t.Optional[bool] = False
    clientService: t.Optional[str] = None
    city: t.Optional[str] = None
    projectTitle: t.Optional[str] = None
    job: t.Optional[str] = None
    endDate: t.Optional[str] = None
    description: t.Optional[str] = None
    shortDescription: t.Optional[str] = None
    task: t.Optional[str] = None
    stack: t.Optional[str] = None
    client: t.Optional[str] = None
    startDate: t.Optional[str] = None
    rank: t.Optional[int] = 0
    significant: t.Optional[bool] = False

@dataclass
class SiiCv():
    experiences: t.Optional[t.List[SiiExperience]]
    job: t.Optional[str] = None
    experience: t.Optional[str] = None
    availability: t.Optional[str] = None
    introduction: t.Optional[str] = None
    technicalSkills: t.Optional[list] = None
    functionalSkills: t.Optional[list] = None
    technology: t.Optional[str] = None
    schools: t.Optional[list] = None
    formations: t.Optional[list] = None
    diplomas: t.Optional[list] = None
    significant: t.Optional[str] = None
    ref: t.Optional[str] = None
    
    
    